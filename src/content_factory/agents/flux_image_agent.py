"""
FLUX Image Agent - 基于 fal.ai FLUX 模型的图片生成
与 gpt-image-1 相比：更高画质、支持精准文字渲染、直接返回 URL

平台模型映射:
  小红书 → FLUX 1.1 Pro Ultra  (摄影级写实，9:16)
  微信   → Ideogram v2         (文字渲染强，信息图，16:9)
  B站    → FLUX 1.1 Pro        (高质量横版，16:9)
  抖音   → FLUX Dev            (快速竖版，9:16)

返回的 image_url 可直接传入 SeedanceVideoAgent 做 I2V 首帧。
"""
import asyncio
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import BaseAgent
from ..models import ContentVersion, Platform, ResearchData
from ..core.openai_client import get_async_client, get_default_model


# ── 平台配置 ──────────────────────────────────────────────────────────────────

PLATFORM_CONFIGS: Dict[str, Dict[str, Any]] = {
    "xiaohongshu": {
        "model": "fal-ai/flux-pro/v1.1-ultra",
        "aspect_ratio": "9:16",
        "style_hint": "lifestyle photography, warm natural lighting, aesthetic, instagram-worthy, soft bokeh",
        "safety_tolerance": "2",
    },
    "wechat": {
        "model": "fal-ai/ideogram/v2",
        "aspect_ratio": "16:9",
        "style_hint": "clean infographic, professional business illustration, readable text, modern flat design",
        "ideogram_style": "design",
    },
    "bilibili": {
        "model": "fal-ai/flux-pro/v1.1",
        "aspect_ratio": "16:9",
        "style_hint": "dynamic composition, vibrant colors, high contrast, eye-catching thumbnail",
        "safety_tolerance": "2",
    },
    "douyin": {
        "model": "fal-ai/flux/dev",
        "aspect_ratio": "9:16",
        "style_hint": "bold graphic design, trendy, high energy, vertical composition, punchy colors",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
    },
}

# fal.ai FLUX 比例 → 像素尺寸映射（flux/dev 需要 image_size 而非 aspect_ratio）
FLUX_DEV_SIZES = {
    "9:16": {"width": 768, "height": 1344},
    "16:9": {"width": 1344, "height": 768},
    "1:1":  {"width": 1024, "height": 1024},
}


