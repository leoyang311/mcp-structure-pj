"""
Scorer Agent - 内容质量评分和优选
集成反幻觉评分确保内容准确性
"""
import asyncio
import os
from typing import Any, Dict, List, Tuple
from datetime import datetime

from .base import BaseAgent
from ..models import ContentVersion, QualityScore, Platform, ContentType
from ..utils import evaluate_content_quality
from ..utils.enhanced_prompts import get_enhanced_scoring_prompt
from ..utils.anti_hallucination import FactCheckingMixin


class ScorerAgent(FactCheckingMixin, BaseAgent):
    """
    评分Agent - 负责对生成的内容进行质量评分和优选
    集成反幻觉技术确保评分准确性
    """
    
    def __init__(self, openai_client=None, logger=None):
        super().__init__("scorer_agent", logger)
        self.openai_client = openai_client
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理评分任务
        
        Args:
            input_data: {
                "content_versions": List[ContentVersion],
                "video_versions": List[ContentVersion],
                "research_data": ResearchData
            }
            
        Returns:
            Dict[str, Any]: {
                "quality_scores": Dict[str, QualityScore],
                "detailed_feedback": Dict[str, Dict[str, List[str]]],
                "best_versions": Dict[Platform, ContentVersion],
                "ranking": List[Tuple[ContentVersion, QualityScore]],
                "status": "completed"
            }
        """
        content_versions = input_data.get("content_versions", [])
        video_versions = input_data.get("video_versions", [])
        research_data = input_data.get("research_data")
        
        all_versions = content_versions + video_versions
        
        if not all_versions:
            raise ValueError("No content versions to score")
        
        self.logger.info(f"开始基于心理洞察评估 {len(all_versions)} 个内容版本")
        
        # 并行评分所有版本
        scoring_tasks = [
            self._score_content_version(version, research_data)
            for version in all_versions
        ]
        
        scoring_results = await asyncio.gather(*scoring_tasks, return_exceptions=True)
        
        # 处理评分结果
        quality_scores = {}
        detailed_feedback = {}
        valid_results = []
        
        for version, result in zip(all_versions, scoring_results):
            if not isinstance(result, Exception):
                score, feedback = result
                quality_scores[version.version_id] = score
                detailed_feedback[version.version_id] = feedback
                valid_results.append((version, score))
            else:
                self.logger.error(f"版本 {version.version_id} 评分失败: {str(result)}")
        
        # 选择最佳版本
        best_versions = self._select_best_versions(valid_results)
        
        # 创建排名
        ranking = sorted(valid_results, key=lambda x: x[1].total_score, reverse=True)
        
        self.logger.info(f"评分完成，{len(valid_results)} 个版本已评估")
        
        # 输出评分概览
        if ranking:
            self.logger.info("=== 评分排名 ===")
            for i, (version, score) in enumerate(ranking[:3], 1):
                self.logger.info(f"第{i}名: {version.platform.value} - {score.total_score:.1f}分")
        
        return {
            "quality_scores": quality_scores,
            "detailed_feedback": detailed_feedback,
            "best_versions": best_versions,
            "ranking": ranking,
            "status": "completed"
        }
    
    async def _score_content_version(
        self, 
        version: ContentVersion, 
        research_data=None
    ) -> Tuple[QualityScore, Dict[str, List[str]]]:
        """
        对单个内容版本进行评分 - 基于心理洞察
        """
        try:
            # 提取关键词用于评分
            keywords = []
            if research_data:
                keywords = research_data.key_points[:5]
            
            # 调用新的质量评估函数，返回评分和详细反馈
            quality_score, feedback = evaluate_content_quality(
                text=version.content,
                title=version.title,
                platform=version.platform,
                keywords=keywords
            )
            
            # 使用AI进行深度内容评估
            ai_feedback = await self._get_ai_quality_assessment(version, research_data)
            
            # 整合AI反馈
            if ai_feedback:
                feedback["AI专业评估"] = [ai_feedback.get("overall_assessment", "")]
                
                # 根据AI评估调整分数
                ai_score = ai_feedback.get("score_adjustment", 0)
                if ai_score != 0:
                    # 调整总分，但不超过100
                    old_total = quality_score.total_score
                    quality_score.total_score = max(0, min(100, old_total + ai_score))
                    feedback["分数调整"] = [f"AI评估调整: {ai_score:+.1f}分 ({old_total:.1f} → {quality_score.total_score:.1f})"]
            
            self.logger.info(f"Version {version.version_id} 评分完成: {quality_score.total_score:.1f}分")
            
            # 记录详细反馈
            for category, items in feedback.items():
                if items:
                    self.logger.debug(f"  {category}: {'; '.join(items[:2])}")
            
            return quality_score, feedback
            
        except Exception as e:
            self.logger.error(f"内容版本评分失败: {str(e)}")
            # 返回默认低分和错误信息
            default_score = QualityScore(
                content_quality=30,
                platform_adaptation=30,
                engagement_potential=30,
                technical_quality=30,
                total_score=30
            )
            error_feedback = {"错误信息": [str(e)]}
            return default_score, error_feedback
    
    async def _get_ai_quality_assessment(
        self, 
        version: ContentVersion, 
        research_data=None
    ) -> Dict[str, Any]:
        """
        使用AI对内容进行深度评估
        """
        if not self.openai_client:
            return None
        
        try:
            # 获取基于心理洞察的评分提示词
            from ..utils.enhanced_prompts import get_enhanced_scoring_prompt
            scoring_prompt = get_enhanced_scoring_prompt()
            
            # 构建评估消息
            assessment_message = f"""
{scoring_prompt}

