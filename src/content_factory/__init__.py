"""
FastMCP Multi-Agent Content Production System
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 版本信息
__version__ = "1.0.0"
__author__ = "Content Factory Team"

# 导入主要组件
from .models import *
from .agents import *
from .core import *
from .utils import *

# 配置OpenAI
import openai

# 配置OpenAI客户端
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

# 系统配置
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "3"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./content_factory.db")

# Agent配置 (统一使用OpenAI)
AGENT_CONFIGS = {
    "research": {
        "model": os.getenv("RESEARCH_MODEL", "deepseek/deepseek-chat-v3-0324:free"),
        "temperature": float(os.getenv("RESEARCH_TEMPERATURE", "0.1")),
        "max_tokens": int(os.getenv("RESEARCH_MAX_TOKENS", "2000"))
    },
    "writer": {
        "model": os.getenv("WRITER_MODEL", "deepseek/deepseek-chat-v3-0324:free"),
        "temperature": float(os.getenv("WRITER_TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv("WRITER_MAX_TOKENS", "4000"))
    },
    "video": {
        "model": os.getenv("VIDEO_MODEL", "deepseek/deepseek-chat-v3-0324:free"),
        "temperature": float(os.getenv("VIDEO_TEMPERATURE", "0.6")),
        "max_tokens": int(os.getenv("VIDEO_MAX_TOKENS", "3000"))
    },
    "scorer": {
        "model": os.getenv("SCORER_MODEL", "deepseek/deepseek-chat-v3-0324:free"),
        "temperature": float(os.getenv("SCORER_TEMPERATURE", "0.2")),
        "max_tokens": int(os.getenv("SCORER_MAX_TOKENS", "1500"))
    }
}
__email__ = "team@contentfactory.ai"

from .core import MasterController, TaskManager, ContentPipeline
from .agents import ResearchAgent, WriterAgent, VideoAgent, ScorerAgent
from .models import ContentTask, Platform, TaskStatus, ContentType
from .utils import get_platform_config, evaluate_content_quality

__all__ = [
    # Core components
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
    # Meta
    "__version__",
    "__author__",
    "__email__",
]
