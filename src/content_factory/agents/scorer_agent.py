"""
Scorer Agent - 内容质量评分和优选
集成反幻觉评分确保内容准确性
"""
import asyncio
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
    
    def __init__(self, logger=None):
        super().__init__("scorer_agent", logger)
    
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
        
        self.logger.info(f"Starting quality evaluation for {len(all_versions)} content versions")
        
        # 并行评分所有版本
        scoring_tasks = [
            self._score_content_version(version, research_data)
            for version in all_versions
        ]
        
        scoring_results = await asyncio.gather(*scoring_tasks, return_exceptions=True)
        
        # 处理评分结果
        quality_scores = {}
        valid_results = []
        
        for version, result in zip(all_versions, scoring_results):
            if not isinstance(result, Exception):
                quality_scores[version.version_id] = result
                valid_results.append((version, result))
            else:
                self.logger.error(f"Failed to score version {version.version_id}: {str(result)}")
        
        # 选择最佳版本
        best_versions = self._select_best_versions(valid_results)
        
        # 创建排名
        ranking = sorted(valid_results, key=lambda x: x[1].total_score, reverse=True)
        
        self.logger.info(f"Completed scoring {len(valid_results)} versions")
        
        return {
            "quality_scores": quality_scores,
            "best_versions": best_versions,
            "ranking": ranking,
            "status": "completed"
        }
    
    async def _score_content_version(
        self, 
        version: ContentVersion, 
        research_data=None
    ) -> QualityScore:
        """
        对单个内容版本进行评分
        """
        try:
            # 提取关键词用于评分
            keywords = []
            if research_data:
                keywords = research_data.key_points[:5]
            
            # 调用质量评估函数
            quality_score = evaluate_content_quality(
                text=version.content,
                title=version.title,
                platform=version.platform,
                keywords=keywords
            )
            
            # 添加额外的平台特定评分
            await self._apply_platform_specific_scoring(version, quality_score)
            
            # 添加内容类型特定评分
            await self._apply_content_type_scoring(version, quality_score)
            
            # 重新计算总分
            quality_score.calculate_total()
            
            self.logger.debug(f"Scored version {version.version_id}: {quality_score.total_score:.2f}")
            
            return quality_score
            
        except Exception as e:
            self.logger.error(f"Failed to score content version: {str(e)}")
            raise
    
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
