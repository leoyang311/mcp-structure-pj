"""
Scorer Agent - 内容质量评分和优选
使用结构化输出替代 JSON 字符串解析，确保类型安全
"""
import asyncio
import os
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from pydantic import BaseModel, Field

from .base import BaseAgent
from ..models import ContentVersion, QualityScore, Platform, ContentType
from ..utils import evaluate_content_quality
from ..utils.enhanced_prompts import get_enhanced_scoring_prompt
from ..utils.anti_hallucination import FactCheckingMixin
from ..core.openai_client import get_async_client, get_default_model, structured_completion


# ── 结构化输出模型 ──────────────────────────────────────────────────────────────

class AIAssessment(BaseModel):
    overall_assessment: str = Field(description="综合评估分析，200字以内")
    score_adjustment: int = Field(ge=-10, le=10, description="分数调整，-10到+10")
    improvement_suggestions: List[str] = Field(
        max_length=3, description="具体改进建议，最多3条"
    )
    strengths: List[str] = Field(max_length=3, description="内容优点，最多3条")
    weaknesses: List[str] = Field(max_length=3, description="内容问题，最多3条")


class ScorerAgent(FactCheckingMixin, BaseAgent):
    """
    评分 Agent - 结构化输出保证评估结果类型安全，无需正则解析
    """

    def __init__(self, openai_client=None, logger=None):
        super().__init__("scorer_agent", logger)
        self.sync_client = openai_client  # 兼容旧接口
        self._async_client = None

    def _get_async_client(self):
        if self._async_client is None:
            self._async_client = get_async_client()
        return self._async_client

    # ── 主处理入口 ──────────────────────────────────────────────────────────────

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        content_versions: List[ContentVersion] = input_data.get("content_versions", [])
        video_versions: List[ContentVersion] = input_data.get("video_versions", [])
        research_data = input_data.get("research_data")

        all_versions = content_versions + video_versions

        if not all_versions:
            raise ValueError("No content versions to score")

        self.logger.info(f"📊 开始评估 {len(all_versions)} 个内容版本")

        # 并行评分
        scoring_tasks = [
            self._score_content_version(v, research_data) for v in all_versions
        ]
        scoring_results = await asyncio.gather(*scoring_tasks, return_exceptions=True)

        quality_scores: Dict[str, QualityScore] = {}
        detailed_feedback: Dict[str, Dict[str, List[str]]] = {}
        valid_results: List[Tuple[ContentVersion, QualityScore]] = []

        for version, result in zip(all_versions, scoring_results):
            if isinstance(result, Exception):
                self.logger.error(f"版本 {version.version_id} 评分失败: {result}")
                continue
            score, feedback = result
            quality_scores[version.version_id] = score
            detailed_feedback[version.version_id] = feedback
            valid_results.append((version, score))

        best_versions = self._select_best_versions(valid_results)
        ranking = sorted(valid_results, key=lambda x: x[1].total_score, reverse=True)

        self.logger.info(f"✅ 评分完成，{len(valid_results)} 个版本已评估")
        if ranking:
            self.logger.info("=== 评分排名 ===")
            for i, (v, s) in enumerate(ranking[:3], 1):
                self.logger.info(f"第{i}名: {v.platform.value} - {s.total_score:.1f}分")

        return {
            "quality_scores": quality_scores,
            "detailed_feedback": detailed_feedback,
            "best_versions": best_versions,
            "ranking": ranking,
            "status": "completed",
        }

    # ── 单版本评分 ──────────────────────────────────────────────────────────────

    async def _score_content_version(
        self, version: ContentVersion, research_data=None
    ) -> Tuple[QualityScore, Dict[str, List[str]]]:
        keywords = research_data.key_points[:5] if research_data else []

        quality_score, feedback = evaluate_content_quality(
            text=version.content,
            title=version.title,
            platform=version.platform,
            keywords=keywords,
        )

        # AI 结构化评估
        assessment = await self._get_ai_assessment(version, research_data)

        if assessment:
            feedback["AI专业评估"] = [assessment.overall_assessment]
            if assessment.strengths:
                feedback["优势"] = assessment.strengths
            if assessment.weaknesses:
                feedback["问题"] = assessment.weaknesses
            if assessment.improvement_suggestions:
                feedback["改进建议"] = assessment.improvement_suggestions

            if assessment.score_adjustment != 0:
                old = quality_score.total_score
                quality_score.total_score = max(
                    0, min(100, old + assessment.score_adjustment)
                )
                feedback["分数调整"] = [
                    f"AI调整: {assessment.score_adjustment:+d}分 "
                    f"({old:.1f} → {quality_score.total_score:.1f})"
                ]

        self.logger.info(
            f"版本 {version.version_id[:8]}… 评分: {quality_score.total_score:.1f}分"
        )
        return quality_score, feedback

    # ── AI 结构化评估（核心升级点）───────────────────────────────────────────────

    async def _get_ai_assessment(
        self, version: ContentVersion, research_data=None
    ) -> Optional[AIAssessment]:
        """
        使用结构化输出替代 JSON 字符串 + 正则解析：
        直接返回 Pydantic 模型实例，类型安全、无解析错误
        """
        client = self._get_async_client()
        model = os.getenv("SCORER_MODEL", get_default_model())

        scoring_prompt = get_enhanced_scoring_prompt()
        research_context = research_data.summary if research_data else "无研究背景"

        try:
            assessment = await structured_completion(
                client=client,
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是专业内容质量评估专家，基于心理学洞察和平台特征进行精准评估。"
                            f"\n\n{scoring_prompt}"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"平台: {version.platform.value}\n"
                            f"标题: {version.title}\n"
                            f"内容类型: {version.content_type.value}\n\n"
                            f"内容正文:\n{version.content[:2000]}\n\n"
                            f"研究背景:\n{research_context[:500]}\n\n"
                            "请从真实性、心理价值、平台适配、内容价值、传播潜力五个维度评估。"
                        ),
                    },
                ],
                response_model=AIAssessment,
                temperature=0.3,
                max_tokens=800,
            )
            self.logger.debug(
                f"AI评估完成: 分数调整 {assessment.score_adjustment:+d}"
            )
            return assessment

        except Exception as e:
            self.logger.error(f"AI结构化评估失败: {e}")
            return None

    # ── 平台/内容类型加分 ────────────────────────────────────────────────────────

    def _get_platform_bonus(self, version: ContentVersion) -> int:
        content = version.content
        platform = version.platform
        bonus = 0

        if platform == Platform.XIAOHONGSHU:
            if self._has_emojis(content): bonus += 5
            if self._has_hashtags(content): bonus += 5
            if self._has_personal_tone(content): bonus += 3
            if len(content.split("\n\n")) >= 3: bonus += 3

        elif platform == Platform.DOUYIN:
            if self._has_trending_words(content): bonus += 8
            if self._has_strong_opening(content): bonus += 5
            if self._has_call_to_action(content): bonus += 4

        elif platform == Platform.BILIBILI:
            if self._has_structured_content(content): bonus += 6
            if self._has_educational_value(content): bonus += 8
            if self._has_engagement_elements(content): bonus += 4

        elif platform == Platform.WECHAT:
            if self._has_professional_tone(content): bonus += 6
            if self._has_data_support(content): bonus += 8
            if self._has_clear_structure(content): bonus += 5

        return bonus

    # ── 最优版本选择 ────────────────────────────────────────────────────────────

    def _select_best_versions(
        self, scored: List[Tuple[ContentVersion, QualityScore]]
    ) -> Dict[Platform, ContentVersion]:
        platform_map: Dict[Platform, List[Tuple[ContentVersion, QualityScore]]] = {}
        for v, s in scored:
            platform_map.setdefault(v.platform, []).append((v, s))
        return {
            plat: max(items, key=lambda x: x[1].total_score)[0]
            for plat, items in platform_map.items()
        }

    # ── 内容分析辅助方法 ────────────────────────────────────────────────────────

    def _has_emojis(self, content: str) -> bool:
        import re
        return len(re.findall(r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]", content)) >= 3

    def _has_hashtags(self, content: str) -> bool:
        import re
        return len(re.findall(r"#[^#\s]+#", content)) >= 2

    def _has_personal_tone(self, content: str) -> bool:
        return any(w in content for w in ["我", "姐妹", "大家", "你们", "咱们", "小伙伴"])

    def _has_trending_words(self, content: str) -> bool:
        return any(w in content for w in ["火爆", "热门", "必看", "绝了", "震惊", "太棒了"])

    def _has_strong_opening(self, content: str) -> bool:
        first = content.split("\n")[0] if content else ""
        return any(w in first for w in ["嘿", "你知道", "震惊", "必看", "重磅"])

    def _has_call_to_action(self, content: str) -> bool:
        return any(w in content for w in ["关注", "点赞", "收藏", "分享", "评论", "三连"])

    def _has_structured_content(self, content: str) -> bool:
        return content.count("#") >= 2 or content.count("===") >= 2

    def _has_educational_value(self, content: str) -> bool:
        return any(w in content for w in ["学习", "教程", "方法", "技巧", "原理", "分析", "解释"])

    def _has_engagement_elements(self, content: str) -> bool:
        return any(w in content for w in ["大家", "同学", "朋友", "评论", "弹幕", "问题"])

    def _has_professional_tone(self, content: str) -> bool:
        words = ["分析", "研究", "数据", "报告", "趋势", "市场", "发展"]
        return sum(1 for w in words if w in content) >= 3

    def _has_data_support(self, content: str) -> bool:
        import re
        return bool(re.search(r"\d+%|\d+倍|\d+万|\d+亿", content)) or any(
            w in content for w in ["数据", "统计", "调查", "研究显示"]
        )

    def _has_clear_structure(self, content: str) -> bool:
        indicators = content.count("##") + content.count("### ") + content.count("**")
        return indicators >= 3 or len(content.split("\n\n")) >= 5
