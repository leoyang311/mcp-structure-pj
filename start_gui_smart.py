#!/usr/bin/env python3
"""
智能GUI启动器
自动检测系统主题，选择合适的GUI版本
"""
import sys
import os
import subprocess
import platform

def detect_dark_mode():
    """检测系统是否使用深色模式"""
    try:
        if platform.system() == "Darwin":  # macOS
            # 使用AppleScript检测系统主题
            result = subprocess.run([
                'osascript', 
                '-e', 
                'tell application "System Events" to tell appearance preferences to get dark mode'
            ], capture_output=True, text=True, timeout=5)
            
            return result.stdout.strip().lower() == 'true'
            
        elif platform.system() == "Windows":
            # Windows注册表检测
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
            # Linux检测GTK主题
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

def check_gui_files():
    """检查GUI文件是否存在"""
    files_to_check = {
        'content_generator_gui.py': '标准GUI',
        'content_generator_gui_dark.py': '深色主题GUI',
        'gui_config.py': '配置文件'
    }
    
    missing_files = []
    for file, desc in files_to_check.items():
        if not os.path.exists(file):
            missing_files.append(f"{file} ({desc})")
    
    return missing_files

def launch_gui(use_dark_mode=False):
    """启动GUI"""
    if use_dark_mode:
        gui_script = 'content_generator_gui_dark.py'
        gui_name = '深色主题GUI'
    else:
        gui_script = 'content_generator_gui.py'
        gui_name = '标准GUI'
    
    print(f"🚀 启动 {gui_name}...")
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        
        # 启动GUI
        if use_dark_mode:
            from content_generator_gui_dark import main as dark_main
            dark_main()
        else:
            from content_generator_gui import main as gui_main
            gui_main()
            
    except ImportError as e:
        print(f"❌ 导入GUI模块失败: {e}")
        print("🔄 尝试直接运行脚本...")
        try:
            subprocess.run([sys.executable, gui_script], env=env)
        except Exception as e2:
            print(f"❌ 直接运行也失败: {e2}")
            return False
    except Exception as e:
        print(f"❌ GUI启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🎨 智能GUI启动器")
    print("=" * 50)
    
    # 检查必要文件
    print("📋 检查文件完整性...")
    missing_files = check_gui_files()
    if missing_files:
        print("❌ 缺少必要文件:")
        for file in missing_files:
            print(f"   - {file}")
        input("请确保所有文件都存在后重试...")
        return
    
    print("✅ 文件检查完成")
    
    # 检测系统主题
    print("\n🔍 检测系统主题...")
    is_dark_mode = detect_dark_mode()
    
    if is_dark_mode:
        print("🌙 检测到深色模式")
        recommended_gui = "深色主题GUI"
        use_dark = True
    else:
        print("☀️  检测到浅色模式")
        recommended_gui = "标准GUI"
        use_dark = False
    
    print(f"💡 推荐使用: {recommended_gui}")
    
    # 用户选择
    print(f"\n🎯 GUI选项:")
    print(f"  1. 深色主题GUI (适合深色模式)")
    print(f"  2. 标准GUI (适合浅色模式)")
    print(f"  3. 自动选择 (推荐: {recommended_gui})")
    print(f"  0. 退出")
    
    try:
        choice = input(f"\n选择GUI版本 (1-3, 默认3): ").strip() or "3"
        
        if choice == "0":
            print("👋 退出程序")
            return
        elif choice == "1":
            use_dark = True
        elif choice == "2":
            use_dark = False
        elif choice == "3":
            # 使用自动检测的结果
            pass
        else:
            print("❌ 无效选择，使用自动模式")
    
    except (KeyboardInterrupt, EOFError):
        print("\n👋 用户取消，退出程序")
        return
    
    # 显示启动信息
    gui_type = "深色主题GUI" if use_dark else "标准GUI"
    print(f"\n🚀 启动 {gui_type}...")
    print("=" * 50)
    
    # 启动GUI
    success = launch_gui(use_dark)
    
    if not success:
        print("\n❌ GUI启动失败")
        print("💡 建议:")
        print("  1. 检查Python环境")
        print("  2. 确保tkinter可用")
        print("  3. 尝试运行 python quick_test_gui.py")
        input("按回车键退出...")

if __name__ == "__main__":
    main()