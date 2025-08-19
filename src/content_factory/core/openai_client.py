"""
OpenAI Client Configuration
支持OpenAI API和兼容接口
"""
import os
import logging
from openai import OpenAI
from typing import Optional

logger = logging.getLogger(__name__)


def get_openai_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> OpenAI:
    """
    获取配置好的OpenAI客户端
    支持OpenAI官方和兼容接口（如OpenRouter）
    
    Args:
        api_key: API密钥，如未提供则从环境变量获取
        base_url: API基础URL，如未提供则使用默认或环境变量
        
    Returns:
        OpenAI: 配置好的客户端实例
    """
    # 获取API密钥
    if not api_key:
        api_key = (
            os.getenv("OPENAI_API_KEY") or 
            os.getenv("YUNWU_API_KEY") or 
            os.getenv("OPENROUTER_API_KEY")
        )
    
    if not api_key:
        raise ValueError("未找到API密钥，请设置OPENAI_API_KEY、YUNWU_API_KEY或OPENROUTER_API_KEY环境变量")
    
    # 获取基础URL
    if not base_url:
        base_url = (
            os.getenv("OPENAI_API_BASE") or 
            os.getenv("OPENAI_BASE_URL") or 
            os.getenv("YUNWU_BASE_URL") or 
            os.getenv("OPENROUTER_BASE_URL")
        )
        
        # 根据API密钥前缀推断服务商
        if not base_url and api_key:
            if api_key.startswith("sk-6MT0V7g6") or "yunwu" in api_key.lower():
                base_url = "https://yunwu.ai/v1"
            elif os.getenv("OPENROUTER_API_KEY"):
                base_url = "https://openrouter.ai/api/v1"
    
    # 创建客户端
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    return client


def get_default_model() -> str:
    """
    获取默认模型名称
    
    Returns:
        str: 模型名称
    """
    # 优先使用环境变量中指定的模型
    model = os.getenv("OPENAI_MODEL")
    if model:
        return model
    
    # 检查是否使用云雾API
    if "yunwu.ai" in (os.getenv("OPENAI_API_BASE", "") or ""):
        return "qwen3-235b-a22b-think"  # 云雾API默认使用Qwen3思考模型
    
    # 检查是否使用OpenRouter
    if os.getenv("OPENROUTER_API_KEY"):
        return os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
    else:
        return "gpt-4o-mini"  # OpenAI默认模型


def test_client_connection(client: OpenAI) -> bool:
    """
    测试客户端连接
    
    Args:
        client: OpenAI客户端实例
        
    Returns:
        bool: 连接是否成功
    """
    try:
        # 发送一个简单的测试请求
        response = client.chat.completions.create(
            model=get_default_model(),
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return bool(response.choices[0].message.content)
        
    except Exception as e:
        logger.error(f"OpenAI客户端连接测试失败: {e}")
        return False


# 全局客户端实例（延迟初始化）
_global_client: Optional[OpenAI] = None


def get_global_client() -> OpenAI:
    """
    获取全局客户端实例（单例模式）
    
    Returns:
        OpenAI: 全局客户端实例
    """
    global _global_client
    
    if _global_client is None:
        _global_client = get_openai_client()
        
        # 测试连接
        if not test_client_connection(_global_client):
            logger.warning("OpenAI客户端连接可能有问题，但仍继续使用")
    
    return _global_client


# 兼容性别名
def get_openai_client_instance():
    """兼容性函数，返回全局客户端"""
    return get_global_client()
