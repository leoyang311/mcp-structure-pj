#!/usr/bin/env python3
"""
反幻觉内容生产演示脚本
展示集成Deep Research反幻觉技术的内容生成能力
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.content_factory.core.master_controller import MasterController
from src.content_factory.models import Platform
from src.content_factory.utils.enhanced_prompts import get_anti_hallucination_base_prompt
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.markdown import Markdown

console = Console()

class AntiHallucinationDemo:
    """反幻觉演示类"""
    
    def __init__(self):
        self.controller = MasterController()
        self.demo_topics = [
            "2024年人工智能大模型发展现状与趋势",
            "可持续能源技术的最新突破",
            "量子计算在金融领域的应用前景",
            "生物技术在医疗诊断中的创新应用"
        ]
    
    def display_banner(self):
        """显示演示横幅"""
        banner = """
🛡️  FastMCP Content Factory - Anti-Hallucination Demo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

基于 Deep Research 反幻觉技术的智能内容生产系统
✅ 事实验证     ✅ 来源引用     ✅ 准确性保证     ✅ 透明推理
"""
        console.print(Panel(banner, style="bold blue", expand=False))
    
    def display_anti_hallucination_features(self):
        """显示反幻觉功能特性"""
        features_table = Table(title="🛡️ 反幻觉技术特性", show_header=True, header_style="bold magenta")
        features_table.add_column("功能", style="cyan", width=20)
        features_table.add_column("描述", style="white", width=50)
        features_table.add_column("状态", style="green", width=10)
        
        features = [
            ("迭代验证", "多层次查询和交叉验证确保信息准确性", "✅ 已启用"),
            ("源引用追踪", "强制引用具体来源，提供可验证链接", "✅ 已启用"),
            ("事实检查", "通过多次搜索交叉验证重要声明", "✅ 已启用"),
            ("具体化要求", "要求具体的实体、数据、时间等信息", "✅ 已启用"),
            ("推理透明度", "提供清晰的推理路径和置信度", "✅ 已启用"),
            ("不确定性标记", "明确标识不确定或需验证的信息", "✅ 已启用"),
            ("置信度评估", "为每个声明提供置信度等级", "✅ 已启用")
        ]
        
        for feature in features:
            features_table.add_row(*feature)
        
        console.print(features_table)
        console.print()
    
    async def demonstrate_topic_selection(self):
        """演示话题选择"""
        console.print("📋 [bold]可用演示话题：[/bold]")
        for i, topic in enumerate(self.demo_topics, 1):
            console.print(f"  {i}. {topic}")
        
        console.print()
        while True:
            try:
                choice = console.input("请选择话题编号 (1-4) 或输入自定义话题: ")
                
                if choice.isdigit() and 1 <= int(choice) <= 4:
                    selected_topic = self.demo_topics[int(choice) - 1]
                    break
                elif choice.strip():
                    selected_topic = choice.strip()
                    break
                else:
                    console.print("[red]请输入有效选择[/red]")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]演示已取消[/yellow]")
                return None
        
        return selected_topic
    
    async def demonstrate_content_generation(self, topic: str):
        """演示反幻觉内容生成"""
        console.print(f"\n🎯 [bold]开始为话题生成反幻觉内容:[/bold] {topic}")
        console.print()
        
        platforms = [Platform.WECHAT, Platform.XIAOHONGSHU, Platform.BILIBILI, Platform.DOUYIN]
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # 研究阶段
            research_task = progress.add_task("🔍 执行深度研究和事实验证...", total=None)
            try:
                research_result = await self.controller.research_agent.process({
                    "topic": topic,
                    "depth": "deep",
                    "platforms": [p.value for p in platforms]
                })
                progress.update(research_task, description="✅ 研究完成")
            except Exception as e:
                progress.update(research_task, description=f"❌ 研究失败: {str(e)}")
                return {}
            
            # 内容生成阶段
            for platform in platforms:
                platform_task = progress.add_task(f"📝 生成{platform.value}平台验证内容...", total=None)
                
                try:
                    # 使用反幻觉功能生成内容
                    content_result = await self.controller.writer_agent.generate_verified_content_for_platform(
                        research_result["research_data"], 
                        platform
                    )
                    
                    # 评分
                    scoring_result = await self.controller.scorer_agent.process({
                        "content_versions": content_result,
                        "research_data": research_result["research_data"]
                    })
                    
                    results[platform] = {
                        "content": content_result[0] if content_result else None,
                        "score": scoring_result.get("quality_scores", {})
                    }
                    
                    progress.update(platform_task, description=f"✅ {platform.value}内容生成完成")
                    
                except Exception as e:
                    progress.update(platform_task, description=f"❌ {platform.value}生成失败: {str(e)}")
                    results[platform] = {"error": str(e)}
        
        return results
    
    def display_content_analysis(self, results: dict, topic: str):
        """显示内容分析结果"""
        console.print("\n📊 [bold]反幻觉内容分析报告[/bold]")
        console.print("=" * 60)
        
        analysis_table = Table(title="内容质量分析", show_header=True, header_style="bold magenta")
        analysis_table.add_column("平台", style="cyan", width=12)
        analysis_table.add_column("准确性评分", style="yellow", width=12)
        analysis_table.add_column("来源引用", style="green", width=12) 
        analysis_table.add_column("验证状态", style="blue", width=15)
        analysis_table.add_column("置信度", style="white", width=10)
        
        for platform, result in results.items():
            if "error" in result:
                analysis_table.add_row(
                    platform.value, 
                    "❌ 错误", 
                    "N/A", 
                    "生成失败", 
                    "0%"
                )
            else:
                content = result.get("content")
                if content:
                    # 分析内容特征
                    source_count = content.content.count("[Source:") if hasattr(content, 'content') else 0
                    verification_count = content.content.count("[VERIFIED]") if hasattr(content, 'content') else 0
                    confidence_indicators = content.content.count("CONFIDENCE") if hasattr(content, 'content') else 0
                    
                    analysis_table.add_row(
                        platform.value,
                        f"⭐ {content.score:.1f}/10" if hasattr(content, 'score') else "N/A",
                        f"📚 {source_count}个来源",
                        f"✅ {verification_count}个验证",
                        f"📊 {confidence_indicators}个指标"
                    )
        
        console.print(analysis_table)
        console.print()
    
    def display_content_sample(self, results: dict):
        """显示内容样本"""
        console.print("📄 [bold]内容样本展示[/bold]")
        console.print("-" * 60)
        
        for platform, result in results.items():
            if "error" not in result and result.get("content"):
                content = result["content"]
                console.print(f"\n🎯 [bold]{platform.value}平台内容样本:[/bold]")
                
                # 显示标题
                if hasattr(content, 'title'):
                    console.print(f"📌 [bold blue]标题:[/bold blue] {content.title}")
                
                # 显示内容预览（前300字符）
                if hasattr(content, 'content'):
                    preview = content.content[:300] + "..." if len(content.content) > 300 else content.content
                    console.print(Panel(
                        Markdown(preview), 
                        title=f"{platform.value} 内容预览",
                        border_style="green"
                    ))
                
                console.print()
    
    def save_results(self, results: dict, topic: str):
        """保存结果到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"anti_hallucination_demo_result_{timestamp}.json"
        
        # 序列化结果
        serialized_results = {}
        for platform, result in results.items():
            if "error" not in result and result.get("content"):
                content = result["content"]
                serialized_results[platform.value] = {
                    "title": getattr(content, 'title', ''),
                    "content": getattr(content, 'content', ''),
                    "score": getattr(content, 'score', 0.0),
                    "platform": platform.value,
                    "created_at": getattr(content, 'created_at', datetime.now()).isoformat()
                }
            else:
                serialized_results[platform.value] = result
        
        result_data = {
            "topic": topic,
            "timestamp": timestamp,
            "anti_hallucination_features": {
                "fact_checking": True,
                "source_citation": True,
                "verification_protocol": True,
                "confidence_indicators": True,
                "transparency_requirements": True
            },
            "results": serialized_results
        }
        
        # 确保results目录存在
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        console.print(f"✅ [green]结果已保存到:[/green] {filepath}")
        return filepath
    
    async def run_demo(self):
        """运行完整演示"""
        self.display_banner()
        console.print()
        
        self.display_anti_hallucination_features()
        
        # 显示反幻觉基础提示词
        console.print("🛡️ [bold]反幻觉基础提示词示例:[/bold]")
        base_prompt = get_anti_hallucination_base_prompt()
        console.print(Panel(
            base_prompt[:500] + "...", 
            title="Anti-Hallucination System Prompt", 
            border_style="blue"
        ))
        console.print()
        
        # 选择演示话题
        topic = await self.demonstrate_topic_selection()
        if not topic:
            return
        
        # 生成内容
        results = await self.demonstrate_content_generation(topic)
        
        if results:
            # 显示分析结果
            self.display_content_analysis(results, topic)
            
            # 显示内容样本
            self.display_content_sample(results)
            
            # 保存结果
            filepath = self.save_results(results, topic)
            
            console.print("\n🎉 [bold green]反幻觉内容生产演示完成！[/bold green]")
            console.print(f"📁 详细结果文件: {filepath}")
        else:
            console.print("\n❌ [red]演示未能生成内容，请检查配置[/red]")

async def main():
    """主函数"""
    try:
        demo = AntiHallucinationDemo()
        await demo.run_demo()
    except KeyboardInterrupt:
        console.print("\n[yellow]演示已被用户中断[/yellow]")
    except Exception as e:
        console.print(f"\n[red]演示出现错误: {str(e)}[/red]")

if __name__ == "__main__":
    asyncio.run(main())
