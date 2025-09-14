"""
Enhanced Writer Agent - 集成深度研究引擎和CASE框架
解决AI味、模板化、信息密度低等问题
"""
import asyncio
import os
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from .base import BaseAgent
from ..models import ContentVersion, Platform, ContentType, ResearchData
from ..core.openai_client import get_openai_client, get_default_model
from ..engines.deep_research_engine import DeepResearchEngine, StructuredResearch
from ..prompts.case_framework_prompts import (
    get_enhanced_content_generation_prompt,
    ContentQualityEnforcer
)
from ..utils.anti_hallucination import FactCheckingMixin
from ..core.anti_censorship_system import AntiCensorshipContentGenerator, CensorshipLevel


class WriterAgent(FactCheckingMixin, BaseAgent):
    """
    增强版Writer Agent - 集成深度研究引擎和CASE框架
    彻底解决内容空洞、AI味、信息密度低等问题
    """
    
    def __init__(self, openai_client=None, logger=None):
        super().__init__("enhanced_writer_agent", logger)
        self.openai_client = openai_client or get_openai_client()
        self.deep_research_engine = DeepResearchEngine()
        self.quality_enforcer = ContentQualityEnforcer()
        self.anti_censorship_generator = AntiCensorshipContentGenerator()
        self.logger.info("✅ Enhanced WriterAgent初始化完成 - 已集成深度研究引擎和反审查系统")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理写作任务 - 增强版流程
        
        Args:
            input_data: {
                "research_data": ResearchData,
                "platforms": List[Platform],
                "versions_per_platform": int
            }
            
        Returns:
            Dict[str, Any]: {
                "content_versions": List[ContentVersion],
                "quality_metrics": Dict,
                "status": "completed"
            }
        """
        research_data = input_data.get("research_data")
        platforms = input_data.get("platforms", [])
        versions_per_platform = input_data.get("versions_per_platform", 1)  # 降为1，保证质量
        # 新增：视频提示词模式（兼容多种开关）
        video_prompt_mode = bool(input_data.get("video_prompt_mode")) \
            or input_data.get("mode") in {"video_prompt", "script_prompt"} \
            or str(input_data.get("content_type", "")).lower() in {"video_script", "video_prompt"}
        video_prompt_engine = str(input_data.get("video_prompt_engine", "minimax")).lower()  # minimax | sora
        video_prompt_duration = int(input_data.get("video_prompt_duration", 6 if video_prompt_engine == "minimax" else 60))
        
        if not research_data:
            raise ValueError("Research data is required for writing")
        
        if not platforms:
            raise ValueError("At least one platform is required")
        
        self.logger.info(f"🚀 开始为{len(platforms)}个平台生成高质量内容")
        
        content_versions = []
        quality_metrics = {}
        
        # 为每个平台生成内容/或视频提示词
        for platform in platforms:
            platform_enum = Platform(platform) if isinstance(platform, str) else platform
            
            self.logger.info(f"📝 正在为{platform_enum.value}平台生成内容...")
            
            try:
                # Step 1: 深度研究增强
                enhanced_research = await self._conduct_deep_research(research_data)
                
                if video_prompt_mode:
                    # Step 2 (视频提示词模式)：生成视频生成器Prompt
                    version = await self._generate_video_prompt_version(
                        enhanced_research=enhanced_research,
                        platform=platform_enum,
                        version_num=1,
                        topic_str=research_data.topic,
                        engine=video_prompt_engine,
                        duration_seconds=video_prompt_duration,
                    )
                else:
                    # Step 2（默认）：生成高质量文章版本
                    version = await self._generate_enhanced_content_version(
                        enhanced_research, platform_enum, 1, research_data.topic
                    )
                
                if version:
                    content_versions.append(version)
                    if not video_prompt_mode:
                        quality_metrics[platform_enum.value] = {
                            "information_density": version.metadata.get("information_density", 0),
                            "case_compliance": version.metadata.get("case_compliance", 0),
                            "quality_score": version.metadata.get("quality_score", 0),
                            "specific_data_count": version.metadata.get("specific_data_count", 0)
                        }
                
                self.logger.info(f"✅ {platform_enum.value}内容生成完成 - 质量评分: {version.metadata.get('quality_score', 0):.2f}")
                
            except Exception as e:
                self.logger.error(f"❌ {platform_enum.value}内容生成失败: {e}")
                # 创建错误版本
                error_version = self._create_error_version(research_data, platform_enum, str(e))
                content_versions.append(error_version)
        
        self.logger.info(f"🎉 内容生成完成 - 共生成{len(content_versions)}个高质量版本")
        
        return {
            "content_versions": content_versions,
            "quality_metrics": quality_metrics,
            "status": "completed"
        }

    async def _generate_video_prompt_version(
        self,
        enhanced_research: StructuredResearch,
        platform: Platform,
        version_num: int,
        topic_str: str,
        engine: str = "minimax",
        duration_seconds: int = 6,
    ) -> Optional[ContentVersion]:
        """根据《AI视频生成Prompt工程指南》生成视频生成器提示词版本。

        engine: minimax(默认，6s短片) | sora(长片，60s)
        """
        try:
            # 1) 生成结构化指令骨架（本地拼装）
            if engine == "sora":
                scaffold = self._build_sora_prompt(enhanced_research, platform, topic_str, duration_seconds)
                engine_guide = (
                    "你是专业视频提示词工程师。使用Sora长视频提示策略：时间线+叙事结构+物理/空间一致性+摄影技术。"
                    "严格输出完善的中文提示词，不要复述‘时间线’标题，直接以完整可用的提示词形式输出，"
                    "确保每段内容有具体动作与画面元素，避免空洞复述主题。"
                )
            else:
                scaffold = self._build_minimax_prompt(enhanced_research, platform, topic_str, duration_seconds)
                engine_guide = (
                    "你是专业视频提示词工程师。使用MiniMax 6秒短视频提示策略："
                    "[镜头类型]+[主体]+[动作]+[环境]+[光线]+[风格]+[质量标签]，并包含0-6秒时间标记。"
                    "请输出高信息密度、可直接投喂模型的中文提示词，避免模板化描述。"
                )

            # 平台风格补充
            platform_hint = {
                Platform.DOUYIN: "节奏快、强冲击、情绪共鸣、垂直画幅优先",
                Platform.XIAOHONGSHU: "生活方式美学、温暖配色、真实体验",
                Platform.BILIBILI: "知识科普、结构清晰、镜头稳定",
                Platform.WECHAT: "专业权威、信息密度高、图表/数据描述"
            }.get(platform, "通用视频风格")

            # 2) 调用LLM生成最终可用提示词（真实API）
            model_name = os.getenv("WRITER_MODEL", get_default_model())
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": engine_guide},
                    {"role": "user", "content": f"主题：{topic_str}\n目标平台：{platform.value}\n平台风格提示：{platform_hint}\n期望时长：{duration_seconds}秒\n\n基于以下结构化要点，给出一个最终可直接用于视频生成模型的中文提示词：\n\n{scaffold}"}
                ],
                temperature=0.3,
                max_tokens=1200
            )

            prompt_text = response.choices[0].message.content.strip()

            title = f"{topic_str} - 视频提示词（{engine.upper()}）"

            metadata = {
                "version_number": version_num,
                "generated_at": datetime.now().isoformat(),
                "research_topic": (topic_str[:50] + "...") if topic_str else "",
                "research_confidence": enhanced_research.confidence_score,
                "video_prompt_engine": engine,
                "video_prompt_duration": duration_seconds,
            }

            return ContentVersion(
                version_id=str(uuid.uuid4()),
                platform=platform,
                content_type=ContentType.VIDEO_SCRIPT,
                title=title,
                content=prompt_text,
                metadata=metadata,
                created_at=datetime.now(),
            )
        except Exception as e:
            self.logger.error(f"❌ 视频提示词生成失败: {e}")
            return None

    def _build_minimax_prompt(
        self,
        research: StructuredResearch,
        platform: Platform,
        topic: str,
        duration_seconds: int = 6,
    ) -> str:
        """构建 MiniMax 风格6秒短片提示词（指南：镜头+主体+动作+环境+光线+风格+质量标签）。"""
        # 提取更有信息量的要点（优先时间线事件，其次核心事实字段，最后回退话题切分）
        key_points = self._extract_video_points(research, topic, max_points=3)

        # 平台风格与镜头偏好
        platform_style = {
            Platform.XIAOHONGSHU: ("近景", "生活方式，温暖配色，柔光箱照明，纪录片风格"),
            Platform.DOUYIN: ("特写", "快节奏，强对比，动感光影，商业级调色"),
            Platform.BILIBILI: ("中景", "知识科普，稳定构图，冷色调，电影级质感"),
            Platform.WECHAT: ("中景", "专业权威，均衡布光，纪录片/广告级混合")
        }.get(platform, ("中景", "电影级质感"))

        lens, style_desc = platform_style
        environment = "现代室内" if platform in {Platform.WECHAT, Platform.XIAOHONGSHU} else "城市户外/工作场景"

        quality_tags = "8K超清, 10-bit色深, HDR高动态范围, 电影级调色, 稳定器跟拍"

        time_marks = (
            f"[0-2秒]: 建立场景\n[2-4秒]: 主要动作展开\n[4-6秒]: 高潮时刻，视觉冲击"
            if duration_seconds <= 6 else
            f"[0-{duration_seconds//3}秒]: 建立场景\n[{duration_seconds//3}-{2*duration_seconds//3}秒]: 动作展开\n[{2*duration_seconds//3}-{duration_seconds}秒]: 高潮与收束"
        )

        prompt = f"""
{lens}，主体：{topic}（关键信息：{'; '.join(key_points[:2])}），
动作：围绕主题的一个核心动作，节奏随时间推进，
环境：{environment}，
光线：黄金时段侧光/柔光箱照明（按场景选择），
风格：{style_desc}，
质量：{quality_tags}

