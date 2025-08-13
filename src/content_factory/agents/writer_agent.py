"""
Writer Agent - 内容写作和生成
集成反幻觉技术确保内容准确性
"""
import asyncio
from typing import Any, Dict, List
from datetime import datetime
import uuid

from .base import BaseAgent
from ..models import ContentVersion, Platform, ContentType, ResearchData
from ..utils import get_content_prompt_template, get_title_generation_prompt
from ..utils.anti_hallucination import FactCheckingMixin


class WriterAgent(FactCheckingMixin, BaseAgent):
    """
    写作Agent - 负责根据研究数据生成多平台适配的内容
    集成反幻觉技术确保内容准确性和可信度
    """
    
    def __init__(self, openai_client=None, logger=None):
        super().__init__("writer_agent", logger)
        self.openai_client = openai_client
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理写作任务
        
        Args:
            input_data: {
                "research_data": ResearchData,
                "platforms": List[Platform],
                "versions_per_platform": int
            }
            
        Returns:
            Dict[str, Any]: {
                "content_versions": List[ContentVersion],
                "status": "completed"
            }
        """
        research_data = input_data.get("research_data")
        platforms = input_data.get("platforms", [])
        versions_per_platform = input_data.get("versions_per_platform", 3)
        
        if not research_data:
            raise ValueError("Research data is required for writing")
        
        if not platforms:
            raise ValueError("At least one platform is required")
        
        self.logger.info(f"Starting content generation for platforms: {platforms}")
        
        content_versions = []
        
        # 为每个平台生成内容
        for platform in platforms:
            platform_enum = Platform(platform) if isinstance(platform, str) else platform
            
            # 并行生成多个版本
            tasks = [
                self._generate_content_version(research_data, platform_enum, i + 1)
                for i in range(versions_per_platform)
            ]
            
            versions = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤成功的版本
            for version in versions:
                if not isinstance(version, Exception):
                    content_versions.append(version)
        
        self.logger.info(f"Generated {len(content_versions)} content versions")
        
        return {
            "content_versions": content_versions,
            "status": "completed"
        }
    
    async def _generate_content_version(
        self, 
        research_data: ResearchData, 
        platform: Platform, 
        version_num: int
    ) -> ContentVersion:
        """
        为特定平台生成一个内容版本
        """
        try:
            # 生成标题
            titles = await self._generate_titles(research_data, platform)
            selected_title = titles[0] if titles else f"{research_data.topic} - 深度解析"
            
            # 生成内容
            content = await self._generate_content(research_data, platform, selected_title)
            
            # 创建内容版本
            version = ContentVersion(
                version_id=str(uuid.uuid4()),
                platform=platform,
                content_type=ContentType.ARTICLE,
                title=selected_title,
                content=content,
                metadata={
                    "version_number": version_num,
                    "word_count": len(content.replace(' ', '').replace('\n', '')),
                    "generated_at": datetime.now().isoformat(),
                    "research_topic": research_data.topic,
                },
                created_at=datetime.now()
            )
            
            return version
            
        except Exception as e:
            self.logger.error(f"Failed to generate content for {platform}: {str(e)}")
            raise
    
    async def _generate_titles(self, research_data: ResearchData, platform: Platform) -> List[str]:
        """
        生成标题列表
        """
        try:
            prompt_template = get_title_generation_prompt(platform)
            
            # 准备提示词数据
            key_points_text = "、".join(research_data.key_points[:3])
            prompt = prompt_template.format(
                topic=research_data.topic,
                key_points=key_points_text
            )
            
            # 如果有LLM客户端，使用AI生成
            if self.openai_client:
                response = await self._call_llm(prompt)
                titles = [title.strip() for title in response.split('\n') if title.strip()]
                if titles:
                    return titles[:3]
            
            # 回退到模板生成
            return self._generate_fallback_titles(research_data, platform)
            
        except Exception as e:
            self.logger.error(f"Title generation failed: {str(e)}")
            return self._generate_fallback_titles(research_data, platform)
    
    def _generate_fallback_titles(self, research_data: ResearchData, platform: Platform) -> List[str]:
        """
        生成回退标题
        """
        topic = research_data.topic
        
        if platform == Platform.XIAOHONGSHU:
            return [
                f"必看！{topic}的完整攻略 ✨",
                f"{topic}踩坑指南，新手必备 🔥",
                f"关于{topic}，你知道这些吗？ 💡"
            ]
        elif platform == Platform.DOUYIN:
            return [
                f"{topic}火爆全网的秘密！",
                f"震惊！{topic}居然还能这样？",
                f"3分钟了解{topic}，绝了！"
            ]
        elif platform == Platform.BILIBILI:
            return [
                f"【深度解析】{topic}完全指南",
                f"关于{topic}，这可能是最全面的分析",
                f"{topic}从入门到精通 - 全程干货"
            ]
        else:  # 微信公众号
            return [
                f"{topic}：深度分析与实践指南",
                f"解读{topic}：机遇、挑战与未来趋势",
                f"{topic}全景解析：你需要知道的一切"
            ]
    
    async def _generate_content(
        self, 
        research_data: ResearchData, 
        platform: Platform, 
        title: str
    ) -> str:
        """
        生成文章内容
        """
        try:
            prompt_template = get_content_prompt_template(platform)
            
            # 构建研究数据文本
            research_text = f"""
话题：{research_data.topic}

关键要点：
{chr(10).join(f"• {point}" for point in research_data.key_points)}

市场趋势：
{chr(10).join(f"• {trend}" for trend in research_data.trends)}

