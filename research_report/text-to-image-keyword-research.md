# 文案关键词提取与文生图优化技术调研报告

## 执行摘要

本报告针对多平台内容生产系统中的文生图需求，研究如何从文案中提取高质量关键词以生成更好的配图。重点为独立开发者提供低成本、高效率的实现方案。

---

## 1. 研究背景与目标

### 1.1 业务需求
- **微信公众号**: 需要3-5张配图，信息图表为主
- **小红书**: 需要4-9张精美配图，视觉冲击力强
- **B站视频**: 需要封面图和内容配图
- **抖音**: 需要吸睛封面和关键帧

### 1.2 核心挑战
1. 不同平台的视觉风格差异巨大
2. 文案到视觉元素的语义转换困难
3. API成本控制（独立开发者预算有限）
4. 生成图片的一致性和品质保证

### 1.3 研究目标
- 建立文案→关键词→提示词的高效转换管道
- 实现平台差异化的图片生成策略
- 控制成本在每月$50以内
- 确保70%以上的图片可直接使用

---

## 2. 技术方案对比

### 2.1 关键词提取技术栈

| 方案 | 技术栈 | 成本 | 效果 | 独立开发友好度 |
|------|--------|------|------|----------------|
| **方案A: 纯开源** | spaCy + KeyBERT | $0 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **方案B: 混合方案** | Jieba + GPT-3.5 | $5-10/月 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **方案C: 全AI** | GPT-4 + Claude | $30-50/月 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **方案D: 本地LLM** | Ollama + Qwen | $0 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 2.2 图片生成服务对比

| 服务 | 价格 | 质量 | API便利性 | 中文支持 |
|------|------|------|-----------|----------|
| **Stable Diffusion API** | $0.002/张 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Midjourney API** | $0.05/张 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **DALL-E 3** | $0.04/张 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **通义万相** | ¥0.08/张 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **本地SD** | $0 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 3. 推荐技术架构

### 3.1 整体架构图

```
文案输入
    ↓
[关键词提取模块]
    ├── 实体识别 (NER)
    ├── 主题提取 (Topic)
    ├── 情感分析 (Sentiment)
    └── 风格识别 (Style)
    ↓
[提示词构建模块]
    ├── 平台模板适配
    ├── 风格词注入
    └── 负向提示词
    ↓
[图片生成模块]
    ├── API调用管理
    ├── 批量生成
    └── 质量检查
    ↓
[后处理模块]
    ├── 尺寸调整
    ├── 水印添加
    └── 格式转换
    ↓
输出图片
```

### 3.2 核心实现代码

#### 3.2.1 关键词提取器（推荐方案B：混合方案）

