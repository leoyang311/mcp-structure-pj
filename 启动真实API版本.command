#!/bin/bash
# FastMCP Content Factory 真实API版本启动脚本
# 仅使用真实API，不包含任何模拟数据

cd "$(dirname "$0")"

echo "🚀 启动 FastMCP Content Factory (仅真实API版本)"
echo "=================================================="
echo "⚠️  重要: 本版本仅使用真实API，请确保配置正确"
echo "=================================================="

# 检查Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ 未找到Python，请先安装Python 3.8+"
    read -p "按回车键退出..."
    exit 1
fi

echo "✅ 使用Python: $($PYTHON_CMD --version)"

# 检查必要文件
if [ ! -f "content_generator_gui_dark.py" ]; then
    echo "❌ 找不到GUI文件"
    read -p "按回车键退出..."
    exit 1
fi

# 检查FastMCP模块
echo "🔍 检查FastMCP模块..."
if [ -d "src/content_factory" ]; then
    echo "✅ 找到FastMCP模块目录"
else
    echo "⚠️  未找到src/content_factory目录"
    echo "   GUI仍会启动，但需要手动配置"
fi

# 运行GUI
echo "🎯 启动真实API版本GUI..."
$PYTHON_CMD start_real_api_gui.py

echo "👋 GUI已关闭"
read -p "按回车键退出..."