"""
Video Agent - 视频内容制作
"""
import asyncio
from typing import Any, Dict, List
from datetime import datetime
import uuid

from .base import BaseAgent
from ..models import ContentVersion, Platform, ContentType, ResearchData
from ..utils import get_video_spec


class VideoAgent(BaseAgent):
    """
    视频Agent - 负责生成视频脚本和相关内容
    """
    
    def __init__(self, openai_client=None, logger=None):
        super().__init__("video_agent", logger)
        self.openai_client = openai_client
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理视频制作任务
        
        Args:
            input_data: {
                "research_data": ResearchData,
                "platforms": List[Platform],
                "content_versions": List[ContentVersion]  # 文字版本作为参考
            }
            
        Returns:
            Dict[str, Any]: {
                "video_versions": List[ContentVersion],
                "status": "completed"
            }
        """
        research_data = input_data.get("research_data")
        platforms = input_data.get("platforms", [])
        content_versions = input_data.get("content_versions", [])
        
        if not research_data:
            raise ValueError("Research data is required for video production")
        
        # 过滤支持视频的平台
        video_platforms = [p for p in platforms if self._supports_video(p)]
        
        if not video_platforms:
            self.logger.info("No video platforms specified, skipping video generation")
            return {
                "video_versions": [],
                "status": "completed"
            }
        
        self.logger.info(f"Starting video content generation for platforms: {video_platforms}")
        
        video_versions = []
        
        # 为每个视频平台生成内容
        for platform in video_platforms:
            platform_enum = Platform(platform) if isinstance(platform, str) else platform
            
            # 找到对应的文字版本作为参考
            reference_content = self._find_reference_content(content_versions, platform_enum)
            
            try:
                video_version = await self._generate_video_content(
                    research_data, platform_enum, reference_content
                )
                video_versions.append(video_version)
                
            except Exception as e:
                self.logger.error(f"Failed to generate video content for {platform}: {str(e)}")
                continue
        
        self.logger.info(f"Generated {len(video_versions)} video versions")
        
        return {
            "video_versions": video_versions,
            "status": "completed"
        }
    
    def _supports_video(self, platform) -> bool:
        """检查平台是否支持视频"""
        video_platforms = [Platform.BILIBILI, Platform.DOUYIN, Platform.XIAOHONGSHU]
        platform_enum = Platform(platform) if isinstance(platform, str) else platform
        return platform_enum in video_platforms
    
    def _find_reference_content(self, content_versions: List[ContentVersion], platform: Platform) -> ContentVersion:
        """找到对应平台的文字版本作为参考"""
        for version in content_versions:
            if version.platform == platform:
                return version
        return None
    
    async def _generate_video_content(
        self, 
        research_data: ResearchData, 
        platform: Platform, 
        reference_content: ContentVersion = None
    ) -> ContentVersion:
        """
        生成视频内容
        """
        try:
            # 获取视频规格
            video_spec = get_video_spec(platform)
            if not video_spec:
                raise ValueError(f"No video spec found for platform {platform}")
            
            # 生成视频脚本
            script = await self._generate_video_script(research_data, platform, video_spec, reference_content)
            
            # 生成视觉规划
            visual_plan = await self._generate_visual_plan(research_data, platform, video_spec)
            
            # 生成字幕内容
            subtitles = await self._generate_subtitles(script, platform)
            
            # 构建元数据
            metadata = {
                "video_spec": {
                    "duration_range": video_spec.duration_range,
                    "resolution": video_spec.resolution,
                    "orientation": video_spec.orientation,
                    "style": video_spec.style,
                },
                "visual_plan": visual_plan,
                "subtitles": subtitles,
                "estimated_duration": self._estimate_duration(script),
                "generated_at": datetime.now().isoformat(),
            }
            
            # 生成标题
            title = await self._generate_video_title(research_data, platform)
            
            # 创建视频版本
            video_version = ContentVersion(
                version_id=str(uuid.uuid4()),
                platform=platform,
                content_type=ContentType.VIDEO_SCRIPT,
                title=title,
                content=script,
                metadata=metadata,
                created_at=datetime.now()
            )
            
            return video_version
            
        except Exception as e:
            self.logger.error(f"Video content generation failed: {str(e)}")
            raise
    
    async def _generate_video_script(
        self, 
        research_data: ResearchData, 
        platform: Platform, 
        video_spec, 
        reference_content: ContentVersion = None
    ) -> str:
        """
        生成视频脚本
        """
        try:
            if platform == Platform.DOUYIN:
                return await self._generate_douyin_script(research_data, video_spec)
            elif platform == Platform.BILIBILI:
                return await self._generate_bilibili_script(research_data, video_spec, reference_content)
            elif platform == Platform.XIAOHONGSHU:
                return await self._generate_xiaohongshu_script(research_data, video_spec)
            else:
                return await self._generate_generic_script(research_data, video_spec)
                
        except Exception as e:
            self.logger.error(f"Script generation failed: {str(e)}")
            raise
    
    async def _generate_douyin_script(self, research_data: ResearchData, video_spec) -> str:
        """
        生成抖音视频脚本 (15-60秒)
        """
        topic = research_data.topic
        key_points = research_data.key_points[:3]
        
        script = f"""【抖音视频脚本】

