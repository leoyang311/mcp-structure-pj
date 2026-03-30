---
description: 为 MiniMax 或 Sora 生成视频提示词（Video Prompt Engineering）
---

# 视频提示词生成

用户想为 AI 视频生成模型（MiniMax/Sora）创建高质量提示词。

## 工作流程

1. **解析参数**：
   - 话题：从用户消息提取
   - 平台：微信/小红书/B站/抖音（影响画风和比例）
   - 引擎：MiniMax（默认，6秒短片）或 Sora（长片，最长60秒）
   - 时长：MiniMax 默认6秒，Sora 默认60秒

2. **生成视频提示词**：
   ```bash
   cd /home/leo/Claude_access/mcp-structure-pj
   python -c "
   import asyncio
   from src.content_factory.agents.writer_agent import WriterAgent
   from src.content_factory.models import ResearchData, Platform
   from datetime import datetime

   async def run():
       agent = WriterAgent()
       rd = ResearchData(
           topic='$TOPIC', sources=[], key_points=[],
           trends=[], competitors=[], summary='', created_at=datetime.now()
       )
       result = await agent.process({
           'research_data': rd,
           'platforms': [Platform.$PLATFORM],
           'video_prompt_mode': True,
           'video_prompt_engine': '$ENGINE',
           'video_prompt_duration': $DURATION,
       })
       for v in result['content_versions']:
           print(v.content)

   asyncio.run(run())
   "
   ```

3. **展示结果**：格式化输出可直接复制使用的提示词

## 引擎选择指南
| 引擎 | 适合场景 | 时长 | 特点 |
|------|---------|------|------|
| MiniMax | 短视频/社交媒体 | 6秒 | 镜头+主体+动作+环境+光线+风格+质量 |
| Sora | 品牌视频/长片 | 15-60秒 | 时间线叙事+物理一致性+摄影技术 |

## 平台适配
- 抖音/小红书 → 竖版画幅，快节奏，情绪共鸣
- B站 → 横版，教育感，稳定构图
- 微信 → 专业权威，信息密度高
