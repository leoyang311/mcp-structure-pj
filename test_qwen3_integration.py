#!/usr/bin/env python3
"""
测试Qwen3模型集成
验证云雾API连接和模型调用
"""
import os
import sys
import asyncio
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.content_factory.core.openai_client import get_global_client, get_default_model, test_client_connection
from src.content_factory.agents.writer_agent import WriterAgent
from src.content_factory.models import ResearchData, Platform


async def test_qwen3_connection():
    """测试Qwen3模型连接"""
    print("🚀 开始测试Qwen3模型集成")
    print("=" * 50)
    
    # 1. 测试客户端连接
    print("1️⃣ 测试OpenAI客户端连接...")
    try:
        client = get_global_client()
        model_name = get_default_model()
        print(f"✅ 客户端初始化成功")
        print(f"📋 当前模型: {model_name}")
        print(f"🔗 API基础URL: {os.getenv('OPENAI_API_BASE')}")
        
        # 测试连接
        if test_client_connection(client):
            print("✅ 连接测试成功")
        else:
            print("❌ 连接测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 客户端初始化失败: {e}")
        return False
    
    # 2. 测试简单对话
    print("\n2️⃣ 测试简单对话...")
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "你好，请简单介绍一下你自己，并告诉我今天的日期。"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        reply = response.choices[0].message.content
        print(f"✅ 模型回复: {reply[:100]}...")
        
    except Exception as e:
        print(f"❌ 简单对话测试失败: {e}")
        return False
    
    # 3. 测试中文写作能力
    print("\n3️⃣ 测试中文写作能力...")
    try:
        writing_prompt = """
请写一篇300字的文章，主题是"人工智能在教育中的应用"。
要求：
1. 结构清晰
2. 语言流畅
3. 举出具体例子
4. 表达观点明确
"""
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "你是专业的中文写作助手，擅长创作高质量的中文文章。"},
                {"role": "user", "content": writing_prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        article = response.choices[0].message.content
        print(f"✅ 写作测试成功，文章长度: {len(article)}字")
        print(f"📄 文章预览: {article[:200]}...")
        
    except Exception as e:
        print(f"❌ 中文写作测试失败: {e}")
        return False
    
    # 4. 测试WriterAgent集成
    print("\n4️⃣ 测试WriterAgent集成...")
    try:
        # 创建测试数据
        research_data = ResearchData(
            topic="人工智能教育应用",
            summary="人工智能技术在教育领域的创新应用正在改变传统教学模式",
            key_points=[
                "个性化学习路径推荐",
                "智能作业批改系统",
                "虚拟教师助手"
            ],
            trends=["AI教育产品增长", "在线教育智能化"],
            sources=["教育部报告", "AI研究机构数据"],
            generated_at=datetime.now()
        )
        
        # 初始化WriterAgent
        writer_agent = WriterAgent()
        print("✅ WriterAgent初始化成功")
        
        # 测试内容生成
        input_data = {
            "research_data": research_data,
            "platforms": [Platform.WECHAT],
            "versions_per_platform": 1
        }
        
        print("🔄 开始生成内容...")
        result = await writer_agent.process(input_data)
        
        if result.get("status") == "completed":
            content_versions = result.get("content_versions", [])
            if content_versions:
                version = content_versions[0]
                print(f"✅ 内容生成成功")
                print(f"📋 标题: {version.title}")
                print(f"📄 内容长度: {len(version.content)}字")
                print(f"🎯 质量评分: {version.metadata.get('quality_score', 'N/A')}")
                print(f"📝 内容预览: {version.content[:200]}...")
            else:
                print("❌ 未生成内容版本")
                return False
        else:
            print(f"❌ 内容生成失败: {result}")
            return False
            
    except Exception as e:
        print(f"❌ WriterAgent测试失败: {e}")
        return False
    
    print("\n🎉 所有测试通过！Qwen3模型集成成功！")
    print("=" * 50)
    return True


def print_environment_info():
    """打印环境信息"""
    print("🔧 环境配置信息:")
    print(f"   OPENAI_API_KEY: {'✅ 已设置' if os.getenv('OPENAI_API_KEY') else '❌ 未设置'}")
    print(f"   OPENAI_API_BASE: {os.getenv('OPENAI_API_BASE', '未设置')}")
    print(f"   WRITER_MODEL: {os.getenv('WRITER_MODEL', '未设置')}")
    print(f"   RESEARCH_MODEL: {os.getenv('RESEARCH_MODEL', '未设置')}")
    print(f"   SCORER_MODEL: {os.getenv('SCORER_MODEL', '未设置')}")
    print()


if __name__ == "__main__":
    print_environment_info()
    
    # 运行测试
    success = asyncio.run(test_qwen3_connection())
    
    if success:
        print("\n🚀 Qwen3模型已成功集成到您的项目中！")
        print("\n📋 后续使用指南:")
        print("   1. 运行 python start.py 启动内容工厂")
        print("   2. 访问 http://localhost:8000 使用Web界面")
        print("   3. 所有Agent将自动使用Qwen3-235B-A22B-Think模型")
        print("   4. 享受高质量的中文内容生成！")
    else:
        print("\n❌ 集成测试失败，请检查配置")
        print("\n🔧 故障排除:")
        print("   1. 确认API密钥正确")
        print("   2. 检查网络连接")
        print("   3. 查看错误日志")
        sys.exit(1)