研究总结：
{research_data.summary}
            """.strip()
            
            prompt = prompt_template.format(
                research_data=research_text,
                topic=research_data.topic
            )
            
            # 如果有LLM客户端，使用AI生成
            if self.openai_client:
                content = await self._call_llm(prompt)
                if content and len(content.strip()) > 100:
                    return content.strip()
            
            # 回退到模板生成
            return self._generate_fallback_content(research_data, platform, title)
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {str(e)}")
            return self._generate_fallback_content(research_data, platform, title)
    
    def _generate_fallback_content(
        self, 
        research_data: ResearchData, 
        platform: Platform, 
        title: str
    ) -> str:
        """
        生成回退内容
        """
        topic = research_data.topic
        key_points = research_data.key_points[:3]
        trends = research_data.trends[:2]
        
        if platform == Platform.XIAOHONGSHU:
            content = f"""✨ {title}

姐妹们！今天来和大家分享{topic}的超全攻略！

🌟 核心要点
{chr(10).join(f"▫️ {point}" for point in key_points)}

🔥 最新趋势
{chr(10).join(f"▫️ {trend}" for trend in trends)}

💡 个人心得
经过深入研究，我发现{topic}真的太有意思了！特别是对于想要了解这个领域的小白来说，掌握这些要点就够了。

📝 总结
{research_data.summary[:200]}...

#话题分享# #{topic}# #干货分享#

喜欢的话记得点赞收藏哦 💕"""
            
        elif platform == Platform.DOUYIN:
            content = f"""{title}

🚀 {topic}最新解析来了！

核心要点：
{chr(10).join(f"✅ {point}" for point in key_points)}

🔥 趋势分析：
{chr(10).join(f"📈 {trend}" for trend in trends)}

💪 总结：{research_data.summary[:150]}

关注我，带你了解更多！
#{topic}# #热门# #必看#"""
            
        elif platform == Platform.BILIBILI:
            content = f"""# {title}

## 前言
大家好，今天给大家带来关于{topic}的深度分析。

## 核心内容

### 关键要点
{chr(10).join(f"- {point}" for point in key_points)}

### 趋势分析
{chr(10).join(f"- {trend}" for trend in trends)}

## 详细解析

{research_data.summary}

## 总结

通过这次分析，我们可以看到{topic}具有很大的发展潜力。希望这个视频对大家有所帮助。

如果觉得有用，别忘了三连支持！"""
            
        else:  # 微信公众号
            content = f"""# {title}

## 引言

在当前快速发展的时代，{topic}正在成为一个备受关注的领域。本文将从多个维度对{topic}进行深度分析。

## 核心要点分析

{chr(10).join(f"### {i+1}. {point}" for i, point in enumerate(key_points))}

## 市场趋势洞察

{chr(10).join(f"**{trend}**" for trend in trends)}

## 深度分析

{research_data.summary}

## 结论与建议

综合以上分析，{topic}在未来具有巨大的发展潜力。对于相关从业者和关注者来说，及时把握机遇、了解趋势变化显得尤为重要。

---
*本文基于最新研究资料整理，如有更新请关注后续内容。*"""
        
        return content
    
    async def _call_llm(self, prompt: str) -> str:
        """
        调用LLM生成内容
        """
        try:
            if not self.openai_client:
                self.logger.warning("No OpenAI client available, using fallback content")
                raise Exception("No OpenAI client available")
            
            # 调用真实的OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # 或使用配置的模型
                messages=[
                    {"role": "system", "content": "你是一个专业的内容创作者，擅长创作高质量、有价值的内容。请根据用户要求创作吸引人且有深度的内容。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            self.logger.info(f"Successfully generated content via OpenAI API (length: {len(content)})")
            return content
            
        except Exception as e:
            self.logger.error(f"LLM call failed: {str(e)}")
            raise

    # 实现FactCheckingMixin要求的方法
    async def _generate_initial_content(self, prompt: str, platform: str, research_data: Dict) -> str:
        """生成初始内容 - 实现FactCheckingMixin接口"""
        try:
            platform_enum = Platform(platform.lower()) if isinstance(platform, str) else platform
            research_data_obj = ResearchData.from_dict(research_data) if isinstance(research_data, dict) else research_data
            
            # 生成标题
            titles = await self._generate_titles(research_data_obj, platform_enum)
            title = titles[0] if titles else f"{research_data_obj.topic} - {platform}"
            
            # 生成内容
            content = await self._generate_content(research_data_obj, platform_enum, title)
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error generating initial content: {e}")
            return "Error generating content"

    async def generate_verified_content_for_platform(
        self, 
        research_data: ResearchData, 
        platform: Platform
    ) -> List[ContentVersion]:
        """
        为指定平台生成经过验证的内容
        """
        try:
            self.logger.info(f"Generating verified content for platform: {platform}")
            
            # 使用反幻觉混入类生成验证内容
            verified_content = await self.generate_verified_content(
                prompt=research_data.topic,
                platform=platform.value,
                research_data=research_data.to_dict()
            )
            
            # 生成标题
            titles = await self._generate_titles(research_data, platform)
            
            # 创建内容版本
            content_versions = []
            for i, title in enumerate(titles[:3]):  # 生成3个版本
                version = ContentVersion(
                    id=str(uuid.uuid4()),
                    title=title,
                    content=verified_content,
                    platform=platform,
                    content_type=ContentType.ARTICLE,
                    score=0.0,
                    created_at=datetime.now()
                )
                content_versions.append(version)
            
            return content_versions
            
        except Exception as e:
            self.logger.error(f"Error generating verified content for {platform}: {str(e)}")
            raise