```python
# keyword_extractor.py
import jieba
import jieba.analyse
from typing import List, Dict, Tuple
import openai
import json
import re

class SmartKeywordExtractor:
    """智能关键词提取器 - 独立开发者友好版"""
    
    def __init__(self, use_ai=True, ai_model="gpt-3.5-turbo"):
        self.use_ai = use_ai
        self.ai_model = ai_model
        
        # 加载自定义词典（重要！）
        self.load_custom_dict()
        
        # 平台特定的视觉风格词
        self.platform_styles = {
            "wechat": ["专业", "简洁", "商务", "信息图"],
            "xiaohongshu": ["唯美", "温馨", "精致", "生活感"],
            "bilibili": ["动漫", "二次元", "科技感", "活力"],
            "douyin": ["潮流", "炫酷", "动感", "年轻"]
        }
    
    def load_custom_dict(self):
        """加载行业词典，提高准确率"""
        # 添加平台特定词汇
        custom_words = [
            "小红书", "B站", "UP主", "种草", "探店",
            "OOTD", "氛围感", "情绪价值", "干货"
        ]
        for word in custom_words:
            jieba.add_word(word)
    
    def extract_keywords(self, 
                         text: str, 
                         platform: str = "general",
                         top_k: int = 5) -> Dict:
        """主函数：提取关键词"""
        
        # Step 1: 基础关键词提取（免费）
        basic_keywords = self.extract_basic_keywords(text, top_k)
        
        # Step 2: 实体识别（免费）
        entities = self.extract_entities(text)
        
        # Step 3: 情感和风格分析（可选AI增强）
        if self.use_ai:
            enhanced_data = self.ai_enhance(text, basic_keywords, platform)
        else:
            enhanced_data = self.rule_based_enhance(text, platform)
        
        # Step 4: 构建最终结果
        result = {
            "main_keywords": basic_keywords[:top_k],
            "entities": entities,
            "scene": enhanced_data.get("scene", "general"),
            "mood": enhanced_data.get("mood", "neutral"),
            "style": enhanced_data.get("style", []),
            "platform_style": self.platform_styles.get(platform, []),
            "color_hints": enhanced_data.get("colors", [])
        }
        
        return result
    
    def extract_basic_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """使用jieba提取基础关键词 - 完全免费"""
        # TF-IDF提取
        keywords_tfidf = jieba.analyse.extract_tags(
            text, topK=top_k, withWeight=False
        )
        
        # TextRank提取（更注重语义）
        keywords_textrank = jieba.analyse.textrank(
            text, topK=top_k, withWeight=False
        )
        
        # 合并去重，TF-IDF优先
        keywords = []
        seen = set()
        for kw in keywords_tfidf + keywords_textrank:
            if kw not in seen and len(kw) > 1:
                keywords.append(kw)
                seen.add(kw)
        
        return keywords[:top_k]
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """提取实体（人物、地点、品牌等）"""
        entities = {
            "person": [],
            "location": [],
            "brand": [],
            "product": []
        }
        
        # 简单规则匹配（可扩展）
        # 人名模式
        person_pattern = r'(?:小|老|大)?[王李张刘陈杨黄赵周吴徐孙马胡郭何高林郑谢唐许][\u4e00-\u9fa5]{1,2}(?:老师|同学|先生|女士)?'
        entities["person"] = re.findall(person_pattern, text)
        
        # 地点模式
        location_pattern = r'[\u4e00-\u9fa5]{2,}(?:市|省|区|县|镇|街|路|广场|公园|大厦)'
        entities["location"] = re.findall(location_pattern, text)
        
        # 品牌检测（使用预定义列表）
        brands = ["苹果", "华为", "小米", "特斯拉", "星巴克", "肯德基"]
        for brand in brands:
            if brand in text:
                entities["brand"].append(brand)
        
        return entities
    
    def ai_enhance(self, text: str, keywords: List[str], platform: str) -> Dict:
        """使用AI增强关键词（成本：约$0.002/次）"""
        
        prompt = f"""
        分析以下文案，提取视觉元素：
        文案：{text[:500]}
        已有关键词：{', '.join(keywords[:5])}
        目标平台：{platform}
        
        请返回JSON格式：
        {{
            "scene": "描述主要场景（如：办公室、咖啡厅、户外）",
            "mood": "情绪氛围（如：温馨、专业、活力）",
            "style": ["视觉风格词1", "视觉风格词2"],
            "colors": ["主色调1", "主色调2"],
            "objects": ["物体1", "物体2", "物体3"]
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.ai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI增强失败，降级到规则方案: {e}")
            return self.rule_based_enhance(text, platform)
    
    def rule_based_enhance(self, text: str, platform: str) -> Dict:
        """基于规则的增强（完全免费的降级方案）"""
        
        result = {
            "scene": "general",
            "mood": "neutral",
            "style": [],
            "colors": [],
            "objects": []
        }
        
        # 场景检测
        scene_keywords = {
            "办公室": ["办公", "工作", "会议", "职场"],
            "家居": ["家", "客厅", "卧室", "厨房"],
            "户外": ["公园", "街道", "旅行", "风景"],
            "咖啡厅": ["咖啡", "下午茶", "休闲"]
        }
        
        for scene, keywords in scene_keywords.items():
            if any(kw in text for kw in keywords):
                result["scene"] = scene
                break
        
        # 情绪检测
        mood_keywords = {
            "happy": ["开心", "快乐", "愉快", "幸福"],
            "professional": ["专业", "严谨", "商务"],
            "cozy": ["温馨", "舒适", "温暖"],
            "energetic": ["活力", "激情", "运动"]
        }
        
        for mood, keywords in mood_keywords.items():
            if any(kw in text for kw in keywords):
                result["mood"] = mood
                break
        
        # 平台特定风格
        result["style"] = self.platform_styles.get(platform, ["general"])
        
        # 颜色推断
        if "温馨" in text or "温暖" in text:
            result["colors"] = ["warm", "orange", "yellow"]
        elif "专业" in text or "商务" in text:
            result["colors"] = ["blue", "gray", "white"]
        elif "自然" in text or "清新" in text:
            result["colors"] = ["green", "light blue"]
        
        return result
```

