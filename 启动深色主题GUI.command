#!/bin/bash
# FastMCP Content Factory 深色主题GUI启动脚本
# 专门为macOS深色模式优化

cd "$(dirname "$0")"

echo "🌙 启动 FastMCP Content Factory 深色主题GUI"
echo "================================================"

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

# 检测深色模式
DARK_MODE=$(osascript -e 'tell application "System Events" to tell appearance preferences to get dark mode' 2>/dev/null)
if [ "$DARK_MODE" = "true" ]; then
    echo "🌙 检测到深色模式 - 使用深色主题GUI"
    GUI_SCRIPT="content_generator_gui_dark.py"
else
    echo "☀️ 检测到浅色模式 - 使用标准GUI"
    GUI_SCRIPT="content_generator_gui.py"
fi

# 运行GUI
echo "🎯 启动GUI界面..."
$PYTHON_CMD $GUI_SCRIPT

echo "👋 GUI已关闭"
read -p "按回车键退出..."