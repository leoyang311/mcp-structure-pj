---
description: 为中文社交平台（微信/小红书/B站/抖音）生成多平台内容
---

# 生成多平台内容

用户想为某个话题生成中文社交媒体内容。

## 工作流程

1. **解析用户输入**：从消息中提取话题、目标平台（默认全平台）、研究深度（默认 medium）
2. **运行内容生成管道**：
   ```bash
   cd /home/leo/Claude_access/mcp-structure-pj
   python -c "
   import asyncio, json
   from src.content_factory.core.content_pipeline import ContentPipeline
   from src.content_factory.models import ContentTask, Platform

   topic = '$TOPIC'
   platforms = [Platform.WECHAT, Platform.XIAOHONGSHU, Platform.BILIBILI, Platform.DOUYIN]
   task = ContentTask(topic=topic, platforms=platforms, research_depth='medium', versions_per_platform=1)

   async def run():
       pipeline = ContentPipeline()
       result = await pipeline.execute(task)
       for v in result.content_versions:
           print(f'=== {v.platform.value} ===')
           print(f'标题: {v.title}')
           print(v.content[:500])
           print()

   asyncio.run(run())
   "
   ```
3. **展示结果**：按平台格式化展示标题和内容预览，标注质量分数
4. **提供保存选项**：询问是否导出到文件

## 注意事项
- 生成前确认话题和平台
- 若用户只提到某平台，只生成该平台内容
- 内容遵循 CASE 框架（具体数据、真实案例、具体细节、专家来源）
