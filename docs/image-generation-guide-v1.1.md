# 图片生成功能使用指南 v1.1.0

## 🎉 功能状态

- **✅ 单平台图片生成** - 已完成测试
- **✅ 多平台批量生成** - 已完成测试  
- **✅ Base64图片处理** - yunwu API返回base64编码图片，自动解码保存
- **✅ 智能缓存机制** - 避免重复API调用
- **✅ 平台适配优化** - 针对不同平台的尺寸和风格优化

## 功能概述

基于yunwu API的gpt-image-1模型，智能化地从文案内容生成适合不同平台的高质量图片。

## 支持的平台配置

| 平台 | 尺寸 | 风格特点 | 适用场景 |
|------|------|----------|----------|
| **小红书** | 1024x1024 (正方形) | 美学生活风格，柔和光线，Ins风 | 种草图、生活分享 |
| **微信公众号** | 1536x1024 (3:2横图) | 专业简洁，商务展示，信息图表风 | 文章配图、头图 |
| **B站** | 1536x1024 (3:2横图) | 动漫插画风格，鲜艳色彩，动态构图 | 视频封面、UP主头图 |
| **抖音** | 1024x1536 (2:3竖图) | 时尚视觉，抓人眼球，现代设计 | 短视频封面、竖屏内容 |

## yunwu API 图片尺寸限制

yunwu API的gpt-image-1模型支持以下尺寸：
- `1024x1024` - 正方形
- `1024x1536` - 竖图 (2:3比例)  
- `1536x1024` - 横图 (3:2比例)
- `auto` - 自动选择

## 快速开始

### 1. 单平台生成

```python
from content_factory.agents.image_agent import quick_image_generation

# 生成小红书配图
result = await quick_image_generation(
    text="分享一个超实用的时间管理技巧！",
    platform="xiaohongshu",
    num_images=1
)

if result['success']:
    image_path = result['images'][0]['image_path']
    print(f"图片已保存到: {image_path}")
```

### 2. 多平台批量生成

```python
from content_factory.agents.image_agent import multi_platform_generation

# 为多个平台生成配图
result = await multi_platform_generation(
    text="分享一个超实用的时间管理技巧！",
    platforms=["xiaohongshu", "wechat", "douyin"]
)

# 查看生成结果
for platform, platform_result in result['results'].items():
    if platform_result['success']:
        image_path = platform_result['images'][0]['image_path']
        print(f"{platform}: {image_path}")
```

### 3. 使用Agent类

```python
from content_factory.agents.image_agent import ImageGenerationAgent

# 创建Agent实例
agent = ImageGenerationAgent()

# 处理生成请求
result = await agent.process({
    "text": "文案内容",
    "platform": "xiaohongshu",
    "num_images": 1,
    "use_cache": True
})
```

## 核心特性

### 🎯 智能内容分析

使用Qwen3模型分析文案内容，提取：
- 主要物体/主题关键词
- 场景描述
- 情绪氛围
- 风格关键词  
- 颜色方案
- 目标受众

### 🎨 平台化风格适配

每个平台都有专门优化的提示词模板：

- **小红书**: 美学生活摄影风格，柔和光线，马卡龙色调
- **微信**: 专业简洁，商务展示，信息图表风格
- **B站**: 动漫插画风格，鲜艳色彩，动态构图
- **抖音**: 时尚视觉，抓人眼球，竖屏构图

### 💾 智能缓存系统

- 基于内容hash的缓存机制
- 24小时缓存有效期
- 自动缓存管理，节省API调用

### 🖼️ Base64图片处理

yunwu API返回base64编码的图片数据，系统自动：
1. 解码base64数据
2. 保存为PNG格式文件
3. 验证文件完整性
4. 返回本地文件路径

## API响应格式

### 成功响应示例
```json
{
  "success": true,
  "platform": "xiaohongshu",
  "platform_description": "小红书种草图",
  "prompt": "content, information, illustration, aesthetic, lifestyle photography...",
  "images": [
    {
      "index": 1,
      "image_path": "/path/to/image.png",
      "size": "1024x1024",
      "platform": "xiaohongshu"
    }
  ],
  "num_generated": 1,
  "model": "gpt-image-1",
  "provider": "yunwu"
}
```

### 多平台响应示例
```json
{
  "success": true,
  "type": "multi_platform",
  "platforms": ["xiaohongshu", "wechat"],
  "results": {
    "xiaohongshu": { "success": true, "images": [...] },
    "wechat": { "success": true, "images": [...] }
  },
  "summary": {
    "total_platforms": 2,
    "successful_platforms": 2,
    "total_images": 2
  }
}
```

## 环境配置

### 必需的环境变量

```bash
# yunwu API配置
export YUNWU_API_KEY="your-yunwu-api-key"

# 或者使用OpenAI兼容配置
export OPENAI_API_KEY="your-yunwu-api-key"
export OPENAI_API_BASE="https://yunwu.ai/v1"
```

### 创建.env文件

```env
# yunwu API配置  
YUNWU_API_KEY=your-yunwu-api-key
OPENAI_API_BASE=https://yunwu.ai/v1

# Qwen3分析模型
QWEN_MODEL=qwen3-235b-a22b-think
```

## 测试脚本

### 快速功能测试
```bash
python test_base64_images.py
```

### 多平台测试
```bash  
python test_multi_platform.py
```

### 完整集成测试
```bash
python test_image_generation.py
```

## 缓存管理

### 缓存目录结构
```
image_cache/
├── 022e38f41d78dac038ad02a943bdc155.png  # 生成的图片文件
├── 022e38f41d78dac038ad02a943bdc155.json # 缓存元数据
└── ...
```

### 手动清理缓存
```bash
rm -rf image_cache/*
```

## 错误处理

### 常见错误及解决方案

1. **API密钥错误**
   ```
   错误: Authentication failed
   解决: 检查YUNWU_API_KEY环境变量
   ```

2. **图片尺寸不支持** 
   ```
   错误: Invalid value for size
   解决: 使用支持的尺寸 1024x1024, 1024x1536, 1536x1024
   ```

3. **内容分析失败**
   ```
   警告: AI分析失败，使用默认分析
   影响: 提示词质量可能降低，但不影响图片生成
   ```

## 性能优化建议

1. **启用缓存**: 对于相同内容，使用缓存可以显著提升响应速度
2. **批量生成**: 多平台需求时使用`multi_platform_generation`
3. **异步处理**: 大量图片生成时使用异步方式
4. **定期清理**: 定期清理过期缓存文件

## 集成示例

查看完整的集成演示:
```bash
python demo_integrated_content_factory.py
```

## 技术规格

- **API提供商**: yunwu.ai
- **模型**: gpt-image-1  
- **图片格式**: PNG
- **图片质量**: 高清 (1M+ 文件大小)
- **分析模型**: qwen3-235b-a22b-think
- **缓存策略**: 24小时有效期

## 更新日志

### v1.1.0 (2024-08-19)
- ✅ 修复yunwu API base64图片处理
- ✅ 更新平台尺寸配置以符合API限制
- ✅ 添加图片格式验证
- ✅ 完善错误处理和日志记录

### v1.0.0 (2024-08-18)  
- ✅ 基础图片生成功能
- ✅ 多平台适配
- ✅ 智能缓存机制
- ✅ 内容分析优化
