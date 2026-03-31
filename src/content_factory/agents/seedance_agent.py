"""
Seedance Video Agent - 使用 ByteDance Seedance 1.5 Pro 生成真实视频
通过 fal.ai API 调用，文章内容 → LLM提炼提示词 → Seedance → MP4 URL

模式:
  T2V (默认): 纯文字提示词 → 视频
  I2V (推荐): FLUX生成首帧图片 + 文字提示词 → 视频（视觉一致性更强）

input_data 中传入 flux_image_results 时自动切换为 I2V 模式。
"""
import asyncio
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import BaseAgent
from ..models import ContentVersion, Platform, ResearchData
from ..core.openai_client import get_async_client, get_default_model


# ── 平台参数配置 ──────────────────────────────────────────────────────────────

PLATFORM_CONFIGS: Dict[Platform, Dict[str, Any]] = {
    Platform.DOUYIN: {
        "aspect_ratio": "9:16",
        "duration": 5,
        "resolution": "720p",
        "style_hint": "抖音短视频：快节奏、视觉冲击强、竖屏构图",
    },
    Platform.BILIBILI: {
        "aspect_ratio": "16:9",
        "duration": 10,
        "resolution": "1080p",
        "style_hint": "B站内容：专业感、横屏、知识性与叙事性并重",
    },
    Platform.XIAOHONGSHU: {
        "aspect_ratio": "9:16",
        "duration": 5,
        "resolution": "720p",
        "style_hint": "小红书：生活化、美观精致、竖屏种草风格",
    },
    Platform.WECHAT: {
        "aspect_ratio": "16:9",
        "duration": 5,
        "resolution": "720p",
        "style_hint": "微信视频号：正式、横屏、信息性强",
    },
}

MODEL_T2V = "fal-ai/bytedance/seedance/v1.5/pro/text-to-video"
MODEL_I2V = "fal-ai/bytedance/seedance/v1.5/pro/image-to-video"