=== 开场 (0-5秒) ===
[镜头：特写镜头，充满活力]
嘿！你知道{topic}吗？今天给你揭秘！

=== 核心内容 (5-45秒) ===
[镜头：快切镜头，配合手势]

重点1 (5-20秒)：
{key_points[0] if key_points else f'{topic}的第一个重点'}
[视觉提示：文字动画 + 图标]

重点2 (20-35秒)：
{key_points[1] if len(key_points) > 1 else f'{topic}的第二个重点'}
[视觉提示：转场效果 + 重点标记]

重点3 (35-45秒)：
{key_points[2] if len(key_points) > 2 else f'{topic}的第三个重点'}
[视觉提示：震撼效果]

=== 结尾 (45-60秒) ===
[镜头：正面直视，真诚表达]
关注我，带你了解更多{topic}秘密！

=== 文案要求 ===
- 语速：150-180字/分钟
- 语调：充满活力，有节奏感
- 配乐：节奏感强的背景音乐
- 字幕：关键词高亮，动态效果"""

        return script
    
    async def _generate_bilibili_script(
        self, 
        research_data: ResearchData, 
        video_spec, 
        reference_content: ContentVersion = None
    ) -> str:
        """
        生成B站视频脚本 (3-10分钟)
        """
        topic = research_data.topic
        key_points = research_data.key_points
        
        script = f"""【B站视频脚本】

=== 开场 (0-30秒) ===
[镜头：正面中景，友好问候]
大家好，我是[UP主名称]。今天给大家带来关于{topic}的详细解析。

[显示标题卡片]
相信很多同学对{topic}都很感兴趣，那么这期视频就来系统地介绍一下。

=== 大纲介绍 (30秒-1分钟) ===
[镜头：屏幕录制或PPT展示]
今天的内容主要分为以下几个部分：
{chr(10).join(f"{i+1}. {point}" for i, point in enumerate(key_points[:4]))}

=== 主要内容 (1分钟-8分钟) ==="""

        # 为每个关键点生成详细内容
        for i, point in enumerate(key_points[:4], 1):
            script += f"""

--- 第{i}部分：{point} ---
[镜头：结合图表或演示]
[详细解释内容，包含实例和数据支撑]
这里需要详细展开{point}的相关内容...

"""

        script += """=== 总结 (8-9分钟) ===
[镜头：正面中景]
总结一下今天的内容：
- 核心要点回顾
- 实践建议
- 注意事项

=== 结尾 (9-10分钟) ===
[镜头：亲和力表达]
如果这期视频对你有帮助，别忘了三连支持！
有问题可以在评论区留言，我会及时回复。

下期预告：[下期内容预告]

=== 制作要求 ===
- 语速：120-140字/分钟
- 画质：1080P以上
- 字幕：完整字幕，关键词标注
- 配乐：轻松背景音乐，不抢夺注意力"""

        return script
    
    async def _generate_xiaohongshu_script(self, research_data: ResearchData, video_spec) -> str:
        """
        生成小红书视频脚本 (30-90秒)
        """
        topic = research_data.topic
        key_points = research_data.key_points[:3]
        
        script = f"""【小红书视频脚本】

=== 开场 (0-10秒) ===
[镜头：美观场景，生活化布置]
姐妹们！今天分享{topic}的超全攻略！

=== 内容展示 (10-70秒) ===
[镜头：分屏展示或产品特写]

要点1 (10-30秒)：
{key_points[0] if key_points else f'{topic}的关键点'}
[视觉：精美图片 + 文字说明]

要点2 (30-50秒)：
{key_points[1] if len(key_points) > 1 else f'{topic}的重要提示'}
[视觉：对比效果 + 标注]

要点3 (50-70秒)：
{key_points[2] if len(key_points) > 2 else f'{topic}的实用建议'}
[视觉：成果展示]