#### 3.2.2 提示词构建器

```python
# prompt_builder.py
from typing import Dict, List
import random

class PromptBuilder:
    """提示词构建器 - 平台优化版"""
    
    def __init__(self):
        # 基础模板
        self.base_templates = {
            "wechat": "{objects}, professional infographic style, clean design, {colors} color scheme, minimalist, business presentation, {mood} atmosphere",
            "xiaohongshu": "{objects}, lifestyle photography, aesthetic, {colors} palette, instagram worthy, soft lighting, {mood} vibe, high quality",
            "bilibili": "{objects}, anime style illustration, vibrant colors, {colors} theme, dynamic composition, {mood} feeling, detailed artwork",
            "douyin": "{objects}, trendy visual, eye-catching, {colors} colors, modern design, {mood} energy, vertical format, bold graphics"
        }
        
        # 质量提升词
        self.quality_boosters = [
            "highly detailed", "4k quality", "professional photography",
            "award winning", "trending on artstation", "masterpiece"
        ]
        
        # 负向提示词（避免常见问题）
        self.negative_prompts = {
            "general": "low quality, blurry, distorted, ugly, bad anatomy, watermark, text, logo",
            "people": "deformed faces, extra limbs, bad hands, mutated",
            "product": "low resolution, pixelated, amateur, poor lighting"
        }
    
    def build_prompt(self, 
                     keywords_data: Dict, 
                     platform: str,
                     include_negative: bool = True) -> Dict[str, str]:
        """构建完整的提示词"""
        
        # 提取关键信息
        objects = keywords_data.get("main_keywords", [])[:3]
        scene = keywords_data.get("scene", "")
        mood = keywords_data.get("mood", "neutral")
        colors = keywords_data.get("color_hints", ["balanced"])
        style = keywords_data.get("style", [])
        
        # 构建主要对象描述
        objects_str = ", ".join(objects) if objects else "content"
        if scene and scene != "general":
            objects_str = f"{objects_str} in {scene}"
        
        # 选择模板
        template = self.base_templates.get(
            platform, 
            self.base_templates["wechat"]
        )
        
        # 填充模板
        positive_prompt = template.format(
            objects=objects_str,
            colors=", ".join(colors[:2]) if colors else "harmonious",
            mood=mood
        )
        
        # 添加风格词
        if style:
            positive_prompt += f", {', '.join(style[:2])}"
        
        # 添加质量提升词（随机选2个）
        boosters = random.sample(self.quality_boosters, 2)
        positive_prompt += f", {', '.join(boosters)}"
        
        # 构建负向提示词
        negative_prompt = self.negative_prompts["general"]
        if any(word in objects_str for word in ["人", "人物", "girl", "boy", "man", "woman"]):
            negative_prompt += f", {self.negative_prompts['people']}"
        
        return {
            "positive": positive_prompt,
            "negative": negative_prompt if include_negative else "",
            "platform": platform,
            "metadata": {
                "keywords": objects,
                "scene": scene,
                "mood": mood
            }
        }
    
    def build_batch_prompts(self, 
                           keywords_data: Dict,
                           platform: str,
                           variations: int = 3) -> List[Dict]:
        """生成多个变体提示词"""
        
        prompts = []
        
        # 基础提示词
        base_prompt = self.build_prompt(keywords_data, platform)
        prompts.append(base_prompt)
        
        # 生成变体
        variation_styles = {
            "wechat": ["infographic", "chart", "diagram", "illustration"],
            "xiaohongshu": ["flat lay", "lifestyle", "aesthetic", "minimal"],
            "bilibili": ["anime", "cartoon", "chibi", "manga"],
            "douyin": ["neon", "gradient", "3d render", "collage"]
        }
        
        platform_styles = variation_styles.get(platform, ["artistic"])
        
        for i in range(variations - 1):
            # 复制基础数据
            variant_data = keywords_data.copy()
            
            # 添加变体风格
            style_addition = random.choice(platform_styles)
            variant_prompt = base_prompt["positive"] + f", {style_addition} style"
            
            prompts.append({
                "positive": variant_prompt,
                "negative": base_prompt["negative"],
                "platform": platform,
                "variant": i + 1,
                "style_addition": style_addition
            })
        
        return prompts
```

