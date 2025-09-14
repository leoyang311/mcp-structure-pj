"""
文生图工具模块
基于yunwu API的gpt-image-1模型实现文案到图片的转换
"""
import os
import asyncio
import logging
from typing import List, Dict, Optional, Union
import jieba
import jieba.analyse
from openai import OpenAI
from ..core.openai_client import get_global_client, get_default_model
import requests
import base64
from pathlib import Path
import hashlib
import json
import time

logger = logging.getLogger(__name__)


class TextToImageGenerator:
    """文生图生成器 - 集成yunwu API"""
    
    def __init__(self, cache_dir: str = "./image_cache"):
        """
        初始化文生图生成器
        
        Args:
            cache_dir: 图片缓存目录
        """
        self.client = get_global_client()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # 平台配置
        self.platform_configs = {
            "wechat": {
                "size": "1792x1024",  # 16:9 横图
                "style": "professional, clean, minimalist, business",
                "quality": "hd"
            },
            "xiaohongshu": {
                "size": "1024x1024",  # 1:1 方图
                "style": "aesthetic, lifestyle, soft lighting, instagram worthy",
                "quality": "hd"
            },
            "bilibili": {
                "size": "1792x1024",  # 16:9 封面
                "style": "anime style, vibrant colors, dynamic composition",
                "quality": "hd"
            },
            "douyin": {
                "size": "1024x1792",  # 9:16 竖图
                "style": "trendy, eye-catching, modern, bold graphics",
                "quality": "hd"
            }
        }
        
        # 加载自定义词典
        self._load_custom_dict()
    
    def _load_custom_dict(self):
        """加载自定义词典"""
        custom_words = [
            "小红书", "B站", "UP主", "种草", "探店",
            "OOTD", "氛围感", "情绪价值", "干货", "种草",
            "测评", "好物推荐", "生活分享"
        ]
        for word in custom_words:
            jieba.add_word(word)
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        从文案中提取关键词
        
        Args:
            text: 输入文案
            max_keywords: 最大关键词数量
            
        Returns:
            List[str]: 关键词列表
        """
        # 使用jieba提取关键词
        keywords_tfidf = jieba.analyse.extract_tags(
            text, topK=max_keywords * 2, withWeight=False
        )
        
        keywords_textrank = jieba.analyse.textrank(
            text, topK=max_keywords * 2, withWeight=False
        )
        
        # 合并去重
        keywords = []
        seen = set()
        for kw in keywords_tfidf + keywords_textrank:
            if kw not in seen and len(kw) > 1:
                keywords.append(kw)
                seen.add(kw)
                if len(keywords) >= max_keywords:
                    break
        
        return keywords[:max_keywords]
    
    def analyze_content(self, text: str) -> Dict:
        """
        使用Qwen3分析文案内容，提取视觉元素
        
        Args:
            text: 输入文案
            
        Returns:
            Dict: 分析结果
        """
        prompt = f"""
        分析以下文案，提取视觉创作元素，用于图片生成：

        文案内容：
        {text[:1000]}

        请分析并返回JSON格式：
        {{
            "main_objects": ["主要物体1", "主要物体2", "主要物体3"],
            "scene": "场景描述（如：办公室、咖啡厅、户外等）",
            "mood": "情绪氛围（如：温馨、专业、活力、轻松等）",
            "style_keywords": ["风格词1", "风格词2"],
            "color_scheme": ["主色调1", "主色调2"],
            "visual_elements": ["视觉元素1", "视觉元素2"]
        }}

        注意：请确保返回的是有效的JSON格式。
        """
        
        try:
            response = self.client.chat.completions.create(
                model=get_default_model(),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
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
            logger.info(f"内容分析成功: {result}")
            return result
            
        except Exception as e:
            logger.warning(f"AI分析失败，使用基础关键词: {e}")
            keywords = self.extract_keywords(text)
            return {
                "main_objects": keywords[:3],
                "scene": "general",
                "mood": "neutral",
                "style_keywords": ["clean", "modern"],
                "color_scheme": ["balanced"],
                "visual_elements": keywords[3:5] if len(keywords) > 3 else []
            }
    
    def build_prompt(self, analysis: Dict, platform: str = "general") -> str:
        """
        构建图片生成提示词
        
        Args:
            analysis: 内容分析结果
            platform: 目标平台
            
        Returns:
            str: 生成的提示词
        """
        platform_config = self.platform_configs.get(platform, {
            "style": "high quality, professional",
            "quality": "hd"
        })
        
        # 构建主要内容
        objects = ", ".join(analysis.get("main_objects", []))
        scene = analysis.get("scene", "")
        mood = analysis.get("mood", "")
        style_keywords = ", ".join(analysis.get("style_keywords", []))
        colors = ", ".join(analysis.get("color_scheme", []))
        
        # 构建完整提示词
        prompt_parts = []
        
        # 主要内容
        if objects:
            if scene and scene != "general":
                prompt_parts.append(f"{objects} in {scene}")
            else:
                prompt_parts.append(objects)
        
        # 风格和氛围
        if mood and mood != "neutral":
            prompt_parts.append(f"{mood} atmosphere")
        
        if style_keywords:
            prompt_parts.append(style_keywords)
        
        # 平台特定风格
        prompt_parts.append(platform_config.get("style", "high quality"))
        
        # 颜色方案
        if colors and "balanced" not in colors:
            prompt_parts.append(f"{colors} color palette")
        
        # 质量提升词
        prompt_parts.extend([
            "highly detailed",
            "professional photography",
            "4k resolution",
            "award winning"
        ])
        
        final_prompt = ", ".join(prompt_parts)
        logger.info(f"生成提示词: {final_prompt}")
        return final_prompt
    
    def generate_image(self, 
                      text: str, 
                      platform: str = "general",
                      num_images: int = 1,
                      use_cache: bool = True) -> Dict:
        """
        生成图片
        
        Args:
            text: 输入文案
            platform: 目标平台
            num_images: 生成图片数量
            use_cache: 是否使用缓存
            
        Returns:
            Dict: 生成结果
        """
        # 1. 分析内容
        logger.info(f"开始分析文案内容...")
        analysis = self.analyze_content(text)
        
        # 2. 构建提示词
        logger.info(f"构建提示词...")
        prompt = self.build_prompt(analysis, platform)
        
        # 3. 检查缓存
        if use_cache:
            cached_result = self._check_cache(prompt)
            if cached_result:
                logger.info("使用缓存结果")
                return cached_result
        
        # 4. 获取平台配置
        platform_config = self.platform_configs.get(platform, {
            "size": "1024x1024",
            "quality": "hd"
        })
        
        # 5. 调用yunwu API生成图片
        logger.info(f"调用yunwu API生成图片...")
        try:
            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                n=num_images,
                size=platform_config.get("size", "1024x1024"),
                quality=platform_config.get("quality", "hd"),
                response_format="url"
            )
            
            # 6. 处理结果
            result = {
                "success": True,
                "platform": platform,
                "prompt": prompt,
                "analysis": analysis,
                "images": [{"url": img.url, "prompt": prompt} for img in response.data],
                "num_generated": len(response.data),
                "model": "gpt-image-1",
                "provider": "yunwu"
            }
            
            # 7. 保存到缓存
            if use_cache:
                self._save_cache(prompt, result)
            
            logger.info(f"图片生成成功，共{len(response.data)}张")
            return result
            
        except Exception as e:
            logger.error(f"图片生成失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform,
                "prompt": prompt,
                "analysis": analysis
            }
    
    def generate_for_multiple_platforms(self, 
                                      text: str, 
                                      platforms: List[str] = None,
                                      images_per_platform: int = 1) -> Dict:
        """
        为多个平台生成图片
        
        Args:
            text: 输入文案
            platforms: 目标平台列表
            images_per_platform: 每个平台生成的图片数量
            
        Returns:
            Dict: 所有平台的生成结果
        """
        if platforms is None:
            platforms = ["wechat", "xiaohongshu", "bilibili", "douyin"]
        
        results = {}
        
        for platform in platforms:
            logger.info(f"为平台 {platform} 生成图片...")
            try:
                result = self.generate_image(
                    text=text,
                    platform=platform,
                    num_images=images_per_platform
                )
                results[platform] = result
                
                # 避免API限流
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"平台 {platform} 生成失败: {e}")
                results[platform] = {
                    "success": False,
                    "error": str(e),
                    "platform": platform
                }
        
        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "platforms": platforms,
            "results": results,
            "total_success": sum(1 for r in results.values() if r.get("success", False)),
            "total_images": sum(r.get("num_generated", 0) for r in results.values())
        }
    
    def _check_cache(self, prompt: str) -> Optional[Dict]:
        """检查缓存"""
        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"读取缓存失败: {e}")
        return None
    
    def _save_cache(self, prompt: str, result: Dict):
        """保存到缓存"""
        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存缓存失败: {e}")
    
    async def generate_image_async(self, 
                                 text: str, 
                                 platform: str = "general",
                                 num_images: int = 1) -> Dict:
        """
        异步生成图片
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, 
            self.generate_image, 
            text, 
            platform, 
            num_images
        )


