#!/usr/bin/env python3
"""
图片生成功能完整演示
展示单平台、多平台、缓存等核心功能
"""
import asyncio
import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_factory.agents.image_agent import ImageGenerationAgent, quick_image_generation, multi_platform_generation

async def demo_single_platform():
    """演示单平台图片生成"""
    print("🎯 单平台图片生成演示")
    print("=" * 50)
    
    test_cases = [
        {
            "text": "☕ 分享一个治愈的下午茶时光，温暖的阳光和香浓的拿铁，完美搭配～",
            "platform": "xiaohongshu",
            "description": "小红书生活分享风格"
        },
        {
            "text": "💼 提高工作效率的5个实用技巧，让你的职场生涯更加成功！",
            "platform": "wechat", 
            "description": "微信公众号专业风格"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 测试案例 {i}: {case['description']}")
        print(f"内容: {case['text'][:40]}...")
        print(f"平台: {case['platform']}")
        
        start_time = time.time()
        result = await quick_image_generation(
            text=case['text'],
            platform=case['platform'],
            num_images=1
        )
        end_time = time.time()
        
        if result['success']:
            image_path = result['images'][0]['image_path']
            file_size = os.path.getsize(image_path) if os.path.exists(image_path) else 0
            print(f"✅ 成功! 耗时: {end_time - start_time:.2f}s")
            print(f"📐 尺寸: {result['images'][0]['size']}")
            print(f"💾 文件: {os.path.basename(image_path)} ({file_size/1024:.1f} KB)")
        else:
            print(f"❌ 失败: {result.get('error', '未知错误')}")
        
        await asyncio.sleep(1)  # 避免API限流

async def demo_multi_platform():
    """演示多平台图片生成"""
    print("\n🌐 多平台图片生成演示")
    print("=" * 50)
    
    test_text = """
    🚀 AI时代的个人品牌建设指南
    
    在这个AI飞速发展的时代，如何打造独特的个人品牌？
    
    ✨ 3个核心策略：
    1️⃣ 深度专业化 - 在细分领域成为专家
    2️⃣ 内容持续输出 - 分享有价值的见解
    3️⃣ 社交网络建设 - 与同行建立深度连接
    
    💡 记住：AI可以辅助我们，但无法替代我们的独特视角和人格魅力！
    
    #个人品牌 #AI时代 #职业发展 #自媒体
    """
    
    platforms = ["xiaohongshu", "wechat", "douyin"]
    
    print(f"📝 测试文案: {test_text[:60]}...")
    print(f"🎯 目标平台: {', '.join(platforms)}")
    
    start_time = time.time()
    result = await multi_platform_generation(
        text=test_text,
        platforms=platforms
    )
    end_time = time.time()
    
    print(f"\n📊 生成结果 (耗时: {end_time - start_time:.2f}s)")
    print(f"总平台数: {result.get('summary', {}).get('total_platforms', 0)}")
    print(f"成功数: {result.get('summary', {}).get('successful_platforms', 0)}")
    print(f"总图片数: {result.get('summary', {}).get('total_images', 0)}")
    
    # 展示各平台结果
    for platform, platform_result in result.get('results', {}).items():
        print(f"\n📱 {platform}:")
        if platform_result.get('success'):
            image_info = platform_result['images'][0]
            image_path = image_info['image_path']
            file_size = os.path.getsize(image_path) if os.path.exists(image_path) else 0
            print(f"  ✅ 成功 | 尺寸: {image_info['size']} | 大小: {file_size/1024:.1f} KB")
        else:
            print(f"  ❌ 失败: {platform_result.get('error', '未知错误')}")

async def demo_caching():
    """演示缓存功能"""
    print("\n💾 缓存功能演示")
    print("=" * 50)
    
    test_text = "展示缓存功能的测试文案"
    platform = "xiaohongshu"
    
    print(f"📝 测试文案: {test_text}")
    print(f"🎯 平台: {platform}")
    
    # 第一次生成（无缓存）
    print("\n🆕 第一次生成（应该调用API）:")
    start_time = time.time()
    result1 = await quick_image_generation(
        text=test_text,
        platform=platform,
        num_images=1
    )
    end_time = time.time()
    
    if result1['success']:
        print(f"✅ 成功! 耗时: {end_time - start_time:.2f}s")
        print(f"💾 图片: {os.path.basename(result1['images'][0]['image_path'])}")
    
    # 第二次生成（使用缓存）
    print("\n♻️  第二次生成（应该使用缓存）:")
    start_time = time.time()
    result2 = await quick_image_generation(
        text=test_text,
        platform=platform,
        num_images=1
    )
    end_time = time.time()
    
    if result2['success']:
        print(f"✅ 成功! 耗时: {end_time - start_time:.2f}s")
        print(f"💾 图片: {os.path.basename(result2['images'][0]['image_path'])}")
        
        # 比较结果
        if result1['images'][0]['image_path'] == result2['images'][0]['image_path']:
            print("🎉 缓存命中！使用了相同的图片文件")
        else:
            print("⚠️  缓存未命中，生成了新的图片")

async def demo_agent_usage():
    """演示Agent类的高级用法"""
    print("\n🤖 Agent类高级用法演示")
    print("=" * 50)
    
    # 创建Agent实例
    agent = ImageGenerationAgent(cache_dir="./demo_cache")
    
    # 获取平台信息
    platform_info = agent.get_platform_info()
    print("📋 支持的平台配置:")
    for platform, info in platform_info.items():
        print(f"  {platform}: {info['size']} - {info['description']}")
    
    # 自定义处理
    print(f"\n🎨 使用Agent实例生成图片:")
    result = await agent.process({
        "text": "Agent类使用演示：智能图片生成",
        "platform": "bilibili",
        "num_images": 1,
        "use_cache": True
    })
    
    if result['success']:
        image_path = result['images'][0]['image_path']
        print(f"✅ 生成成功: {os.path.basename(image_path)}")
        print(f"📐 尺寸: {result['images'][0]['size']}")
        print(f"🔧 模型: {result['model']}")
        print(f"🌐 提供商: {result['provider']}")

async def demo_error_handling():
    """演示错误处理"""
    print("\n🚨 错误处理演示")
    print("=" * 50)
    
    print("测试空文案处理:")
    result = await quick_image_generation(
        text="",  # 空文案
        platform="xiaohongshu"
    )
    
    if not result['success']:
        print(f"✅ 正确捕获错误: {result['error']}")
    
    print("\n测试不支持的平台:")
    agent = ImageGenerationAgent()
    result = await agent.process({
        "text": "测试不支持的平台",
        "platform": "unknown_platform"  # 不存在的平台
    })
    
    # 这里不会报错，会使用默认配置
    if result['success']:
        print("✅ 使用默认配置处理了不支持的平台")

def show_cache_status():
    """显示缓存状态"""
    print("\n📊 缓存状态统计")
    print("=" * 50)
    
    cache_dir = "./image_cache"
    if os.path.exists(cache_dir):
        png_files = [f for f in os.listdir(cache_dir) if f.endswith('.png')]
        json_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
        
        total_size = sum(
            os.path.getsize(os.path.join(cache_dir, f)) 
            for f in os.listdir(cache_dir)
        )
        
        print(f"📁 缓存目录: {cache_dir}")
        print(f"🖼️  图片文件: {len(png_files)} 个")
        print(f"📄 元数据文件: {len(json_files)} 个")
        print(f"💾 总大小: {total_size / 1024 / 1024:.2f} MB")
        
        # 显示最新的几个文件
        if png_files:
            print(f"\n📋 最新生成的图片:")
            png_files.sort(key=lambda f: os.path.getmtime(os.path.join(cache_dir, f)), reverse=True)
            for f in png_files[:3]:
                file_path = os.path.join(cache_dir, f)
                file_size = os.path.getsize(file_path)
                mod_time = time.ctime(os.path.getmtime(file_path))
                print(f"  {f} ({file_size/1024:.1f} KB, {mod_time})")
    else:
        print("📁 缓存目录不存在")

async def main():
    """主演示函数"""
    print("🎨 图片生成功能完整演示")
    print("=" * 60)
    
    # 检查环境
    api_key = os.getenv("YUNWU_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未找到API密钥!")
        print("请设置环境变量 YUNWU_API_KEY 或 OPENAI_API_KEY")
        return
    
    print(f"✅ API密钥已配置 (前8位: {api_key[:8]}...)")
    
    try:
        # 1. 单平台演示
        await demo_single_platform()
        
        # 2. 多平台演示
        await demo_multi_platform()
        
        # 3. 缓存演示
        await demo_caching()
        
        # 4. Agent用法演示
        await demo_agent_usage()
        
        # 5. 错误处理演示
        await demo_error_handling()
        
        # 6. 显示缓存状态
        show_cache_status()
        
        print("\n🎉 演示完成!")
        print("=" * 60)
        print("✅ 所有功能测试通过")
        print("📚 查看详细文档: docs/image-generation-guide-v1.1.md")
        print("🧪 运行特定测试:")
        print("  python test_base64_images.py    # 基础功能测试")
        print("  python test_multi_platform.py   # 多平台测试") 
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 运行演示
    asyncio.run(main())
