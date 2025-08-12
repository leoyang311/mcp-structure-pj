#!/usr/bin/env python3
"""
项目健康检查脚本
检查环境配置、依赖状态、服务状态等
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_environment():
    """检查环境变量"""
    print("🔍 检查环境变量...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env 文件不存在")
        return False
    
    required_vars = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
    env_content = env_file.read_text()
    
    for var in required_vars:
        if var not in env_content:
            print(f"❌ 缺少环境变量: {var}")
            return False
        print(f"✅ {var} 已配置")
    
    return True

def check_dependencies():
    """检查依赖状态"""
    print("\n📦 检查依赖状态...")
    
    try:
        result = subprocess.run(
            ["uv", "pip", "list", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        packages = json.loads(result.stdout)
        print(f"✅ 已安装 {len(packages)} 个包")
        
        # 检查关键依赖
        key_packages = ["fastapi", "openai", "tavily-python", "redis", "rich"]
        installed_packages = {pkg["name"].lower() for pkg in packages}
        
        for pkg in key_packages:
            if pkg in installed_packages:
                print(f"✅ {pkg}")
            else:
                print(f"❌ 缺少关键依赖: {pkg}")
                return False
                
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖检查失败: {e}")
        return False
    
    return True

def check_docker_services():
    """检查Docker服务状态"""
    print("\n🐳 检查Docker服务...")
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                containers.append(json.loads(line))
        
        redis_running = any(
            "redis" in container.get("Image", "").lower() 
            for container in containers
        )
        
        if redis_running:
            print("✅ Redis 服务运行中")
        else:
            print("⚠️ Redis 服务未运行")
            return False
            
    except subprocess.CalledProcessError:
        print("❌ Docker 不可用或Redis未启动")
        return False
    
    return True

def check_project_structure():
    """检查项目结构"""
    print("\n📁 检查项目结构...")
    
    required_files = [
        "pyproject.toml",
        "docker-compose.yml",
        "start.py",
        "demo_optimized.py",
        "src/content_factory/__init__.py",
        "src/content_factory/agents/__init__.py",
        "src/content_factory/core/__init__.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ 缺少文件: {file_path}")
            all_exist = False
    
    return all_exist

def run_quick_test():
    """运行快速测试"""
    print("\n🧪 运行快速测试...")
    
    try:
        # 测试导入核心模块
        subprocess.run([
            "uv", "run", "python", "-c", 
            "from src.content_factory.core.master_controller import MasterController; print('核心模块导入通过')"
        ], check=True, capture_output=True)
        print("✅ 核心模块导入正常")
        
        # 测试导入Agent模块
        subprocess.run([
            "uv", "run", "python", "-c", 
            "from src.content_factory.agents.research_agent import ResearchAgent; print('Agent模块导入通过')"
        ], check=True, capture_output=True)
        print("✅ Agent模块导入正常")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 快速测试失败: {e}")
        return False

def main():
    """主检查函数"""
    print("🏥 FastMCP Content Factory 项目健康检查")
    print("=" * 50)
    
    checks = [
        ("环境变量", check_environment),
        ("依赖状态", check_dependencies),
        ("Docker服务", check_docker_services),
        ("项目结构", check_project_structure),
        ("快速测试", run_quick_test)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {name} 检查异常: {e}")
            results.append(False)
    
    print("\n📊 检查结果汇总:")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 所有检查通过 ({passed}/{total})")
        print("项目健康状况良好，可以正常使用！")
        return 0
    else:
        print(f"⚠️ 部分检查失败 ({passed}/{total})")
        print("请根据上述提示修复问题后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main())