时间控制：
{time_marks}
建议内容细化：
- 要点A：{key_points[0] if key_points else topic}
- 要点B：{key_points[1] if len(key_points) > 1 else '补充一个与要点A互为对照的信息点'}
""".strip()
        return prompt

    def _build_sora_prompt(
        self,
        research: StructuredResearch,
        platform: Platform,
        topic: str,
        duration_seconds: int = 60,
    ) -> str:
        """构建 Sora 风格长视频提示词（时间线+叙事结构+物理/空间一致性）。"""
        # 关键点/时间线（优先使用 research.timeline 的事件描述）
        points = self._extract_video_points(research, topic, max_points=4)
        while len(points) < 4:
            points.append(topic)

        # 切分时间段（四段）
        seg = duration_seconds // 4 or 15
        timeline = [
            f"[0-{seg}秒] 引入主题：{topic}，建立环境与主体",
            f"[{seg}-{2*seg}秒] 展开信息1：{points[0]}",
            f"[{2*seg}-{3*seg}秒] 展开信息2：{points[1]}",
            f"[{3*seg}-{duration_seconds}秒] 总结与高潮：{points[2]} / {points[3]}"
        ]

        physical = (
            "重力9.8m/s²；光影一致；材质PBR真实；运动遵循动量守恒；主体/道具/环境保持持续性标识"
        )
        camera = "推拉摇移结合；稳定器/轨道推进；对称/三分构图；Anamorphic光晕（按需）"

        prompt = f"""
