"""
反幻觉增强模块 - 基于Deep Research的反幻觉技术
消除AI幻觉，确保内容准确性和可信度
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re
from urllib.parse import urlparse

import aiohttp
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    
try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

logger = logging.getLogger(__name__)

class AntiHallucinationEngine:
    """反幻觉引擎 - 确保生成内容的准确性和可信度"""
    
    def __init__(self, openai_client: OpenAI, tavily_client: TavilyClient):
        self.openai_client = openai_client
        self.tavily_client = tavily_client
        self.fact_check_threshold = 0.8  # 事实检查通过阈值
        self.max_verification_iterations = 3  # 最大验证迭代次数
        
    def get_anti_hallucination_system_prompt(self) -> str:
        """获取反幻觉系统提示词"""
        current_time = datetime.now().isoformat()
        
        return f"""You are an expert fact-checker and researcher. Today is {current_time}. Follow these strict anti-hallucination protocols:

ACCURACY REQUIREMENTS:
- Never make up facts, numbers, dates, or statistics
- Always cite specific sources when making factual claims
- Use phrases like "According to [source]" or "Based on the research from [source]"
- If uncertain about a fact, explicitly state your uncertainty
- Distinguish between verified facts and speculation/analysis

SOURCING REQUIREMENTS:
- Include specific URLs, publication names, and dates when available
- Quote exact text from sources when making specific claims
- If a claim cannot be verified, mark it as [UNVERIFIED] or [REQUIRES VERIFICATION]
- Prefer recent sources over older ones unless historical context is needed

VERIFICATION PROTOCOLS:
- Cross-reference claims across multiple sources when possible
- Flag any conflicts between sources
- Note when information is from primary vs secondary sources
- Include confidence levels for claims (HIGH/MEDIUM/LOW confidence)

ENTITY PRECISION:
- Include full names, titles, and affiliations for people
- Provide exact dates, locations, and numerical data
- Specify units of measurement and currency
- Include version numbers, model names, and technical specifications

REASONING TRANSPARENCY:
- Show your reasoning process step by step
- Explain how you reached conclusions from the evidence
- Acknowledge limitations in the available data
- Separate established facts from interpretations/opinions

ERROR PREVENTION:
- Double-check numerical calculations
- Verify that quotes are accurately attributed
- Ensure dates and timelines are consistent
- Check that technical terms are used correctly

