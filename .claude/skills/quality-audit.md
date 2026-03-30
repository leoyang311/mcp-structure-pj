---
description: 对已生成的内容进行质量审计，输出详细评分和改进建议
---

# 内容质量审计

用户想对一段内容进行质量评估，或审计最近生成的内容批次。

## 工作流程

1. **获取内容**：
   - 若用户提供了文本 → 直接使用
   - 若用户说"审计最近的内容" → 读取 `view_articles.py` 或最新输出文件

2. **运行结构化评分**：
   ```bash
   cd /home/leo/Claude_access/mcp-structure-pj
   python -c "
   import asyncio
   from src.content_factory.agents.scorer_agent import ScorerAgent
   from src.content_factory.models import ContentVersion, Platform, ContentType
   import uuid

   content_text = '''$CONTENT'''
   version = ContentVersion(
       version_id=str(uuid.uuid4()),
       platform=Platform.$PLATFORM,
       content_type=ContentType.ARTICLE,
       title='待审计内容',
       content=content_text,
       metadata={}
   )

   async def run():
       agent = ScorerAgent()
       result = await agent.process({'content_versions': [version], 'video_versions': []})
       for vid, score in result['quality_scores'].items():
           print(f'综合得分: {score.total_score:.1f}')
           print(f'  内容质量: {score.content_quality:.1f}')
           print(f'  平台适配: {score.platform_adaptation:.1f}')
           print(f'  互动潜力: {score.engagement_potential:.1f}')
           print(f'  技术质量: {score.technical_quality:.1f}')
       for vid, fb in result['detailed_feedback'].items():
           for cat, items in fb.items():
               if items: print(f'\n【{cat}】')
               for item in items: print(f'  {item}')

   asyncio.run(run())
   "
   ```

3. **展示结果**：
   - 雷达图式分维度评分（文字版）
   - AI 专业评估意见
   - 优先级排序的改进建议

4. **提供改写选项**：是否根据建议重新生成

## 评分维度说明
| 维度 | 权重 | 说明 |
|------|------|------|
| 内容质量 | 30% | CASE框架合规度，信息密度 |
| 平台适配 | 25% | 符合平台调性和格式 |
| 互动潜力 | 25% | 用户痛点，传播动机 |
| 技术质量 | 20% | 结构、字数、格式规范 |
