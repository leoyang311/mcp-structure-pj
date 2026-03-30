---
description: 对话题进行深度研究，使用 Tavily 搜索 + LLM 分析生成研究报告
---

# 话题深度研究

用户想对某个话题进行研究并生成分析报告。

## 工作流程

1. **提取话题**：从用户消息中识别研究对象
2. **选择研究深度**：
   - 若用户说"快速了解/简单看看" → `shallow`
   - 若未指定 → `medium`（2-3 轮搜索）
   - 若用户说"深度研究/全面分析" → `deep`（3-5 轮搜索）
3. **执行研究**：
   ```bash
   cd /home/leo/Claude_access/mcp-structure-pj
   python -c "
   import asyncio
   from src.content_factory.agents.research_agent import ResearchAgent

   async def run():
       agent = ResearchAgent()
       result = await agent.process({'topic': '$TOPIC', 'depth': '$DEPTH', 'platforms': []})
       rd = result['research_data']
       print('## 研究摘要')
       print(rd.summary)
       print('\n## 关键要点')
       for p in rd.key_points: print(f'• {p}')
       print('\n## 趋势')
       for t in rd.trends: print(f'• {t}')
       print(f'\n来源数量: {len(rd.sources)}')

   asyncio.run(run())
   "
   ```
4. **格式化输出**：以 Markdown 结构展示研究报告
5. **询问后续行动**：是否基于此研究生成内容

## 输出格式
研究报告包含：话题背景、核心发现（含具体数字）、市场趋势、挑战风险、结论建议
