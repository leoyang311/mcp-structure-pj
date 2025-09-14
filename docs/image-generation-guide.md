# 图片生成功能使用指南

## 功能概述

基于yunwu API的`gpt-image-1`模型，我为您的内容工厂框架添加了智能图片生成功能。该功能可以从文案内容中自动提取关键信息，并为不同平台生成适配的图片。

## 快速开始

### 1. 基础用法

```python
import asyncio
from src.content_factory.agents.image_agent import quick_image_generation

# 生成单张小红书图片
result = await quick_image_generation(
    text="今天分享一个超实用的时间管理方法！番茄工作法真的很有效...",
    platform="xiaohongshu",
    num_images=1
)

if result['success']:
    print(f"图片URL: {result['images'][0]['url']}")
```

### 2. 多平台批量生成

```python
from src.content_factory.agents.image_agent import multi_platform_generation

# 为多个平台生成图片
result = await multi_platform_generation(
    text="咖啡店探店分享...",
    platforms=["xiaohongshu", "wechat", "douyin"]
)

# 查看结果
for platform, platform_result in result['results'].items():
    if platform_result['success']:
        print(f"{platform}: {platform_result['images'][0]['url']}")
```

### 3. Agent方式调用

```python
from src.content_factory.agents.image_agent import create_image_agent

# 创建Agent实例
agent = create_image_agent()

# 执行生成任务
result = await agent.execute({
    "text": "您的文案内容",
    "platform": "xiaohongshu",
    "num_images": 2,
    "use_cache": True
})
```

## 支持的平台

| 平台 | 尺寸比例 | 适用场景 | 风格特点 |
|------|----------|----------|----------|
| **xiaohongshu** | 1:1 (1024x1024) | 小红书种草图 | 美学生活、柔和光线、INS风 |
| **wechat** | 16:9 (1792x1024) | 微信公众号配图 | 专业简洁、商务信息图 |
| **bilibili** | 16:9 (1792x1024) | B站视频封面 | 动漫插画、鲜艳色彩 |
| **douyin** | 9:16 (1024x1792) | 抖音短视频封面 | 潮流时尚、醒目图形 |

## 核心功能

### 1. 智能内容分析

系统会使用Qwen3模型分析您的文案，提取：
- 主要物体/主题
- 场景描述
- 情绪氛围
- 风格关键词
- 颜色方案
- 目标受众

### 2. 平台适配优化

每个平台都有专门优化的：
- 图片尺寸规格
- 视觉风格偏好
- 色彩搭配方案
- 构图特点

### 3. 缓存机制

- 自动缓存生成结果
- 24小时缓存有效期
- 减少重复API调用

## 集成到现有工作流

### 在Writer Agent中集成

```python
from .image_agent import create_image_agent

class EnhancedWriterAgent(WriterAgent):
    def __init__(self):
        super().__init__()
        self.image_agent = create_image_agent()
    
    async def generate_content_with_images(self, topic: str, platform: str):
        # 1. 生成文案
        content = await self.generate_content(topic)
        
        # 2. 生成配图
        images = await self.image_agent.execute({
            "text": content,
            "platform": platform,
            "num_images": 3
        })
        
        return {
            "content": content,
            "images": images
        }
```

### 批量内容生产

```python
async def batch_content_production(topics: List[str], platforms: List[str]):
    """批量生产内容和图片"""
    image_agent = create_image_agent()
    
    for topic in topics:
        # 生成文案
        content = await generate_content(topic)
        
        # 为所有平台生成图片
        images = await image_agent.execute({
            "text": content,
            "platforms": platforms,
            "num_images": 1
        })
        
        # 保存结果
        save_content_package(topic, content, images)
```

## 环境配置

确保您的环境变量已正确配置：

```bash
# yunwu API配置（必需）
export YUNWU_API_KEY="your-yunwu-api-key"
export YUNWU_BASE_URL="https://yunwu.ai/v1"  # 可选，默认会自动设置

# 或者使用通用OpenAI配置
export OPENAI_API_KEY="your-yunwu-api-key"
export OPENAI_API_BASE="https://yunwu.ai/v1"
```

## 成本和限制

### API成本
- 使用yunwu API的`gpt-image-1`模型
- 具体价格请参考yunwu官方定价

### 技术限制
- 支持中文和英文提示词
- 最佳效果建议每张图片提示词长度在200-500字符
- 建议单次生成不超过10张图片

### 缓存优化
- 相同提示词和平台的图片会被缓存24小时
- 缓存文件存储在`./image_cache/`目录

## 错误处理

系统具备完善的错误处理机制：

```python
result = await quick_image_generation(text="", platform="xiaohongshu")
if not result['success']:
    print(f"生成失败: {result['error']}")
    # 处理失败情况
```

常见错误类型：
- 文案内容为空
- API密钥配置错误
- 网络连接问题
- API限额超出

## 测试验证

运行测试脚本验证功能：

```bash
cd /Users/yangshuntian/Downloads/mcp-structure-pj/fastmcp-content-factory
python test_image_generation.py
```

测试将验证：
- 单平台图片生成
- 多平台批量生成
- 错误处理机制
- Agent配置信息

## 自定义扩展

### 添加新平台

```python
# 在ImageGenerationAgent中添加新平台配置
self.platform_configs["new_platform"] = {
    "size": "1080x1350",  # 4:5比例
    "style": "minimalist, elegant, soft colors",
    "quality": "hd",
    "description": "新平台配图"
}
```

### 自定义提示词模板

```python
def custom_prompt_builder(self, analysis: Dict, platform: str) -> str:
    """自定义提示词构建逻辑"""
    # 您的自定义逻辑
    return custom_prompt
```

## 最佳实践

1. **文案质量**: 提供详细、生动的文案描述能获得更好的图片效果
2. **平台选择**: 根据内容类型选择最适合的平台配置
3. **批量生成**: 对于大量内容，建议使用批量接口减少调用次数
4. **缓存利用**: 相似内容可以复用缓存结果
5. **错误处理**: 始终检查返回结果的`success`字段

## 支持与反馈

如果您在使用过程中遇到问题，请检查：
1. 环境变量配置是否正确
2. yunwu API密钥是否有效
3. 网络连接是否正常
4. 查看日志输出获取详细错误信息
