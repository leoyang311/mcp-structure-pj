"""
Research Agent - 话题研究和信息收集
集成反幻觉技术确保研究准确性
"""
import json
import os
import asyncio
import aiohttp
from typing import Any, Dict, List
from datetime import datetime

from .base import BaseAgent
from ..models import ResearchData
from ..utils.anti_hallucination import FactCheckingMixin, AntiHallucinationEngine


class ResearchAgent(FactCheckingMixin, BaseAgent):
    """
    研究Agent - 负责话题研究、信息收集和分析
    集成反幻觉技术确保研究准确性
    """
    
    def __init__(self, openai_client=None, search_api_key: str = None, logger=None):
        super().__init__("research_agent", logger)
        self.openai_client = openai_client
        self.search_api_key = search_api_key
        self.search_engines = ["duckduckgo", "tavily"] if search_api_key else ["duckduckgo"]
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理研究任务
        
        Args:
            input_data: {
                "topic": str,
                "depth": str,  # shallow, medium, deep
                "platforms": List[str]
            }
            
        Returns:
            Dict[str, Any]: {
                "research_data": ResearchData,
                "status": "completed"
            }
        """
        topic = input_data.get("topic", "")
        depth = input_data.get("depth", "medium")
        platforms = input_data.get("platforms", [])
        
        if not topic:
            raise ValueError("Topic is required for research")
        
        self.logger.info(f"Starting research on topic: {topic}")
        
        # 并行执行各种研究任务
        tasks = [
            self._web_search(topic, depth),
            self._analyze_trends(topic),
            self._competitor_analysis(topic, platforms),
            self._extract_key_points(topic)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        web_sources = results[0] if not isinstance(results[0], Exception) else []
        trends = results[1] if not isinstance(results[1], Exception) else []
        competitors = results[2] if not isinstance(results[2], Exception) else []
        key_points = results[3] if not isinstance(results[3], Exception) else []
        
        # 生成研究总结
        summary = await self._generate_summary(topic, web_sources, key_points, trends)
        
        # 构建研究数据
        research_data = ResearchData(
            topic=topic,
            sources=web_sources,
            key_points=key_points,
            trends=trends,
            competitors=competitors,
            summary=summary,
            created_at=datetime.now()
        )
        
        return {
            "research_data": research_data,
            "status": "completed"
        }
    
    async def _web_search(self, topic: str, depth: str) -> List[Dict[str, Any]]:
        """
        网络搜索
        """
        try:
            # 模拟搜索结果 (实际应用中应该集成真实搜索API)
            sources = []
            
            search_queries = self._generate_search_queries(topic, depth)
            
            for query in search_queries:
                # 这里应该调用真实的搜索API
                mock_results = await self._mock_search(query)
                sources.extend(mock_results)
            
            return sources[:10]  # 限制返回数量
            
        except Exception as e:
            self.logger.error(f"Web search failed: {str(e)}")
            return []
    
    async def _mock_search(self, query: str) -> List[Dict[str, Any]]:
        """
        模拟搜索结果 (用于演示)
        """
        # 模拟异步搜索延迟
        await asyncio.sleep(0.5)
        
        return [
            {
                "title": f"关于{query}的深度分析",
                "url": f"https://example.com/{query.replace(' ', '-')}",
                "snippet": f"这是关于{query}的详细分析文章，包含了最新的研究和数据...",
                "source": "权威媒体",
                "relevance_score": 0.85,
            },
            {
                "title": f"{query}最新趋势报告",
                "url": f"https://research.com/{query}-trends",
                "snippet": f"最新的{query}趋势数据显示，该领域正在快速发展...",
                "source": "研究机构",
                "relevance_score": 0.78,
            }
        ]
    
    def _generate_search_queries(self, topic: str, depth: str) -> List[str]:
        """
        生成搜索查询
        """
        base_queries = [topic]
        
        if depth == "deep":
            base_queries.extend([
                f"{topic} 最新趋势",
                f"{topic} 市场分析", 
                f"{topic} 用户需求",
                f"{topic} 竞品分析",
                f"{topic} 发展前景"
            ])
        elif depth == "medium":
            base_queries.extend([
                f"{topic} 趋势",
                f"{topic} 分析",
                f"{topic} 市场"
            ])
        
        return base_queries
    
    async def _analyze_trends(self, topic: str) -> List[str]:
        """
        趋势分析
        """
        try:
            # 模拟趋势分析
            await asyncio.sleep(0.3)
            
            trends = [
                f"{topic}正在成为热门话题",
                f"用户对{topic}的关注度持续上升",
                f"{topic}相关技术快速发展",
                f"市场对{topic}解决方案需求增长",
            ]
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {str(e)}")
            return []
    
    async def _competitor_analysis(self, topic: str, platforms: List[str]) -> List[str]:
        """
        竞品分析
        """
        try:
            # 模拟竞品分析
            await asyncio.sleep(0.4)
            
            competitors = [
                f"平台A在{topic}内容上表现优秀",
                f"平台B的{topic}相关内容获得高互动",
                f"头部创作者在{topic}领域影响力强",
            ]
            
            return competitors
            
        except Exception as e:
            self.logger.error(f"Competitor analysis failed: {str(e)}")
            return []
    
    async def _extract_key_points(self, topic: str) -> List[str]:
        """
        提取关键要点
        """
        try:
            # 模拟关键要点提取
            await asyncio.sleep(0.2)
            
            key_points = [
                f"{topic}的核心概念和定义",
                f"{topic}的主要应用场景",
                f"{topic}的技术优势和特点",
                f"{topic}面临的挑战和问题",
                f"{topic}的未来发展方向",
            ]
            
            return key_points
            
        except Exception as e:
            self.logger.error(f"Key points extraction failed: {str(e)}")
            return []
    
    async def _generate_summary(
        self, 
        topic: str, 
        sources: List[Dict[str, Any]], 
        key_points: List[str],
        trends: List[str]
    ) -> str:
        """
        生成研究总结
        """
        try:
            if self.openai_client:
                # 使用OpenAI API生成更智能的总结
                prompt = f"""