# 便捷函数
def quick_generate(text: str, platform: str = "xiaohongshu", num_images: int = 1) -> Dict:
    """
    快速生成图片的便捷函数
    
    Args:
        text: 输入文案
        platform: 目标平台
        num_images: 生成图片数量
        
    Returns:
        Dict: 生成结果
    """
    generator = TextToImageGenerator()
    return generator.generate_image(text, platform, num_images)


def batch_generate(text: str, platforms: List[str] = None) -> Dict:
    """
    批量为多平台生成图片的便捷函数
    
    Args:
        text: 输入文案
        platforms: 目标平台列表
        
    Returns:
        Dict: 所有平台的生成结果
    """
    generator = TextToImageGenerator()
    return generator.generate_for_multiple_platforms(text, platforms)


if __name__ == "__main__":
    # 测试代码
    test_text = """
    今天和大家分享一个超实用的时间管理方法！
    作为一个每天要处理无数任务的职场人，我发现番茄工作法真的太有效了。
    25分钟专注工作，5分钟休息，每4个番茄钟休息15-30分钟。
    这样不仅提高了效率，还避免了长时间工作带来的疲劳。
    办公室里配上一杯咖啡，简直是完美的工作状态！
    """
    
    # 快速测试
    result = quick_generate(test_text, "xiaohongshu", 1)
    print(json.dumps(result, ensure_ascii=False, indent=2))
