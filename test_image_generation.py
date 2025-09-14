#!/usr/bin/env python3
"""
图片生成功能测试脚本
测试基于yunwu API的gpt-image-1模型的文生图功能
"""
import asyncio
import json
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.content_factory.agents.image_agent import (
    create_image_agent, 
    quick_image_generation, 
    multi_platform_generation
)


async def test_single_platform():
    """测试单平台图片生成"""
    print("="*60)
    print("🖼️  测试单平台图片生成")
    print("="*60)
    
    test_text = """
    今天和大家分享一个超实用的时间管理方法！
    作为一个每天要处理无数任务的职场人，我发现番茄工作法真的太有效了。
    25分钟专注工作，5分钟休息，每4个番茄钟休息15-30分钟。
    这样不仅提高了效率，还避免了长时间工作带来的疲劳。
    办公室里配上一杯咖啡，简直是完美的工作状态！
    """
    
    # 测试小红书平台
    print("\n📱 测试小红书平台...")
    result = await quick_image_generation(
        text=test_text,
        platform="xiaohongshu",
        num_images=2
    )
    
    print(f"生成结果: {result['success']}")
    if result['success']:
        print(f"平台: {result['platform']}")
        print(f"生成数量: {result['num_generated']}")
        print(f"提示词: {result['prompt'][:100]}...")
        for i, img in enumerate(result['images']):
            print(f"  图片 {i+1}: {img['url']}")
    else:
        print(f"错误: {result['error']}")


async def test_multi_platform():
    """测试多平台图片生成"""
    print("\n" + "="*60)
    print("🌟 测试多平台图片生成")
    print("="*60)
    
    test_text = """
    🌸 春日咖啡时光 ☕
    
    今天在这家超美的咖啡厅发现了宝藏拿铁！
    奶泡绵密，咖啡香浓，配上店里温暖的灯光，
    整个下午都被治愈了～
    
    📍 地址：市中心那家有猫咪的小店
    💰 价格：28r一杯，性价比超高
    🕐 营业时间：9:00-22:00
    
    #咖啡店探店 #下午茶时光 #治愈系 #拿铁
    """
    
    platforms = ["xiaohongshu", "wechat", "douyin"]
    
    print(f"\n🚀 为平台 {platforms} 生成图片...")
    result = await multi_platform_generation(
        text=test_text,
        platforms=platforms
    )
    
    print(f"\n📊 生成汇总:")
    print(f"总平台数: {result['summary']['total_platforms']}")
    print(f"成功平台数: {result['summary']['successful_platforms']}")
    print(f"总图片数: {result['summary']['total_images']}")
    
    print(f"\n📋 详细结果:")
    for platform, platform_result in result['results'].items():
        print(f"\n{platform}:")
        if platform_result['success']:
            print(f"  ✅ 成功生成 {platform_result['num_generated']} 张图片")
            print(f"  📝 描述: {platform_result['platform_description']}")
            print(f"  🔗 第一张图片: {platform_result['images'][0]['url']}")
        else:
            print(f"  ❌ 失败: {platform_result['error']}")


async def test_agent_info():
    """测试获取Agent配置信息"""
    print("\n" + "="*60)
    print("ℹ️  图片生成Agent配置信息")
    print("="*60)
    
    agent = create_image_agent()
    platform_info = agent.get_platform_info()
    
    for platform, info in platform_info.items():
        print(f"\n📱 {platform}:")
        print(f"  尺寸: {info['size']}")
        print(f"  描述: {info['description']}")
        print(f"  风格重点: {info['style_focus']}")


async def test_error_handling():
    """测试错误处理"""
    print("\n" + "="*60)
    print("🛠️  测试错误处理")
    print("="*60)
    
    # 测试空文案
    print("\n📝 测试空文案...")
    result = await quick_image_generation(text="", platform="xiaohongshu")
    print(f"空文案处理: {'✅ 正确处理' if not result['success'] else '❌ 应该失败'}")
    print(f"错误信息: {result.get('error', 'None')}")
    
    # 测试无效平台
    print(f"\n🌐 测试无效平台...")
    result = await quick_image_generation(
        text="测试文案", 
        platform="invalid_platform"
    )
    print(f"无效平台处理: {'✅ 能够处理' if result else '❌ 处理失败'}")


async def main():
    """主测试函数"""
    print("🎨 图片生成功能测试开始")
    print("使用模型: gpt-image-1 (yunwu API)")
    print("时间:", asyncio.get_event_loop().time())
    
    try:
        # 基础信息
        await test_agent_info()
        
        # 单平台测试
        await test_single_platform()
        
        # 多平台测试  
        await test_multi_platform()
        
        # 错误处理测试
        await test_error_handling()
        
        print("\n" + "="*60)
        print("✅ 所有测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())