Remember: Accuracy and truthfulness are paramount. It's better to say "I cannot verify this information" than to provide potentially false information."""

    async def generate_fact_checking_queries(self, content: str, num_queries: int = 3) -> List[Dict[str, str]]:
        """生成事实检查查询"""
        try:
            prompt = f"""Analyze the following content and generate {num_queries} specific fact-checking queries to verify the most important factual claims. Focus on:
- Specific statistics, numbers, or data points
- Names, dates, and events
- Technical claims or specifications
- Recent developments or news

Content to fact-check:
{content}

Generate queries that would help verify the accuracy of specific claims made in this content."""

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.get_anti_hallucination_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                functions=[{
                    "name": "generate_fact_check_queries",
                    "description": "Generate fact-checking queries",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "queries": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string", "description": "Search query for fact checking"},
                                        "claim_to_verify": {"type": "string", "description": "Specific claim being verified"},
                                        "verification_goal": {"type": "string", "description": "What this query aims to verify"}
                                    },
                                    "required": ["query", "claim_to_verify", "verification_goal"]
                                }
                            }
                        },
                        "required": ["queries"]
                    }
                }],
                function_call={"name": "generate_fact_check_queries"}
            )
            
            function_args = json.loads(response.choices[0].message.function_call.arguments)
            return function_args.get("queries", [])[:num_queries]
            
        except Exception as e:
            logger.error(f"Error generating fact-checking queries: {e}")
            return []

    async def verify_claims_with_search(self, queries: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """通过搜索验证声明"""
        verification_results = []
        
        for query_info in queries:
            try:
                # 使用Tavily搜索验证
                search_results = await asyncio.to_thread(
                    self.tavily_client.search,
                    query_info["query"],
                    max_results=5,
                    include_raw_content=True
                )
                
                # 分析搜索结果
                verification = await self._analyze_verification_results(
                    query_info, search_results
                )
                verification_results.append(verification)
                
            except Exception as e:
                logger.error(f"Error verifying claim '{query_info['claim_to_verify']}': {e}")
                verification_results.append({
                    "claim": query_info["claim_to_verify"],
                    "verification_status": "ERROR",
                    "confidence": 0.0,
                    "sources": [],
                    "notes": f"Verification failed: {str(e)}"
                })
        
        return verification_results

    async def _analyze_verification_results(self, query_info: Dict[str, str], search_results: Dict) -> Dict[str, Any]:
        """分析验证结果"""
        try:
            sources = []
            content_pieces = []
            
            for result in search_results.get("results", []):
                sources.append({
                    "url": result.get("url"),
                    "title": result.get("title"),
                    "content": result.get("content", "")[:500]  # 限制内容长度
                })
                content_pieces.append(result.get("content", ""))
            
            # 让AI分析验证结果
            analysis_content = "\n\n".join(content_pieces)
            prompt = f"""Analyze the following search results to verify this claim:

Claim to verify: {query_info['claim_to_verify']}
Verification goal: {query_info['verification_goal']}

Search results:
{analysis_content}

Based on the search results, provide:
1. Verification status (VERIFIED/PARTIALLY_VERIFIED/UNVERIFIED/CONTRADICTED)
2. Confidence level (0.0-1.0)
3. Supporting evidence
4. Any conflicting information
5. Recommended corrections if the claim is inaccurate"""

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.get_anti_hallucination_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                functions=[{
                    "name": "analyze_verification",
                    "description": "Analyze verification results",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "verification_status": {
                                "type": "string",
                                "enum": ["VERIFIED", "PARTIALLY_VERIFIED", "UNVERIFIED", "CONTRADICTED"]
                            },
                            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "supporting_evidence": {"type": "string"},
                            "conflicting_information": {"type": "string"},
                            "recommended_corrections": {"type": "string"}
                        },
                        "required": ["verification_status", "confidence", "supporting_evidence"]
                    }
                }],
                function_call={"name": "analyze_verification"}
            )
            
            analysis = json.loads(response.choices[0].message.function_call.arguments)
            
            return {
                "claim": query_info["claim_to_verify"],
                "verification_status": analysis["verification_status"],
                "confidence": analysis["confidence"],
                "supporting_evidence": analysis["supporting_evidence"],
                "conflicting_information": analysis.get("conflicting_information", ""),
                "recommended_corrections": analysis.get("recommended_corrections", ""),
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error analyzing verification results: {e}")
            return {
                "claim": query_info["claim_to_verify"],
                "verification_status": "ERROR",
                "confidence": 0.0,
                "sources": sources,
                "notes": f"Analysis failed: {str(e)}"
            }

    async def enhance_content_with_verification(self, original_content: str, verification_results: List[Dict[str, Any]]) -> str:
        """使用验证结果增强内容"""
        try:
            # 创建验证摘要
            verification_summary = self._create_verification_summary(verification_results)
            
            prompt = f"""Based on the fact-checking verification results, enhance and correct the original content. Follow these rules:

1. CORRECT any claims that were marked as "CONTRADICTED" or "UNVERIFIED"
2. ADD proper source citations for verified claims
3. STRENGTHEN claims that were verified with supporting evidence
4. ADD disclaimers for partially verified or uncertain information
5. INCLUDE a confidence indicator for major claims
6. MAINTAIN the original style and structure while improving accuracy

Original content:
{original_content}

Verification results:
{verification_summary}

Enhanced content should:
- Include [Source: URL] citations
- Mark uncertain claims with [PARTIAL] or [UNVERIFIED] tags
- Add confidence levels like [HIGH CONFIDENCE] or [REQUIRES VERIFICATION]
- Correct any factual errors found during verification"""

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.get_anti_hallucination_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3  # 低温度确保一致性
            )
            
            enhanced_content = response.choices[0].message.content
            
            # 添加验证报告
            verification_report = self._generate_verification_report(verification_results)
            
            return f"{enhanced_content}\n\n{verification_report}"
            
        except Exception as e:
            logger.error(f"Error enhancing content with verification: {e}")
            return original_content

    def _create_verification_summary(self, verification_results: List[Dict[str, Any]]) -> str:
        """创建验证摘要"""
        summary_parts = []
        
        for result in verification_results:
            status = result["verification_status"]
            confidence = result["confidence"]
            claim = result["claim"]
            evidence = result.get("supporting_evidence", "")
            corrections = result.get("recommended_corrections", "")
            
            summary_parts.append(f"""
Claim: {claim}
Status: {status} (Confidence: {confidence:.2f})
Evidence: {evidence}
{f'Corrections needed: {corrections}' if corrections else ''}
""")
        
        return "\n".join(summary_parts)

    def _generate_verification_report(self, verification_results: List[Dict[str, Any]]) -> str:
        """生成验证报告"""
        if not verification_results:
            return ""
        
        verified_count = sum(1 for r in verification_results if r["verification_status"] == "VERIFIED")
        total_count = len(verification_results)
        
        report = f"\n## 内容验证报告\n\n"
        report += f"已验证声明: {verified_count}/{total_count}\n\n"
        
        # 按状态分组
        status_groups = {}
        for result in verification_results:
            status = result["verification_status"]
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(result)
        
        for status, results in status_groups.items():
            if status == "VERIFIED":
                report += f"### ✅ 已验证声明 ({len(results)})\n\n"
            elif status == "PARTIALLY_VERIFIED":
                report += f"### ⚠️ 部分验证声明 ({len(results)})\n\n"
            elif status == "UNVERIFIED":
                report += f"### ❓ 未验证声明 ({len(results)})\n\n"
            elif status == "CONTRADICTED":
                report += f"### ❌ 相矛盾声明 ({len(results)})\n\n"
            
            for result in results:
                report += f"- **声明**: {result['claim']}\n"
                if result.get('sources'):
                    report += f"  **来源**: {', '.join([s.get('url', 'N/A') for s in result['sources'][:2]])}\n"
                report += "\n"
        
        return report

