# FastMCP Content Factory - 启动与配置说明

## 🚀 启动方式

### 方法1: 智能 GUI 启动（推荐）
```bash
python start_gui_smart.py
```
自动检测系统主题（深色/浅色），选择合适界面

### 方法2: 直接启动深色主题 GUI
```bash
python content_generator_gui_dark.py
```

### 方法3: 命令行模式
```bash
python cli.py --help
```

### 方法4: REST API 服务
```bash
python api_server.py
# 访问 http://localhost:8000/docs 查看接口文档
```

## 🔧 配置要求

### 环境依赖
```bash
# 使用 uv 安装（推荐，速度更快）
uv sync

# 或使用 pip
pip install -e .
```

Python 版本要求：**3.10+**

### API 密钥配置
复制并填写 `.env` 文件：
```bash
cp .env.example .env
```

```env
# 主力 API（云雾，支持 Qwen3 和 Claude）
OPENAI_API_KEY=your_yunwu_key
OPENAI_API_BASE=https://yunwu.ai/v1
OPENAI_MODEL=qwen3-235b-a22b-think

# 研究搜索（Tavily，用于真实网络搜索）
TAVILY_API_KEY=your_tavily_key

# 备用模型
BACKUP_MODEL_NAME=claude-sonnet-4-20250514-thinking
```

### 验证配置
```bash
uv run python -c "
from src.content_factory.core.openai_client import get_openai_client, get_default_model
client = get_openai_client()
print('✅ API 连接正常')
print(f'默认模型: {get_default_model()}')
"
```

## 🎯 使用流程

### GUI 使用
1. 运行 `python start_gui_smart.py`
2. 输入内容主题
3. 勾选目标平台（微信/小红书/B站/抖音）
4. 选择内容类型（文章 / 视频脚本）
5. 点击「开始生成」或按 **Ctrl+G**
6. 在分标签页查看各平台结果

### 快捷键
| 快捷键 | 功能 |
|--------|------|
| Ctrl+G | 开始生成 |
| Ctrl+S | 保存结果 |
| Ctrl+R | 重置界面 |
| Ctrl+N | 选择新主题 |
| Ctrl+T | 切换深色/浅色主题 |
| F5 | 清空结果 |
| F1 | 显示帮助 |

## ⚠️ 重要提醒

- 需要稳定网络连接（Tavily 搜索 + AI API）
- Tavily 搜索为实时数据，结果比模拟数据准确
- 注意各 API 的使用配额限制

## 📁 当前文件结构

```
mcp-structure-pj/
├── api_server.py                      # REST API 服务
├── cli.py                             # 命令行工具（typer + rich）
├── content_generator_gui_dark.py      # 深色主题 GUI
├── start_gui_smart.py                 # 智能 GUI 启动器
├── gui_config.py                      # GUI 配置管理
├── start.py                           # 主启动脚本
├── health_check.py                    # API 健康检查
├── filter_thinking_content.py         # 过滤 <think> 标签
├── export_readable_articles.py        # 导出可读文章
├── generate_complete_articles.py      # 批量生成工具
├── view_articles.py                   # 文章查看器
├── test_enhanced_anti_censorship.py   # 反审查系统测试
├── test_qwen3_three_topics.py         # Qwen3 生产级测试
├── src/content_factory/               # 核心模块
│   ├── core/                          # API 客户端、反审查、管道
│   ├── agents/                        # 多 Agent 系统
│   ├── engines/                       # 深度研究引擎
│   ├── prompts/                       # CASE 框架提示词
│   └── utils/                         # 工具函数
├── .claude/skills/                    # Claude Code 技能
│   ├── generate-content.md
│   ├── research-topic.md
│   ├── quality-audit.md
│   └── video-prompt.md
└── .env                               # API 配置（不提交到 git）
```

---

**版本**: v3.1
**更新时间**: 2026年3月
**Python**: 3.10+
**兼容性**: macOS / Windows / Linux
