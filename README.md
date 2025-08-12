# FastMCP Multi-Agent Intelligent Content Production System

> 🚀 基于多Agent架构的智能内容生产平台，让AI为您自动创作高质量内容！

## ✨ 特性

- 🤖 **多Agent协作**: Research、Writer、Video、Scorer四个专业Agent协同工作
- 🎯 **平台适配**: 支持微信公众号、小红书、B站、抖音等主流平台  
- 📊 **质量保证**: 内置多维度质量评估算法，确保内容质量
- 🔄 **任务调度**: 异步任务管理，支持批量处理和并发控制
- � **智能优化**: 基于平台特性自动优化内容风格和格式
- � **多种接口**: CLI工具、HTTP API、Python SDK三种使用方式

## 🏗️ 系统架构

```
FastMCP Content Factory
├── Master Controller     # 主控制器
├── Task Manager          # 任务管理器
├── Content Pipeline      # 内容流水线
└── Multi-Agent System    # 多Agent系统
    ├── Research Agent    # 研究分析Agent
    ├── Writer Agent      # 内容创作Agent 
    ├── Video Agent       # 视频内容Agent
    └── Scorer Agent      # 质量评估Agent
```

## 📦 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd fastmcp-content-factory

# 自动安装依赖
python start.py install

# 或手动安装
pip install -e .
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env
```

必需的环境变量：
```bash
# LLM API配置
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
TAVILY_API_KEY=your_tavily_api_key  # 用于网络搜索

# Redis配置（可选，默认本地Redis）
REDIS_URL=redis://localhost:6379

# 数据库配置（可选，默认SQLite）
DATABASE_URL=sqlite:///./content_factory.db
```

### 3. 启动使用

#### 方式1: CLI工具（推荐入门）

```bash
# 启动CLI工具
python start.py cli

# 创建内容任务
content-factory create-task "人工智能在教育领域的应用" 
  --platforms wechat,xiaohongshu 
  --depth medium 
  --versions 3

# 查看任务状态
content-factory status <task-id>

# 获取结果
content-factory result <task-id>
```

#### 方式2: HTTP API（推荐生产）

```bash
# 启动API服务器
python start.py api

# 访问API文档
# http://localhost:8000/docs
```

API使用示例：
```bash
# 创建任务
curl -X POST "http://localhost:8000/tasks" 
  -H "Content-Type: application/json" 
  -d '{
    "topic": "人工智能在教育领域的应用",
    "platforms": ["wechat", "xiaohongshu"],
    "research_depth": "medium",
    "versions_per_platform": 3
  }'

# 查看状态
curl "http://localhost:8000/tasks/{task_id}"

# 获取结果
curl "http://localhost:8000/tasks/{task_id}/result"
```

#### 方式3: Python SDK

```python
import asyncio
from content_factory import MasterController

async def main():
    # 创建控制器
    master = MasterController()
    await master.start_processing()
    
    # 创建任务
    result = await master.create_content_task(
        topic="人工智能在教育领域的应用",
        platforms=["wechat", "xiaohongshu"],
        research_depth="medium",
        versions_per_platform=3,
        include_video=True
    )
    
    task_id = result["task_id"];
    
    # 等待完成
    while True:
        status = await master.get_task_status(task_id)
        if status['status'] == 'completed':
            break
        await asyncio.sleep(5)
    
    # 获取结果
    final_result = await master.get_task_result(task_id)
    print(f"最佳版本: {final_result['best_version']['title']}")
    
    await master.stop_processing()

