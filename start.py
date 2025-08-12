#!/usr/bin/env python3
"""
FastMCP Content Factory 启动脚本
提供多种启动方式：CLI、API服务器、示例演示
"""
import sys
import subprocess
import argparse
from pathlib import Path


def check_dependencies():
    """检查依赖是否已安装"""
    try:
        # 检查是否在 uv 虚拟环境中
        result = subprocess.run(["uv", "run", "python", "-c", "import sys; print('ok')"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ uv 虚拟环境已就绪")
            return True
        else:
            print("❌ uv 虚拟环境未就绪，请运行: python start.py install")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uv 未安装或虚拟环境未就绪")
        return False


def start_cli():
    """启动CLI工具"""
    print("🚀 启动FastMCP Content Factory CLI工具...")
    try:
        subprocess.run(["uv", "run", "python", "cli.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ CLI启动失败: {e}")
        sys.exit(1)


def start_api_server(host="127.0.0.1", port=8000, reload=True):
    """启动API服务器"""
    print(f"🚀 启动FastMCP Content Factory API服务器...")
    print(f"   地址: http://{host}:{port}")
    print(f"   文档: http://{host}:{port}/docs")
    
    try:
        cmd = ["uv", "run", "uvicorn", "api_server:app", 
               "--host", host, "--port", str(port)]
        if reload:
            cmd.append("--reload")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ API服务器启动失败: {e}")
        sys.exit(1)


def run_examples():
    """运行示例"""
    print("🎯 运行FastMCP Content Factory示例...")
    try:
        subprocess.run(["uv", "run", "python", "examples.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 示例运行失败: {e}")
        sys.exit(1)


def install_dependencies():
    """安装项目依赖"""
    print("📦 安装项目依赖...")
    
    # 检查是否有uv
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✅ 检测到uv，使用uv管理依赖")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 未检测到uv，请先安装uv: https://docs.astral.sh/uv/getting-started/installation/")
        return False
    
    try:
        # 使用uv sync安装所有依赖（包括dev依赖）
        print("🔄 同步依赖...")
        subprocess.run(["uv", "sync"], check=True)
        print("✅ 依赖安装完成!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False


def setup_redis():
    """启动Redis服务"""
    print("🐳 启动Redis服务...")
    
    # 检查Docker是否可用
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker未安装或不可用")
        print("请安装Docker或手动启动Redis服务: redis-server")
        return False
    
    try:
        # 启动Redis容器
        subprocess.run(["docker-compose", "up", "-d", "redis"], check=True)
        print("✅ Redis服务启动完成!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Redis服务启动失败")
        print("请检查docker-compose.yml文件或手动启动Redis")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="FastMCP Multi-Agent Content Production System",
        epilog="""
使用示例:
  python start.py cli                    # 启动CLI工具
  python start.py api                    # 启动API服务器
  python start.py api --port 8080        # 指定端口启动API
  python start.py examples               # 运行示例
  python start.py install                # 安装依赖
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "mode",
        choices=["cli", "api", "examples", "install", "setup-redis"],
        help="启动模式"
    )
    
    # API服务器选项
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="API服务器主机地址 (默认: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API服务器端口 (默认: 8000)"
    )
    
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="禁用自动重载（生产环境）"
    )
    
    args = parser.parse_args()
    
    print("🎉 FastMCP Multi-Agent Content Production System")
    print("=" * 50)
    
    # 安装模式
    if args.mode == "install":
        success = install_dependencies()
        if success:
            print("\n✨ 现在可以使用以下命令:")
            print("python start.py setup-redis # 启动Redis服务")
            print("python start.py cli        # CLI工具")
            print("python start.py api        # API服务器") 
            print("python start.py examples   # 运行示例")
        return
    
    # 设置Redis
    if args.mode == "setup-redis":
        setup_redis()
        return
    
    # 检查依赖
    if not check_dependencies():
        print("\n💡 提示: 运行 'python start.py install' 自动安装依赖")
        return
    
    # 根据模式启动
    if args.mode == "cli":
        start_cli()
    elif args.mode == "api":
        start_api_server(
            host=args.host,
            port=args.port,
            reload=not args.no_reload
        )
    elif args.mode == "examples":
        run_examples()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 再见!")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        sys.exit(1)
