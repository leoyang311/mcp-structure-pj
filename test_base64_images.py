#!/usr/bin/env python3
"""
测试yunwu API base64图片处理
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_factory.agents.image_agent import ImageGenerationAgent

async def test_base64_image_generation():
    """测试base64图片生成功能"""
    print("🎨 测试yunwu API base64图片生成功能")
    print("=" * 60)
    
    # 创建Agent
    agent = ImageGenerationAgent()
    
    # 测试数据
    test_data = {
        "text": "一杯香浓的咖啡，温暖的阳光，完美的下午茶时光",
        "platform": "xiaohongshu",
        "num_images": 1,
        "use_cache": False  # 不使用缓存，确保调用API
    }
    
    print(f"📝 测试文案: {test_data['text']}")
    print(f"🎯 目标平台: {test_data['platform']}")
    print(f"🖼️  生成数量: {test_data['num_images']}")
    print("-" * 60)
    
    try:
        print("🚀 开始调用API生成图片...")
        # 执行生成
        result = await agent.process(test_data)
        
        print("\n=== 生成结果 ===")
        print(f"✅ 成功状态: {result.get('success')}")
        
        if result.get('success'):
            print(f"📱 平台: {result.get('platform')}")
            print(f"🔧 模型: {result.get('model', 'gpt-image-1')}")
            print(f"🌐 提供商: {result.get('provider', 'yunwu')}")
            print(f"💭 提示词: {result.get('prompt', '未知')[:100]}...")
            print(f"📊 生成数量: {result.get('num_generated', 0)}")
            
            images = result.get('images', [])
            for img in images:
                print(f"\n🖼️  图片 {img.get('index', '?')}:")
                print(f"  📐 尺寸: {img.get('size', '未知')}")
                
                # 检查图片路径
                if 'image_path' in img:
                    image_path = img['image_path']
                    print(f"  💾 本地路径: {image_path}")
                    
                    # 验证文件存在性和大小
                    if os.path.exists(image_path):
                        file_size = os.path.getsize(image_path)
                        print(f"  📏 文件大小: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                        print(f"  ✅ 图片文件保存成功!")
                        
                        # 尝试验证图片格式
                        try:
                            with open(image_path, 'rb') as f:
                                header = f.read(8)
                                if header.startswith(b'\x89PNG'):
                                    print(f"  🎨 文件格式: PNG")
                                elif header.startswith(b'\xff\xd8\xff'):
                                    print(f"  🎨 文件格式: JPEG") 
                                else:
                                    print(f"  ⚠️  未知图片格式")
                        except Exception as e:
                            print(f"  ⚠️  无法验证图片格式: {e}")
                    else:
                        print(f"  ❌ 图片文件不存在")
                
                # 检查URL（兼容性）
                if 'url' in img:
                    print(f"  🔗 URL: {img['url']}")
                    
        else:
            print(f"❌ 生成失败")
            print(f"🔴 错误信息: {result.get('error', '未知错误')}")
            
            # 显示更多调试信息
            if 'prompt' in result:
                print(f"🤔 使用的提示词: {result['prompt']}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        print("\n📋 详细错误信息:")
        traceback.print_exc()

async def main():
    """主函数"""
    # 检查环境变量
    api_key = os.getenv("YUNWU_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未找到API密钥!")
        print("请设置环境变量:")
        print("  export YUNWU_API_KEY='your-api-key'")
        print("  或")  
        print("  export OPENAI_API_KEY='your-yunwu-api-key'")
        print("  export OPENAI_API_BASE='https://yunwu.ai/v1'")
        return
    
    print(f"✅ API密钥已配置 (前8位: {api_key[:8]}...)")
    
    # 检查缓存目录
    cache_dir = "./image_cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
        print(f"📁 创建缓存目录: {cache_dir}")
    else:
        print(f"📁 缓存目录已存在: {cache_dir}")
    
    # 运行测试
    await test_base64_image_generation()

if __name__ == "__main__":
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 运行测试
    asyncio.run(main())
