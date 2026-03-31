"""
图片生成Agent
基于yunwu API的gpt-image-1模型实现文案到图片的智能生成
"""
import os
import asyncio
import logging
from typing import Any, Dict, List, Optional
import json
from .base import BaseAgent
from ..core.openai_client import get_global_client, get_default_model
from pathlib import Path
import hashlib
import time


class ImageGenerationAgent(BaseAgent):
    """
    图片生成Agent
    专门负责从文案生成适合不同平台的图片
    """
    
    def __init__(self, cache_dir: str = "./image_cache"):
        super().__init__("ImageGeneration")
        self.client = get_global_client()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # 平台配置
        self.platform_configs = {
            "wechat": {
                "size": "1536x1024",  # 3:2 横图，适合微信文章
                "style": "professional, clean, minimalist, business presentation, infographic style",
                "description": "微信公众号配图"
            },
            "xiaohongshu": {
                "size": "1024x1024",  # 1:1 方图，小红书标准
                "style": "aesthetic, lifestyle photography, soft lighting, instagram worthy, pastel colors",
                "description": "小红书种草图"
            },
            "bilibili": {
                "size": "1536x1024",  # 3:2 横图，B站封面
                "style": "anime style illustration, vibrant colors, dynamic composition, eye-catching",
                "description": "B站视频封面"
            },
            "douyin": {
                "size": "1024x1536",  # 2:3 竖图，抖音标准
                "style": "trendy visual, eye-catching, modern design, bold graphics, vertical composition",
                "description": "抖音短视频封面"
            }
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理图片生成请求
        
        Args:
            input_data: 包含以下字段的字典
                - text: 源文案内容
                - platform: 目标平台 (可选，默认xiaohongshu)
                - num_images: 生成图片数量 (可选，默认1)
                - platforms: 多平台列表 (可选)
                - use_cache: 是否使用缓存 (可选，默认True)
                
        Returns:
            Dict[str, Any]: 生成结果
        """
        text = input_data.get("text", "")
        if not text:
            return {"success": False, "error": "缺少文案内容"}
        
        # 检查是否为多平台生成
        platforms = input_data.get("platforms")
        if platforms:
            return await self._generate_for_multiple_platforms(
                text=text,
                platforms=platforms,
                images_per_platform=input_data.get("num_images", 1),
                use_cache=input_data.get("use_cache", True)
            )
        else:
            # 单平台生成
            platform = input_data.get("platform", "xiaohongshu")
            num_images = input_data.get("num_images", 1)
            use_cache = input_data.get("use_cache", True)
            
            return await self._generate_single_platform(
                text=text,
                platform=platform,
                num_images=num_images,
                use_cache=use_cache
            )
    
    async def _generate_single_platform(self,
                                      text: str,
                                      platform: str,
                                      num_images: int,
                                      use_cache: bool) -> Dict[str, Any]:
        """生成单个平台的图片"""
        try:
            # 1. 分析文案内容
            self.logger.info(f"开始分析文案内容（平台：{platform}）")
            analysis = await self._analyze_content(text)
            
            # 2. 构建提示词
            self.logger.info("构建图片生成提示词")
            prompt = self._build_prompt(analysis, platform)
            
            # 3. 检查缓存
            if use_cache:
                cached_result = self._check_cache(prompt, platform)
                if cached_result:
                    self.logger.info("使用缓存结果")
                    return cached_result
            
            # 4. 生成图片
            self.logger.info(f"调用yunwu API生成图片（数量：{num_images}）")
            result = await self._call_image_api(
                prompt=prompt,
                platform=platform,
                num_images=num_images
            )
            
            # 5. 保存缓存
            if use_cache and result.get("success"):
                self._save_cache(prompt, platform, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"图片生成失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform,
                "text_preview": text[:100] + "..." if len(text) > 100 else text
            }
    
    async def _generate_for_multiple_platforms(self,
                                             text: str,
                                             platforms: List[str],
                                             images_per_platform: int,
                                             use_cache: bool) -> Dict[str, Any]:
        """为多个平台并行生成图片"""
        async def _one(platform: str) -> tuple[str, Dict]:
            try:
                result = await self._generate_single_platform(
                    text=text,
                    platform=platform,
                    num_images=images_per_platform,
                    use_cache=use_cache,
                )
                return platform, result
            except Exception as e:
                self.logger.error(f"平台 {platform} 生成失败: {e}")
                return platform, {"success": False, "error": str(e), "platform": platform}

        pairs = await asyncio.gather(*[_one(p) for p in platforms])
        results = dict(pairs)

        return {
            "success": True,
            "type": "multi_platform",
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "platforms": platforms,
            "results": results,
            "summary": {
                "total_platforms": len(platforms),
                "successful_platforms": sum(1 for r in results.values() if r.get("success", False)),
                "total_images": sum(r.get("num_generated", 0) for r in results.values() if r.get("success")),
            },
        }
    
    async def _analyze_content(self, text: str) -> Dict:
        """使用Qwen3分析文案内容"""
        prompt = f"""
        请分析以下文案，提取用于图片生成的关键视觉元素：

        文案内容：
        {text[:1000]}

        请提取以下信息并以JSON格式返回：
        {{
            "main_objects": ["主要物体/主题（3-5个关键词）"],
            "scene": "场景描述（办公室/咖啡厅/户外/家居等）",
            "mood": "情绪氛围（专业/温馨/活力/轻松/时尚等）",
            "style_keywords": ["风格关键词（现代/简约/可爱/商务等）"],
            "color_scheme": ["颜色方案（温暖/清新/深色/明亮等）"],
            "target_audience": "目标受众（职场人士/年轻女性/学生等）"
        }}

        注意：
        1. 请确保返回有效的JSON格式
        2. 关键词要具体且适合图片生成
        3. 考虑中国用户的审美偏好
        """
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=get_default_model(),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=600
                )
            )
            
            content = response.choices[0].message.content.strip()
            
            # 提取JSON部分
            if "```json" in content:
                json_part = content.split("```json")[1].split("```")[0]
            elif "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                json_part = content[start:end]
            else:
                json_part = content
            
            result = json.loads(json_part)
            self.logger.info(f"内容分析成功: {result}")
            return result
            
        except Exception as e:
            self.logger.warning(f"AI分析失败，使用默认分析: {e}")
            return {
                "main_objects": ["content", "information", "illustration"],
                "scene": "clean background",
                "mood": "professional",
                "style_keywords": ["modern", "clean"],
                "color_scheme": ["balanced"],
                "target_audience": "general"
            }
    
    def _build_prompt(self, analysis: Dict, platform: str) -> str:
        """构建图片生成提示词"""
        platform_config = self.platform_configs.get(platform, {
            "style": "high quality, professional",
            "quality": "hd"
        })
        
        # 提取分析结果
        objects = ", ".join(analysis.get("main_objects", []))
        scene = analysis.get("scene", "")
        mood = analysis.get("mood", "")
        style_keywords = ", ".join(analysis.get("style_keywords", []))
        colors = ", ".join(analysis.get("color_scheme", []))
        
        # 构建提示词组件
        prompt_parts = []
        
        # 主要内容和场景
        if objects:
            if scene and scene != "clean background":
                prompt_parts.append(f"{objects} in {scene}")
            else:
                prompt_parts.append(objects)
        
        # 情绪和氛围
        if mood and mood != "professional":
            prompt_parts.append(f"{mood} atmosphere")
        
        # 风格关键词
        if style_keywords:
            prompt_parts.append(style_keywords)
        
        # 平台特定风格
        prompt_parts.append(platform_config.get("style", "high quality"))
        
        # 颜色方案
        if colors and "balanced" not in colors:
            prompt_parts.append(f"{colors} color palette")
        
        # 质量和技术规格
        quality_specs = [
            "highly detailed",
            "professional photography",
            "4k resolution",
            "award winning composition",
            "perfect lighting"
        ]
        prompt_parts.extend(quality_specs)
        
        # 针对中文内容的特殊处理
        prompt_parts.append("Chinese aesthetic preferences")
        
        final_prompt = ", ".join(prompt_parts)
        self.logger.info(f"生成的提示词: {final_prompt}")
        return final_prompt
    
    async def _call_image_api(self, 
                            prompt: str, 
                            platform: str, 
                            num_images: int) -> Dict[str, Any]:
        """调用yunwu API生成图片"""
        platform_config = self.platform_configs.get(platform, {
            "size": "1024x1024"
        })
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    n=num_images,
                    size=platform_config.get("size", "1024x1024")
                    # yunwu API的gpt-image-1不支持quality和response_format参数
                )
            )
            
            # 处理响应 - yunwu API返回base64编码的图片
            images = []
            for i, img in enumerate(response.data):
                image_path = None
                image_url = None
                
                # yunwu API返回base64编码的图片数据
                if hasattr(img, 'b64_json') and img.b64_json:
                    import base64
                    
                    # 保存base64图片到本地文件
                    cache_key = hashlib.md5(f"{prompt}_{platform}_{i}".encode()).hexdigest()
                    image_filename = f"{cache_key}.png"
                    image_path = self.cache_dir / image_filename
                    
                    # 解码并保存图片
                    image_bytes = base64.b64decode(img.b64_json)
                    with open(image_path, 'wb') as f:
                        f.write(image_bytes)
                    
                    self.logger.info(f"图片已保存到: {image_path}")
                    image_path = str(image_path)  # 转换为字符串路径
                    
                elif hasattr(img, 'url') and img.url:
                    # 如果API返回URL（兼容性处理）
                    image_url = img.url
                    self.logger.info(f"获取图片URL: {image_url}")
                else:
                    self.logger.error(f"图片数据格式不正确: {img}")
                    continue
                
                image_info = {
                    "index": i + 1,
                    "prompt": prompt,
                    "size": platform_config.get("size"),
                    "platform": platform
                }
                
                # 添加图片数据
                if image_path:
                    image_info["image_path"] = image_path
                if image_url:
                    image_info["url"] = image_url
                    
                images.append(image_info)
            
            if not images:
                return {
                    "success": False,
                    "error": "未能处理任何图片数据",
                    "platform": platform,
                    "prompt": prompt
                }
            
            result = {
                "success": True,
                "platform": platform,
                "platform_description": platform_config.get("description", platform),
                "prompt": prompt,
                "images": images,
                "num_generated": len(images),
                "model": "gpt-image-1",
                "provider": "yunwu",
                "generation_time": time.time()
            }
            
            self.logger.info(f"成功生成 {len(images)} 张图片")
            return result
            
        except Exception as e:
            self.logger.error(f"图片API调用失败 (platform={platform}): {e}")
            raise RuntimeError(f"图片API调用失败 (platform={platform}): {e}") from e
    
    def _check_cache(self, prompt: str, platform: str) -> Optional[Dict]:
        """检查缓存"""
        cache_key = hashlib.md5(f"{prompt}_{platform}".encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    # 检查缓存是否过期（24小时）
                    if time.time() - cached_data.get("generation_time", 0) < 86400:
                        return cached_data
            except Exception as e:
                self.logger.warning(f"读取缓存失败: {e}")
        return None
    
    def _save_cache(self, prompt: str, platform: str, result: Dict):
        """保存到缓存"""
        cache_key = hashlib.md5(f"{prompt}_{platform}".encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning(f"保存缓存失败: {e}")
    
    def get_platform_info(self) -> Dict[str, Dict]:
        """获取所有平台配置信息"""
        return {
            platform: {
                "size": config["size"],
                "description": config["description"],
                "style_focus": config["style"].split(",")[0].strip()
            }
            for platform, config in self.platform_configs.items()
        }


# Agent工厂函数
def create_image_agent(cache_dir: str = "./image_cache") -> ImageGenerationAgent:
    """
    创建图片生成Agent实例
    
    Args:
        cache_dir: 缓存目录
        
    Returns:
        ImageGenerationAgent: Agent实例
    """
    return ImageGenerationAgent(cache_dir)


# 便捷函数
async def quick_image_generation(text: str, 
                               platform: str = "xiaohongshu", 
                               num_images: int = 1) -> Dict[str, Any]:
    """
    快速图片生成的便捷函数
    
    Args:
        text: 文案内容
        platform: 目标平台
        num_images: 生成数量
        
    Returns:
        Dict[str, Any]: 生成结果
    """
    agent = create_image_agent()
    return await agent.execute({
        "text": text,
        "platform": platform,
        "num_images": num_images
    })


async def multi_platform_generation(text: str, 
                                  platforms: List[str] = None) -> Dict[str, Any]:
    """
    多平台图片生成的便捷函数
    
    Args:
        text: 文案内容
        platforms: 平台列表
        
    Returns:
        Dict[str, Any]: 生成结果
    """
    if platforms is None:
        platforms = ["wechat", "xiaohongshu", "bilibili", "douyin"]
    
    agent = create_image_agent()
    return await agent.execute({
        "text": text,
        "platforms": platforms,
        "num_images": 1
    })