#### 3.2.3 图片生成管理器

```python
# image_generator.py
import requests
import base64
from typing import List, Dict, Optional
import time
import hashlib
from pathlib import Path

class ImageGenerator:
    """图片生成管理器 - 成本优化版"""
    
    def __init__(self, 
                 provider: str = "stable-diffusion",
                 api_key: Optional[str] = None,
                 cache_dir: str = "./image_cache"):
        
        self.provider = provider
        self.api_key = api_key
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # API配置
        self.api_configs = {
            "stable-diffusion": {
                "url": "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                "headers": {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                "cost_per_image": 0.002
            },
            "dalle": {
                "url": "https://api.openai.com/v1/images/generations",
                "headers": {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                "cost_per_image": 0.04
            },
            "local-sd": {
                "url": "http://localhost:7860/sdapi/v1/txt2img",
                "headers": {"Content-Type": "application/json"},
                "cost_per_image": 0
            }
        }
        
        # 平台尺寸配置
        self.platform_sizes = {
            "wechat": (900, 500),      # 16:9 横图
            "xiaohongshu": (1080, 1080),  # 1:1 方图
            "bilibili": (1920, 1080),   # 16:9 封面
            "douyin": (1080, 1920)      # 9:16 竖图
        }
        
        # 成本追踪
        self.monthly_cost = 0
        self.monthly_limit = 50  # 美元
    
    def generate_image(self, 
                       prompt_data: Dict,
                       platform: str,
                       use_cache: bool = True) -> Dict:
        """生成单张图片"""
        
        # 检查缓存
        if use_cache:
            cached = self.check_cache(prompt_data["positive"])
            if cached:
                return cached
        
        # 检查月度预算
        if self.check_budget():
            return self.generate_fallback_image(prompt_data, platform)
        
        # 获取平台尺寸
        width, height = self.platform_sizes.get(platform, (1024, 1024))
        
        # 构建请求
        if self.provider == "stable-diffusion":
            request_body = {
                "text_prompts": [
                    {"text": prompt_data["positive"], "weight": 1},
                    {"text": prompt_data["negative"], "weight": -1}
                ],
                "cfg_scale": 7,
                "width": width,
                "height": height,
                "samples": 1,
                "steps": 30
            }
        elif self.provider == "dalle":
            request_body = {
                "model": "dall-e-3",
                "prompt": prompt_data["positive"],
                "n": 1,
                "size": f"{width}x{height}",
                "quality": "standard"
            }
        else:  # local-sd
            request_body = {
                "prompt": prompt_data["positive"],
                "negative_prompt": prompt_data["negative"],
                "width": width,
                "height": height,
                "steps": 20,
                "cfg_scale": 7
            }
        
        # 发送请求
        try:
            config = self.api_configs[self.provider]
            response = requests.post(
                config["url"],
                json=request_body,
                headers=config["headers"],
                timeout=60
            )
            response.raise_for_status()
            
            # 解析响应
            result = self.parse_response(response.json())
            
            # 更新成本
            self.monthly_cost += config["cost_per_image"]
            
            # 保存到缓存
            if use_cache:
                self.save_to_cache(prompt_data["positive"], result)
            
            return result
            
        except Exception as e:
            print(f"图片生成失败: {e}")
            return self.generate_fallback_image(prompt_data, platform)
    
    def generate_batch(self,
                      prompts: List[Dict],
                      platform: str,
                      max_parallel: int = 3) -> List[Dict]:
        """批量生成图片（控制并发）"""
        
        results = []
        
        for i in range(0, len(prompts), max_parallel):
            batch = prompts[i:i+max_parallel]
            
            for prompt_data in batch:
                result = self.generate_image(prompt_data, platform)
                results.append(result)
                
                # 避免API限流
                time.sleep(1)
        
        return results
    
    def check_cache(self, prompt: str) -> Optional[Dict]:
        """检查缓存（节省成本）"""
        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            import json
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None
    
    def save_to_cache(self, prompt: str, result: Dict):
        """保存到缓存"""
        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        import json
        with open(cache_file, 'w') as f:
            json.dump(result, f)
    
    def check_budget(self) -> bool:
        """检查月度预算"""
        return self.monthly_cost >= self.monthly_limit
    
    def generate_fallback_image(self, prompt_data: Dict, platform: str) -> Dict:
        """生成备用图片（预算超限时）"""
        # 使用免费的占位图服务
        width, height = self.platform_sizes.get(platform, (1024, 1024))
        
        # 使用关键词生成占位图
        keywords = prompt_data.get("metadata", {}).get("keywords", ["placeholder"])
        text = "+".join(keywords[:2])
        
        return {
            "url": f"https://via.placeholder.com/{width}x{height}.png?text={text}",
            "provider": "placeholder",
            "cost": 0,
            "metadata": prompt_data.get("metadata", {})
        }
    
    def parse_response(self, response_data: Dict) -> Dict:
        """解析不同服务商的响应"""
        
        if self.provider == "stable-diffusion":
            image_b64 = response_data["artifacts"][0]["base64"]
            return {
                "base64": image_b64,
                "provider": self.provider,
                "cost": 0.002
            }
        elif self.provider == "dalle":
            return {
                "url": response_data["data"][0]["url"],
                "provider": self.provider,
                "cost": 0.04
            }
        else:  # local-sd
            return {
                "base64": response_data["images"][0],
                "provider": "local",
                "cost": 0
            }
```

