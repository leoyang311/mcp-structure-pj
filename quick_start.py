#!/usr/bin/env python3
"""
FastMCP Content Factory 快速启动脚本
"""
import subprocess
import sys

def main():
    print("🚀 FastMCP Content Factory - 快速启动菜单")
    print("=" * 50)
    print("1. 🔧 安装/更新依赖")
    print("2. 🐳 启动Redis服务")
    print("3. 🧪 运行内容生成演示")
    print("4. 🌐 启动API服务器")
    print("5. 💻 启动CLI工具")
    print("6. 📊 查看系统状态")
    print("0. ❌ 退出")
    
    while True:
        choice = input("\n请选择操作 (0-6): ").strip()
        
        if choice == "0":
            print("👋 再见!")
            break
        elif choice == "1":
            print("🔧 安装/更新依赖...")
            subprocess.run(["uv", "sync"], check=True)
            print("✅ 依赖更新完成!")
        elif choice == "2":
            print("🐳 启动Redis服务...")
            subprocess.run(["docker-compose", "up", "-d", "redis"], check=True)
            print("✅ Redis服务启动完成!")
        elif choice == "3":
            print("🧪 运行内容生成演示...")
            subprocess.run(["uv", "run", "python", "demo_optimized.py"])
        elif choice == "4":
            print("🌐 启动API服务器...")
            subprocess.run(["uv", "run", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
        elif choice == "5":
            print("💻 启动CLI工具...")
            subprocess.run(["uv", "run", "python", "cli.py"])
        elif choice == "6":
            print("📊 检查系统状态...")
            print("🐳 Docker容器状态:")
            subprocess.run(["docker", "ps", "--filter", "name=content-factory"])
            print("\n📦 Python环境:")
            subprocess.run(["uv", "run", "python", "--version"])
            subprocess.run(["uv", "pip", "list", "--format", "columns"])
        else:
            print("❌ 无效选择，请输入0-6")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 操作取消")
    except Exception as e:
        print(f"❌ 错误: {e}")
