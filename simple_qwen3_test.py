#!/usr/bin/env python3
"""
Qwen3 集成简单测试脚本
避免循环导入问题，直接测试API连接和模型调用
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

def test_yunwu_api():
    """测试Yunwu API连接"""
    print("=== 测试Yunwu API连接 ===")
    
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    
    print(f"API Base: {api_base}")
    print(f"API Key: {api_key[:10]}...{api_key[-4:] if api_key else 'None'}")
    
    if not api_key:
        print("❌ 未找到OPENAI_API_KEY环境变量")
        return False
        
    if not api_base:
        print("❌ 未找到OPENAI_API_BASE环境变量")
        return False
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        # 测试简单聊天
        response = client.chat.completions.create(
            model="qwen3-235b-a22b-think",
            messages=[
                {"role": "user", "content": "你好，请用中文简单介绍一下你自己。"}
            ],
            max_tokens=200
        )
        
        print("✅ API连接成功！")
        print(f"模型响应: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ API连接失败: {str(e)}")
        return False

def test_qwen3_writing():
    """测试Qwen3写作能力"""
    print("\n=== 测试Qwen3写作能力 ===")
    
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    
    if not api_key or not api_base:
        print("❌ 环境变量配置不完整")
        return False
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        # 测试写作任务
        prompt = """
        请写一篇关于"人工智能在教育领域的应用"的500字文章，要求：
        1. 结构清晰，有引言、正文、结论
        2. 语言流畅，符合中文表达习惯
        3. 内容专业且具有实用性
        """
        
        response = client.chat.completions.create(
            model="qwen3-235b-a22b-think",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        print("✅ 写作测试成功！")
        print(f"生成的文章:\n{content}")
        print(f"\n文章长度: {len(content)} 字符")
        return True
        
    except Exception as e:
        print(f"❌ 写作测试失败: {str(e)}")
        return False

def test_model_configurations():
    """测试模型配置"""
    print("\n=== 测试模型配置 ===")
    
    models = {
        "WRITER_MODEL": os.getenv("WRITER_MODEL"),
        "RESEARCH_MODEL": os.getenv("RESEARCH_MODEL"), 
        "SCORER_MODEL": os.getenv("SCORER_MODEL")
    }
    
    print("当前配置的模型:")
    for key, value in models.items():
        print(f"  {key}: {value}")
    
    # 检查是否都设置为Qwen3
    all_qwen3 = all(value == "qwen3-235b-a22b-think" for value in models.values())
    
    if all_qwen3:
        print("✅ 所有模型都已配置为Qwen3-235b-a22b-think")
        return True
    else:
        print("⚠️  部分模型未配置为Qwen3")
        return False

def main():
    """主测试函数"""
    print("🚀 开始Qwen3集成测试...\n")
    
    results = []
    
    # 1. 测试环境变量配置
    results.append(test_model_configurations())
    
    # 2. 测试API连接
    results.append(test_yunwu_api())
    
    # 3. 测试写作能力
    results.append(test_qwen3_writing())
    
    # 总结测试结果
    print(f"\n{'='*50}")
    print("📊 测试结果总结:")
    print(f"总测试数: {len(results)}")
    print(f"成功数: {sum(results)}")
    print(f"失败数: {len(results) - sum(results)}")
    
    if all(results):
        print("🎉 所有测试通过！Qwen3集成成功！")
        return 0
    else:
        print("❌ 部分测试失败，请检查配置和网络连接")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