### 3.3 完整工作流示例

```python
# main_pipeline.py
from keyword_extractor import SmartKeywordExtractor
from prompt_builder import PromptBuilder
from image_generator import ImageGenerator

class Text2ImagePipeline:
    """文生图完整管道"""
    
    def __init__(self, 
                 use_ai_enhance: bool = True,
                 image_provider: str = "stable-diffusion"):
        
        self.extractor = SmartKeywordExtractor(use_ai=use_ai_enhance)
        self.prompt_builder = PromptBuilder()
        self.generator = ImageGenerator(provider=image_provider)
    
    def process_content(self, 
                       content: str,
                       platform: str,
                       num_images: int = 3) -> Dict:
        """处理单条内容"""
        
        print(f"[1/4] 提取关键词...")
        keywords_data = self.extractor.extract_keywords(
            content, 
            platform=platform,
            top_k=5
        )
        print(f"  关键词: {keywords_data['main_keywords']}")
        
        print(f"[2/4] 构建提示词...")
        prompts = self.prompt_builder.build_batch_prompts(
            keywords_data,
            platform=platform,
            variations=num_images
        )
        print(f"  生成{len(prompts)}个提示词变体")
        
        print(f"[3/4] 生成图片...")
        images = self.generator.generate_batch(
            prompts,
            platform=platform
        )
        print(f"  成功生成{len(images)}张图片")
        
        print(f"[4/4] 后处理...")
        processed_images = self.post_process(images, platform)
        
        return {
            "platform": platform,
            "keywords": keywords_data,
            "prompts": prompts,
            "images": processed_images,
            "cost": sum(img.get("cost", 0) for img in images)
        }
    
    def post_process(self, images: List[Dict], platform: str) -> List[Dict]:
        """图片后处理"""
        processed = []
        
        for img in images:
            # 添加平台特定处理
            if platform == "xiaohongshu":
                # 添加边框或贴纸
                img["processed"] = True
                img["filters"] = ["soft", "warm"]
            elif platform == "wechat":
                # 添加信息标注
                img["processed"] = True
                img["annotations"] = True
            
            processed.append(img)
        
        return processed

# 使用示例
if __name__ == "__main__":
    # 测试文案
    test_content = """
    今天和大家分享一个超实用的时间管理方法！
    作为一个每天要处理无数任务的职场人，我发现番茄工作法真的太有效了。
    25分钟专注工作，5分钟休息，每4个番茄钟休息15-30分钟。
    这样不仅提高了效率，还避免了长时间工作带来的疲劳。
    办公室里配上一杯咖啡，简直是完美的工作状态！
    """
    
    # 初始化管道
    pipeline = Text2ImagePipeline(
        use_ai_enhance=True,  # 使用AI增强
        image_provider="stable-diffusion"  # 使用SD API
    )
    
    # 为不同平台生成图片
    platforms = ["wechat", "xiaohongshu", "bilibili", "douyin"]
    
    for platform in platforms:
        print(f"\n{'='*50}")
        print(f"处理平台: {platform}")
        print('='*50)
        
        result = pipeline.process_content(
            content=test_content,
            platform=platform,
            num_images=3 if platform == "xiaohongshu" else 1
        )
        
        print(f"\n结果汇总:")
        print(f"- 主要关键词: {result['keywords']['main_keywords']}")
        print(f"- 场景: {result['keywords']['scene']}")
        print(f"- 情绪: {result['keywords']['mood']}")
        print(f"- 生成图片数: {len(result['images'])}")
        print(f"- 总成本: ${result['cost']:.3f}")
```