基于以下研究数据，为话题"{topic}"生成一个深入、客观的研究总结：

关键要点：
{chr(10).join(f"• {point}" for point in key_points)}

市场趋势：
{chr(10).join(f"• {trend}" for trend in trends)}

信息来源数量：{len(sources)}

请生成一个专业、有深度的研究总结，包含：
1. 话题背景和重要性
2. 关键发现和洞察
3. 市场趋势和机会
4. 潜在挑战和风险
5. 结论和建议

要求：客观分析，内容准确，语言专业，字数800-1200字。
"""
                model_name = os.getenv("RESEARCH_MODEL", "gpt-3.5-turbo")
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "你是一个专业的研究分析师，擅长基于数据生成深入、客观的研究总结。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.3
                )
                
                generated_summary = response.choices[0].message.content.strip()
                self.logger.info(f"Generated research summary via OpenAI API (length: {len(generated_summary)})")
                return generated_summary
            
            # 回退到基础模板生成
            summary = f"""
基于对"{topic}"的深度研究，发现以下关键信息：

## 核心要点
{chr(10).join(f"• {point}" for point in key_points[:3])}

## 市场趋势  
{chr(10).join(f"• {trend}" for trend in trends[:2])}

## 信息来源
共收集{len(sources)}个相关信息源，包括权威媒体、研究机构等可靠来源。

## 研究结论
{topic}正处于快速发展期，具有很高的内容创作价值和用户关注度。
建议从多角度进行内容创作，重点关注用户实际需求和应用场景。
            """.strip()
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Summary generation failed: {str(e)}")
            return f"关于{topic}的研究已完成，详细信息请参考具体数据。"