时间线：
{chr(10).join(timeline)}

空间/物理一致性：
- {physical}

摄影技术：
- {camera}
""".strip()
        return prompt

    def _extract_video_points(self, research: StructuredResearch, topic: str, max_points: int = 4) -> List[str]:
        """从结构化研究数据中提取更有信息量的视频要点。
        优先顺序：timeline.event → core_facts(拼接money/dates/people) → topic切分。
        """
        points: List[str] = []
        try:
            # 1) 时间线事件
            if getattr(research, 'timeline', None):
                for ev in research.timeline:
                    ev_text = ''
                    if isinstance(ev, dict):
                        date = ev.get('date')
                        event = ev.get('event') or ev.get('description')
                        if event:
                            ev_text = f"{date + '：' if date else ''}{event}"
                    if ev_text:
                        points.append(ev_text)
                        if len(points) >= max_points:
                            return points[:max_points]

            # 2) 核心事实（money/dates/people拼接）
            if getattr(research, 'core_facts', None):
                for fact in research.core_facts:
                    if not isinstance(fact, dict):
                        continue
                    money = ', '.join(fact.get('money', [])[:2]) if fact.get('money') else ''
                    dates = ', '.join(fact.get('dates', [])[:2]) if fact.get('dates') else ''
                    people = ', '.join(fact.get('people', [])[:2]) if fact.get('people') else ''
                    parts = []
                    if dates:
                        parts.append(f"时间：{dates}")
                    if money:
                        parts.append(f"数据：{money}")
                    if people:
                        parts.append(f"人物：{people}")
                    if parts:
                        points.append('；'.join(parts))
                        if len(points) >= max_points:
                            return points[:max_points]

            # 3) 回退：从主题切分关键词
            topic_clean = topic.replace('\n', ' ').replace('\r', ' ')
            for sep in ['；', ';', '，', ',', '。', '.', '、', '/', '|', '—', '-', '：', ':']:
                topic_clean = topic_clean.replace(sep, ' ')
            for token in topic_clean.split(' '):
                token = token.strip()
                if len(token) >= 2 and token not in points:
                    points.append(token)
                if len(points) >= max_points:
                    break
        except Exception:
            pass
        return points[:max_points] if points else [topic]
    
    async def _conduct_deep_research(self, research_data: ResearchData) -> StructuredResearch:
        """进行深度研究增强"""
        try:
            self.logger.info(f"🔍 对主题'{research_data.topic}'进行深度研究...")
            
            # 使用深度研究引擎（异步执行）
            enhanced_research = await self.deep_research_engine.execute_depth_research(
                topic=research_data.topic, topic_type="企业产品"
            )
            
            self.logger.info(f"✅ 深度研究完成 - 信息密度: {enhanced_research.information_density:.2f}")
            return enhanced_research
            
        except Exception as e:
            self.logger.warning(f"⚠️ 深度研究失败，降级到结构化基础研究: {e}")
            # 降级处理
            return self._convert_to_structured_research(research_data)
    
    def _convert_to_structured_research(self, research_data: ResearchData) -> StructuredResearch:
        """将基础研究转换为结构化研究"""
        return StructuredResearch(
            core_facts=[
                {
                    "type": "basic_summary",
                    "content": research_data.summary,
                    "money": [],
                    "dates": [],
                    "people": [],
                    "source": "basic_research"
                }
            ] + [
                {
                    "type": "key_point",
                    "content": point,
                    "money": [],
                    "dates": [],
                    "people": [],
                    "source": "basic_research"
                }
                for point in research_data.key_points[:3]
            ],
            key_players=[
                {
                    "name": "待深度挖掘",
                    "position": "相关人员",
                    "organization": "待确认",
                    "role_in_event": "参与者"
                }
            ],
            timeline=[
                {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "event": research_data.topic,
                    "impact": "话题关注度上升"
                }
            ],
            hidden_details=[],
            evidence_sources=["基础研究数据"],
            confidence_score=0.4,
            information_density=0.3
        )
    
    async def _generate_enhanced_content_version(
        self, 
        enhanced_research: StructuredResearch, 
        platform: Platform, 
        version_num: int,
        topic_str: str
    ) -> Optional[ContentVersion]:
        """生成增强版内容"""
        try:
            # Step 1: 生成CASE框架提示词
            case_prompt = get_enhanced_content_generation_prompt(platform, enhanced_research)
            
            # Step 2: 构建完整提示词
            full_prompt = self._build_complete_prompt(enhanced_research, platform, case_prompt)
            
            # Step 3: 生成内容（带质量控制重试）
            content_result = await self._generate_with_quality_control(
                full_prompt, topic_str, platform
            )
            
            if not content_result["success"]:
                self.logger.error(f"❌ {platform.value}内容质量控制失败")
                return None
            
            content = content_result["content"]
            quality_metrics = content_result["quality_metrics"]
            
            # Step 4: 生成标题
            title = await self._generate_enhanced_title(enhanced_research, platform, topic_str)
            
            # Step 5: 创建内容版本
            version = ContentVersion(
                version_id=str(uuid.uuid4()),
                platform=platform,
                content_type=ContentType.ARTICLE,
                title=title,
                content=content,
                metadata={
                    "version_number": version_num,
                    "word_count": len(content.replace(' ', '').replace('\n', '')),
                    "generated_at": datetime.now().isoformat(),
                    "research_topic": (topic_str[:50] + "...") if topic_str else "",
                    "research_confidence": enhanced_research.confidence_score,
                    "information_density": quality_metrics["total_density_score"],
                    "case_compliance": quality_metrics["case_compliance"],
                    "quality_score": quality_metrics["total_density_score"],
                    "specific_data_count": quality_metrics["specific_data_count"],
                    "quality_grade": quality_metrics["grade"]
                },
                created_at=datetime.now()
            )
            
            return version
            
        except Exception as e:
            self.logger.error(f"❌ 生成{platform.value}内容版本失败: {e}")
            return None
    
    def _build_complete_prompt(self, research: StructuredResearch, platform: Platform, case_prompt: str) -> str:
        """构建完整提示词"""
        return f"""
