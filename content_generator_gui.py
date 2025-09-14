#!/usr/bin/env python3
"""
FastMCP Content Factory GUI
简单可靠的图形界面，支持多平台内容生成
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
    print(f"Warning: Content Factory modules not found. Using mock mode. Error: {e}")


class ContentGeneratorGUI:
    """内容生成器GUI主类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FastMCP Content Factory - 内容生成器")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 初始化生成器
        self.generator = None
        self.init_generator()
        
        # 创建界面
        self.create_widgets()
        
        # 结果存储
        self.current_results = {}
        
        print("✅ GUI初始化完成")
    
    def init_generator(self):
        """初始化内容生成器"""
        try:
            if HAS_CONTENT_FACTORY:
                self.generator = AntiCensorshipContentGenerator()
                print("✅ AntiCensorshipContentGenerator初始化成功")
            else:
                self.generator = None
                print("⚠️  使用模拟模式")
        except Exception as e:
            print(f"❌ 生成器初始化失败: {e}")
            self.generator = None
    
    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 1. 主题输入区
        ttk.Label(main_frame, text="📝 内容主题:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.topic_var = tk.StringVar(value="小米汽车市场竞争分析")
        self.topic_entry = ttk.Entry(main_frame, textvariable=self.topic_var, font=("Arial", 11))
        self.topic_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 2. 平台选择区
        ttk.Label(main_frame, text="🎯 目标平台:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky=(tk.W, tk.N), pady=(10, 5)
        )
        
        platform_frame = ttk.Frame(main_frame)
        platform_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # 平台复选框
        self.platform_vars = {}
        platforms = [
            ("微信公众号", "wechat", "深度分析，专业权威"),
            ("小红书", "xiaohongshu", "生活分享，真实体验"),
            ("B站", "bilibili", "知识科普，专业有趣"),
            ("抖音", "douyin", "短视频，情感共鸣")
        ]
        
        for i, (name, key, desc) in enumerate(platforms):
            var = tk.BooleanVar(value=True if i < 2 else False)  # 默认选中前两个
            self.platform_vars[key] = var
            
            cb = ttk.Checkbutton(platform_frame, text=f"{name} ({desc})", variable=var)
            cb.grid(row=i, column=0, sticky=tk.W, pady=2)
        
        # 3. 内容类型选择
        ttk.Label(main_frame, text="📄 内容类型:", font=("Arial", 12, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(10, 5)
        )
        
        type_frame = ttk.Frame(main_frame)
        type_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(10, 5))
        
        self.content_type_var = tk.StringVar(value="article")
        content_types = [
            ("📰 文章", "article"),
            ("🎬 视频脚本", "video_script"),
            ("🖼️ 图文混排", "mixed_content")
        ]
        
        for i, (name, value) in enumerate(content_types):
            ttk.Radiobutton(type_frame, text=name, variable=self.content_type_var, value=value).grid(
                row=0, column=i, sticky=tk.W, padx=(0, 20)
            )
        
        # 4. 高级选项
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ 高级选项", padding="5")
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        options_frame.columnconfigure(1, weight=1)
        
        # 反审查模式
        self.anti_censorship_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="🛡️ 反审查模式 (智能模型切换)", 
                       variable=self.anti_censorship_var).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        # 质量模式
        ttk.Label(options_frame, text="质量模式:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.quality_var = tk.StringVar(value="high")
        quality_combo = ttk.Combobox(options_frame, textvariable=self.quality_var, 
                                   values=["standard", "high", "premium"], state="readonly", width=15)
        quality_combo.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))

        # 视频引擎（用于视频脚本提示词生成）
        ttk.Label(options_frame, text="视频引擎:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.video_engine_var = tk.StringVar(value="minimax")
        video_engine_combo = ttk.Combobox(options_frame, textvariable=self.video_engine_var,
                                          values=["minimax", "sora"], state="readonly", width=15)
        video_engine_combo.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))

        # 单次生成时长（用于引擎受限，如sora单次10秒）
        ttk.Label(options_frame, text="单次时长(秒):").grid(row=2, column=2, sticky=tk.W, pady=(5, 0), padx=(15,0))
        self.single_clip_var = tk.IntVar(value=10)
        single_entry = ttk.Entry(options_frame, textvariable=self.single_clip_var, width=8)
        single_entry.grid(row=2, column=3, sticky=tk.W, pady=(5, 0))

        # 总时长（用于sora分段，或作为目标时长）
        ttk.Label(options_frame, text="总时长(秒):").grid(row=2, column=4, sticky=tk.W, pady=(5, 0), padx=(15,0))
        self.total_duration_var = tk.IntVar(value=60)
        total_entry = ttk.Entry(options_frame, textvariable=self.total_duration_var, width=8)
        total_entry.grid(row=2, column=5, sticky=tk.W, pady=(5, 0))

        # SAT 话题池随机
        self.use_sat_topic_pool_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="🎯 使用SAT随机话题池（视频脚本）",
                        variable=self.use_sat_topic_pool_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5,0))
        
        # 5. 生成按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        self.generate_button = ttk.Button(button_frame, text="🚀 开始生成内容", 
                                        command=self.start_generation, style="Accent.TButton")
        self.generate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="💾 保存结果", 
                  command=self.save_results).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔄 清空", 
                  command=self.clear_results).pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(button_frame, variable=self.progress_var, 
                                          mode="determinate", length=200)
        self.progress_bar.pack(side=tk.RIGHT)
        
        # 6. 结果显示区
        result_frame = ttk.LabelFrame(main_frame, text="📋 生成结果", padding="5")
        result_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(1, weight=1)
        
        # 平台标签选择
        self.result_notebook = ttk.Notebook(result_frame)
        self.result_notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
    
    def start_generation(self):
        """开始内容生成"""
        # 验证输入
        topic = self.topic_var.get().strip()
        if not topic:
            messagebox.showerror("错误", "请输入内容主题")
            return
        
        selected_platforms = [k for k, v in self.platform_vars.items() if v.get()]
        if not selected_platforms:
            messagebox.showerror("错误", "请至少选择一个平台")
            return
        
        # 如果启用SAT随机话题池且为视频脚本，覆盖主题
        try:
            if self.content_type_var.get() == "video_script" and self.use_sat_topic_pool_var.get():
                sat_topics = self._get_sat_topic_pool()
                topic = random.choice(sat_topics)
                self.topic_var.set(topic)
                print(f"[GUI] 使用SAT随机话题: {topic}")
        except Exception:
            pass

        # 后端终端打印关键信息
        try:
            selected_flags = {
                "anti_censorship": bool(self.anti_censorship_var.get()),
                "content_type": self.content_type_var.get()
            }
            print("[GUI] Start generation:")
            print(f"  - topic: {topic}")
            print(f"  - platforms: {selected_platforms}")
            print(f"  - options: {selected_flags}")
            print(f"  - generator: {'REAL' if (self.generator and HAS_CONTENT_FACTORY) else 'MOCK/NONE'}")
        except Exception as _:
            pass

        # 禁用生成按钮
        self.generate_button.config(state="disabled")
        self.status_var.set("正在生成内容...")
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
                self.root.after(0, lambda: self.progress_var.set((i / total_platforms) * 100))
                self.root.after(0, lambda p=platform: self.status_var.set(f"正在为{p}生成内容..."))
                
                if self.generator and HAS_CONTENT_FACTORY:
                    # 使用真实生成器
                    result = await self.generate_real_content(topic, platform)
                else:
                    # 禁止使用模拟内容，返回错误
                    raise RuntimeError("生成器未初始化或模块不可用，无法调用真实API")
                
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
                # 构造最小研究数据（WriterAgent内部仍会做深度研究增强）
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
                # 引擎有效总时长
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
                        result = await writer.process(input_payload)
                        versions = result.get("content_versions", [])
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
                    result = await writer.process(input_payload)
                    versions = result.get("content_versions", [])
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
                    "topic": topic
                }

            # 使用反审查生成器
            if self.anti_censorship_var.get():
                # 构建prompt
                content_type = self.content_type_var.get()
                prompt = f"请为{platform}平台写一篇关于{topic}的{content_type}"
                
                # 终端打印API调用详情
                try:
                    print("[API] AntiCensorshipContentGenerator.generate_content request:")
                    print(f"  - platform: {platform}")
                    print(f"  - topic: {topic}")
                    print(f"  - expected_length: 2000")
                    print(f"  - prompt: {prompt[:180]}{'...' if len(prompt)>180 else ''}")
                except Exception:
                    pass

                # AntiCensorshipContentGenerator.generate_content 为同步方法
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self.generator.generate_content,
                    prompt,
                    topic,
                    2000,
                )
                
                # 打印结果摘要
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
                    "topic": topic
                }
            else:
                # 标准模式：直接调用Qwen3（不走反审查）
                try:
                    print("[API] Standard mode (qwen3) request:")
                    print(f"  - platform: {platform}")
                    print(f"  - topic: {topic}")
                    print(f"  - prompt: 请为{platform}平台写一篇关于{topic}的{self.content_type_var.get()}")
                except Exception:
                    pass

                loop = asyncio.get_event_loop()
                content = await loop.run_in_executor(
                    None,
                    self.generator._generate_with_model,
                    f"请为{platform}平台写一篇关于{topic}的{self.content_type_var.get()}",
                    "qwen3",
                )

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
                    "topic": topic
                }
                
        except Exception as e:
            raise Exception(f"生成失败: {str(e)}")
    
    def generate_mock_content(self, topic: str, platform: str) -> Dict[str, Any]:
        """生成模拟内容（当真实系统不可用时）"""
        platform_styles = {
            "wechat": f"""# {topic} - 深度分析报告

## 市场现状分析
根据最新数据显示，{topic}在当前市场中占据重要地位...

## 核心竞争优势
1. 技术创新能力
2. 市场响应速度  
3. 用户体验优化

## 发展趋势预测
预计未来3-5年，{topic}将呈现以下发展趋势：
- 市场规模持续扩大
- 技术迭代加速
- 用户需求多样化

## 结论与建议
基于以上分析，我们建议...""",

            "xiaohongshu": f"""✨ {topic}超全攻略来啦！

姐妹们，今天给大家分享{topic}的全面解析！

🔥 核心要点：
• 要点一：关键信息
• 要点二：实用建议  
• 要点三：注意事项

💡 小贴士：
记得收藏起来慢慢看哦～

#内容创作 #{topic} #干货分享""",

            "bilibili": f"""【{topic}】详细解析 - 你想知道的都在这里！

大家好，我是UP主。今天给大家带来{topic}的全面介绍。

🎯 本期内容：
00:00 开场介绍
02:00 核心概念解析
05:00 实际案例分析
08:00 总结与建议

如果这期视频对你有帮助，别忘了三连支持！""",

            "douyin": f"""🔥 {topic}的秘密，99%的人不知道！

开场（0-3秒）：
你知道{topic}吗？今天给你揭秘！

核心内容（3-30秒）：
重点1：关键信息
重点2：实用技巧
重点3：注意事项

结尾（30秒）：
关注我，带你了解更多秘密！"""
        }
        
        return {
            "content": platform_styles.get(platform, f"为{platform}生成的{topic}相关内容"),
            "model_used": "mock",
            "quality_score": 88,
            "generated_at": datetime.now().isoformat(),
            "platform": platform,
            "topic": topic,
            "word_count": len(platform_styles.get(platform, "")),
            "note": "这是演示内容，实际使用时会调用真实的AI生成器"
        }
    
    def on_generation_complete(self, results: Dict[str, Any]):
        """生成完成回调"""
        self.current_results = results
        self.display_results(results)
        self.generate_button.config(state="normal")
        self.status_var.set(f"生成完成 - 共生成 {len(results)} 个平台内容")
    
    def on_generation_error(self, error: str):
        """生成错误回调"""
        messagebox.showerror("生成失败", f"内容生成时发生错误：\n{error}")
        self.generate_button.config(state="normal")
        self.status_var.set("生成失败")
        self.progress_var.set(0)
    
    def display_results(self, results: Dict[str, Any]):
        """显示生成结果"""
        # 清空现有标签页
        for tab in self.result_notebook.tabs():
            self.result_notebook.forget(tab)
        
        platform_names = {
            "wechat": "微信公众号",
            "xiaohongshu": "小红书", 
            "bilibili": "B站",
            "douyin": "抖音"
        }
        
        for platform, result in results.items():
            # 创建标签页
            frame = ttk.Frame(self.result_notebook)
            self.result_notebook.add(frame, text=platform_names.get(platform, platform))
            
            # 配置网格
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(1, weight=1)
            
            # 信息栏
            info_frame = ttk.Frame(frame)
            info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
            
            if "error" in result:
                ttk.Label(info_frame, text=f"❌ 生成失败: {result['error']}", 
                         foreground="red").pack(side=tk.LEFT)
            else:
                info_text = f"✅ 模型: {result.get('model_used', 'unknown')} | "
                info_text += f"质量分: {result.get('quality_score', 0)} | "
                info_text += f"字数: {result.get('word_count', len(result.get('content', '')))} | "
                info_text += f"时间: {result.get('generated_at', '')[:16]}"
                
                ttk.Label(info_frame, text=info_text, font=("Arial", 9)).pack(side=tk.LEFT)
                
                # 复制按钮
                ttk.Button(info_frame, text="📋 复制", 
                          command=lambda r=result: self.copy_to_clipboard(r.get('content', ''))).pack(side=tk.RIGHT)
            
            # 内容显示
            content_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Arial", 10))
            content_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            if "error" not in result:
                content_text.insert(tk.END, result.get('content', ''))
                content_text.config(state=tk.DISABLED)
    
    def copy_to_clipboard(self, content: str):
        """复制到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.status_var.set("内容已复制到剪贴板")
    
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
                    # 纯文本：仅输出可直接用于Web端的 Prompt，减少杂项
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
                
                self.status_var.set(f"结果已保存到: {filename}")
                messagebox.showinfo("成功", f"结果已保存到:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("保存失败", f"保存文件时发生错误:\n{str(e)}")
    
    def clear_results(self):
        """清空结果"""
        for tab in self.result_notebook.tabs():
            self.result_notebook.forget(tab)
        self.current_results = {}
        self.status_var.set("结果已清空")
        self.progress_var.set(0)
    
    def run(self):
        """运行GUI"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n用户中断，退出程序")
        except Exception as e:
            print(f"GUI运行错误: {e}")


def main():
    """主函数"""
    print("🚀 启动 FastMCP Content Factory GUI...")
    
    try:
        app = ContentGeneratorGUI()
        app.run()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        input("按回车键退出...")


if __name__ == "__main__":
    main()
