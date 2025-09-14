#!/bin/bash
# 仓库清理脚本
# 清理临时文件，保留核心功能和文档

echo "🧹 开始清理仓库..."

# 进入项目目录
cd /Users/yangshuntian/Downloads/mcp-structure-pj/fastmcp-content-factory

# 创建results目录保存重要的测试结果
mkdir -p results

# 保留重要的测试结果文档
echo "📄 保留重要文档..."
mv "完整文章集_反审查版_20250817_232618.md" results/
mv enhanced_anti_censorship_report_20250817_232524.md results/
mv enhanced_anti_censorship_results_20250817_232524.json results/

# 移除临时测试文件
echo "🗑️  移除临时测试文件..."
rm -f *_test_*.py
rm -f test_*.py
rm -f demo_*.py
rm -f simple_*.py
rm -f check_*.py
rm -f fix_*.py
rm -f export_*.py
rm -f view_*.py
rm -f filter_*.py
rm -f generate_*.py
rm -f integrated_*.py

# 移除临时数据文件
echo "🗑️  移除临时数据文件..."
rm -f *.json
rm -f censorship_*.json
rm -f real_*.json
rm -f filtered_*.json
rm -f *.log

# 移除临时markdown文件（除了results目录中的）
rm -f "澳洲华人洗钱案分析_完整版_"*.md

# 清理备份文件
rm -f .env.backup

# 检查并保留核心文件
echo "✅ 保留的核心文件:"
echo "  - 源代码目录: src/"
echo "  - 环境配置: .env"
echo "  - 项目文档: README.md, CHANGELOG_v2.0.md"
echo "  - 配置文件: pyproject.toml, docker-compose.yml"
echo "  - 重要脚本: api_server.py, cli.py, start.py"

echo "✅ 保留的测试结果:"
ls -la results/

echo "🎉 仓库清理完成！"
