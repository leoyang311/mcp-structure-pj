# FastMCP Content Factory

多 Agent 智能内容生产系统，集成深度研究引擎（Tavily 真实搜索）+ CASE 框架 + 反审查机制，为微信、小红书、B 站、抖音生成高质量内容。

## 核心特性

- **真实搜索**：Tavily API 实时网络搜索，LLM Tool Use 编排多轮检索
- **结构化输出**：Pydantic 模型约束 LLM 输出，类型安全，无 JSON 解析错误
- **CASE 框架**：Concrete（具体数字）/ Actual（真实案例）/ Specific（具体细节）/ Expert（专家来源）
- **反审查机制**：Qwen3 → Claude 自动故障转移，多维度检测
- **多 Agent 流水线**：Research → Writer → Scorer，支持并行处理

## 快速开始

### 安装

```bash
# 推荐使用 uv（速度更快）
uv sync

# 或 pip
pip install -e .
```

要求 Python **3.10+**

### 配置

```bash
cp .env.example .env
# 编辑 .env，填写 API 密钥
```

```env
OPENAI_API_KEY=your_yunwu_key
OPENAI_API_BASE=https://yunwu.ai/v1
OPENAI_MODEL=qwen3-235b-a22b-think
TAVILY_API_KEY=your_tavily_key
BACKUP_MODEL_NAME=claude-sonnet-4-20250514-thinking
```

### 启动方式

```bash
# GUI（推荐）
python start_gui_smart.py

# CLI
python cli.py --help

# REST API
python api_server.py
# 访问 http://localhost:8000/docs

# 主启动脚本
python start.py --help
```

## 架构

```
src/content_factory/
├── core/
│   ├── openai_client.py          # 同步/异步双客户端 + structured_completion()
│   ├── anti_censorship_system.py # Qwen3→Claude 自动切换
│   ├── content_pipeline.py       # Research→Writer→Scorer 流水线
│   └── master_controller.py      # 任务调度
├── agents/
│   ├── research_agent.py         # Tavily Tool Use 真实搜索 + 结构化摘要
│   ├── writer_agent.py           # 结构化输出（标题+正文一次生成）
│   ├── scorer_agent.py           # Pydantic 评估模型（无正则解析）
│   ├── video_agent.py            # 视频脚本生成
│   └── image_agent.py            # 图片生成
├── engines/
│   └── deep_research_engine.py   # DEPTH 深度研究框架
├── prompts/
│   └── case_framework_prompts.py # CASE 框架提示词
└── utils/
    ├── platform_config.py        # 平台配置
    ├── quality_metrics.py        # 质量评估
    └── anti_hallucination.py     # 反幻觉机制
```

## 代码使用

```python
import asyncio
from src.content_factory.core.content_pipeline import ContentPipeline
from src.content_factory.models import ContentTask, Platform

async def main():
    task = ContentTask(
        topic="小米 SU7 2024年市场竞争分析",
        platforms=[Platform.WECHAT, Platform.XIAOHONGSHU],
        research_depth="medium",
        versions_per_platform=1,
    )
    pipeline = ContentPipeline()
    result = await pipeline.execute(task)

    for version in result.content_versions:
        print(f"[{version.platform.value}] {version.title}")
        print(version.content[:300])

asyncio.run(main())
```

## Makefile 命令

```bash
make install      # 安装依赖
make dev-install  # 安装含开发依赖
make test         # 运行测试
make lint         # ruff 代码检查
make format       # ruff 格式化
make check-env    # 验证环境变量配置
make run-gui      # 启动 GUI
make run-api      # 启动 REST API
make run-cli      # 命令行帮助
make clean        # 清理缓存
```

## Claude Code Skills

项目内置 4 个 Claude Code 技能（`.claude/skills/`），在 Claude Code 中输入 `/` 可调用：

| 命令 | 功能 |
|------|------|
| `/generate-content` | 生成多平台内容 |
| `/research-topic` | 话题深度研究 |
| `/quality-audit` | 内容质量审计 |
| `/video-prompt` | 视频提示词生成 |

## 测试

```bash
# 反审查系统完整测试
uv run python test_enhanced_anti_censorship.py

# Qwen3 生产级三话题测试
uv run python test_qwen3_three_topics.py
```

---

**版本**: v2.0.0 | **Python**: 3.10+ | **协议**: MIT
