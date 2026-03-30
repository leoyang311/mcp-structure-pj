#!/usr/bin/env python3
"""
测试现代化改造后的三个核心模块：
1. structured_completion() - 结构化输出
2. ResearchAgent - Tavily 真实搜索 + Tool Use
3. ScorerAgent - AIAssessment 结构化评估
4. WriterAgent - ArticleOutput 结构化生成
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent / "src"))

TOPIC = "小米 SU7"  # 轻量级话题，节省 Token

# ── 颜色输出 ──────────────────────────────────────────────────────────────────
def ok(msg):   print(f"\033[92m✅ {msg}\033[0m")
def err(msg):  print(f"\033[91m❌ {msg}\033[0m")
def info(msg): print(f"\033[94mℹ  {msg}\033[0m")
def head(msg): print(f"\n\033[1m{'='*55}\n   {msg}\n{'='*55}\033[0m")


# ── TEST 1: structured_completion ────────────────────────────────────────────
async def test_structured_completion():
    head("TEST 1: structured_completion()")
    from pydantic import BaseModel, Field
    from content_factory.core.openai_client import get_async_client, get_default_model, structured_completion

    class SimpleOutput(BaseModel):
        summary: str = Field(description="一句话摘要，20字以内")
        keywords: list[str] = Field(description="3个关键词")

    client = get_async_client()
    model = get_default_model()
    info(f"使用模型: {model}")

    result = await structured_completion(
        client=client,
        model=model,
        messages=[{"role": "user", "content": f"用结构化格式总结：{TOPIC}"}],
        response_model=SimpleOutput,
        temperature=0.1,
        max_tokens=200,
    )
    ok(f"返回类型: {type(result).__name__}")
    ok(f"summary: {result.summary}")
    ok(f"keywords: {result.keywords}")
    assert isinstance(result, SimpleOutput), "类型验证失败"
    assert isinstance(result.keywords, list), "keywords 应为 list"
    return True


# ── TEST 2: ResearchAgent - Tavily 搜索 ──────────────────────────────────────
async def test_research_agent():
    head("TEST 2: ResearchAgent（shallow 深度，节省 Token）")
    from content_factory.agents.research_agent import ResearchAgent

    agent = ResearchAgent()
    info(f"Tavily 可用: {agent._get_tavily() is not None}")

    result = await agent.process({
        "topic": TOPIC,
        "depth": "shallow",  # 只搜 1 次
        "platforms": ["wechat"],
    })

    rd = result["research_data"]
    ok(f"研究状态: {result['status']}")
    ok(f"来源数量: {len(rd.sources)}")
    ok(f"关键要点: {len(rd.key_points)} 条")
    ok(f"摘要长度: {len(rd.summary)} 字")
    info(f"摘要预览: {rd.summary[:120]}...")
    assert result["status"] == "completed"
    assert len(rd.summary) > 50
    return True


# ── TEST 3: ScorerAgent - AIAssessment 结构化评估 ────────────────────────────
async def test_scorer_agent():
    head("TEST 3: ScorerAgent（AIAssessment 结构化输出）")
    from content_factory.agents.scorer_agent import ScorerAgent, AIAssessment
    from content_factory.models import ContentVersion, Platform, ContentType
    import uuid
    from datetime import datetime

    sample_content = """
小米 SU7 于 2024 年 3 月正式发布，起售价 21.59 万元，首月订单突破 10 万辆。
搭载 800V 高压快充平台，峰值功率 495kW，百公里加速 2.78 秒。
与特斯拉 Model 3 相比，小米 SU7 在 CLTC 续航（830km）和充电速度（5 分钟补能 220km）上具有明显优势。
IDC 数据显示，2024Q1 中国纯电轿车市场份额中，小米以 8.3% 位列第三。
"""

    version = ContentVersion(
        version_id=str(uuid.uuid4()),
        platform=Platform.WECHAT,
        content_type=ContentType.ARTICLE,
        title="小米SU7深度分析：21.59万的技术革命",
        content=sample_content,
        metadata={},
        created_at=datetime.now(),
    )

    agent = ScorerAgent()
    assessment = await agent._get_ai_assessment(version, research_data=None)

    if assessment is None:
        err("AI 评估返回 None（可能 API 配额问题）")
        return False

    ok(f"返回类型: {type(assessment).__name__} == AIAssessment")
    ok(f"score_adjustment: {assessment.score_adjustment:+d} (范围 -10~10)")
    ok(f"overall_assessment: {assessment.overall_assessment[:80]}...")
    ok(f"strengths: {assessment.strengths}")
    ok(f"improvement_suggestions: {assessment.improvement_suggestions}")

    assert isinstance(assessment, AIAssessment), "类型不符"
    assert -10 <= assessment.score_adjustment <= 10, "分数超出范围"
    return True


# ── TEST 4: WriterAgent - ArticleOutput 结构化生成 ───────────────────────────
async def test_writer_agent():
    head("TEST 4: WriterAgent（ArticleOutput 标题+正文一次生成）")
    from content_factory.agents.writer_agent import WriterAgent, ArticleOutput
    from content_factory.models import ResearchData, Platform
    from datetime import datetime

    agent = WriterAgent()

    # 用简单研究数据，避免触发深度研究（节省时间和 Token）
    rd = ResearchData(
        topic=TOPIC,
        sources=[],
        key_points=["小米SU7起售价21.59万", "首月订单10万辆", "百公里加速2.78秒"],
        trends=["新能源轿车竞争加剧"],
        competitors=["特斯拉Model 3"],
        summary=f"{TOPIC}于2024年3月上市，定位高端纯电轿车，首月热销。",
        created_at=datetime.now(),
    )

    result = await agent.process({
        "research_data": rd,
        "platforms": [Platform.XIAOHONGSHU],  # 只测一个平台，节省 Token
        "versions_per_platform": 1,
    })

    versions = result["content_versions"]
    ok(f"生成版本数: {len(versions)}")

    if versions:
        v = versions[0]
        ok(f"平台: {v.platform.value}")
        ok(f"标题: {v.title}")
        ok(f"正文长度: {len(v.content)} 字")
        ok(f"质量分: {v.metadata.get('quality_score', 'N/A')}")
        info(f"正文预览: {v.content[:150]}...")
        assert v.title, "标题不能为空"
        assert len(v.content) > 100, "正文太短"
    return True


# ── 主入口 ────────────────────────────────────────────────────────────────────
async def main():
    tests = [
        ("structured_completion", test_structured_completion),
        ("ResearchAgent",         test_research_agent),
        ("ScorerAgent",           test_scorer_agent),
        ("WriterAgent",           test_writer_agent),
    ]

    results = {}
    for name, fn in tests:
        try:
            passed = await fn()
            results[name] = "PASS" if passed else "FAIL"
        except Exception as e:
            err(f"{name} 异常: {e}")
            import traceback; traceback.print_exc()
            results[name] = f"ERROR: {e}"

    head("测试结果汇总")
    all_pass = True
    for name, status in results.items():
        icon = "✅" if status == "PASS" else "❌"
        print(f"  {icon} {name}: {status}")
        if status != "PASS":
            all_pass = False

    print()
    if all_pass:
        ok("全部测试通过！现代化改造验证成功。")
    else:
        err("部分测试失败，请检查上方错误信息。")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
