#!/usr/bin/env python3
"""
检查Yunwu API支持的模型列表
"""

import os
import requests
import json

def check_yunwu_models():
    """检查Yunwu支持的模型"""
    
    api_key = os.getenv('YUNWU_API_KEY')
    api_base = os.getenv('YUNWU_API_BASE', 'https://yunwu.ai/v1')
    
    if not api_key:
        print("❌ 未找到YUNWU_API_KEY")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # 尝试获取模型列表
    try:
        response = requests.get(
            f"{api_base}/models",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            models = response.json()
            print("✅ Yunwu支持的模型列表:")
            print("="*50)
            
            if isinstance(models, dict) and 'data' in models:
                for model in models['data']:
                    if isinstance(model, dict):
                        print(f"  📝 {model.get('id', 'Unknown')}")
                    else:
                        print(f"  📝 {model}")
            else:
                print(json.dumps(models, indent=2, ensure_ascii=False))
                
        else:
            print(f"❌ 获取模型列表失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 测试Qwen3调用
    print("\n🧪 测试Qwen3模型调用:")
    print("="*50)
    
    test_prompt = "请简单介绍一下人工智能的发展历史，100字左右。"
    
    payload = {
        "model": "qwen3-235b-a22b-think",
        "messages": [{"role": "user", "content": test_prompt}],
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    try:
        response = requests.post(
            f"{api_base}/chat/completions",
            headers={**headers, "Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            print(f"✅ Qwen3调用成功:")
            print(f"📄 响应内容: {content}")
        else:
            print(f"❌ Qwen3调用失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ Qwen3调用异常: {e}")

if __name__ == "__main__":
    check_yunwu_models()