请评估以下内容：

## 基本信息
- 平台: {version.platform.value}
- 标题: {version.title}
- 内容类型: {version.content_type.value}

## 内容正文
{version.content}

## 研究背景
{research_data.summary if research_data else "无研究背景数据"}

请从以下维度进行评估：
1. 真实性检查（是否有AI套话？）
2. 心理价值（是否击中用户痛点？）
3. 平台适配度（是否符合平台特征？）
4. 内容价值（是否提供实用信息？）
5. 传播潜力（是否有分享转发动机？）

请给出：
- 详细评估分析（200字内）
- 分数调整建议（-10到+10分之间）
- 具体改进建议（3条内）

输出格式：
```json
{{
    "overall_assessment": "详细评估分析",
    "score_adjustment": 调整分数,
    "improvement_suggestions": ["建议1", "建议2", "建议3"],
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["问题1", "问题2"]
}}
```
"""
            
            # 调用LLM进行评估
            model_name = os.getenv("SCORER_MODEL", "gpt-4o-mini")
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的内容质量评估专家，基于心理学洞察和平台特征进行精准评估。"},
                    {"role": "user", "content": assessment_message}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            # 解析响应
            response_text = response.choices[0].message.content.strip()
            
            # 尝试提取JSON部分
            import json
            import re
            
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    ai_feedback = json.loads(json_match.group(1))
                    self.logger.debug(f"AI评估完成: {ai_feedback.get('score_adjustment', 0):+.1f}分调整")
                    return ai_feedback
                except json.JSONDecodeError:
                    self.logger.warning("AI评估响应JSON解析失败")
            
            # 如果没有找到JSON，尝试直接解析整个响应
            try:
                ai_feedback = json.loads(response_text)
                return ai_feedback
            except json.JSONDecodeError:
                self.logger.warning("AI评估响应格式无效，使用文本分析")
                return {
                    "overall_assessment": response_text[:200],
                    "score_adjustment": 0,
                    "improvement_suggestions": ["需要重新评估"],
                    "strengths": [],
                    "weaknesses": []
                }
        
        except Exception as e:
            self.logger.error(f"AI质量评估失败: {str(e)}")
            return None
    
    async def _apply_platform_specific_scoring(
        self, 
        version: ContentVersion, 
        quality_score: QualityScore
    ) -> None:
        """
        应用平台特定评分调整
        """
        try:
            platform = version.platform
            content = version.content
            title = version.title
            
            # 平台特定的加分项
            bonus_points = 0
            
            if platform == Platform.XIAOHONGSHU:
                # 小红书偏好评估
                if self._has_emojis(content):
                    bonus_points += 5
                if self._has_hashtags(content):
                    bonus_points += 5
                if self._has_personal_tone(content):
                    bonus_points += 3
                if len(content.split('\n\n')) >= 3:  # 分段明确
                    bonus_points += 3
                    
            elif platform == Platform.DOUYIN:
                # 抖音偏好评估
                if self._has_trending_words(content):
                    bonus_points += 8
                if self._has_strong_opening(content):
                    bonus_points += 5
                if self._has_call_to_action(content):
                    bonus_points += 4
                    
            elif platform == Platform.BILIBILI:
                # B站偏好评估
                if self._has_structured_content(content):
                    bonus_points += 6
                if self._has_educational_value(content):
                    bonus_points += 8
                if self._has_engagement_elements(content):
                    bonus_points += 4
                    
            elif platform == Platform.WECHAT:
                # 微信公众号偏好评估
                if self._has_professional_tone(content):
                    bonus_points += 6
                if self._has_data_support(content):
                    bonus_points += 8
                if self._has_clear_structure(content):
                    bonus_points += 5
            
            # 应用加分
            quality_score.platform_adaptation = min(100, quality_score.platform_adaptation + bonus_points)
            
        except Exception as e:
            self.logger.error(f"Platform specific scoring failed: {str(e)}")
    
    async def _apply_content_type_scoring(
        self, 
        version: ContentVersion, 
        quality_score: QualityScore
    ) -> None:
        """
        应用内容类型特定评分调整
        """
        try:
            if version.content_type == ContentType.VIDEO_SCRIPT:
                # 视频脚本特殊评分
                await self._score_video_script(version, quality_score)
            elif version.content_type == ContentType.ARTICLE:
                # 文章内容特殊评分
                await self._score_article_content(version, quality_score)
                
        except Exception as e:
            self.logger.error(f"Content type scoring failed: {str(e)}")
    
    async def _score_video_script(
        self, 
        version: ContentVersion, 
        quality_score: QualityScore
    ) -> None:
        """
        为视频脚本进行特殊评分
        """
        content = version.content
        bonus = 0
        
        # 检查脚本结构
        if "开场" in content or "=== 开场" in content:
            bonus += 5
        if "结尾" in content or "=== 结尾" in content:
            bonus += 5
        
        # 检查视觉指导
        if "[镜头" in content or "[视觉" in content:
            bonus += 8
        
        # 检查时间规划
        if any(time_marker in content for time_marker in ["秒", "分钟", "(0-", "==="] ):
            bonus += 6
        
        # 检查字幕规划
        metadata = version.metadata or {}
        if "subtitles" in metadata and metadata["subtitles"]:
            bonus += 5
        
        quality_score.technical_quality = min(100, quality_score.technical_quality + bonus)
    
    async def _score_article_content(
        self, 
        version: ContentVersion, 
        quality_score: QualityScore
    ) -> None:
        """
        为文章内容进行特殊评分
        """
        content = version.content
        title = version.title
        bonus = 0
        
        # 检查标题质量
        if len(title) <= 30 and len(title) >= 10:
            bonus += 3
        if any(word in title for word in ["深度", "全面", "完整", "必看", "攻略"]):
            bonus += 2
        
        # 检查内容结构
        if content.count('#') >= 3:  # 有层级标题
            bonus += 5
        if len(content.split('\n\n')) >= 4:  # 段落分明
            bonus += 3
        
        # 检查内容深度
        word_count = len(content.replace(' ', '').replace('\n', ''))
        if word_count >= 1000:
            bonus += 5
        
        quality_score.content_quality = min(100, quality_score.content_quality + bonus)
    
    def _select_best_versions(
        self, 
        scored_versions: List[Tuple[ContentVersion, QualityScore]]
    ) -> Dict[Platform, ContentVersion]:
        """
        为每个平台选择最佳版本
        """
        best_versions = {}
        
        # 按平台分组
        platform_versions = {}
        for version, score in scored_versions:
            platform = version.platform
            if platform not in platform_versions:
                platform_versions[platform] = []
            platform_versions[platform].append((version, score))
        
        # 为每个平台选择最高分版本
        for platform, versions in platform_versions.items():
            best_version = max(versions, key=lambda x: x[1].total_score)
            best_versions[platform] = best_version[0]
        
        return best_versions
    
    # 内容分析辅助方法
    def _has_emojis(self, content: str) -> bool:
        """检查是否包含emoji"""
        import re
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]')
        return len(emoji_pattern.findall(content)) >= 3
    
    def _has_hashtags(self, content: str) -> bool:
        """检查是否包含话题标签"""
        import re
        return len(re.findall(r'#[^#\s]+#', content)) >= 2
    
    def _has_personal_tone(self, content: str) -> bool:
        """检查是否使用个人化语调"""
        personal_words = ["我", "姐妹", "大家", "你们", "咱们", "小伙伴"]
        return any(word in content for word in personal_words)
    
    def _has_trending_words(self, content: str) -> bool:
        """检查是否包含热门词汇"""
        trending_words = ["火爆", "热门", "必看", "绝了", "震惊", "不敢相信", "太棒了"]
        return any(word in content for word in trending_words)
    
    def _has_strong_opening(self, content: str) -> bool:
        """检查是否有强力开场"""
        lines = content.split('\n')
        first_line = lines[0] if lines else ""
        strong_openings = ["嘿", "你知道", "震惊", "必看", "重磅"]
        return any(word in first_line for word in strong_openings)
    
    def _has_call_to_action(self, content: str) -> bool:
        """检查是否有行动引导"""
        cta_words = ["关注", "点赞", "收藏", "分享", "评论", "三连"]
        return any(word in content for word in cta_words)
    
    def _has_structured_content(self, content: str) -> bool:
        """检查内容是否结构化"""
        return content.count('#') >= 2 or content.count('===') >= 2
    
    def _has_educational_value(self, content: str) -> bool:
        """检查是否具有教育价值"""
        edu_keywords = ["学习", "教程", "方法", "技巧", "原理", "分析", "解释"]
        return any(word in content for word in edu_keywords)
    
    def _has_engagement_elements(self, content: str) -> bool:
        """检查是否包含互动元素"""
        engagement_words = ["大家", "同学", "朋友", "评论", "弹幕", "问题"]
        return any(word in content for word in engagement_words)
    
    def _has_professional_tone(self, content: str) -> bool:
        """检查是否使用专业语调"""
        professional_words = ["分析", "研究", "数据", "报告", "趋势", "市场", "发展"]
        return sum(1 for word in professional_words if word in content) >= 3
    
    def _has_data_support(self, content: str) -> bool:
        """检查是否有数据支撑"""
        import re
        # 检查数字、百分比、统计数据等
        has_numbers = bool(re.search(r'\d+%|\d+倍|\d+万|\d+亿', content))
        has_data_words = any(word in content for word in ["数据", "统计", "调查", "研究显示"])
        return has_numbers or has_data_words
    
    def _has_clear_structure(self, content: str) -> bool:
        """检查是否有清晰结构"""
        structure_indicators = content.count('##') + content.count('### ') + content.count('**')
        paragraphs = len(content.split('\n\n'))
        return structure_indicators >= 3 or paragraphs >= 5
