#!/usr/bin/env python3
"""
FastMCP Content Factory GUI - 黑色模式优化版
专门为macOS黑色模式优化的图形界面
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import asyncio
import threading
import json
import os
import sys
import random
from datetime import datetime
from typing import Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.content_factory.core.anti_censorship_system import AntiCensorshipContentGenerator
    from src.content_factory.models import Platform
    from src.content_factory.agents.writer_agent import WriterAgent
    from src.content_factory.models.task import ResearchData
    HAS_CONTENT_FACTORY = True
except ImportError as e:
    HAS_CONTENT_FACTORY = False
    print(f"Warning: Content Factory modules not found. Error: {e}")


class ContentFactoryGUI:
    """FastMCP Content Factory GUI类 - 支持深色/浅色主题切换"""
    
    # 主题配色方案
    DARK_COLORS = {
        'bg': '#2b2b2b',           # 背景色
        'fg': '#ffffff',           # 前景色(文字)
        'select_bg': '#404040',    # 选中背景
        'select_fg': '#ffffff',    # 选中文字
        'button_bg': '#404040',    # 按钮背景
        'button_fg': '#ffffff',    # 按钮文字
        'entry_bg': '#404040',     # 输入框背景
        'entry_fg': '#ffffff',     # 输入框文字
        'frame_bg': '#2b2b2b',     # 框架背景
        'accent': '#0078d4',       # 强调色(蓝色)
        'success': '#107c10',      # 成功色(绿色)
        'warning': '#ff8c00',      # 警告色(橙色)
        'error': '#d13438'         # 错误色(红色)
    }
    
    LIGHT_COLORS = {
        'bg': '#ffffff',           # 背景色
        'fg': '#000000',           # 前景色(文字)
        'select_bg': '#e1e1e1',    # 选中背景
        'select_fg': '#000000',    # 选中文字
        'button_bg': '#f0f0f0',    # 按钮背景
        'button_fg': '#000000',    # 按钮文字
        'entry_bg': '#ffffff',     # 输入框背景
        'entry_fg': '#000000',     # 输入框文字
        'frame_bg': '#ffffff',     # 框架背景
        'accent': '#0078d4',       # 强调色(蓝色)
        'success': '#107c10',      # 成功色(绿色)
        'warning': '#ff8c00',      # 警告色(橙色)
        'error': '#d13438'         # 错误色(红色)
    }
    
    @property
    def COLORS(self):
        return self.DARK_COLORS if self.dark_mode else self.LIGHT_COLORS
    
    def __init__(self, dark_mode=True):
        self.dark_mode = dark_mode
        self.root = tk.Tk()
        self.setup_window()
        
        # 初始化生成器
        self.generator = None
        self.init_generator()
        
        # 应用主题
        self.apply_theme()
        
        # 创建界面
        self.create_widgets()
        
        # 结果存储
        self.current_results = {}
        
        mode_name = "黑色模式" if self.dark_mode else "白天模式"
        print(f"✅ {mode_name}GUI初始化完成")
    
    def setup_window(self):
        """设置窗口基本属性"""
        theme_name = "深色模式" if self.dark_mode else "浅色模式"
        self.root.title(f"FastMCP Content Factory - 内容生成器 ({theme_name})")
        self.root.geometry("1200x800")
        self.root.minsize(900, 700)
        
        # 设置窗口背景
        self.root.configure(bg=self.COLORS['bg'])
        
        # 尝试使用系统原生外观
        try:
            # macOS 特有设置
            self.root.tk.call('tk', 'scaling', 1.0)
            
            # 如果可能的话，使用系统暗色主题
            if sys.platform == "darwin":  # macOS
                try:
                    self.root.tk.call("set", "::tk::mac::CGAntialiasLimit", 1)
                    self.root.tk.call("set", "::tk::mac::antialiasedtext", 1)
                except:
                    pass
        except:
            pass
    
    def apply_theme(self):
        """应用主题样式"""
        style = ttk.Style()
        
        # 配置各种组件的样式
        
        # 标签样式
        style.configure(
            'Dark.TLabel',
            background=self.COLORS['bg'],
            foreground=self.COLORS['fg'],
            font=('SF Pro Display', 11) if sys.platform == "darwin" else ('Segoe UI', 11)
        )
        
        # 大标题样式
        style.configure(
            'Title.TLabel',
            background=self.COLORS['bg'],
            foreground=self.COLORS['fg'],
            font=('SF Pro Display', 14, 'bold') if sys.platform == "darwin" else ('Segoe UI', 14, 'bold')
        )
        
        # 按钮样式
        style.configure(
            'Dark.TButton',
            background=self.COLORS['button_bg'],
            foreground=self.COLORS['button_fg'],
            borderwidth=1,
            focuscolor='none',
            font=('SF Pro Display', 11) if sys.platform == "darwin" else ('Segoe UI', 11)
        )
        
        # 按钮悬停样式
        style.map(
            'Dark.TButton',
            background=[
                ('active', self.COLORS['select_bg']),
                ('pressed', self.COLORS['accent'])
            ],
            foreground=[
                ('active', self.COLORS['select_fg']),
                ('pressed', '#ffffff')
            ]
        )
        
        # 强调按钮样式
        style.configure(
            'Accent.TButton',
            background=self.COLORS['accent'],
            foreground='#ffffff',
            borderwidth=1,
            focuscolor='none',
            font=('SF Pro Display', 12, 'bold') if sys.platform == "darwin" else ('Segoe UI', 12, 'bold')
        )
        
        # 成功按钮样式
        style.configure(
            'Success.TButton',
            background=self.COLORS['success'],
            foreground='#ffffff',
            borderwidth=1,
            focuscolor='none'
        )
        
        # 框架样式
        style.configure(
            'Dark.TFrame',
            background=self.COLORS['bg'],
            borderwidth=1,
            relief='solid'
        )
        
        # 带标题的框架样式
        style.configure(
            'Dark.TLabelframe',
            background=self.COLORS['bg'],
            foreground=self.COLORS['fg'],
            borderwidth=2,
            relief='groove'
        )
        
        style.configure(
            'Dark.TLabelframe.Label',
            background=self.COLORS['bg'],
            foreground=self.COLORS['fg'],
            font=('SF Pro Display', 11, 'bold') if sys.platform == "darwin" else ('Segoe UI', 11, 'bold')
        )
        
        # 输入框样式
        style.configure(
            'Dark.TEntry',
            fieldbackground=self.COLORS['entry_bg'],
            background=self.COLORS['entry_bg'],
            foreground=self.COLORS['entry_fg'],
            borderwidth=1,
            insertcolor=self.COLORS['fg']
        )
        
        # 复选框样式
        style.configure(
            'Dark.TCheckbutton',
            background=self.COLORS['bg'],
            foreground=self.COLORS['fg'],
            focuscolor='none',
            font=('SF Pro Display', 11) if sys.platform == "darwin" else ('Segoe UI', 11)
        )
        
        # 单选按钮样式
        style.configure(
            'Dark.TRadiobutton',
            background=self.COLORS['bg'],
            foreground=self.COLORS['fg'],
            focuscolor='none',
            font=('SF Pro Display', 11) if sys.platform == "darwin" else ('Segoe UI', 11)
        )
        
        # 组合框样式
        style.configure(
            'Dark.TCombobox',
            fieldbackground=self.COLORS['entry_bg'],
            background=self.COLORS['entry_bg'],
            foreground=self.COLORS['entry_fg'],
            arrowcolor=self.COLORS['fg']
        )
        
        # 进度条样式
        style.configure(
            'Dark.Horizontal.TProgressbar',
            background=self.COLORS['accent'],
            troughcolor=self.COLORS['select_bg'],
            borderwidth=1,
            lightcolor=self.COLORS['accent'],
            darkcolor=self.COLORS['accent']
        )
        
        # Notebook样式
        style.configure(
            'Dark.TNotebook',
            background=self.COLORS['bg'],
            borderwidth=0
        )
        
        style.configure(
            'Dark.TNotebook.Tab',
            background=self.COLORS['select_bg'],
            foreground=self.COLORS['fg'],
            padding=[12, 8],
            font=('SF Pro Display', 11) if sys.platform == "darwin" else ('Segoe UI', 11)
        )
        
        style.map(
            'Dark.TNotebook.Tab',
            background=[
                ('selected', self.COLORS['accent']),
                ('active', self.COLORS['button_bg'])
            ],
            foreground=[
                ('selected', '#ffffff'),
                ('active', self.COLORS['fg'])
            ]
        )
    
    def init_generator(self):
        """初始化内容生成器"""
        try:
            if HAS_CONTENT_FACTORY:
                self.generator = AntiCensorshipContentGenerator()
                print("✅ AntiCensorshipContentGenerator初始化成功")
                print("[GUI] Generator ready: AntiCensorshipContentGenerator (REAL)")
                return True
            else:
                print("❌ FastMCP Content Factory模块未找到")
                print("请确保src/content_factory模块正确安装")
                self.generator = None
                return False
        except Exception as e:
            print(f"❌ 生成器初始化失败: {e}")
            print("请检查API配置和模块安装")
            self.generator = None
            return False
    
    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, style='Dark.TFrame', padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # 标题栏
        title_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        title_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(
            title_frame, 
            text="🚀 FastMCP Content Factory", 
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # 主题切换按钮
        theme_icon = "🌙" if not self.dark_mode else "☀️"
        theme_text = "深色模式" if not self.dark_mode else "浅色模式"
        self.theme_button = ttk.Button(
            title_frame,
            text=f"{theme_icon} {theme_text}",
            command=self.toggle_theme,
            style='Dark.TButton',
            width=12
        )
        self.theme_button.grid(row=0, column=2, sticky=tk.E)
        
        # 1. 主题输入区
        ttk.Label(
            main_frame, 
            text="📝 内容主题:", 
            style='Dark.TLabel'
        ).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.topic_var = tk.StringVar(value="小米汽车市场竞争分析")
        self.topic_entry = ttk.Entry(
            main_frame, 
            textvariable=self.topic_var, 
            style='Dark.TEntry',
            font=('SF Pro Display', 11) if sys.platform == "darwin" else ('Segoe UI', 11),
            width=40
        )
        self.topic_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 2. 平台选择区
        ttk.Label(
            main_frame, 
            text="🎯 目标平台:", 
            style='Dark.TLabel'
        ).grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(15, 5))
        
        platform_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        platform_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(15, 5))
        
        # 平台复选框
        self.platform_vars = {}
        platforms = [
            ("微信公众号", "wechat", "深度分析，专业权威", "📰"),
            ("小红书", "xiaohongshu", "生活分享，真实体验", "📱"),
            ("B站", "bilibili", "知识科普，专业有趣", "🎬"),
            ("抖音", "douyin", "短视频，情感共鸣", "📺")
        ]
        
        for i, (name, key, desc, emoji) in enumerate(platforms):
            var = tk.BooleanVar(value=True if i < 2 else False)
            self.platform_vars[key] = var
            
            cb = ttk.Checkbutton(
                platform_frame, 
                text=f"{emoji} {name} - {desc}", 
                variable=var,
                style='Dark.TCheckbutton'
            )
            cb.grid(row=i, column=0, sticky=tk.W, pady=3)
        
        # 3. 内容类型选择
        ttk.Label(
            main_frame, 
            text="📄 内容类型:", 
            style='Dark.TLabel'
        ).grid(row=3, column=0, sticky=tk.W, pady=(15, 5))
        
        type_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        type_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(15, 5))
        
        self.content_type_var = tk.StringVar(value="article")
        content_types = [
            ("📰 文章", "article"),
            ("🎬 视频脚本", "video_script"),
            ("🖼️ 图文混排", "mixed_content")
        ]
        
        for i, (name, value) in enumerate(content_types):
            ttk.Radiobutton(
                type_frame, 
                text=name, 
                variable=self.content_type_var, 
                value=value,
                style='Dark.TRadiobutton'
            ).grid(row=0, column=i, sticky=tk.W, padx=(0, 25))
        
        # 4. 高级选项
        options_frame = ttk.LabelFrame(
            main_frame, 
            text="⚙️ 高级选项", 
            style='Dark.TLabelframe',
            padding="10"
        )
        options_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 5))
        options_frame.columnconfigure(1, weight=1)
        
        # 反审查模式
        self.anti_censorship_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame, 
            text="🛡️ 反审查模式 (智能模型切换)", 
            variable=self.anti_censorship_var,
            style='Dark.TCheckbutton'
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        # 质量模式
        ttk.Label(
            options_frame, 
            text="质量模式:", 
            style='Dark.TLabel'
        ).grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        self.quality_var = tk.StringVar(value="high")
        quality_combo = ttk.Combobox(
            options_frame, 
            textvariable=self.quality_var, 
            values=["standard", "high", "premium"], 
            state="readonly", 
            width=15,
            style='Dark.TCombobox'
        )
        quality_combo.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # 视频引擎（视频脚本提示词风格）
        ttk.Label(
            options_frame,
            text="视频引擎:",
            style='Dark.TLabel'
        ).grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.video_engine_var = tk.StringVar(value="minimax")
        video_engine_combo = ttk.Combobox(
            options_frame,
            textvariable=self.video_engine_var,
            values=["minimax", "sora"],
            state="readonly",
            width=15,
            style='Dark.TCombobox'
        )
        video_engine_combo.grid(row=2, column=1, sticky=tk.W, pady=(10, 0))

        # SAT 话题池随机（视频脚本）
        self.use_sat_topic_pool_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="🎯 使用SAT随机话题池（视频脚本）",
            variable=self.use_sat_topic_pool_var,
            style='Dark.TCheckbutton'
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(8, 0))

        # 单次生成时长（用于引擎受限，如sora单次10秒）
        ttk.Label(options_frame, text="单次时长(秒):", style='Dark.TLabel').grid(row=2, column=2, sticky=tk.W, pady=(10, 0), padx=(15,0))
        self.single_clip_var = tk.IntVar(value=10)
        single_entry = ttk.Entry(options_frame, textvariable=self.single_clip_var, width=10)
        single_entry.grid(row=2, column=3, sticky=tk.W, pady=(10,0))

        # 总时长（用于sora分段，或作为目标时长）
        ttk.Label(options_frame, text="总时长(秒):", style='Dark.TLabel').grid(row=2, column=4, sticky=tk.W, pady=(10, 0), padx=(15,0))
        self.total_duration_var = tk.IntVar(value=60)
        total_entry = ttk.Entry(options_frame, textvariable=self.total_duration_var, width=10)
        total_entry.grid(row=2, column=5, sticky=tk.W, pady=(10,0))
        
        # 5. 操作按钮区
        button_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 10), sticky=(tk.W, tk.E))
        
        # 左侧按钮组
        left_buttons = ttk.Frame(button_frame, style='Dark.TFrame')
        left_buttons.pack(side=tk.LEFT)
        
        self.generate_button = ttk.Button(
            left_buttons, 
            text="🚀 开始生成内容", 
            command=self.start_generation, 
            style="Accent.TButton",
            width=20
        )
        self.generate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            left_buttons, 
            text="💾 保存结果", 
            command=self.save_results,
            style="Success.TButton",
            width=12
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            left_buttons, 
            text="🔄 清空", 
            command=self.clear_results,
            style="Dark.TButton",
            width=8
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # 重置按钮
        ttk.Button(
            left_buttons, 
            text="🆕 重置", 
            command=self.reset_all,
            style="Dark.TButton",
            width=8
        ).pack(side=tk.LEFT)
        
        # 右侧进度条和状态
        right_info = ttk.Frame(button_frame, style='Dark.TFrame')
        right_info.pack(side=tk.RIGHT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            right_info, 
            variable=self.progress_var, 
            mode="determinate", 
            length=250,
            style='Dark.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 6. 结果显示区
        result_frame = ttk.LabelFrame(
            main_frame, 
            text="📋 生成结果", 
            style='Dark.TLabelframe',
            padding="10"
        )
        result_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(15, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 平台标签选择
        self.result_notebook = ttk.Notebook(result_frame, style='Dark.TNotebook')
        self.result_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        status_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        status_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_var = tk.StringVar(value="准备就绪 - 选择平台和主题后点击生成 (快捷键: Ctrl+G)")
        self.status_label = ttk.Label(
            status_frame, 
            textvariable=self.status_var, 
            style='Dark.TLabel',
            font=('SF Pro Display', 10) if sys.platform == "darwin" else ('Segoe UI', 10)
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 绑定快捷键
        self.bind_shortcuts()
    
    def bind_shortcuts(self):
        """绑定键盘快捷键"""
        try:
            # Ctrl+G: 开始生成
            self.root.bind('<Control-g>', lambda e: self.start_generation())
            self.root.bind('<Control-G>', lambda e: self.start_generation())
            
            # Ctrl+S: 保存结果
            self.root.bind('<Control-s>', lambda e: self.save_results())
            self.root.bind('<Control-S>', lambda e: self.save_results())
            
            # Ctrl+R: 重置
            self.root.bind('<Control-r>', lambda e: self.reset_all())
            self.root.bind('<Control-R>', lambda e: self.reset_all())
            
            # F5: 刷新/清空
            self.root.bind('<F5>', lambda e: self.clear_results())
            
            # F1: 显示帮助
            self.root.bind('<F1>', lambda e: self.show_help())
            
            # Ctrl+N: 新主题
            self.root.bind('<Control-n>', lambda e: self.show_quick_topic_selector())
            self.root.bind('<Control-N>', lambda e: self.show_quick_topic_selector())
            
            # Ctrl+T: 切换主题
            self.root.bind('<Control-t>', lambda e: self.toggle_theme())
            self.root.bind('<Control-T>', lambda e: self.toggle_theme())
            
            # 确保主窗口可以接收焦点
            self.root.focus_set()
            
        except Exception as e:
            print(f"❌ 快捷键绑定失败: {e}")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """🔥 FastMCP Content Factory 帮助

