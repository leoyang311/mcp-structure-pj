"""
FastMCP Multi-Agent Content Production System
"""
import os
from dotenv import load_dotenv

load_dotenv()

__version__ = "2.0.0"
__author__ = "Content Factory Team"
__email__ = "team@contentfactory.ai"

# 显式导入，避免通配符污染命名空间
from .core import MasterController, TaskManager, ContentPipeline
from .agents import ResearchAgent, WriterAgent, VideoAgent, ScorerAgent
from .models import ContentTask, Platform, TaskStatus, ContentType
from .utils import get_platform_config, evaluate_content_quality

# 懒加载 OpenAI 客户端（避免导入时因缺少 API key 报错）
def _get_client():
    from .core.openai_client import get_global_client
    return get_global_client()

# 系统配置（从环境变量读取）
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "3"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./content_factory.db")

# Agent 模型配置（模型名通过 get_default_model() 动态获取，避免硬编码）
def _make_agent_config(env_model_key: str, temperature: float, max_tokens: int) -> dict:
    from .core.openai_client import get_default_model
    return {
        "model": os.getenv(env_model_key, get_default_model()),
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

AGENT_CONFIGS = {
    "research": _make_agent_config("RESEARCH_MODEL", 0.1, 2000),
    "writer":   _make_agent_config("WRITER_MODEL",   0.2, 4000),
    "video":    _make_agent_config("VIDEO_MODEL",    0.6, 3000),
    "scorer":   _make_agent_config("SCORER_MODEL",   0.2, 1500),
}

__all__ = [
    # Core
    "MasterController",
    "TaskManager",
    "ContentPipeline",
    # Agents
    "ResearchAgent",
    "WriterAgent",
    "VideoAgent",
    "ScorerAgent",
    # Models
    "ContentTask",
    "Platform",
    "TaskStatus",
    "ContentType",
    # Utils
    "get_platform_config",
    "evaluate_content_quality",
    # Config
    "AGENT_CONFIGS",
    # Meta
    "__version__",
    "__author__",
    "__email__",
]
