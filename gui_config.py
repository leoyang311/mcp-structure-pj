"""
GUI配置和环境检查模块
确保GUI在任何环境下都能运行
"""
import os
import sys
from typing import Dict, Any, Optional

class GuiConfig:
    """GUI配置管理类"""
    
    def __init__(self):
        self.config_file = ".env"
        self.mock_mode = False
        self.api_keys = {}
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            self.api_keys[key.strip()] = value.strip().strip('"\'')
                print(f"✅ 配置文件加载成功: {len(self.api_keys)} 个配置项")
            else:
                print("⚠️  配置文件不存在，将使用模拟模式")
                self.mock_mode = True
        except Exception as e:
            print(f"⚠️  配置文件加载失败: {e}")
            self.mock_mode = True
    
    def get_api_key(self, key: str) -> Optional[str]:
        """获取API密钥"""
        return self.api_keys.get(key)
    
    def has_valid_config(self) -> bool:
        """检查是否有有效配置"""
        required_keys = ['OPENAI_API_KEY', 'TAVILY_API_KEY']
        return any(self.get_api_key(key) for key in required_keys)
    
    def get_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取平台配置"""
        return {
            "wechat": {
                "name": "微信公众号",
                "description": "深度分析，专业权威",
                "word_range": "2000-5000字",
                "style": "理性权威",
                "color": "#1AAD19"
            },
            "xiaohongshu": {
                "name": "小红书", 
                "description": "生活分享，真实体验",
                "word_range": "500-1500字",
                "style": "真诚分享",
                "color": "#FF2442"
            },
            "bilibili": {
                "name": "B站",
                "description": "知识科普，专业有趣", 
                "word_range": "1000-2500字",
                "style": "专业有趣",
                "color": "#00A1D6"
            },
            "douyin": {
                "name": "抖音",
                "description": "短视频，情感共鸣",
                "word_range": "200-500字", 
                "style": "接地气娱乐",
                "color": "#000000"
            }
        }
    
    def get_demo_topics(self) -> list:
        """获取演示主题列表"""
        return [
            "小米汽车市场竞争分析",
            "2024年人工智能发展趋势",
            "年轻人理财投资指南", 
            "健康饮食搭配攻略",
            "远程办公效率提升方法",
            "新能源汽车购买指南",
            "短视频创作技巧分享",
            "职场沟通技巧详解"
        ]
    
    def create_sample_env(self):
        """创建示例配置文件"""
        sample_content = """# FastMCP Content Factory 配置文件
# 请填入你的API密钥

# OpenAI API密钥 (必需)
OPENAI_API_KEY=your_openai_api_key_here

# Tavily搜索API密钥 (可选，用于研究功能)
TAVILY_API_KEY=your_tavily_api_key_here

# 模型配置 (可选)
DEFAULT_MODEL=gpt-4
BACKUP_MODEL=gpt-3.5-turbo

# 生成配置 (可选)
MAX_TOKENS=4000
TEMPERATURE=0.7
"""
        try:
            with open(self.config_file + ".example", 'w', encoding='utf-8') as f:
                f.write(sample_content)
            print(f"✅ 示例配置文件已创建: {self.config_file}.example")
            return True
        except Exception as e:
            print(f"❌ 创建示例配置失败: {e}")
            return False


# 全局配置实例
gui_config = GuiConfig()

def ensure_compatibility():
    """确保兼容性"""
    try:
        # 检查基础依赖
        import tkinter
        import json
        import asyncio
        import threading
        from datetime import datetime
        
        print("✅ 所有必需模块可用")
        return True
        
    except ImportError as e:
        print(f"❌ 缺少必需模块: {e}")
        return False

def get_mock_generator():
    """获取模拟生成器（当真实API不可用时）"""
    class MockGenerator:
        async def generate_with_fallback(self, prompt: str, topic: str, platform: str):
            """模拟生成内容"""
            import asyncio
            import time
            await asyncio.sleep(1)  # 模拟API调用延迟
            
            templates = {
                "wechat": f"# {topic}\n\n深度分析报告...\n\n基于最新市场数据和行业趋势...",
                "xiaohongshu": f"✨ {topic} 分享\n\n姐妹们好！今天给大家分享...\n\n#干货分享 #{topic}",
                "bilibili": f"【{topic}】详细解析\n\n大家好，这期视频讲解...\n\n别忘了三连支持！",
                "douyin": f"🔥 {topic}\n\n开场：你知道吗？\n\n核心：关键要点...\n\n结尾：关注了解更多！"
            }
            
            return {
                "final_content": templates.get(platform, f"{topic}相关内容"),
                "model_used": "mock-gpt-4",
                "quality_score": 85,
                "word_count": 500,
                "generation_time": 1.0
            }
    
    return MockGenerator()

if __name__ == "__main__":
    # 测试配置
    print("🧪 测试GUI配置...")
    
    if ensure_compatibility():
        print("✅ 兼容性检查通过")
    else:
        print("❌ 兼容性检查失败")
    
    config = GuiConfig()
    print(f"📋 平台配置: {len(config.get_platform_configs())} 个平台")
    print(f"🎯 演示主题: {len(config.get_demo_topics())} 个主题")
    
    if not config.has_valid_config():
        config.create_sample_env()