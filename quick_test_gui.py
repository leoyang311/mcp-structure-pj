#!/usr/bin/env python3
"""
GUI快速测试脚本
验证所有功能是否正常
"""
import sys
import os

def test_basic_imports():
    """测试基础导入"""
    print("🧪 测试基础模块导入...")
    try:
        import tkinter
        import asyncio
        import threading
        import json
        from datetime import datetime
        print("✅ 基础模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 基础模块导入失败: {e}")
        return False

def test_gui_config():
    """测试GUI配置"""
    print("🧪 测试GUI配置...")
    try:
        from gui_config import GuiConfig, ensure_compatibility, get_mock_generator
        
        # 测试兼容性
        if not ensure_compatibility():
            print("❌ 兼容性检查失败")
            return False
        
        # 测试配置加载
        config = GuiConfig()
        platforms = config.get_platform_configs()
        topics = config.get_demo_topics()
        
        print(f"✅ 配置加载成功: {len(platforms)}个平台, {len(topics)}个主题")
        
        # 测试模拟生成器
        generator = get_mock_generator()
        print("✅ 模拟生成器创建成功")
        
        return True
    except Exception as e:
        print(f"❌ GUI配置测试失败: {e}")
        return False

def test_async_generation():
    """测试异步生成功能"""
    print("🧪 测试异步生成功能...")
    try:
        import asyncio
        from gui_config import get_mock_generator
        
        async def test_generation():
            generator = get_mock_generator()
            result = await generator.generate_with_fallback(
                prompt="测试提示",
                topic="测试主题", 
                platform="wechat"
            )
            return result
        
        # 运行测试
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(test_generation())
            loop.close()
            
            if result and 'final_content' in result:
                print("✅ 异步生成测试成功")
                return True
            else:
                print("❌ 异步生成结果异常")
                return False
        except Exception as inner_e:
            print(f"❌ 异步执行失败: {inner_e}")
            return False
            
    except Exception as e:
        print(f"❌ 异步生成测试失败: {e}")
        return False

def test_gui_creation():
    """测试GUI创建（不显示窗口）"""
    print("🧪 测试GUI创建...")
    try:
        import tkinter as tk
        
        # 创建测试窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 测试基本组件
        frame = tk.Frame(root)
        label = tk.Label(frame, text="测试")
        entry = tk.Entry(frame)
        button = tk.Button(frame, text="按钮")
        
        print("✅ GUI组件创建成功")
        
        # 清理
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ GUI创建测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 FastMCP Content Factory GUI 快速测试")
    print("=" * 50)
    
    tests = [
        ("基础模块导入", test_basic_imports),
        ("GUI配置", test_gui_config),
        ("异步生成功能", test_async_generation),
        ("GUI创建", test_gui_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n📋 {name}:")
        if test_func():
            passed += 1
        else:
            print(f"💥 {name} 测试失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！GUI可以正常运行")
        print("\n🚀 启动命令:")
        print("   python start_gui.py")
        print("   或")
        print("   python content_generator_gui.py")
    else:
        print("⚠️  部分测试失败，可能影响GUI功能")
        print("\n🔧 建议:")
        print("1. 检查Python版本 (需要3.8+)")
        print("2. 安装缺失依赖: pip install tkinter asyncio")
        print("3. 查看详细错误信息")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    if not success:
        input("\n按回车键退出...")
    sys.exit(0 if success else 1)