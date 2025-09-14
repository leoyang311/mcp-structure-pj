# FastMCP Content Factory - Enhanced Anti-Censorship Version

高质量内容生成系统，集成反审查机制和DEPTH+CASE框架。

## 🌟 核心特性

### ✅ 反审查机制
- **智能模型切换**: Qwen3 → Claude 自动故障转移
- **审查检测算法**: 多维度智能检测机制
- **质量保证**: 链式思维过滤 + DEPTH+CASE框架

### ✅ 高质量生成
- **Qwen3-235b-a22b-think**: 主力模型，支持复杂推理
- **Claude-Sonnet-4**: 备用模型，规避审查限制
- **Yunwu API**: 统一接口，支持多模型切换

### ✅ 多平台适配
- 微信公众号: 专业深度分析
- 小红书: 真实体验分享
- B站: 知识型内容
- 抖音: 数据密集短内容

## 📊 测试验证

### 最新测试结果 (2025-08-17)
- **总测试**: 12次 (3话题 × 4平台)
- **成功率**: 100%
- **模型切换**: 3次智能切换
- **内容质量**: 27,858字高质量内容

### 话题覆盖
1. **澳洲杨lanlan事件分析** - 政治敏感话题
2. **小米汽车市场竞争分析** - 商业深度分析
3. **雅鲁藏布江水电站经济影响** - 投资机会分析

## 🏗️ 架构设计

```
src/content_factory/
├── core/
│   ├── anti_censorship_system.py    # 反审查核心系统
│   └── openai_client.py            # 统一API客户端
├── agents/
│   ├── research_agent.py           # 研究代理
│   ├── writer_agent.py             # 写作代理
│   └── scorer_agent.py             # 质量评分代理
└── engines/                        # 内容生成引擎
```

## 🚀 快速开始

### 环境配置
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置API密钥
```

### 基础使用
```python
from src.content_factory.core.anti_censorship_system import AntiCensorshipContentGenerator

# 初始化生成器
generator = AntiCensorshipContentGenerator()

# 生成内容（带反审查检测与自动切换）
result = generator.generate_content(
    prompt="你的内容提示",
    topic="话题名称",
    expected_length=1500  # 可选，用于长度与质量检测
)

print(f"使用模型: {result.get('model_used')}")
print(f"内容: {result.get('final_content')[:200]}...")
```

### 高级测试
```bash
# 运行完整的三话题四平台测试
python enhanced_anti_censorship_test.py

# 查看测试结果
ls results/
```

## 📋 DEPTH+CASE框架

### 质量标准
- **C (Concrete)**: 精确数字，时间精确到日期
- **A (Actual)**: 实名公司、真实人物、具体事件  
- **S (Specific)**: 技术参数、财务数据、政策条款
- **E (Expert)**: 专家实名、报告编号、权威机构

### 禁用表达
- ❌ "据了解"、"有消息称"、"业内人士表示"
- ❌ "大约"、"左右"、"相关"、"一定程度上"  
- ❌ "值得注意的是"、"引起关注"、"备受期待"

## 🔧 技术特色

### 反审查机制
1. **多维度检测**: 关键词 + 内容长度 + 质量指标
2. **智能切换**: 检测到审查时自动切换模型
3. **质量保证**: 确保切换后内容质量不降低

### 链式思维过滤
- 自动移除 `<think>...</think>` 标签
- 保留纯净的正文内容
- 提升可读性和专业度

## 📈 商业价值

### 已验证应用场景
- ✅ 专业财经分析报告
- ✅ 深度新闻调查内容
- ✅ 高质量自媒体文章
- ✅ 敏感话题客观分析

### 核心优势
- **无审查限制**: 可处理政治敏感等话题
- **高质量输出**: 符合专业媒体标准
- **平台适配**: 针对不同平台优化风格
- **自动化程度**: 减少人工干预，提高效率

## 📚 测试报告

详细的测试结果和分析报告保存在 `results/` 目录:

- `enhanced_anti_censorship_report_*.md` - 反审查测试报告
- `完整文章集_反审查版_*.md` - 完整生成内容集合
- `enhanced_anti_censorship_results_*.json` - 原始测试数据

## 🛠️ 开发

### 项目结构
```
fastmcp-content-factory/
├── src/                    # 源代码
├── results/               # 测试结果
├── docs/                  # 文档
├── .env                   # 环境配置
├── pyproject.toml         # 项目配置
└── README.md             # 项目说明
```

### 贡献指南
1. Fork 项目
2. 创建特性分支
3. 提交变更
4. 发起 Pull Request

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

**版本**: v2.0.0 (反审查增强版)  
**更新时间**: 2025-08-17  
**技术支持**: Enhanced Anti-Censorship Content Factory
