#!/usr/bin/env python3
"""
真实API GUI启动器
只使用真实API，不包含任何模拟数据
"""
import sys
import os
import subprocess
import platform

def detect_dark_mode():
    """检测系统是否使用深色模式"""
    try:
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run([
                'osascript', 
                '-e', 
                'tell application "System Events" to tell appearance preferences to get dark mode'
            ], capture_output=True, text=True, timeout=5)
            
            return result.stdout.strip().lower() == 'true'
            
        elif platform.system() == "Windows":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return value == 0  # 0表示深色模式
            except:
                return False
                
        elif platform.system() == "Linux":
            try:
                result = subprocess.run([
                    'gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'
                ], capture_output=True, text=True, timeout=5)
                
                theme = result.stdout.strip().lower()
                return 'dark' in theme or 'adwaita-dark' in theme
            except:
                return False
                
    except Exception as e:
        print(f"⚠️  无法检测系统主题: {e}")
    
    return False

def check_fastmcp_modules():
    """检查FastMCP模块是否可用"""
    try:
        # 检查模块导入
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from src.content_factory.core.anti_censorship_system import AntiCensorshipContentGenerator
        from src.content_factory.models import Platform
        
        # 尝试初始化生成器
        generator = AntiCensorshipContentGenerator()
        
        print("✅ FastMCP Content Factory模块检查通过")
        return True
        
    except ImportError as e:
        print(f"❌ FastMCP模块导入失败: {e}")
        print("请确保src/content_factory目录存在且模块已正确安装")
        return False
    except Exception as e:
        print(f"❌ FastMCP初始化失败: {e}")
        print("请检查API配置和网络连接")
        return False

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version.split()[0]}")
    
    # 检查tkinter
    try:
        import tkinter
        print("✅ tkinter可用")
    except ImportError:
        print("❌ tkinter不可用")
        return False
    
    # 检查必要模块
    required_modules = ['asyncio', 'threading', 'json', 'datetime']
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            print(f"❌ 缺少必要模块: {module}")
            return False
    
    print("✅ 基础环境检查通过")
    return True

def main():
    """主函数"""
    print("🚀 FastMCP Content Factory 真实API GUI启动器")
    print("=" * 60)
    print("⚠️  重要提醒: 本GUI仅使用真实API，不包含模拟数据")
    print("=" * 60)
    
    # 环境检查
    if not check_environment():
        print("\n❌ 环境检查失败")
        input("按回车键退出...")
        return
    
    # FastMCP模块检查
    print("\n🔍 检查FastMCP Content Factory模块...")
    if not check_fastmcp_modules():
        print("\n❌ FastMCP模块检查失败")
        print("\n💡 解决方案:")
        print("1. 确保src/content_factory目录存在")
        print("2. 检查.env文件中的API密钥配置")
        print("3. 确保网络连接正常")
        print("4. 运行pip install相关依赖")
        
        choice = input("\n是否仍要启动GUI? (y/N): ").strip().lower()
        if choice != 'y':
            return
    
    # 检测系统主题
    print("\n🎨 检测系统主题...")
    is_dark_mode = detect_dark_mode()
    
    if is_dark_mode:
        print("🌙 检测到深色模式")
        default_theme = "深色"
        suggested_mode = True
    else:
        print("☀️  检测到浅色模式")
        default_theme = "浅色"
        suggested_mode = False
    
    # 用户选择
    print(f"\n🎯 主题选项:")
    print(f"  1. 深色主题")
    print(f"  2. 浅色主题")
    print(f"  3. 自动选择 (推荐: {default_theme})")
    print(f"  0. 退出")
    
    try:
        choice = input(f"\n选择主题 (1-3, 默认3): ").strip() or "3"
        
        if choice == "0":
            print("👋 退出程序")
            return
        elif choice == "1":
            use_dark = True
        elif choice == "2":
            use_dark = False
        elif choice == "3":
            use_dark = suggested_mode
        else:
            print("❌ 无效选择，使用自动模式")
            use_dark = suggested_mode
    
    except (KeyboardInterrupt, EOFError):
        print("\n👋 用户取消，退出程序")
        return
    
    # 显示最终配置
    theme_name = "深色主题" if use_dark else "浅色主题"
    print(f"\n✅ 最终配置:")
    print(f"   - 主题模式: {theme_name}")
    print(f"   - API模式: 仅真实API")
    print(f"   - 模拟数据: 已禁用")
    
    # 启动GUI
    print(f"\n🚀 启动GUI...")
    print("=" * 60)
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        
        # 导入并启动GUI
        from content_generator_gui_dark import ContentFactoryGUI
        app = ContentFactoryGUI(dark_mode=use_dark)
        app.run()
        
    except ImportError as e:
        print(f"❌ GUI模块导入失败: {e}")
    except Exception as e:
        print(f"❌ GUI启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()