# 内容生成任务

## 研究质量评估
- 信息密度: {research.information_density:.2f}
- 置信度: {research.confidence_score:.2f}
- 事实数量: {len(research.core_facts)}
- 证据来源: {len(research.evidence_sources)}

## 目标平台
- 平台: {platform.value}
- 要求: 符合平台用户心理和内容调性

{case_prompt}

## 质量要求确认
请严格按照CASE框架生成内容：
1. Concrete Data - 具体数据（每段至少3个精确数字）
2. Actual Examples - 真实案例（具体公司、人名、事件）
3. Specific Details - 具体细节（技术参数、时间、地点）
4. Expert Sources - 专家来源（报告编号、发布机构）

禁止使用任何模糊表达，如"据了解"、"相关人士"、"大约"等。
"""
    
    async def _generate_with_quality_control(
        self, 
        prompt: str, 
        topic: str, 
        platform: Platform, 
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """带质量控制的内容生成"""
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"🔄 第{attempt + 1}次尝试生成{platform.value}内容...")
                
                # 调用LLM生成内容 - 使用环境变量配置的模型
                model_name = os.getenv("WRITER_MODEL", get_default_model())
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是专业内容创作专家，严格遵循CASE框架，生成高信息密度、零AI味的内容。绝对禁止空话、套话、模板化表达。"
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=3000,
                    temperature=0.2  # 低随机性保证质量稳定
                )
                
                content = response.choices[0].message.content.strip()
                
                # 质量验证
                validation = self.quality_enforcer.validate_content(content, topic)
                
                if validation["passed"]:
                    self.logger.info(f"✅ 内容质量合格 - 评分: {validation['score']:.2f}")
                    return {
                        "success": True,
                        "content": content,
                        "quality_metrics": validation["metrics"]
                    }
                else:
                    self.logger.warning(f"⚠️ 第{attempt + 1}次质量不达标: {', '.join(validation['issues'][:2])}")
                    
                    if attempt < max_retries - 1:
                        # 增强提示词要求改进
                        prompt += f"\n\n⚠️ 上次内容存在问题: {', '.join(validation['issues'][:2])}，请严格改正并重新生成。"
                    else:
                        # 最后一次尝试，返回当前结果
                        return {
                            "success": False,
                            "content": content,
                            "quality_metrics": validation["metrics"],
                            "issues": validation["issues"]
                        }
                        
            except Exception as e:
                self.logger.error(f"❌ 第{attempt + 1}次生成失败: {e}")
                if attempt == max_retries - 1:
                    return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "达到最大重试次数"}
    
    async def _generate_enhanced_title(self, research: StructuredResearch, platform: Platform, topic_str: str) -> str:
        """生成增强版标题"""
        try:
            topic = topic_str[:30] + "..." if topic_str else "深度话题"
            
            title_prompt = f"""