class SeedanceVideoAgent(BaseAgent):
    """
    真实视频生成 Agent（区别于 VideoAgent 只生成脚本文本）

    工作流:
      1. 从文章内容用 LLM 提炼英文视频提示词
      2. 调用 fal.ai Seedance 1.5 Pro T2V
      3. 返回可直接使用的 MP4 视频 URL

    多平台并行生成，单个平台失败时 raise（错误必须可见）。
    """

    def __init__(self, fal_api_key: Optional[str] = None, logger=None):
        super().__init__("seedance_video_agent", logger)
        self._fal_key = fal_api_key or os.getenv("FAL_KEY")
        self._async_client = None

    # ── 初始化辅助 ────────────────────────────────────────────────────────────

    def _get_fal(self):
        try:
            import fal_client
        except ImportError:
            raise RuntimeError(
                "fal-client 未安装，请运行: uv add fal-client"
            )
        if self._fal_key:
            fal_client.api_key = self._fal_key
        elif not os.getenv("FAL_KEY"):
            raise RuntimeError(
                "FAL_KEY 未配置，请设置环境变量或传入 fal_api_key 参数"
            )
        return fal_client

    def _get_openai(self):
        if self._async_client is None:
            self._async_client = get_async_client()
        return self._async_client

    # ── 主处理入口 ────────────────────────────────────────────────────────────

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        input_data:
            content_versions: List[ContentVersion]  —— 写作阶段输出，取文章内容
            research_data:    ResearchData           —— 兜底信息来源
            platforms:        List[Platform]         —— 需要生成视频的平台

        output:
            video_results: Dict[str, Dict]  —— platform_name → {video_url, prompt, ...}
            status: "completed"
        """
        content_versions: List[ContentVersion] = input_data.get("content_versions", [])
        research_data: ResearchData = input_data.get("research_data")
        platforms: List = input_data.get("platforms", [])

        if not research_data:
            raise ValueError("research_data 是必填项")

        # 按平台归集文章内容（取最长的那份）
        platform_content: Dict[Platform, str] = {}
        for v in content_versions:
            p = v.platform if isinstance(v.platform, Platform) else Platform(v.platform)
            if p not in platform_content or len(v.content) > len(platform_content[p]):
                platform_content[p] = v.content

        target_platforms = [
            Platform(p) if isinstance(p, str) else p for p in platforms
        ] or list(platform_content.keys())

        if not target_platforms:
            raise ValueError("未指定任何目标平台")

        self.logger.info(
            f"🎬 Seedance视频生成启动 - {len(target_platforms)} 个平台"
            f" ({', '.join(p.value for p in target_platforms)})"
        )

        # 检查是否有 FLUX 图片可用作 I2V 首帧
        flux_images: Dict[str, Dict] = input_data.get("flux_image_results", {})

        # 并行生成所有平台视频
        tasks = [
            self._generate_for_platform(
                platform=p,
                article_content=platform_content.get(p, research_data.summary),
                topic=research_data.topic,
                image_url=flux_images.get(p.value, {}).get("image_url"),
            )
            for p in target_platforms
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        video_results: Dict[str, Dict] = {}
        for platform, result in zip(target_platforms, results):
            if isinstance(result, Exception):
                self.logger.error(f"❌ {platform.value} 视频生成失败: {result}")
                raise result
            video_results[platform.value] = result
            self.logger.info(f"✅ {platform.value} 视频 URL: {result['video_url'][:70]}...")

        return {"video_results": video_results, "status": "completed"}

    # ── 单平台生成 ────────────────────────────────────────────────────────────

    async def _generate_for_platform(
        self,
        platform: Platform,
        article_content: str,
        topic: str,
        image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS[Platform.WECHAT])
        mode = "I2V" if image_url else "T2V"

        # 1. 提炼视频提示词
        prompt = await self._build_video_prompt(article_content, topic, platform, config)
        self.logger.info(f"  [{platform.value}][{mode}] 提示词: {prompt[:80]}...")

        # 2. 调用 Seedance（有首帧图片则用 I2V，否则用 T2V）
        video_url = await self._call_seedance(prompt, config, image_url=image_url)

        return {
            "platform": platform.value,
            "video_url": video_url,
            "prompt": prompt,
            "mode": mode,
            "model": MODEL_I2V if image_url else MODEL_T2V,
            "image_url": image_url,
            "aspect_ratio": config["aspect_ratio"],
            "duration": config["duration"],
            "resolution": config["resolution"],
            "generated_at": datetime.now().isoformat(),
        }

    # ── 提示词生成 ────────────────────────────────────────────────────────────

    async def _build_video_prompt(
        self,
        article: str,
        topic: str,
        platform: Platform,
        config: Dict[str, Any],
    ) -> str:
        """
        用 LLM 将文章内容提炼为 Seedance 英文视频提示词。
        目标: 50-150 英文单词，描述具体视觉场景、动作、光线、构图。
        """
        client = self._get_openai()
        response = await client.chat.completions.create(
            model=get_default_model(),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert at writing prompts for AI video generation models. "
                        "Convert the given article into a cinematic English video prompt. "
                        "Rules:\n"
                        "- 50 to 150 English words\n"
                        "- Describe concrete visual scenes, actions, lighting, and composition\n"
                        "- Do NOT include text overlays, subtitles, or on-screen text\n"
                        "- Do NOT include watermarks or logos\n"
                        "- Make it visually specific and cinematically rich"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Topic: {topic}\n"
                        f"Platform style: {config['style_hint']}\n"
                        f"Video spec: {config['aspect_ratio']}, "
                        f"{config['duration']}s, {config['resolution']}\n\n"
                        f"Article excerpt:\n{article[:800]}\n\n"
                        "Write the English video generation prompt:"
                    ),
                },
            ],
            temperature=0.4,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()

    # ── Seedance API 调用 ─────────────────────────────────────────────────────

    async def _call_seedance(
        self,
        prompt: str,
        config: Dict[str, Any],
        image_url: Optional[str] = None,
    ) -> str:
        """
        通过 fal.ai 调用 Seedance 1.5 Pro。
        - image_url 为 None → T2V
        - image_url 有值   → I2V（以该图片为首帧，视觉一致性更强）
        生成通常需要 30-120 秒。
        """
        fal = self._get_fal()
        model = MODEL_I2V if image_url else MODEL_T2V

        arguments: Dict[str, Any] = {
            "prompt": prompt,
            "duration": str(config["duration"]),
            "resolution": config["resolution"],
            "aspect_ratio": config["aspect_ratio"],
            "generate_audio": True,
        }
        if image_url:
            arguments["image_url"] = image_url

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: fal.subscribe(model, arguments=arguments),
        )

        video_url: Optional[str] = result.get("video", {}).get("url")
        if not video_url:
            raise RuntimeError(
                f"Seedance API ({model}) 返回结果中未包含视频 URL。"
                f"完整响应: {result}"
            )

        return video_url
