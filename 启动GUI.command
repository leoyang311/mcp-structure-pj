#!/bin/bash
# FastMCP Content Factory GUI 启动脚本
# 双击运行此文件启动GUI

cd "$(dirname "$0")"

echo "🚀 启动 FastMCP Content Factory GUI..."
echo "================================"

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

# 运行GUI
echo "🎯 启动GUI界面..."
$PYTHON_CMD start_gui.py

echo "👋 GUI已关闭"
read -p "按回车键退出..."