=== 结尾 (70-90秒) ===
[镜头：亲密感表达]
记得收藏起来慢慢看！
有问题评论区见 💕

=== 制作要求 ===
- 滤镜：温暖明亮
- 音乐：轻快愉悦
- 文字：可爱字体，颜色丰富
- 节奏：舒缓不紧迫"""

        return script
    
    async def _generate_generic_script(self, research_data: ResearchData, video_spec) -> str:
        """
        生成通用视频脚本
        """
        topic = research_data.topic
        
        script = f"""【通用视频脚本】

主题：{topic}

开场：
简单介绍主题和价值

主要内容：
{chr(10).join(f"- {point}" for point in research_data.key_points[:3])}

结尾：
总结和行动引导

制作规格：
- 时长：{video_spec.duration_range[0]}-{video_spec.duration_range[1]}秒
- 分辨率：{video_spec.resolution[0]}x{video_spec.resolution[1]}
- 方向：{video_spec.orientation}"""

        return script
    
    async def _generate_visual_plan(self, research_data: ResearchData, platform: Platform, video_spec) -> Dict[str, Any]:
        """
        生成视觉规划
        """
        plan = {
            "style": video_spec.style,
            "color_scheme": self._get_platform_color_scheme(platform),
            "visual_elements": [
                "标题卡片",
                "关键词高亮",
                "数据图表",
                "转场动画",
            ],
            "camera_angles": [
                "正面中景" if platform == Platform.BILIBILI else "特写镜头",
                "产品特写" if platform == Platform.XIAOHONGSHU else "屏幕录制",
            ],
        }
        
        return plan
    
    def _get_platform_color_scheme(self, platform: Platform) -> List[str]:
        """获取平台配色方案"""
        schemes = {
            Platform.DOUYIN: ["#000000", "#FF0050", "#FFFFFF"],
            Platform.BILIBILI: ["#00A1D6", "#FFFFFF", "#F25D8E"],
            Platform.XIAOHONGSHU: ["#FF2442", "#FFFFFF", "#FFB6C1"],
        }
        return schemes.get(platform, ["#000000", "#FFFFFF"])
    
    async def _generate_subtitles(self, script: str, platform: Platform) -> List[Dict[str, Any]]:
        """
        生成字幕内容
        """
        # 简化的字幕生成 (实际应用中应该更智能)
        lines = [line.strip() for line in script.split('\n') if line.strip() and not line.startswith('[') and not line.startswith('===')]
        
        subtitles = []
        current_time = 0
        
        for line in lines[:10]:  # 限制字幕数量
            if line and not line.startswith('=') and not line.startswith('-'):
                duration = len(line) * 0.1  # 简单的时长估算
                subtitles.append({
                    "text": line,
                    "start_time": current_time,
                    "end_time": current_time + duration,
                    "style": self._get_subtitle_style(platform)
                })
                current_time += duration + 0.5
        
        return subtitles
    
    def _get_subtitle_style(self, platform: Platform) -> Dict[str, Any]:
        """获取字幕样式"""
        styles = {
            Platform.DOUYIN: {
                "font_size": "large",
                "font_weight": "bold",
                "color": "#FFFFFF",
                "background": "rgba(0,0,0,0.5)",
                "animation": "fade_in"
            },
            Platform.BILIBILI: {
                "font_size": "medium",
                "font_weight": "normal",
                "color": "#FFFFFF",
                "background": "rgba(0,0,0,0.7)",
                "animation": "none"
            },
            Platform.XIAOHONGSHU: {
                "font_size": "medium",
                "font_weight": "bold",
                "color": "#FF2442",
                "background": "rgba(255,255,255,0.8)",
                "animation": "bounce"
            },
        }
        return styles.get(platform, styles[Platform.BILIBILI])
    
    def _estimate_duration(self, script: str) -> float:
        """
        估算视频时长 (基于脚本内容)
        """
        # 简单的时长估算逻辑
        text_content = len([line for line in script.split('\n') if line.strip() and not line.startswith('[')])
        return min(max(text_content * 2, 30), 600)  # 30秒到10分钟之间
    
    async def _generate_video_title(self, research_data: ResearchData, platform: Platform) -> str:
        """
        生成视频标题
        """
        topic = research_data.topic
        
        if platform == Platform.DOUYIN:
            return f"{topic}的秘密，99%的人不知道！"
        elif platform == Platform.BILIBILI:
            return f"【深度解析】关于{topic}，这可能是最全面的介绍"
        elif platform == Platform.XIAOHONGSHU:
            return f"{topic}完整攻略！姐妹们必看 ✨"
        else:
            return f"{topic} - 详细解读"
