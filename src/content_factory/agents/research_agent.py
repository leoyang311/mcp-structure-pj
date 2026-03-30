"""
Research Agent - 话题研究和信息收集
使用 Tavily 真实搜索 + LLM Tool Use 编排研究流程 + 结构化输出
"""
import json
import os
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from .base import BaseAgent
from ..models import ResearchData
from ..utils.anti_hallucination import FactCheckingMixin
from ..core.openai_client import get_async_client, get_default_model, structured_completion
from ..engines.rag_engine import RAGEngine


# ── 结构化输出模型 ──────────────────────────────────────────────────────────────

class ResearchSummary(BaseModel):
    background: str = Field(description="话题背景与重要性（100-200字）")
    key_findings: List[str] = Field(description="3-5条核心发现与洞察")
    market_trends: List[str] = Field(description="2-4条市场趋势与机会")
    challenges: List[str] = Field(description="1-3条潜在挑战与风险")
    conclusion: str = Field(description="结论与行动建议（50-100字）")


# ── Tavily 搜索工具定义（供 LLM Tool Use）────────────────────────────────────

SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "tavily_search",
        "description": "搜索互联网获取关于某话题的最新信息、新闻、数据与趋势",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询语句，建议使用中文或英文精确关键词",
                },
                "search_depth": {
                    "type": "string",
                    "enum": ["basic", "advanced"],
                    "description": "搜索深度：basic 速度快，advanced 结果更丰富",
                    "default": "basic",
                },
                "max_results": {
                    "type": "integer",
                    "description": "最大返回结果数，1-10",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}