请为{platform.value}平台生成一个吸引人的标题，主题是：{topic}

要求：
1. 必须包含具体数据或关键词
2. 符合{platform.value}平台的内容调性
3. 避免标题党，但要有吸引力
4. 20字以内

只返回一个最佳标题，不需要其他内容。
"""
            
            model_name = os.getenv("WRITER_MODEL", get_default_model())
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "你是标题优化专家，生成精准、有吸引力的标题。"},
                    {"role": "user", "content": title_prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            title = response.choices[0].message.content.strip()
            return title if title else f"【深度】{topic}"
            
        except Exception as e:
            self.logger.error(f"❌ 标题生成失败: {e}")
            # 回退标题
            topic_short = topic_str[:20] if topic_str else "热门话题"
            return f"【{platform.value}深度】{topic_short}"
    
    def _create_error_version(self, research_data: ResearchData, platform: Platform, error_msg: str) -> ContentVersion:
        """创建错误版本"""
        return ContentVersion(
            version_id=str(uuid.uuid4()),
            platform=platform,
            content_type=ContentType.ARTICLE,
            title=f"【系统提示】{research_data.topic}",
            content=f"抱歉，由于技术原因暂时无法生成高质量内容。错误: {error_msg[:100]}",
            metadata={
                "error": True,
                "error_message": error_msg,
                "generated_at": datetime.now().isoformat(),
                "quality_score": 0.0
            },
            created_at=datetime.now()
        )
    
    # 实现FactCheckingMixin接口
    async def _generate_initial_content(self, prompt: str, platform: str, research_data: Dict) -> str:
        """生成初始内容 - 集成反审查机制"""
        try:
            platform_enum = Platform(platform.lower()) if isinstance(platform, str) else Platform.WECHAT
            # 兼容 dict → Pydantic 模型
            research_obj = research_data
            if isinstance(research_data, dict):
                try:
                    research_obj = ResearchData(**research_data)
                except Exception:
                    try:
                        research_obj = ResearchData.parse_obj(research_data)  # pydantic v1 兼容
                    except Exception:
                        research_obj = ResearchData(**{})
            
            enhanced_research = await self._conduct_deep_research(research_obj)
            case_prompt = get_enhanced_content_generation_prompt(platform_enum, enhanced_research)
            
            # 构建完整提示词
            full_prompt = f"{prompt}\n\n{case_prompt}"
            
            # 使用反审查系统生成内容
            result = self.anti_censorship_generator.generate_content(
                prompt=full_prompt,
                topic=research_obj.topic,
                expected_length=self._get_expected_length(platform_enum),
                preferred_model="qwen3"
            )
            
            # 记录反审查结果
            if result["switches_made"]:
                self.logger.warning(f"🔄 模型切换: {result['switches_made']}")
            
            if not result["success"]:
                self.logger.error(f"❌ 反审查生成失败，使用降级策略")
                # 降级到原有方法
                return await self._fallback_generate_content(full_prompt)
            
            self.logger.info(f"✅ 内容生成成功，使用模型: {result['model_used']}")
            return result["final_content"]
            
        except Exception as e:
            self.logger.error(f"❌ 生成初始内容失败: {e}")
            return f"内容生成失败: {str(e)}"
    
    def _get_expected_length(self, platform: Platform) -> int:
        """获取平台期望的内容长度"""
        length_map = {
            Platform.WECHAT: 2000,
            Platform.XIAOHONGSHU: 1000,
            Platform.BILIBILI: 1500,
            Platform.DOUYIN: 500,
        }
        return length_map.get(platform, 1500)
    
    async def _fallback_generate_content(self, prompt: str) -> str:
        """降级内容生成方法（当反审查系统失败时使用）"""
        try:
            model_name = os.getenv("WRITER_MODEL", get_default_model())
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "专业内容创作专家"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"❌ 降级生成也失败: {e}")
            return "内容生成完全失败，请检查系统配置"
