# 🔥 FastMCP Content Factory - 真实API版本

## ⚠️ 重要更新

根据用户要求，GUI已完全更新为**仅使用真实API版本**，所有模拟数据已被移除。

### ✅ 主要改进

#### 1. **仅真实API模式**
- ❌ **移除所有模拟数据生成**
- ✅ **仅使用FastMCP Content Factory真实API**
- ✅ **严格的API验证和错误处理**
- ✅ **生成前确认对话框**

#### 2. **主题切换功能**
- 🌙 **深色模式**: 适合深色系统环境
- ☀️ **浅色模式**: 适合浅色系统环境
- 🔄 **一键切换**: 点击按钮或Ctrl+T快速切换
- 💾 **状态保持**: 切换主题时保持所有输入和结果

#### 3. **增强的错误处理**
- 🛡️ **生成器状态检查**: 确保API可用才允许生成
- 📋 **详细错误提示**: 明确指出问题所在
- 🔧 **解决方案建议**: 提供具体的修复步骤

## 🚀 启动方式

### 方法1: 智能启动器（推荐）
```bash
python start_real_api_gui.py
```
- 自动检查FastMCP模块
- 智能检测系统主题
- 完整的环境验证

### 方法2: 直接启动
```bash
python content_generator_gui_dark.py
```
- 直接启动GUI
- 自动检测系统主题

### 方法3: 双击启动
```bash
双击 "启动真实API版本.command"
```

### 方法4: 一行完整指令
```bash
cd /Users/yangshuntian/Downloads/mcp-structure-pj/fastmcp-content-factory && python start_real_api_gui.py
```

## 🔧 配置要求

### 必需配置
1. **FastMCP Content Factory模块**
   - `src/content_factory/` 目录必须存在
   - 所有相关Python模块已安装

2. **API密钥配置**
   - `.env` 文件中配置了正确的API密钥
   - 网络连接正常，能访问API服务

3. **Python环境**
   - Python 3.8+ 
   - tkinter (通常内置)
   - asyncio, threading等标准库

### 检查命令
```bash
# 检查FastMCP模块
python -c "from src.content_factory.core.anti_censorship_system import AntiCensorshipContentGenerator; print('✅ 模块正常')"

# 检查API配置
python -c "from src.content_factory.core.anti_censorship_system import AntiCensorshipContentGenerator; gen = AntiCensorshipContentGenerator(); print('✅ API配置正常')"
```

## 🎯 使用流程

### 首次启动
1. **环境检查**: 启动器会自动检查所有依赖
2. **模块验证**: 确认FastMCP模块可用
3. **主题选择**: 选择深色或浅色主题
4. **API验证**: 确认生成器初始化成功

### 内容生成
1. **输入主题**: 填写要生成的内容主题
2. **选择平台**: 勾选目标平台（微信/小红书/B站/抖音）
3. **配置选项**: 设置内容类型和质量模式
4. **确认生成**: 系统会显示确认对话框
5. **等待结果**: 实时显示生成进度
6. **查看内容**: 在分标签页中查看结果

### 多次使用
1. **生成完成**: 自动弹出操作选项对话框
2. **快速操作**: 
   - 保存并继续生成新内容
   - 直接继续生成（不保存）
   - 重置界面到初始状态
3. **主题选择**: 从热门主题列表快速选择
4. **无缝切换**: 无需重启即可连续生成

## 💡 新功能特性

### 🎨 主题切换
- **动态切换**: 运行时一键切换深色/浅色主题
- **状态保持**: 切换时保持所有输入内容和生成结果
- **智能检测**: 自动检测系统主题并推荐合适模式
- **快捷键**: Ctrl+T 快速切换

### 🛡️ API验证
- **启动检查**: 程序启动时验证API可用性
- **生成前确认**: 显示详细的生成参数确认
- **错误恢复**: 详细的错误信息和解决建议
- **状态指示**: 实时显示API连接状态

### ⌨️ 快捷键支持
- **Ctrl+G**: 开始生成内容
- **Ctrl+S**: 保存生成结果
- **Ctrl+R**: 重置界面
- **Ctrl+N**: 选择新主题
- **Ctrl+T**: 切换主题模式
- **F5**: 清空结果
- **F1**: 显示帮助

## ⚠️ 重要提醒

### 关于API使用
- ✅ **仅真实API**: 不包含任何模拟数据或演示内容
- ✅ **完整功能**: 使用FastMCP的反审查和质量控制功能
- ⚠️ **网络依赖**: 需要稳定的网络连接
- ⚠️ **API配额**: 注意API使用量限制

### 故障排除
1. **"生成器未就绪"错误**:
   - 检查src/content_factory模块是否存在
   - 确认.env文件API密钥配置
   - 测试网络连接

2. **主题切换失败**:
   - 确保有足够内存
   - 检查是否有其他GUI程序冲突

3. **生成失败**:
   - 查看控制台错误信息
   - 确认API密钥有效
   - 检查网络连接状态

## 📁 文件结构

```
fastmcp-content-factory/
├── content_generator_gui_dark.py      # 主GUI程序 ⭐
├── start_real_api_gui.py              # 智能启动器 ⭐
├── 启动真实API版本.command            # 快速启动脚本 ⭐
├── 真实API版本说明.md                 # 本说明文件 ⭐
├── src/content_factory/               # FastMCP核心模块
│   ├── core/
│   │   ├── anti_censorship_system.py # 反审查系统
│   │   └── ...
│   └── ...
└── .env                              # API配置文件
```

⭐ 标记为新增或重大更新的文件

---

**版本**: v3.0 (真实API专用版)  
**更新时间**: 2024年  
**特性**: 仅真实API + 主题切换 + 多次使用  
**兼容性**: macOS/Windows/Linux