class FactCheckingMixin:
    """事实检查混入类 - 为Agent添加反幻觉能力"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 确保openai_client存在后再初始化
        if hasattr(self, 'openai_client') and self.openai_client:
            tavily_client = getattr(self, 'tavily_client', None)
            self.anti_hallucination_engine = AntiHallucinationEngine(
                self.openai_client, 
                tavily_client
            )
        else:
            self.anti_hallucination_engine = None
    
    async def generate_verified_content(self, prompt: str, platform: str, research_data: Dict) -> str:
        """生成经过验证的内容"""
        # 1. 生成初始内容
        initial_content = await self._generate_initial_content(prompt, platform, research_data)
        
        # 2. 生成事实检查查询
        fact_check_queries = await self.anti_hallucination_engine.generate_fact_checking_queries(
            initial_content, num_queries=5
        )
        
        # 3. 验证声明
        verification_results = await self.anti_hallucination_engine.verify_claims_with_search(
            fact_check_queries
        )
        
        # 4. 基于验证结果增强内容
        verified_content = await self.anti_hallucination_engine.enhance_content_with_verification(
            initial_content, verification_results
        )
        
        return verified_content
    
    async def _generate_initial_content(self, prompt: str, platform: str, research_data: Dict) -> str:
        """生成初始内容 - 由子类实现"""
        raise NotImplementedError("Subclasses must implement _generate_initial_content")

    def get_enhanced_system_prompt(self, base_prompt: str) -> str:
        """获取增强的系统提示词"""
        anti_hallucination_prompt = self.anti_hallucination_engine.get_anti_hallucination_system_prompt()
        
        return f"""{base_prompt}

{anti_hallucination_prompt}

ADDITIONAL PLATFORM-SPECIFIC REQUIREMENTS:
- Always include proper source citations in the format appropriate for the platform
- Use fact-based storytelling that builds trust with the audience
- When discussing trends or statistics, always cite the source and date of the data
- If making future predictions, clearly label them as speculation based on current trends"""

# 示例：增强的研究Agent
class EnhancedResearchAgent(FactCheckingMixin):
    """增强的研究Agent - 具备反幻觉能力"""
    
    async def _generate_initial_content(self, prompt: str, platform: str, research_data: Dict) -> str:
        """生成初始研究内容"""
        enhanced_prompt = self.get_enhanced_system_prompt("""
You are a research specialist focusing on accuracy and credibility.
Your task is to analyze research data and provide factual, well-sourced insights.
""")
        
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": enhanced_prompt},
                    {"role": "user", "content": f"""
Based on the following research data, create content for {platform}:

Topic: {prompt}
Research Data: {json.dumps(research_data, ensure_ascii=False, indent=2)}

Requirements:
1. Focus on verifiable facts and data
2. Include specific sources and dates
3. Distinguish between facts and analysis
4. Provide actionable insights based on evidence
"""}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating initial research content: {e}")
            return "Error generating content. Please try again."
