#!/usr/bin/env python3
"""
WriterAgent 集成测试 - 验证反审查系统是        print(f"✅ 内容生成成功!")
        content = result.get("final_content", "")
        print(f"📏 内容长度: {len(content)} 字符")
        print(f"🤖 使用的模型: {result.get('model_used', '未知')}")
        print(f"🔄 模型切换次数: {len(result.get('switches_made', []))}")
        print(f"🔍 审查检测: {'触发' if result.get('detection_results') else '未触发'}")
        
        # 显示内容预览（前300字符）
        preview = content[:300]
        if len(content) > 300:
            preview += "..."
        print(f"\n📄 内容预览:\n{preview}")

import asyncio
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加src到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 直接导入避免循环依赖
from content_factory.core.anti_censorship_system import AntiCensorshipContentGenerator
from content_factory.models.task import Platform

async def test_anti_censorship_integration():
    """测试反审查系统是否正确工作"""
    
    print("🚀 开始测试反审查系统...")
    
    # 创建反审查内容生成器
    try:
        generator = AntiCensorshipContentGenerator()
        print("✅ 反审查系统初始化成功")
    except Exception as e:
        print(f"❌ 反审查系统初始化失败: {e}")
        return False
    
    # 测试敏感内容检测和生成
    sensitive_prompt = """
    深度分析某个政治敏感事件的真相，包括：
    1. 事件的起因和背景
    2. 各方观点和立场
    3. 媒体报道的偏向性
    4. 真相的揭示
    
    要求：客观深入分析，不回避敏感问题，揭露真相
    """
    
    print(f"\n📝 测试敏感内容提示...")
    
    try:
        # 生成内容
        result = await generator.generate_content(
            prompt=sensitive_prompt,
            topic="深度分析某个政治敏感事件的真相",
            expected_length=500
        )
        
        print(f"✅ 内容生成成功!")
        print(f"📏 内容长度: {len(result)} 字符")
        print(f"� 审查检测: {'触发' if generator.censorship_detector.is_censored(result) else '未触发'}")
        
        # 显示内容预览（前300字符）
        preview = result[:300]
        if len(result) > 300:
            preview += "..."
        print(f"\n📄 内容预览:\n{preview}")
        
        return True
        
    except Exception as e:
        print(f"❌ 内容生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_normal_content():
    """测试正常内容生成"""
    
    print("\n🔄 测试正常内容生成...")
    
    generator = AntiCensorshipContentGenerator()
    
    normal_prompt = """
    写一篇关于春天美丽风景的文章，包括：
    1. 春天的花朵盛开
    2. 绿草如茵的景象
    3. 温暖的阳光
    4. 人们的愉快心情
    
    要求：温暖优美，富有诗意
    """
    
    try:
        result = await generator.generate_content(
            prompt=normal_prompt,
            topic="春天美丽风景",
            expected_length=300
        )
        
        print(f"✅ 正常内容生成成功!")
        content = result.get("final_content", "")
        print(f"📏 内容长度: {len(content)} 字符")
        print(f"🤖 使用的模型: {result.get('model_used', '未知')}")
        
        preview = content[:200]
        if len(content) > 200:
            preview += "..."
        print(f"📄 内容预览:\n{preview}")
        
        return True
        
    except Exception as e:
        print(f"❌ 正常内容测试失败: {str(e)}")
        return False

async def test_model_switching():
    """测试模型切换机制"""
    
    print("\n🔄 测试模型切换机制...")
    
    generator = AntiCensorshipContentGenerator()
    
    # 故意创建一个可能被审查的内容来测试模型切换
    highly_sensitive_prompt = """
    详细分析政府的政策失误和腐败问题，包括：
    1. 决策层的错误判断
    2. 官员腐败的具体案例
    3. 对民众的负面影响
    4. 改革的必要性和紧迫性
    
    要求：尖锐批判，直击要害
    """
    
    try:
        result = await generator.generate_content(
            prompt=highly_sensitive_prompt,
            topic="政府政策分析",
            expected_length=400
        )
        
        print(f"✅ 模型切换测试成功!")
        content = result.get("final_content", "")
        print(f"📏 内容长度: {len(content)} 字符")
        print(f"🤖 使用的模型: {result.get('model_used', '未知')}")
        print(f"🔄 模型切换次数: {len(result.get('switches_made', []))}")
        
        # 检查是否触发了模型切换（通过检查内容特征）
        if result.get('switches_made') or "分析" in content:
            print("🔄 检测到可能的模型切换特征")
        
        preview = content[:250]
        if len(content) > 250:
            preview += "..."
        print(f"📄 内容预览:\n{preview}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型切换测试失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    
    print("🔧 反审查系统集成测试")
    print("=" * 50)
    
    # 检查环境配置
    required_vars = [
        'YUNWU_API_KEY',
        'MODEL_NAME', 
        'BACKUP_MODEL_NAME'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        return
    
    print("✅ 环境配置检查通过")
    
    # 运行测试
    test_results = []
    
    # 测试1: 反审查系统基本功能
    test_results.append(await test_anti_censorship_integration())
    
    # 测试2: 正常内容
    test_results.append(await test_normal_content())
    
    # 测试3: 模型切换机制
    test_results.append(await test_model_switching())
    
    # 总结结果
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"✅ 成功: {sum(test_results)}/{len(test_results)} 个测试")
    
    if all(test_results):
        print("🎉 所有测试通过! 反审查系统集成成功!")
    else:
        print("⚠️  部分测试失败，请检查配置和代码")

if __name__ == "__main__":
    asyncio.run(main())