📋 功能说明:
• 支持 4 个主流平台内容生成 (微信/小红书/B站/抖音)
• 智能反审查模式，使用真实API突破内容限制
• 实时质量评分和字数统计
• 批量生成和结果导出
• 深色/浅色主题切换

⌨️  快捷键:
• Ctrl+G  开始生成内容
• Ctrl+S  保存生成结果
• Ctrl+R  重置界面
• Ctrl+N  选择新主题
• Ctrl+T  切换深色/浅色主题
• F5      清空结果
• F1      显示帮助

🎯 使用流程:
1. 确保API配置正确
2. 输入内容主题
3. 选择目标平台
4. 配置生成选项
5. 点击生成或按 Ctrl+G
6. 查看和复制结果

⚠️  重要提醒:
• 本GUI只使用真实API，不包含模拟数据
• 需要正确配置FastMCP Content Factory模块
• 确保API密钥和网络连接正常
• 开启反审查模式可处理敏感话题

💡 小贴士:
• 生成完成后会自动弹出快速操作菜单
• 支持自定义主题和热门主题选择
• 使用Ctrl+T快速切换主题模式"""
        
        messagebox.showinfo("帮助", help_text)
    
    def create_scrolled_text_widget(self, parent):
        """创建支持黑色主题的滚动文本框"""
        # 创建框架
        text_frame = tk.Frame(parent, bg=self.COLORS['bg'])
        
        # 创建文本框
        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            bg=self.COLORS['entry_bg'],
            fg=self.COLORS['entry_fg'],
            insertbackground=self.COLORS['fg'],
            selectbackground=self.COLORS['accent'],
            selectforeground='#ffffff',
            font=('SF Mono', 11) if sys.platform == "darwin" else ('Consolas', 11),
            relief='solid',
            borderwidth=1
        )
        
        # 创建滚动条
        scrollbar = tk.Scrollbar(
            text_frame,
            bg=self.COLORS['select_bg'],
            troughcolor=self.COLORS['bg'],
            activebackground=self.COLORS['accent']
        )
        
        # 配置滚动
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_widget.yview)
        
        # 布局
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return text_frame, text_widget
    
    def start_generation(self):
        """开始内容生成"""
        # 验证生成器可用性
        if not self.generator or not HAS_CONTENT_FACTORY:
            messagebox.showerror(
                "生成器未就绪", 
                "内容生成器未初始化。\n\n请确保:\n1. FastMCP Content Factory模块已安装\n2. API密钥已正确配置\n3. 网络连接正常"
            )
            return
        
        # 验证输入
        topic = self.topic_var.get().strip()
        if not topic:
            messagebox.showerror("错误", "请输入内容主题")
            return
        
        selected_platforms = [k for k, v in self.platform_vars.items() if v.get()]
        if not selected_platforms:
            messagebox.showerror("错误", "请至少选择一个平台")
            return
        
        # SAT随机话题池（仅视频脚本）
        try:
            if self.content_type_var.get() == "video_script" and self.use_sat_topic_pool_var.get():
                sat_topics = self._get_sat_topic_pool()
                topic = random.choice(sat_topics)
                self.topic_var.set(topic)
                print(f"[GUI] 使用SAT随机话题: {topic}")
        except Exception:
            pass
        
        # 后端打印关键信息
        try:
            selected_flags = {
                "anti_censorship": bool(self.anti_censorship_var.get()),
                "content_type": self.content_type_var.get()
            }
            print("[GUI] Start generation:")
            print(f"  - topic: {topic}")
            print(f"  - platforms: {selected_platforms}")
            print(f"  - options: {selected_flags}")
        except Exception:
            pass
        
        # 确认开始生成
        platform_names = {
            "wechat": "微信公众号",
            "xiaohongshu": "小红书", 
            "bilibili": "B站",
            "douyin": "抖音"
        }
        
        selected_names = [platform_names.get(p, p) for p in selected_platforms]
        confirm_msg = f"确认生成以下内容?\n\n主题: {topic}\n平台: {', '.join(selected_names)}\n模式: {'反审查模式' if self.anti_censorship_var.get() else '标准模式'}"
        
        if not messagebox.askyesno("确认生成", confirm_msg):
            return
        
        # 禁用生成按钮
        self.generate_button.config(state="disabled", text="⏳ 生成中...")
        self.status_var.set("正在连接API生成内容，请稍候...")
        self.progress_var.set(0)
        
        # 在单独线程中运行异步生成
        threading.Thread(target=self.run_generation, args=(topic, selected_platforms), daemon=True).start()

    def _get_sat_topic_pool(self):
        return [
            "《家长必读：SAT备考中，你90%的“好心帮忙”正在拖孩子后腿》 (针对家长常见误区：过度施压、盲目刷题、不懂技术)",
            "《机考自适应机制详解：第一模块做不好，第二模块还有救吗？策略大公开》 (关键！机考核心策略)",
            "《词汇量3000也能读懂SAT阅读？用“语境预测法”高效猜词实战解析》(附真题段落演练)",
            "《SAT数学“粗心”是借口！这4类单位/小数点/计算陷阱，90%考生都栽过》(附避坑清单)",
            "《机考计算器使用禁忌：哪些题用计算器反而更慢更易错？》",
        ]
    
    def run_generation(self, topic: str, platforms: list):
        """在线程中运行生成任务"""
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 运行异步生成
            results = loop.run_until_complete(self.generate_content_async(topic, platforms))
            
            # 在主线程中更新UI
            self.root.after(0, self.on_generation_complete, results)
            
        except Exception as e:
            self.root.after(0, self.on_generation_error, str(e))
        finally:
            loop.close()
    
    async def generate_content_async(self, topic: str, platforms: list) -> Dict[str, Any]:
        """异步生成内容"""
        results = {}
        total_platforms = len(platforms)
        
        for i, platform in enumerate(platforms):
            try:
                progress = (i / total_platforms) * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                
                platform_names = {
                    "wechat": "微信公众号",
                    "xiaohongshu": "小红书",
                    "bilibili": "B站",
                    "douyin": "抖音"
                }
                
                platform_name = platform_names.get(platform, platform)
                self.root.after(0, lambda p=platform_name: self.status_var.set(f"正在为{p}生成内容..."))
                
                if self.generator and HAS_CONTENT_FACTORY:
                    # 使用真实生成器
                    result = await self.generate_real_content(topic, platform)
                else:
                    # 没有可用的生成器，返回错误
                    raise Exception("生成器未初始化，请检查API配置和模块安装")
                
                results[platform] = result
                
            except Exception as e:
                print(f"平台 {platform} 生成失败: {e}")
                results[platform] = {"error": str(e)}
        
        self.root.after(0, lambda: self.progress_var.set(100))
        return results
    
    async def generate_real_content(self, topic: str, platform: str) -> Dict[str, Any]:
        """使用真实生成器生成内容"""
        try:
            # 视频脚本：走WriterAgent视频提示词模式
            if self.content_type_var.get() == "video_script":
                try:
                    print("[AGENT] WriterAgent video_prompt_mode request:")
                    print(f"  - platform: {platform}")
                    print(f"  - topic: {topic}")
                except Exception:
                    pass

                writer = WriterAgent()
                rd = ResearchData(
                    topic=topic,
                    sources=[], key_points=[topic], trends=[], competitors=[], summary=f"视频脚本：{topic}"
                )
                engine = self.video_engine_var.get() if hasattr(self, 'video_engine_var') else 'minimax'
                # 读取总时长配置
                try:
                    total_duration_input = int(self.total_duration_var.get()) if hasattr(self, 'total_duration_var') else (60 if engine=='sora' else 6)
                except Exception:
                    total_duration_input = 60 if engine == 'sora' else 6
                total_duration = min(6, total_duration_input) if engine == 'minimax' else max(1, total_duration_input)
                single_clip = max(1, int(self.single_clip_var.get() or 10))

                # 分段生成（保持风格一致），仅当sora且需要切分时
                segments_contents = []
                if engine == 'sora' and total_duration > single_clip:
                    import math
                    seg_count = math.ceil(total_duration / single_clip)
                    for i in range(seg_count):
                        seg_dur = single_clip if i < seg_count - 1 else (total_duration - single_clip * (seg_count - 1))
                        seg_topic = f"{topic}（第{i+1}/{seg_count}段，风格一致、叙事连续）"
                        rd_seg = ResearchData(topic=seg_topic, sources=[], key_points=[topic], trends=[], competitors=[], summary=f"视频脚本：{seg_topic}")
                        input_payload = {
                            "research_data": rd_seg,
                            "platforms": [platform],
                            "versions_per_platform": 1,
                            "video_prompt_mode": True,
                            "video_prompt_engine": engine,
                            "video_prompt_duration": seg_dur,
                            "content_type": "video_script",
                        }
                        writer_result = await writer.process(input_payload)
                        versions = writer_result.get("content_versions", [])
                        version = versions[0] if versions else None
                        seg_content = version.content if version else ""
                        segments_contents.append(f"【片段 {i+1}/{seg_count} | {seg_dur}s】\n{seg_content}".strip())
                    content = "\n\n".join(segments_contents)
                else:
                    input_payload = {
                        "research_data": rd,
                        "platforms": [platform],
                        "versions_per_platform": 1,
                        "video_prompt_mode": True,
                        "video_prompt_engine": engine,
                        "video_prompt_duration": total_duration if engine != 'sora' else min(total_duration, single_clip),
                        "content_type": "video_script",
                    }
                    writer_result = await writer.process(input_payload)
                    versions = writer_result.get("content_versions", [])
                    version = versions[0] if versions else None
                    content = version.content if version else ""

                try:
                    print("[AGENT] WriterAgent video_prompt_mode response:")
                    print(f"  - content_length: {len(content)}")
                    if version:
                        print(f"  - engine: {version.metadata.get('video_prompt_engine')}")
                except Exception:
                    pass

                return {
                    "content": content,
                    "model_used": "writer_agent(video_prompt)",
                    "quality_score": 0,
                    "generated_at": datetime.now().isoformat(),
                    "platform": platform,
                    "topic": topic,
                    "word_count": len(content)
                }

            # 使用反审查生成器
            if self.anti_censorship_var.get():
                # 构建详细的prompt
                content_type = self.content_type_var.get()
                
                # 平台特定的prompt
                platform_prompts = {
                    "wechat": f"请为微信公众号写一篇关于{topic}的深度分析文章，要求专业权威，结构清晰，字数1500-3000字",
                    "xiaohongshu": f"请为小红书写一篇关于{topic}的生活分享内容，要求真实体验，有情感共鸣，字数300-1000字", 
                    "bilibili": f"请为B站写一份关于{topic}的视频脚本，要求知识科普，专业有趣，适合视频讲解",
                    "douyin": f"请为抖音写一份关于{topic}的短视频脚本，要求简短有力，情感共鸣，15-60秒时长"
                }
                
                prompt = platform_prompts.get(platform, f"请写一篇关于{topic}的{content_type}")
                
                # 打印API请求详情
                try:
                    print("[API] AntiCensorshipContentGenerator.generate_content request:")
                    print(f"  - platform: {platform}")
                    print(f"  - topic: {topic}")
                    print(f"  - expected_length: 2000")
                    print(f"  - prompt: {prompt[:180]}{'...' if len(prompt)>180 else ''}")
                except Exception:
                    pass
                
                # 使用正确的方法名和参数（同步调用）
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    self.generator.generate_content,
                    prompt,
                    topic,
                    2000
                )
                
                # 打印响应摘要
                try:
                    print("[API] AntiCensorshipContentGenerator.generate_content response:")
                    print(f"  - model_used: {result.get('model_used')}")
                    print(f"  - switches_made: {result.get('switches_made')}")
                    det = result.get('detection_results')
                    if det:
                        last = det[-1]
                        if isinstance(last, dict) and 'detection' in last:
                            d = last['detection']
                            print(f"  - detection.level: {getattr(d, 'level', None)} confidence: {getattr(d, 'confidence', None)} triggers: {getattr(d, 'triggers', None)}")
                    print(f"  - content_length: {len(result.get('final_content',''))}")
                except Exception:
                    pass
                
                return {
                    "content": result.get("final_content", ""),
                    "model_used": result.get("model_used", "unknown"),
                    "quality_score": result.get("quality_score", 0),
                    "generated_at": datetime.now().isoformat(),
                    "platform": platform,
                    "topic": topic,
                    "word_count": len(result.get("final_content", ""))
                }
            else:
                # 标准生成模式 - 也使用真实API但不启用反审查
                content_type = self.content_type_var.get()
                
                platform_prompts = {
                    "wechat": f"请为微信公众号写一篇关于{topic}的深度分析文章，要求专业权威，结构清晰，字数1500-3000字",
                    "xiaohongshu": f"请为小红书写一篇关于{topic}的生活分享内容，要求真实体验，有情感共鸣，字数300-1000字", 
                    "bilibili": f"请为B站写一份关于{topic}的视频脚本，要求知识科普，专业有趣，适合视频讲解",
                    "douyin": f"请为抖音写一份关于{topic}的短视频脚本，要求简短有力，情感共鸣，15-60秒时长"
                }
                
                prompt = platform_prompts.get(platform, f"请写一篇关于{topic}的{content_type}")
                
                # 打印标准模式请求详情
                try:
                    print("[API] Standard mode (qwen3) request:")
                    print(f"  - platform: {platform}")
                    print(f"  - topic: {topic}")
                    print(f"  - prompt: {prompt[:180]}{'...' if len(prompt)>180 else ''}")
                except Exception:
                    pass
                
                # 直接调用Qwen3模型（标准模式）
                loop = asyncio.get_event_loop()
                content = await loop.run_in_executor(
                    None,
                    self.generator._generate_with_model,
                    prompt,
                    "qwen3"
                )
                
                # 打印响应摘要
                try:
                    print("[API] Standard mode (qwen3) response:")
                    print(f"  - content_length: {len(content)}")
                except Exception:
                    pass
                
                return {
                    "content": content,
                    "model_used": "qwen3",
                    "quality_score": 85,
                    "generated_at": datetime.now().isoformat(),
                    "platform": platform,
                    "topic": topic,
                    "word_count": len(content)
                }
                
        except Exception as e:
            raise Exception(f"生成失败: {str(e)}")
    
    
    def on_generation_complete(self, results: Dict[str, Any]):
        """生成完成回调"""
        self.current_results = results
        self.display_results(results)
        self.generate_button.config(state="normal", text="🚀 开始生成内容")
        
        success_count = len([r for r in results.values() if 'error' not in r])
        total_count = len(results)
        
        # 计算总字数
        total_words = sum(r.get('word_count', 0) for r in results.values() if 'error' not in r)
        
        status_msg = f"✅ 生成完成 - {success_count}/{total_count} 个平台成功，共 {total_words:,} 字"
        self.status_var.set(status_msg)
        
        # 显示完成对话框，提供快速操作选项
        self.show_completion_dialog(success_count, total_count, total_words)
    
    def on_generation_error(self, error: str):
        """生成错误回调"""
        messagebox.showerror("生成失败", f"内容生成时发生错误：\n{error}")
        self.generate_button.config(state="normal", text="🚀 开始生成内容")
        self.status_var.set("❌ 生成失败")
        self.progress_var.set(0)
    
    def display_results(self, results: Dict[str, Any]):
        """显示生成结果"""
        # 清空现有标签页
        for tab in self.result_notebook.tabs():
            self.result_notebook.forget(tab)
        
        platform_names = {
            "wechat": "📰 微信公众号",
            "xiaohongshu": "📱 小红书",
            "bilibili": "🎬 B站",
            "douyin": "📺 抖音"
        }
        
        for platform, result in results.items():
            # 创建标签页框架
            tab_frame = ttk.Frame(self.result_notebook, style='Dark.TFrame')
            tab_name = platform_names.get(platform, platform)
            self.result_notebook.add(tab_frame, text=tab_name)
            
            # 配置网格
            tab_frame.columnconfigure(0, weight=1)
            tab_frame.rowconfigure(1, weight=1)
            
            # 信息栏
            info_frame = ttk.Frame(tab_frame, style='Dark.TFrame')
            info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=(10, 5))
            info_frame.columnconfigure(0, weight=1)
            
            if "error" in result:
                error_label = ttk.Label(
                    info_frame, 
                    text=f"❌ 生成失败: {result['error']}", 
                    style='Dark.TLabel'
                )
                error_label.grid(row=0, column=0, sticky=tk.W)
            else:
                info_text = f"✅ 模型: {result.get('model_used', 'unknown')} | "
                info_text += f"质量分: {result.get('quality_score', 0)} | "
                info_text += f"字数: {result.get('word_count', len(result.get('content', '')))} | "
                info_text += f"时间: {result.get('generated_at', '')[:16]}"
                
                info_label = ttk.Label(
                    info_frame, 
                    text=info_text, 
                    style='Dark.TLabel'
                )
                info_label.grid(row=0, column=0, sticky=tk.W)
                
                # 复制按钮
                copy_btn = ttk.Button(
                    info_frame, 
                    text="📋 复制", 
                    command=lambda r=result: self.copy_to_clipboard(r.get('content', '')),
                    style='Dark.TButton',
                    width=8
                )
                copy_btn.grid(row=0, column=1, sticky=tk.E)
            
            # 内容显示区域
            if "error" not in result:
                content_frame, content_text = self.create_scrolled_text_widget(tab_frame)
                content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
                
                content_text.insert(tk.END, result.get('content', ''))
                content_text.config(state=tk.DISABLED)
    
    def copy_to_clipboard(self, content: str):
        """复制到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.status_var.set("📋 内容已复制到剪贴板")
        
        # 3秒后恢复状态
        self.root.after(3000, lambda: self.status_var.set("准备就绪"))
    
    def save_results(self):
        """保存生成结果"""
        if not self.current_results:
            messagebox.showwarning("警告", "没有可保存的结果")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")],
            title="保存生成结果"
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.current_results, f, ensure_ascii=False, indent=2)
                else:
                    # 纯文本：仅输出可直接用于Web端的 Prompt
                    with open(filename, 'w', encoding='utf-8') as f:
                        platform_names = {
                            "wechat": "微信公众号",
                            "xiaohongshu": "小红书",
                            "bilibili": "B站", 
                            "douyin": "抖音"
                        }
                        for platform, result in self.current_results.items():
                            prompt = result.get('content', '')
                            name = platform_names.get(platform, platform)
                            f.write(f"## Direct Web Prompt ({name})\n\n")
                            f.write(prompt.strip() + '\n\n')
                
                self.status_var.set(f"💾 结果已保存到: {os.path.basename(filename)}")
                messagebox.showinfo("保存成功", f"结果已保存到:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("保存失败", f"保存文件时发生错误:\n{str(e)}")
    
    def clear_results(self):
        """清空结果"""
        for tab in self.result_notebook.tabs():
            self.result_notebook.forget(tab)
        self.current_results = {}
        self.status_var.set("🔄 结果已清空")
        self.progress_var.set(0)
    
    def reset_all(self):
        """完全重置GUI到初始状态"""
        try:
            # 1. 清空结果
            for tab in self.result_notebook.tabs():
                self.result_notebook.forget(tab)
            self.current_results = {}
            
            # 2. 重置输入字段
            self.topic_var.set("小米汽车市场竞争分析")  # 设置默认主题
            
            # 3. 重置平台选择（默认选中前两个）
            for i, (key, var) in enumerate(self.platform_vars.items()):
                var.set(True if i < 2 else False)
            
            # 4. 重置内容类型
            self.content_type_var.set("article")
            
            # 5. 重置高级选项
            self.anti_censorship_var.set(True)
            self.quality_var.set("high")
            
            # 6. 重置UI状态
            self.generate_button.config(state="normal", text="🚀 开始生成内容")
            self.progress_var.set(0)
            self.status_var.set("🆕 已重置，准备开始新的内容生成")
            
            # 7. 聚焦到主题输入框
            self.topic_entry.focus_set()
            self.topic_entry.select_range(0, tk.END)
            
            print("✅ GUI已重置到初始状态")
            
        except Exception as e:
            print(f"❌ 重置过程出错: {e}")
            messagebox.showerror("重置失败", f"重置过程中发生错误:\n{str(e)}")
    
    def show_completion_dialog(self, success_count, total_count, total_words):
        """显示生成完成对话框"""
        try:
            # 创建自定义对话框
            dialog = tk.Toplevel(self.root)
            dialog.title("生成完成")
            dialog.geometry("450x300")
            dialog.configure(bg=self.COLORS['bg'])
            dialog.resizable(False, False)
            
            # 设置对话框位置（居中）
            dialog.transient(self.root)
            dialog.grab_set()
            
            # 居中显示
            dialog.geometry("+{}+{}".format(
                self.root.winfo_rootx() + 50,
                self.root.winfo_rooty() + 50
            ))
            
            # 主框架
            main_frame = tk.Frame(dialog, bg=self.COLORS['bg'], padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 标题
            title_label = tk.Label(
                main_frame,
                text="🎉 内容生成完成！",
                bg=self.COLORS['bg'],
                fg=self.COLORS['fg'],
                font=('SF Pro Display', 16, 'bold') if sys.platform == "darwin" else ('Segoe UI', 16, 'bold')
            )
            title_label.pack(pady=(0, 15))
            
            # 统计信息
            stats_text = f"✅ 成功生成: {success_count}/{total_count} 个平台\n📝 总字数: {total_words:,} 字"
            stats_label = tk.Label(
                main_frame,
                text=stats_text,
                bg=self.COLORS['bg'],
                fg=self.COLORS['fg'],
                font=('SF Pro Display', 12) if sys.platform == "darwin" else ('Segoe UI', 12),
                justify=tk.LEFT
            )
            stats_label.pack(pady=(0, 20))
            
            # 操作选项框架
            actions_frame = tk.Frame(main_frame, bg=self.COLORS['bg'])
            actions_frame.pack(fill=tk.X, pady=(0, 15))
            
            # 快速操作按钮
            def save_and_continue():
                dialog.destroy()
                self.save_results()
                self.show_quick_topic_selector()
            
            def continue_new():
                dialog.destroy()
                self.show_quick_topic_selector()
            
            def just_close():
                dialog.destroy()
            
            # 按钮样式
            button_style = {
                'bg': self.COLORS['button_bg'],
                'fg': self.COLORS['button_fg'],
                'activebackground': self.COLORS['accent'],
                'activeforeground': '#ffffff',
                'relief': 'flat',
                'borderwidth': 1,
                'font': ('SF Pro Display', 11) if sys.platform == "darwin" else ('Segoe UI', 11),
                'cursor': 'hand2',
                'padx': 15,
                'pady': 8
            }
            
            # 第一行按钮
            row1 = tk.Frame(actions_frame, bg=self.COLORS['bg'])
            row1.pack(fill=tk.X, pady=(0, 10))
            
            save_btn = tk.Button(
                row1,
                text="💾 保存并继续生成",
                command=save_and_continue,
                **button_style,
                width=18
            )
            save_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            continue_btn = tk.Button(
                row1,
                text="🆕 继续生成新内容",
                command=continue_new,
                **button_style,
                width=18
            )
            continue_btn.pack(side=tk.LEFT)
            
            # 第二行按钮
            row2 = tk.Frame(actions_frame, bg=self.COLORS['bg'])
            row2.pack(fill=tk.X)
            
            close_btn = tk.Button(
                row2,
                text="✅ 完成",
                command=just_close,
                **button_style,
                width=10
            )
            close_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            reset_btn = tk.Button(
                row2,
                text="🔄 重置界面",
                command=lambda: (dialog.destroy(), self.reset_all()),
                **button_style,
                width=10
            )
            reset_btn.pack(side=tk.LEFT)
            
            # 提示信息
            tip_label = tk.Label(
                main_frame,
                text="💡 提示: 可以查看生成的内容，复制使用，或继续生成其他主题",
                bg=self.COLORS['bg'],
                fg=self.COLORS['warning'],
                font=('SF Pro Display', 10) if sys.platform == "darwin" else ('Segoe UI', 10),
                wraplength=400
            )
            tip_label.pack(pady=(15, 0))
            
            # 设置默认焦点
            continue_btn.focus_set()
            
            # 按ESC关闭
            dialog.bind('<Escape>', lambda e: dialog.destroy())
            
        except Exception as e:
            print(f"❌ 显示完成对话框失败: {e}")
    
    def show_quick_topic_selector(self):
        """显示快速主题选择器"""
        try:
            # 创建主题选择对话框
            selector = tk.Toplevel(self.root)
            selector.title("快速选择新主题")
            selector.geometry("500x400")
            selector.configure(bg=self.COLORS['bg'])
            selector.resizable(True, False)
            
            # 设置对话框位置（居中）
            selector.transient(self.root)
            selector.grab_set()
            
            # 居中显示
            selector.geometry("+{}+{}".format(
                self.root.winfo_rootx() + 25,
                self.root.winfo_rooty() + 25
            ))
            
            # 主框架
            main_frame = tk.Frame(selector, bg=self.COLORS['bg'], padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 标题
            title_label = tk.Label(
                main_frame,
                text="🎯 选择新的内容主题",
                bg=self.COLORS['bg'],
                fg=self.COLORS['fg'],
                font=('SF Pro Display', 14, 'bold') if sys.platform == "darwin" else ('Segoe UI', 14, 'bold')
            )
            title_label.pack(pady=(0, 15))
            
            # 热门主题列表
            topics_frame = tk.Frame(main_frame, bg=self.COLORS['bg'])
            topics_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            
            # 创建滚动区域
            canvas = tk.Canvas(topics_frame, bg=self.COLORS['bg'], highlightthickness=0)
            scrollbar = tk.Scrollbar(topics_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=self.COLORS['bg'])
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # 热门主题列表
            popular_topics = [
                "🚗 特斯拉2024年财报分析",
                "🤖 ChatGPT-5最新功能评测", 
                "📱 iPhone 16 Pro深度体验",
                "💰 2024年投资理财策略",
                "🏠 北京房价走势分析",
                "🎬 2024年春节档电影盘点",
                "💊 健康生活方式指南",
                "📚 高效学习方法总结",
                "🍕 网红美食探店攻略",
                "✈️ 2024年旅游目的地推荐",
                "👔 职场沟通技巧大全",
                "🎮 2024年游戏行业趋势",
                "📊 抖音运营实战经验",
                "🏋️ 居家健身计划制定",
                "🎨 AI绘画工具对比评测"
            ]
            
            def select_topic(topic):
                # 移除emoji，获取纯文本主题
                clean_topic = topic.split(' ', 1)[1] if ' ' in topic else topic
                self.topic_var.set(clean_topic)
                self.topic_entry.focus_set()
                self.topic_entry.select_range(0, tk.END)
                selector.destroy()
                self.status_var.set(f"🎯 已选择主题: {clean_topic}")
            
            # 按钮样式
            topic_button_style = {
                'bg': self.COLORS['select_bg'],
                'fg': self.COLORS['fg'],
                'activebackground': self.COLORS['accent'],
                'activeforeground': '#ffffff',
                'relief': 'flat',
                'borderwidth': 1,
                'font': ('SF Pro Display', 11) if sys.platform == "darwin" else ('Segoe UI', 11),
                'cursor': 'hand2',
                'anchor': 'w',
                'padx': 15,
                'pady': 8
            }
            
            # 添加主题按钮
            for i, topic in enumerate(popular_topics):
                btn = tk.Button(
                    scrollable_frame,
                    text=topic,
                    command=lambda t=topic: select_topic(t),
                    **topic_button_style
                )
                btn.pack(fill=tk.X, pady=2)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # 自定义输入框架
            custom_frame = tk.Frame(main_frame, bg=self.COLORS['bg'])
            custom_frame.pack(fill=tk.X, pady=(10, 15))
            
            custom_label = tk.Label(
                custom_frame,
                text="或输入自定义主题:",
                bg=self.COLORS['bg'],
                fg=self.COLORS['fg'],
                font=('SF Pro Display', 11) if sys.platform == "darwin" else ('Segoe UI', 11)
            )
            custom_label.pack(anchor=tk.W, pady=(0, 5))
            
            custom_var = tk.StringVar()
            custom_entry = tk.Entry(
                custom_frame,
                textvariable=custom_var,
                bg=self.COLORS['entry_bg'],
                fg=self.COLORS['entry_fg'],
                insertbackground=self.COLORS['fg'],
                font=('SF Pro Display', 11) if sys.platform == "darwin" else ('Segoe UI', 11),
                relief='solid',
                borderwidth=1
            )
            custom_entry.pack(fill=tk.X, pady=(0, 5))
            
            def use_custom():
                custom_topic = custom_var.get().strip()
                if custom_topic:
                    self.topic_var.set(custom_topic)
                    self.topic_entry.focus_set()
                    self.topic_entry.select_range(0, tk.END)
                    selector.destroy()
                    self.status_var.set(f"🎯 已设置自定义主题: {custom_topic}")
                else:
                    messagebox.showwarning("提示", "请输入主题内容")
            
            # 底部按钮
            bottom_frame = tk.Frame(main_frame, bg=self.COLORS['bg'])
            bottom_frame.pack(fill=tk.X)
            
            button_style = {
                'bg': self.COLORS['button_bg'],
                'fg': self.COLORS['button_fg'],
                'activebackground': self.COLORS['accent'],
                'activeforeground': '#ffffff',
                'relief': 'flat',
                'borderwidth': 1,
                'font': ('SF Pro Display', 11) if sys.platform == "darwin" else ('Segoe UI', 11),
                'cursor': 'hand2',
                'padx': 15,
                'pady': 8
            }
            
            use_btn = tk.Button(
                bottom_frame,
                text="✅ 使用自定义主题",
                command=use_custom,
                **button_style
            )
            use_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            cancel_btn = tk.Button(
                bottom_frame,
                text="❌ 取消",
                command=selector.destroy,
                **button_style
            )
            cancel_btn.pack(side=tk.LEFT)
            
            # 绑定回车键
            custom_entry.bind('<Return>', lambda e: use_custom())
            selector.bind('<Escape>', lambda e: selector.destroy())
            
            # 设置焦点
            custom_entry.focus_set()
            
        except Exception as e:
            print(f"❌ 显示主题选择器失败: {e}")
    
    def toggle_theme(self):
        """切换主题模式"""
        try:
            # 切换主题状态
            self.dark_mode = not self.dark_mode
            
            # 显示切换提示
            theme_name = "深色模式" if self.dark_mode else "浅色模式"
            self.status_var.set(f"🎨 正在切换到{theme_name}...")
            
            # 保存当前数据
            current_topic = self.topic_var.get()
            current_platforms = {k: v.get() for k, v in self.platform_vars.items()}
            current_type = self.content_type_var.get()
            current_anti_censorship = self.anti_censorship_var.get()
            current_quality = self.quality_var.get()
            current_results = self.current_results.copy()
            
            # 销毁当前窗口
            self.root.destroy()
            
            # 创建新的主题GUI
            new_app = ContentFactoryGUI(dark_mode=self.dark_mode)
            
            # 恢复数据
            new_app.topic_var.set(current_topic)
            for k, v in current_platforms.items():
                if k in new_app.platform_vars:
                    new_app.platform_vars[k].set(v)
            new_app.content_type_var.set(current_type)
            new_app.anti_censorship_var.set(current_anti_censorship)
            new_app.quality_var.set(current_quality)
            new_app.current_results = current_results
            
            # 如果有结果，重新显示
            if current_results:
                new_app.display_results(current_results)
            
            new_app.status_var.set(f"✅ 已切换到{theme_name}")
            
            # 启动新GUI
            new_app.run()
            
        except Exception as e:
            print(f"❌ 主题切换失败: {e}")
            messagebox.showerror("切换失败", f"主题切换时发生错误:\n{str(e)}")
    
    def run(self):
        """运行GUI"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n用户中断，退出程序")
        except Exception as e:
            print(f"GUI运行错误: {e}")


def main(dark_mode=None):
    """主函数"""
    if dark_mode is None:
        # 自动检测系统主题
        try:
            import subprocess
            import platform as pf
            if pf.system() == "Darwin":  # macOS
                result = subprocess.run([
                    'osascript', '-e', 
                    'tell application "System Events" to tell appearance preferences to get dark mode'
                ], capture_output=True, text=True, timeout=5)
                dark_mode = result.stdout.strip().lower() == 'true'
            else:
                dark_mode = True  # 默认深色模式
        except:
            dark_mode = True  # 默认深色模式
    
    theme_name = "深色模式" if dark_mode else "浅色模式"
    print(f"🚀 启动 FastMCP Content Factory GUI ({theme_name})...")
    
    try:
        app = ContentFactoryGUI(dark_mode=dark_mode)
        app.run()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        input("按回车键退出...")


if __name__ == "__main__":
    main()
