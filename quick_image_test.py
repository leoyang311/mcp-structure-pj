#!/usr/bin/env python3
"""
图片生成功能快速测试脚本
一键测试yunwu API的gpt-image-1模型图片生成功能
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.content_factory.agents.image_agent import quick_image_generation


async def quick_test():
    """快速测试函数"""
    print("🎨 yunwu API gpt-image-1 模型快速测试")
    print("=" * 50)
    
    # 测试文案
    test_text = """
    🌸 春日下午茶时光 ☕
    
    今天在这家超美的咖啡厅度过了完美的下午！
    温暖的阳光透过大落地窗洒进来，配上香浓的拿铁，
    整个人都被治愈了～
    
    这里的手冲咖啡真的绝了，酸甜平衡，
    还有超可爱的拉花，随手一拍都是大片！
    
    #咖啡时光 #下午茶 #治愈系 #春日美好
    """
    
    print(f"📝 测试文案: {test_text[:50]}...")
    print(f"🎯 目标平台: 小红书")
    print(f"🖼️  生成数量: 1张")
    print("-" * 50)
    
    try:
        # 调用图片生成
        print("🚀 开始生成图片...")
        result = await quick_image_generation(
            text=test_text,
            platform="xiaohongshu",
            num_images=1
        )
        
        # 显示结果
        if result['success']:
            print("✅ 图片生成成功!")
            print(f"📱 平台: {result['platform']}")
            print(f"🔧 模型: {result['model']}")
            print(f"🌐 提供商: {result['provider']}")
            print(f"📐 尺寸: {result['images'][0]['size']}")
            print(f"🔗 图片URL: {result['images'][0]['url']}")
            print(f"💭 生成提示词: {result['prompt'][:100]}...")
        else:
            print("❌ 图片生成失败!")
            print(f"错误信息: {result['error']}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    return result.get('success', False)


async def main():
    """主函数"""
    print("检查环境配置...")
    
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
    
    # 运行测试
    success = await quick_test()
    
    if success:
        print("\n🎉 测试成功完成!")
        print("您现在可以:")
        print("  1. 运行完整测试: python test_image_generation.py")
        print("  2. 运行集成演示: python demo_integrated_content_factory.py")
        print("  3. 查看使用文档: docs/image-generation-guide.md")
    else:
        print("\n🔧 测试失败，请检查:")
        print("  1. API密钥是否正确")
        print("  2. 网络连接是否正常") 
        print("  3. yunwu API服务是否可用")


if __name__ == "__main__":
    asyncio.run(main())