class FluxImageAgent(BaseAgent):
    """
    基于 fal.ai FLUX / Ideogram 的高质量图片生成 Agent

    优于 gpt-image-1 的地方：
    - 摄影级写实（FLUX Pro Ultra）
    - 精准文字渲染（Ideogram v2，适合微信信息图）
    - 与 Seedance 同一 API Key，降低运维复杂度
    - 返回直接可用的 URL，可作为 Seedance I2V 首帧

    多平台并行生成，任一平台失败时在结果中记录错误但不中断其他平台。
    """

    def __init__(self, fal_api_key: Optional[str] = None, logger=None):
        super().__init__("flux_image_agent", logger)
        self._fal_key = fal_api_key or os.getenv("FAL_KEY")
        self._async_client = None

    # ── 初始化辅助 ────────────────────────────────────────────────────────────

    def _get_fal(self):
        try:
            import fal_client
        except ImportError:
            raise RuntimeError("fal-client 未安装，请运行: uv add fal-client")
        if self._fal_key:
            fal_client.api_key = self._fal_key
        elif not os.getenv("FAL_KEY"):
            raise RuntimeError("FAL_KEY 未配置")
        return fal_client

    def _get_openai(self):
        if self._async_client is None:
            self._async_client = get_async_client()
        return self._async_client

    # ── 主处理入口 ────────────────────────────────────────────────────────────

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        input_data:
            content_versions: List[ContentVersion]  —— 取文章文本生成图片提示词
            research_data:    ResearchData
            platforms:        List[Platform | str]

        output:
            image_results: Dict[str, Dict]  —— platform → {image_url, prompt, model, ...}
            status: "completed"
        """
        content_versions: List[ContentVersion] = input_data.get("content_versions", [])
        research_data: ResearchData = input_data.get("research_data")
        platforms: List = input_data.get("platforms", [])

        if not research_data:
            raise ValueError("research_data 是必填项")

        # 按平台归集文章内容
        platform_content: Dict[str, str] = {}
        for v in content_versions:
            pname = v.platform.value if hasattr(v.platform, "value") else str(v.platform)
            if pname not in platform_content or len(v.content) > len(platform_content[pname]):
                platform_content[pname] = v.content

        target_platforms = [
            p.value if hasattr(p, "value") else str(p) for p in platforms
        ] or list(platform_content.keys())

        if not target_platforms:
            raise ValueError("未指定任何目标平台")

        self.logger.info(f"🖼️  FLUX图片生成启动 - {len(target_platforms)} 个平台")

        # 并行生成
        tasks = [
            self._generate_for_platform(
                platform=p,
                article_content=platform_content.get(p, research_data.summary),
                topic=research_data.topic,
            )
            for p in target_platforms
        ]
        outcomes = await asyncio.gather(*tasks, return_exceptions=True)

        image_results: Dict[str, Dict] = {}
        for platform, outcome in zip(target_platforms, outcomes):
            if isinstance(outcome, Exception):
                # 图片生成是辅助功能，单平台失败记录但不中断整体
                self.logger.error(f"❌ {platform} 图片生成失败: {outcome}")
                image_results[platform] = {"success": False, "error": str(outcome)}
            else:
                image_results[platform] = outcome
                self.logger.info(f"✅ {platform} 图片: {outcome['image_url'][:70]}...")

        successful = sum(1 for r in image_results.values() if r.get("success", True) and "image_url" in r)
        self.logger.info(f"🖼️  FLUX生成完成: {successful}/{len(target_platforms)} 个平台成功")

        return {"image_results": image_results, "status": "completed"}

    # ── 单平台生成 ────────────────────────────────────────────────────────────

    async def _generate_for_platform(
        self, platform: str, article_content: str, topic: str
    ) -> Dict[str, Any]:
        cfg = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS["wechat"])

        # 1. LLM 提炼图片提示词
        prompt = await self._build_image_prompt(article_content, topic, platform, cfg)
        self.logger.info(f"  [{platform}] 提示词: {prompt[:80]}...")

        # 2. 调用对应模型
        model = cfg["model"]
        if "ideogram" in model:
            image_url = await self._call_ideogram(prompt, cfg)
        elif "ultra" in model:
            image_url = await self._call_flux_ultra(prompt, cfg)
        elif "flux/dev" in model:
            image_url = await self._call_flux_dev(prompt, cfg)
        else:
            image_url = await self._call_flux_pro(prompt, cfg)

        return {
            "platform": platform,
            "image_url": image_url,
            "prompt": prompt,
            "model": model,
            "aspect_ratio": cfg["aspect_ratio"],
            "generated_at": datetime.now().isoformat(),
        }

    # ── 提示词生成 ────────────────────────────────────────────────────────────

    async def _build_image_prompt(
        self, article: str, topic: str, platform: str, cfg: Dict[str, Any]
    ) -> str:
        """用 LLM 将文章提炼为平台适配的英文图片提示词"""
        client = self._get_openai()
        is_ideogram = "ideogram" in cfg["model"]

        system = (
            "You are an expert image generation prompt writer. "
            "Convert the article into a precise English image prompt. "
            "Rules:\n"
            "- 30 to 80 English words\n"
            "- Describe scene, lighting, composition, mood, color palette\n"
            + ("- Include readable Chinese or English text elements if relevant for infographics\n"
               if is_ideogram else
               "- NO text overlays, NO watermarks\n")
            + "- Be visually specific"
        )

        response = await self._get_openai().chat.completions.create(
            model=get_default_model(),
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": (
                        f"Topic: {topic}\n"
                        f"Platform: {platform}\n"
                        f"Style direction: {cfg['style_hint']}\n"
                        f"Aspect ratio: {cfg['aspect_ratio']}\n\n"
                        f"Article excerpt:\n{article[:600]}\n\n"
                        "Write the image prompt:"
                    ),
                },
            ],
            temperature=0.3,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()

    # ── fal.ai API 调用 ───────────────────────────────────────────────────────

    async def _fal_subscribe(self, model: str, arguments: Dict[str, Any]) -> Dict:
        """通用 fal.ai 阻塞调用包装为 async"""
        fal = self._get_fal()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: fal.subscribe(model, arguments=arguments),
        )

    def _extract_image_url(self, result: Dict, model: str) -> str:
        """从 fal.ai 响应中提取图片 URL"""
        images = result.get("images") or result.get("image")
        if isinstance(images, list) and images:
            url = images[0].get("url") if isinstance(images[0], dict) else images[0]
        elif isinstance(images, dict):
            url = images.get("url")
        else:
            url = result.get("image_url") or result.get("url")

        if not url:
            raise RuntimeError(f"fal.ai ({model}) 返回结果中无图片 URL: {result}")
        return url

    async def _call_flux_ultra(self, prompt: str, cfg: Dict) -> str:
        result = await self._fal_subscribe(
            "fal-ai/flux-pro/v1.1-ultra",
            {
                "prompt": prompt,
                "aspect_ratio": cfg["aspect_ratio"],
                "num_images": 1,
                "safety_tolerance": cfg.get("safety_tolerance", "2"),
                "output_format": "jpeg",
            },
        )
        return self._extract_image_url(result, "flux-pro/v1.1-ultra")

    async def _call_flux_pro(self, prompt: str, cfg: Dict) -> str:
        result = await self._fal_subscribe(
            "fal-ai/flux-pro/v1.1",
            {
                "prompt": prompt,
                "aspect_ratio": cfg["aspect_ratio"],
                "num_images": 1,
                "safety_tolerance": cfg.get("safety_tolerance", "2"),
                "output_format": "jpeg",
            },
        )
        return self._extract_image_url(result, "flux-pro/v1.1")

    async def _call_flux_dev(self, prompt: str, cfg: Dict) -> str:
        size = FLUX_DEV_SIZES.get(cfg["aspect_ratio"], FLUX_DEV_SIZES["9:16"])
        result = await self._fal_subscribe(
            "fal-ai/flux/dev",
            {
                "prompt": prompt,
                "image_size": size,
                "num_inference_steps": cfg.get("num_inference_steps", 28),
                "guidance_scale": cfg.get("guidance_scale", 3.5),
                "num_images": 1,
                "enable_safety_checker": True,
            },
        )
        return self._extract_image_url(result, "flux/dev")

    async def _call_ideogram(self, prompt: str, cfg: Dict) -> str:
        result = await self._fal_subscribe(
            "fal-ai/ideogram/v2",
            {
                "prompt": prompt,
                "aspect_ratio": cfg["aspect_ratio"],
                "style": cfg.get("ideogram_style", "realistic"),
                "magic_prompt_option": "off",
            },
        )
        return self._extract_image_url(result, "ideogram/v2")
