"""
OpenAI Client Configuration
支持同步/异步双客户端，结构化输出辅助函数
"""
import os
import logging
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from openai import OpenAI, AsyncOpenAI

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def _resolve_api_params(api_key: Optional[str], base_url: Optional[str]) -> tuple[str, Optional[str]]:
    """解析API参数，统一处理环境变量回退逻辑"""
    if not api_key:
        api_key = (
            os.getenv("OPENAI_API_KEY")
            or os.getenv("YUNWU_API_KEY")
            or os.getenv("OPENROUTER_API_KEY")
        )

    if not api_key:
        raise ValueError(
            "未找到API密钥，请设置 OPENAI_API_KEY、YUNWU_API_KEY 或 OPENROUTER_API_KEY"
        )

    if not base_url:
        base_url = (
            os.getenv("OPENAI_API_BASE")
            or os.getenv("OPENAI_BASE_URL")
            or os.getenv("YUNWU_BASE_URL")
            or os.getenv("OPENROUTER_BASE_URL")
        )
        if not base_url:
            if api_key.startswith("sk-6MT0V7g6") or "yunwu" in api_key.lower():
                base_url = "https://yunwu.ai/v1"
            elif os.getenv("OPENROUTER_API_KEY"):
                base_url = "https://openrouter.ai/api/v1"

    return api_key, base_url


def get_openai_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> OpenAI:
    """获取同步 OpenAI 客户端"""
    api_key, base_url = _resolve_api_params(api_key, base_url)
    return OpenAI(api_key=api_key, base_url=base_url)


def get_async_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> AsyncOpenAI:
    """获取异步 OpenAI 客户端（用于 async/await 场景）"""
    api_key, base_url = _resolve_api_params(api_key, base_url)
    return AsyncOpenAI(api_key=api_key, base_url=base_url)


def get_default_model() -> str:
    """获取默认模型名称"""
    model = os.getenv("OPENAI_MODEL")
    if model:
        return model
    if "yunwu.ai" in (os.getenv("OPENAI_API_BASE", "") or ""):
        return "qwen3-235b-a22b-think"
    if os.getenv("OPENROUTER_API_KEY"):
        return os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
    return "gpt-4o-mini"


async def structured_completion(
    client: AsyncOpenAI,
    model: str,
    messages: list,
    response_model: Type[T],
    temperature: float = 0.3,
    max_tokens: int = 2000,
) -> T:
    """
    结构化输出辅助函数：要求模型返回 JSON，并用 Pydantic 模型解析验证。
    使用 response_format={"type": "json_object"} 确保跨 API 兼容性。
    """
    import json

    # 在 system 消息中注入 JSON schema 描述
    schema_hint = response_model.model_json_schema()
    json_instruction = (
        f"\n\n请严格按照以下 JSON schema 输出，不要添加任何额外字段或说明文字：\n"
        f"```json\n{json.dumps(schema_hint, ensure_ascii=False, indent=2)}\n```"
    )

    augmented_messages = list(messages)
    if augmented_messages and augmented_messages[0]["role"] == "system":
        augmented_messages[0] = {
            "role": "system",
            "content": augmented_messages[0]["content"] + json_instruction,
        }
    else:
        augmented_messages.insert(0, {"role": "system", "content": json_instruction})

    response = await client.chat.completions.create(
        model=model,
        messages=augmented_messages,
        response_format={"type": "json_object"},
        temperature=temperature,
        max_tokens=max_tokens,
    )

    raw = response.choices[0].message.content.strip()
    return response_model.model_validate_json(raw)


def test_client_connection(client: OpenAI) -> bool:
    """测试客户端连接"""
    try:
        response = client.chat.completions.create(
            model=get_default_model(),
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5,
        )
        return bool(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"OpenAI客户端连接测试失败: {e}")
        return False


# 全局客户端实例（延迟初始化）
_global_client: Optional[OpenAI] = None
_global_async_client: Optional[AsyncOpenAI] = None


def get_global_client() -> OpenAI:
    """获取全局同步客户端（单例）"""
    global _global_client
    if _global_client is None:
        _global_client = get_openai_client()
        if not test_client_connection(_global_client):
            logger.warning("OpenAI客户端连接可能有问题，但仍继续使用")
    return _global_client


def get_global_async_client() -> AsyncOpenAI:
    """获取全局异步客户端（单例）"""
    global _global_async_client
    if _global_async_client is None:
        _global_async_client = get_async_client()
    return _global_async_client


# 兼容性别名
get_openai_client_instance = get_global_client