asyncio.run(main())
```

### 4. 运行示例

```bash
# 运行完整示例演示
python start.py examples
```

## 🎮 使用指南

### 支持的平台

| 平台 | 内容特点 | 适用场景 |
|-----|----------|----------|
| **微信公众号** | 专业深度，长文为主 | 知识分享、专业分析 |
| **小红书** | 轻松活泼，图文并茂 | 生活分享、产品推荐 |
| **B站** | 教育向，视频脚本 | 教程制作、知识科普 |
| **抖音** | 娱乐向，短视频 | 趣味内容、热点话题 |

### 研究深度选择

- **shallow**: 快速生产，基础调研（1-2分钟）
- **medium**: 平衡质量，中度调研（3-5分钟）  
- **deep**: 高质量，深度调研（5-10分钟）

### 内容质量评估

系统会从以下维度评估内容质量：
- 📖 **内容质量**: 信息准确性、逻辑性、完整性
- 🎯 **平台适配**: 符合平台特点、用户喜好
- 📱 **格式规范**: 标题、结构、长度、标签使用
- 💡 **创新性**: 观点新颖性、表达创意
- 📈 **传播潜力**: 话题热度、互动可能性

## 🔧 高级配置

### 自定义Agent配置

```python
# 在content_factory/__init__.py中修改
AGENT_CONFIGS = {
    "research": {
        "model": "gpt-4",
        "temperature": 0.1,
        "max_tokens": 2000
    },
    "writer": {
        "model": "claude-3-sonnet",
        "temperature": 0.7,
        "max_tokens": 4000
    }
}
```

### 并发控制

```python
# 调整并发任务数
master = MasterController(max_concurrent_tasks=5)
```

### 自定义平台模板

在 `utils/platform_config.py` 中添加新平台配置：

```python
PLATFORM_CONFIGS = {
    "custom_platform": {
        "name": "自定义平台",
        "content_types": ["article", "video"],
        "max_length": 2000,
        "style": "professional"
    }
}
```

## 📊 系统监控

### CLI监控

```bash
# 查看系统状态
content-factory list-tasks

# 实时监控任务
content-factory status <task-id> --watch
```

### API监控

```bash
# 系统状态
curl "http://localhost:8000/system/status"

# 任务列表
curl "http://localhost:8000/tasks?status=processing&limit=10"
```

## 🛠️ 开发指南

### 项目结构

```
fastmcp-content-factory/
├── content_factory/          # 主包
│   ├── __init__.py          # 包初始化
│   ├── models/              # 数据模型
│   ├── agents/              # Agent实现
│   ├── core/                # 核心组件
│   └── utils/               # 工具函数
├── cli.py                   # CLI工具
├── api_server.py            # API服务器
├── examples.py              # 使用示例
├── start.py                 # 启动脚本
├── pyproject.toml           # 项目配置
└── README.md                # 项目文档
```

### 添加新Agent

1. 继承 `BaseAgent` 类
2. 实现 `async def process()` 方法
3. 在 `MasterController` 中注册

```python
from content_factory.agents.base import BaseAgent

class CustomAgent(BaseAgent):
    async def process(self, task_data: dict) -> dict:
        # 实现自定义逻辑
        return {"result": "processed"}
```

### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行测试
pytest tests/

# 运行特定测试
pytest tests/test_agents.py -v
```

## 🐛 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   # 使用清华源
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -e .
   ```

2. **Redis连接失败**
   ```bash
   # 启动本地Redis
   redis-server
   
   # 或使用Docker
   docker run -d -p 6379:6379 redis:alpine
   ```

3. **API Key配置错误**
   - 检查 `.env` 文件是否存在
   - 确认API Key格式正确
   - 验证API Key有效性

4. **任务执行失败**
   - 检查网络连接
   - 查看日志文件 `logs/`
   - 确认模型可用性

### 日志查看

```bash
# 实时查看日志
tail -f logs/content_factory.log

# 按级别过滤
grep "ERROR" logs/content_factory.log
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交Pull Request

### 代码规范

```bash
# 代码格式化
black .

# 导入排序
isort .

# 类型检查
mypy content_factory/
```

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- OpenAI GPT系列模型
- Anthropic Claude系列模型
- Tavily搜索API
- FastAPI Web框架
- 所有贡献者和使用者

## 📞 联系我们

- 📧 Email: team@contentfactory.ai
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/fastmcp-content-factory/issues)
- 📖 文档: [在线文档](https://docs.contentfactory.ai)

---

<p align="center">
  <strong>让AI为您创作出色内容！</strong><br>
  ⭐ 如果这个项目对您有帮助，请给我们一个Star！
</p>
