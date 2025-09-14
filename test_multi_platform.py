#!/usr/bin/env python3
"""
测试多平台图片生成功能
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_factory.agents.image_agent import multi_platform_generation

async def test_multi_platform():
    """测试多平台图片生成"""
    print("🎨 测试多平台图片生成功能")
    print("=" * 60)
    
    # 测试文案
    test_text = """
    🌟 分享一个超实用的时间管理技巧！
    
    最近我发现了一个神奇的方法，可以让工作效率提升50%以上！
    就是"番茄工作法" + "时间块规划"的组合使用。
    
    具体操作：
    1️⃣ 把一天划分成几个专注时间块
    2️⃣ 每个时间块专门处理一类任务
    3️⃣ 使用25分钟专注+5分钟休息的节奏
    
    试了一周，效果惊人！不仅完成了更多工作，
    还感觉没那么疲惫了～
    
    #时间管理 #工作效率 #生活技巧 #职场干货
    """
    
    # 选择部分平台进行测试（避免API调用过多）
    platforms = ["xiaohongshu", "wechat"]
    
    print(f"📝 测试文案: {test_text[:50]}...")
    print(f"🎯 目标平台: {', '.join(platforms)}")
    print("-" * 60)
    
    try:
        print("🚀 开始为多个平台生成图片...")
        result = await multi_platform_generation(
            text=test_text,
            platforms=platforms
        )
        
        print("\n=== 多平台生成结果 ===")
        print(f"✅ 总体成功状态: {result.get('success')}")
        print(f"📊 总平台数: {result.get('summary', {}).get('total_platforms', 0)}")
        print(f"✅ 成功平台数: {result.get('summary', {}).get('successful_platforms', 0)}")
        print(f"🖼️  总图片数: {result.get('summary', {}).get('total_images', 0)}")
        
        # 显示各平台结果
        platform_results = result.get('results', {})
        for platform, platform_result in platform_results.items():
            print(f"\n📱 平台: {platform}")
            print("-" * 40)
            
            if platform_result.get('success'):
                print(f"  ✅ 生成成功")
                print(f"  📐 尺寸: {platform_result.get('images', [{}])[0].get('size', '未知')}")
                print(f"  📄 描述: {platform_result.get('platform_description', '未知')}")
                
                # 检查图片文件
                images = platform_result.get('images', [])
                for img in images:
                    if 'image_path' in img:
                        image_path = img['image_path']
                        if os.path.exists(image_path):
                            file_size = os.path.getsize(image_path)
                            print(f"  💾 文件: {os.path.basename(image_path)} ({file_size/1024:.1f} KB)")
                        else:
                            print(f"  ❌ 文件不存在: {image_path}")
            else:
                print(f"  ❌ 生成失败: {platform_result.get('error', '未知错误')}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 运行测试
    asyncio.run(test_multi_platform())
