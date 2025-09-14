#!/usr/bin/env python3
"""
调试yunwu API响应结构
"""
import os
import sys
import json
from openai import OpenAI

# 加载环境变量
def load_env():
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def debug_api_response():
    """调试API响应结构"""
    load_env()
    
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE')
    
    print(f"🔑 API Key: {api_key[:8]}...")
    print(f"🌐 API Base: {api_base}")
    
    client = OpenAI(
        api_key=api_key,
        base_url=api_base
    )
    
    print('\n🔍 调试yunwu API响应结构...')
    
    try:
        response = client.images.generate(
            model='gpt-image-1',
            prompt='a beautiful sunset over mountains',
            n=1,
            size='1024x1024'
        )
        
        print('✅ API调用成功!')
        print(f'📊 响应类型: {type(response)}')
        print(f'📊 response.data类型: {type(response.data)}')
        print(f'📊 response.data长度: {len(response.data)}')
        
        if response.data:
            first_item = response.data[0]
            print(f'📊 第一个图片对象类型: {type(first_item)}')
            print(f'📊 第一个图片对象属性: {[attr for attr in dir(first_item) if not attr.startswith("_")]}')
            
            # 尝试访问各种可能的属性
            for attr in ['url', 'b64_json', 'revised_prompt']:
                try:
                    value = getattr(first_item, attr, 'NOT_FOUND')
                    print(f'  📎 {attr}: {value}')
                except Exception as e:
                    print(f'  ❌ {attr}: ERROR - {e}')
            
            # 尝试转换为字典查看完整结构
            try:
                if hasattr(first_item, 'model_dump'):
                    item_dict = first_item.model_dump()
                elif hasattr(first_item, 'dict'):
                    item_dict = first_item.dict()
                else:
                    item_dict = vars(first_item)
                
                print(f'\n📋 完整对象结构:')
                print(json.dumps(item_dict, indent=2, ensure_ascii=False))
                
            except Exception as e:
                print(f'❌ 无法序列化对象: {e}')
        
    except Exception as e:
        print(f'❌ API调用失败: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api_response()
