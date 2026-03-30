"""
RAG Engine - 基于向量检索的知识增强模块
目标：减少幻觉 + 提升文章深度

工作流程：
  1. ResearchAgent 搜索完成后 → store_sources() 分块存入 ChromaDB
  2. WriterAgent 写作前 → retrieve_context() 检索相关原始段落注入 Prompt
  3. WriterAgent 生成后 → verify_content_claims() 批量验证声明置信度
"""
import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    向量知识库引擎，使用 ChromaDB + sentence-transformers (多语言模型支持中文)

    所有方法在依赖未安装时静默降级，不影响主流程。
    """

    EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self, persist_dir: Optional[str] = None):
        self._collection = None
        self._persist_dir = persist_dir or str(
            Path.home() / ".content_factory" / "rag_db"
        )
        self._init_db()

    # ── 初始化 ───────────────────────────────────────────────────────────────────

    def _init_db(self):
        """初始化 ChromaDB，依赖缺失时静默跳过"""
        try:
            import chromadb
            from chromadb.utils.embedding_functions import (
                SentenceTransformerEmbeddingFunction,
            )

            ef = SentenceTransformerEmbeddingFunction(model_name=self.EMBED_MODEL)
            client = chromadb.PersistentClient(path=self._persist_dir)
            self._collection = client.get_or_create_collection(
                name="research_chunks",
                embedding_function=ef,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"✅ RAG知识库初始化 - 路径: {self._persist_dir}")
        except ImportError:
            logger.warning("⚠️ chromadb/sentence-transformers 未安装，RAG功能已跳过")
        except Exception as e:
            logger.warning(f"⚠️ RAG初始化失败: {e}")

    @property
    def available(self) -> bool:
        return self._collection is not None

    # ── 存储 ─────────────────────────────────────────────────────────────────────

    def store_sources(self, topic: str, sources: List[Dict]) -> int:
        """
        将搜索结果分块并存入向量库。
        使用 upsert 防止重复，返回实际存入块数。
        """
        if not self.available:
            return 0

        chunks, ids, metadatas = [], [], []
        for source in sources:
            content = source.get("content", "") or source.get("snippet", "")
            url = source.get("url", "")
            title = source.get("title", "")
            if not content or not url:
                continue

            for i, para in enumerate(self._chunk_text(content)):
                if len(para.strip()) < 20:
                    continue
                chunk_id = f"{hashlib.md5(url.encode()).hexdigest()}_{i}"
                chunks.append(para)
                ids.append(chunk_id)
                metadatas.append(
                    {
                        "topic": topic[:64],
                        "url": url[:256],
                        "title": title[:128],
                        "chunk_index": i,
                    }
                )

        if not chunks:
            return 0

        try:
            self._collection.upsert(documents=chunks, ids=ids, metadatas=metadatas)
            logger.info(f"📚 RAG存储 {len(chunks)} 块 (话题: {topic[:30]})")
        except Exception as e:
            logger.warning(f"⚠️ RAG存储失败: {e}")
            return 0

        return len(chunks)

    # ── 检索 ─────────────────────────────────────────────────────────────────────

    def retrieve_context(
        self,
        query: str,
        n_results: int = 6,
        topic_filter: Optional[str] = None,
        min_similarity: float = 0.3,
    ) -> List[Dict]:
        """
        检索与 query 最相关的段落列表，按相似度降序。
        每项包含: content / url / title / similarity
        """
        if not self.available:
            return []
        try:
            total = self._collection.count()
            if total == 0:
                return []

            where = {"topic": topic_filter} if topic_filter else None
            results = self._collection.query(
                query_texts=[query],
                n_results=min(n_results, total),
                where=where,
                include=["documents", "metadatas", "distances"],
            )

            chunks = []
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                similarity = max(0.0, 1.0 - float(dist))
                if similarity < min_similarity:
                    continue
                chunks.append(
                    {
                        "content": doc,
                        "url": meta.get("url", ""),
                        "title": meta.get("title", ""),
                        "similarity": round(similarity, 3),
                    }
                )
            return chunks
        except Exception as e:
            logger.warning(f"⚠️ RAG检索失败: {e}")
            return []

    # ── 声明验证 ──────────────────────────────────────────────────────────────────

    def verify_claim(self, claim: str, threshold: float = 0.55) -> Dict:
        """
        验证单条声明是否有来源支撑。
        返回: {verified: bool|None, confidence: float, evidence: list}
        """
        if not self.available:
            return {"verified": None, "confidence": 0.0, "evidence": []}

        evidence = self.retrieve_context(claim, n_results=3, min_similarity=0.2)
        if not evidence:
            return {"verified": False, "confidence": 0.0, "evidence": []}

        best_score = evidence[0]["similarity"]
        return {
            "verified": best_score >= threshold,
            "confidence": best_score,
            "evidence": evidence[:2],
        }

    def verify_content_claims(self, content: str) -> Dict:
        """
        批量验证文章中含数字/实体的声明句。
        返回: {total, verified, unverified, unverified_claims[]}
        """
        claims = self._extract_claims(content)
        if not claims:
            return {"total": 0, "verified": 0, "unverified": 0, "unverified_claims": []}

        verified_count = 0
        unverified_claims = []

        for claim in claims:
            result = self.verify_claim(claim)
            if result["verified"]:
                verified_count += 1
            elif result["verified"] is False:
                unverified_claims.append(
                    {"claim": claim[:80], "confidence": result["confidence"]}
                )

        total = len(claims)
        return {
            "total": total,
            "verified": verified_count,
            "unverified": total - verified_count,
            "unverified_claims": unverified_claims[:5],
        }

    # ── 内部辅助 ──────────────────────────────────────────────────────────────────

    def _chunk_text(self, text: str, max_chars: int = 250) -> List[str]:
        """按中文句子边界分块，避免截断语义"""
        sentences = re.split(r"[。！？\n]", text)
        chunks, current = [], ""
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            if len(current) + len(sent) + 1 <= max_chars:
                current = (current + "。" + sent) if current else sent
            else:
                if current:
                    chunks.append(current)
                current = sent
        if current:
            chunks.append(current)
        return chunks

    def _extract_claims(self, content: str) -> List[str]:
        """
        提取文章中可验证的声明句（含具体数字、百分比、金额、年份）。
        最多返回 10 条。
        """
        sentences = re.split(r"[。！？\n]", content)
        claims = []
        pattern = re.compile(
            r"\d+(\.\d+)?[%亿万元年月]"
            r"|\d{4}年"
            r"|\d+\s*(亿|万|百万|千万|%)"
        )
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 15 and pattern.search(sent):
                claims.append(sent)
        return claims[:10]