class ResearchAgent(FactCheckingMixin, BaseAgent):
    """
    研究 Agent - 使用真实 Tavily 搜索 + LLM Tool Use 编排多轮检索
    结构化输出保证摘要质量一致
    """

    def __init__(self, openai_client=None, search_api_key: str = None, logger=None):
        super().__init__("research_agent", logger)
        self.sync_client = openai_client  # 兼容旧接口（sync）
        self._search_api_key = search_api_key or os.getenv("TAVILY_API_KEY")
        self._tavily: Optional[Any] = None  # 延迟初始化
        self._async_client: Optional[AsyncOpenAI] = None
        self.rag_engine = RAGEngine()  # 向量知识库，供 WriterAgent 共享

    # ── 初始化辅助 ──────────────────────────────────────────────────────────────

    def _get_tavily(self):
        """延迟初始化 Tavily 客户端"""
        if self._tavily is None:
            try:
                from tavily import TavilyClient
                self._tavily = TavilyClient(api_key=self._search_api_key)
            except Exception as e:
                self.logger.warning(f"Tavily 初始化失败，将使用 LLM 内置知识: {e}")
        return self._tavily

    def _get_async_client(self) -> AsyncOpenAI:
        if self._async_client is None:
            self._async_client = get_async_client()
        return self._async_client

    # ── 主处理入口 ──────────────────────────────────────────────────────────────

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic", "")
        depth = input_data.get("depth", "medium")
        platforms = input_data.get("platforms", [])

        if not topic:
            raise ValueError("Topic is required for research")

        self.logger.info(f"🔍 开始研究话题: {topic} (深度: {depth})")

        # 1. 通过 LLM Tool Use 编排多轮搜索
        sources, raw_search_data = await self._tool_use_research(topic, depth)

        # 1b. 将搜索结果分块存入向量知识库（供 WriterAgent 检索验证）
        if self.rag_engine.available:
            stored = self.rag_engine.store_sources(topic, sources)
            self.logger.info(f"📚 RAG存储 {stored} 个文本块")

        # 2. 并行提取趋势、竞品、关键点（基于搜索结果）
        trends, competitors, key_points = await asyncio.gather(
            self._extract_trends(topic, raw_search_data),
            self._extract_competitors(topic, raw_search_data, platforms),
            self._extract_key_points(topic, raw_search_data),
        )

        # 3. 结构化输出生成研究摘要
        summary = await self._generate_structured_summary(
            topic, sources, key_points, trends
        )

        research_data = ResearchData(
            topic=topic,
            sources=sources,
            key_points=key_points,
            trends=trends,
            competitors=competitors,
            summary=summary,
            created_at=datetime.now(),
        )

        self.logger.info(f"✅ 研究完成 - 收集 {len(sources)} 个来源")
        return {"research_data": research_data, "status": "completed"}

    # ── LLM Tool Use 研究编排 ────────────────────────────────────────────────────

    async def _tool_use_research(
        self, topic: str, depth: str
    ) -> tuple[List[Dict], str]:
        """
        让 LLM 自主决定搜索策略：通过 tool_use 循环，模型可多次调用 tavily_search
        返回 (去重来源列表, 所有搜索结果合并文本)
        """
        client = self._get_async_client()
        model = os.getenv("RESEARCH_MODEL", get_default_model())

        depth_instruction = {
            "shallow": "执行 1 次搜索，获取基础信息",
            "medium": "执行 2-3 次搜索，覆盖核心事实、趋势与案例",
            "deep": "执行 3-5 次搜索，深入挖掘数据、竞品、用户需求与前景",
        }.get(depth, "执行 2-3 次搜索")

        messages = [
            {
                "role": "system",
                "content": (
                    "你是专业研究分析师。请通过调用 tavily_search 工具收集关于指定话题的信息。"
                    f"{depth_instruction}。每次搜索针对不同角度（核心概念/市场数据/最新动态/用户痛点等）。"
                    "搜索结束后，输出：'RESEARCH_COMPLETE'。"
                ),
            },
            {"role": "user", "content": f"请研究话题：{topic}"},
        ]

        all_sources: List[Dict] = []
        all_text_parts: List[str] = []
        seen_urls: set = set()
        max_rounds = 6  # 防止无限循环

        for _ in range(max_rounds):
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                tools=[SEARCH_TOOL],
                tool_choice="auto",
                max_tokens=800,
            )

            msg = response.choices[0].message
            messages.append(msg.model_dump(exclude_none=True))

            # 没有工具调用 → 研究结束
            if not msg.tool_calls:
                break

            # 执行所有工具调用
            for tc in msg.tool_calls:
                if tc.function.name != "tavily_search":
                    continue
                args = json.loads(tc.function.arguments)
                results = await self._execute_tavily_search(
                    query=args["query"],
                    search_depth=args.get("search_depth", "basic"),
                    max_results=args.get("max_results", 5),
                )

                # 去重并收集来源
                for r in results:
                    url = r.get("url", "")
                    if url not in seen_urls:
                        seen_urls.add(url)
                        all_sources.append(r)

                # 将结果文本送回 LLM
                result_text = self._format_search_results(results, args["query"])
                all_text_parts.append(result_text)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result_text[:3000],  # 限制每次工具响应长度
                    }
                )

        return all_sources[:10], "\n\n".join(all_text_parts)

    # ── Tavily 搜索执行 ──────────────────────────────────────────────────────────

    async def _execute_tavily_search(
        self, query: str, search_depth: str = "basic", max_results: int = 5
    ) -> List[Dict]:
        """异步执行 Tavily 搜索"""
        tavily = self._get_tavily()
        if tavily is None:
            raise RuntimeError(
                "Tavily 客户端未初始化，请检查 TAVILY_API_KEY 环境变量"
            )

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: tavily.search(
                    query=query,
                    search_depth=search_depth,
                    max_results=max_results,
                    include_answer=True,
                ),
            )
            results = []
            for item in response.get("results", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", "")[:400],
                        "source": item.get("url", "").split("/")[2] if item.get("url") else "未知",
                        "relevance_score": item.get("score", 0.5),
                    }
                )
            # 附加 Tavily 生成的答案摘要
            if response.get("answer"):
                results.insert(
                    0,
                    {
                        "title": f"[Tavily摘要] {query}",
                        "url": "",
                        "snippet": response["answer"][:400],
                        "source": "tavily_answer",
                        "relevance_score": 0.95,
                    },
                )
            return results
        except Exception as e:
            self.logger.error(f"Tavily 搜索失败 ({query}): {e}")
            raise RuntimeError(f"Tavily 搜索失败 (query='{query}'): {e}") from e

    def _format_search_results(self, results: List[Dict], query: str) -> str:
        lines = [f"搜索查询：{query}\n结果："]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. [{r['title']}]({r['url']})\n   {r['snippet']}")
        return "\n".join(lines)

    # ── 信息提取（基于搜索结果的 LLM 分析）────────────────────────────────────

    async def _extract_trends(self, topic: str, search_text: str) -> List[str]:
        if not search_text:
            return [f"{topic}正处于快速发展阶段"]
        return await self._llm_extract_list(
            topic=topic,
            search_text=search_text,
            task="从以上搜索结果中提取3-5条关于该话题的市场趋势或发展动向",
            fallback=[f"{topic}用户关注度持续上升"],
        )

    async def _extract_competitors(
        self, topic: str, search_text: str, platforms: List[str]
    ) -> List[str]:
        platform_hint = f"（目标平台：{', '.join(platforms)}）" if platforms else ""
        return await self._llm_extract_list(
            topic=topic,
            search_text=search_text,
            task=f"提取2-4条关于该话题的竞品分析或市场格局信息{platform_hint}",
            fallback=[f"{topic}领域头部玩家竞争激烈"],
        )

    async def _extract_key_points(self, topic: str, search_text: str) -> List[str]:
        return await self._llm_extract_list(
            topic=topic,
            search_text=search_text,
            task="提取5条最重要的核心要点（优先包含具体数字/日期/人名等可验证信息）",
            fallback=[
                f"{topic}的核心概念与定义",
                f"{topic}的主要应用场景",
                f"{topic}的技术优势",
                f"{topic}面临的挑战",
                f"{topic}的未来方向",
            ],
        )

    async def _llm_extract_list(
        self,
        topic: str,
        search_text: str,
        task: str,
        fallback: List[str],
        max_items: int = 5,
    ) -> List[str]:
        """通用 LLM 列表提取，失败时返回 fallback"""
        client = self._get_async_client()
        model = os.getenv("RESEARCH_MODEL", get_default_model())
        try:

            class _ListOutput(BaseModel):
                items: List[str] = Field(description=f"提取的条目列表，最多{max_items}条")

            result = await structured_completion(
                client=client,
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"话题：{topic}\n\n搜索结果摘要：\n{search_text[:2000]}\n\n"
                            f"任务：{task}。每条不超过50字，优先引用具体数据。"
                        ),
                    }
                ],
                response_model=_ListOutput,
                temperature=0.2,
                max_tokens=600,
            )
            return result.items[:max_items] if result.items else fallback
        except Exception as e:
            self.logger.warning(f"列表提取失败: {e}")
            return fallback

    # ── 结构化摘要生成 ──────────────────────────────────────────────────────────

    async def _generate_structured_summary(
        self,
        topic: str,
        sources: List[Dict],
        key_points: List[str],
        trends: List[str],
    ) -> str:
        """使用结构化输出生成高质量研究摘要"""
        client = self._get_async_client()
        model = os.getenv("RESEARCH_MODEL", get_default_model())

        source_snippets = "\n".join(
            f"- {s['title']}: {s['snippet']}" for s in sources[:6]
        )
        points_text = "\n".join(f"• {p}" for p in key_points)
        trends_text = "\n".join(f"• {t}" for t in trends)

        try:
            result = await structured_completion(
                client=client,
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是专业研究分析师，基于真实数据生成深入客观的研究摘要。",
                    },
                    {
                        "role": "user",
                        "content": (
                            f"话题：{topic}\n\n"
                            f"核心要点：\n{points_text}\n\n"
                            f"市场趋势：\n{trends_text}\n\n"
                            f"信息来源摘录（{len(sources)}条）：\n{source_snippets}\n\n"
                            "请生成专业的研究摘要，每个字段必须包含具体数据或可验证信息，禁止模糊表述。"
                        ),
                    },
                ],
                response_model=ResearchSummary,
                temperature=0.3,
                max_tokens=1500,
            )

            # 将结构化摘要拼接为 Markdown 格式
            sections = [
                f"## 话题背景\n{result.background}",
                "## 核心发现\n" + "\n".join(f"• {f}" for f in result.key_findings),
                "## 市场趋势\n" + "\n".join(f"• {t}" for t in result.market_trends),
                "## 挑战与风险\n" + "\n".join(f"• {c}" for c in result.challenges),
                f"## 结论\n{result.conclusion}",
            ]
            return "\n\n".join(sections)

        except Exception as e:
            self.logger.error(f"结构化摘要生成失败: {e}")
            return (
                f"关于「{topic}」的研究摘要（{len(sources)} 个来源）：\n"
                + "\n".join(f"• {p}" for p in key_points[:5])
            )
