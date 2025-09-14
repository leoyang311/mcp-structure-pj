#!/usr/bin/env python3
"""
GUI启动脚本 - 确保100%可用性
"""
import sys
import os
import subprocess
import platform

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本: {sys.version.split()[0]}")
    return True

def check_tkinter():
    """检查tkinter是否可用"""
    try:
        import tkinter
        print("✅ tkinter可用")
        return True
    except ImportError:
        print("❌ tkinter不可用")
        if platform.system() == "Linux":
            print("请安装: sudo apt-get install python3-tk")
        elif platform.system() == "Darwin":
            print("tkinter应该已包含在macOS Python中")
        return False

def check_dependencies():
    """检查依赖项"""
    required = ['requests', 'asyncio']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✅ {pkg}")
        except ImportError:
            missing.append(pkg)
            print(f"❌ {pkg}")
    
    if missing:
        print(f"\n请安装缺失的依赖: pip install {' '.join(missing)}")
        return False
    return True

def install_optional_dependencies():
    """安装可选依赖"""
    try:
        print("\n🔄 检查并安装可选依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", 
                              "openai", "python-dotenv", "--quiet"])
        print("✅ 可选依赖安装完成")
    except subprocess.CalledProcessError:
        print("⚠️  可选依赖安装失败，将使用模拟模式")

def main():
    """主启动函数"""
    print("🚀 FastMCP Content Factory GUI 启动检查\n")
    
    # 基础检查
    if not check_python_version():
        input("按回车键退出...")
        return
    
    if not check_tkinter():
        input("按回车键退出...")
        return
    
    if not check_dependencies():
        try:
            print("\n🔄 尝试自动安装依赖...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", 
                                  "requests", "--quiet"])
            print("✅ 基础依赖安装完成")
        except subprocess.CalledProcessError:
            print("❌ 自动安装失败，请手动安装")
            input("按回车键退出...")
            return
    
    # 安装可选依赖（用于完整功能）
    install_optional_dependencies()
    
    print("\n✅ 所有检查通过，启动GUI...")
    
    # 设置环境变量
    os.environ['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))
    
    # 启动GUI
    try:
        from content_generator_gui import main as gui_main
        gui_main()
    except Exception as e:
        print(f"❌ GUI启动失败: {e}")
        print("\n🔄 尝试直接运行...")
        
        try:
            import subprocess
            subprocess.run([sys.executable, "content_generator_gui.py"])
        except Exception as e2:
            print(f"❌ 直接运行也失败: {e2}")
            input("按回车键退出...")

if __name__ == "__main__":
    main()