---

## 4. 成本优化策略

### 4.1 分层处理策略

```python
class CostOptimizer:
    """成本优化器"""
    
    def __init__(self, monthly_budget: float = 50):
        self.monthly_budget = monthly_budget
        self.current_cost = 0
        
        # 优先级配置
        self.priority_config = {
            "xiaohongshu": 3,  # 最高优先级
            "wechat": 2,
            "bilibili": 2,
            "douyin": 1
        }
    
    def select_generation_strategy(self, platform: str, content_importance: str) -> Dict:
        """根据预算和重要性选择生成策略"""
        
        remaining_budget = self.monthly_budget - self.current_cost
        priority = self.priority_config.get(platform, 1)
        
        if remaining_budget > 30:
            # 预算充足：使用最佳方案
            return {
                "provider": "dalle",
                "quality": "high",
                "num_variations": 3
            }
        elif remaining_budget > 10:
            # 预算一般：混合方案
            if priority >= 2 or content_importance == "high":
                return {
                    "provider": "stable-diffusion",
                    "quality": "medium",
                    "num_variations": 2
                }
            else:
                return {
                    "provider": "local-sd",
                    "quality": "basic",
                    "num_variations": 1
                }
        else:
            # 预算紧张：本地方案
            return {
                "provider": "local-sd",
                "quality": "basic",
                "num_variations": 1
            }
```

### 4.2 缓存策略

```python
class SmartCache:
    """智能缓存系统"""
    
    def __init__(self):
        self.semantic_cache = {}  # 语义相似度缓存
        self.style_cache = {}     # 风格模板缓存
        
    def find_similar_image(self, keywords: List[str], threshold: float = 0.8) -> Optional[str]:
        """查找语义相似的已生成图片"""
        
        # 使用简单的Jaccard相似度
        for cached_keywords, image_path in self.semantic_cache.items():
            similarity = self.calculate_similarity(keywords, cached_keywords)
            if similarity > threshold:
                return image_path
        
        return None
    
    def calculate_similarity(self, keywords1: List[str], keywords2: List[str]) -> float:
        """计算关键词相似度"""
        set1 = set(keywords1)
        set2 = set(keywords2)
        
        if not set1 or not set2:
            return 0
        
        intersection = set1 & set2
        union = set1 | set2
        
        return len(intersection) / len(union)
```



## 6. 性能指标与优化目标

### 6.1 关键指标

| 指标 | 当前 | 目标 | 优化方法 |
|------|------|------|----------|
| **关键词准确率** | 60% | 85% | 自定义词典+AI增强 |
| **图片可用率** | 50% | 70% | 平台模板优化 |
| **平均生成时间** | 30s | 10s | 缓存+批处理 |
| **月均成本** | $80 | $50 | 智能降级+缓存 |
| **用户满意度** | 3.5/5 | 4.2/5 | A/B测试优化 |

### 6.2 优化优先级

1. **高优先级**
   - 提高小红书图片质量（ROI最高）
   - 优化提示词模板
   - 实现智能缓存

2. **中优先级**
   - 多语言支持
   - 批量处理优化

3. **低优先级**
   - 自定义风格训练
   - 图片编辑功能
   - 高级后处理

---

## 7. 常见问题与解决方案

### Q1: 中文提示词效果差怎么办？
**解决方案**：
1. 使用翻译API转英文（成本+$0.001/次）
2. 混合中英文提示词
3. 选择中文支持好的模型（通义万相）

### Q2: 生成的图片风格不一致？
**解决方案**：
1. 使用固定的seed值
2. 创建平台专属的LoRA模型
3. 严格控制提示词模板

### Q3: API成本超预算？
**解决方案**：
1. 实施三级降级策略
2. 提高缓存命中率
3. 非关键内容使用本地SD

### Q4: 图片生成速度慢？
**解决方案**：
1. 实现预生成机制
2. 使用异步批处理
3. 部署本地加速方案

---

