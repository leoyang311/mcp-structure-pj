#!/usr/bin/env python3
"""
Content Factory CLI - 命令行工具
"""
import asyncio
import json
import sys
import logging
from typing import List, Optional
from pathlib import Path

import sys
import logging
from pathlib import Path

# 添加src路径到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    from rich.json import JSON
except ImportError:
    print("请先安装依赖: python start.py install")
    sys.exit(1)

from content_factory import MasterController, Platform, TaskStatus

app = typer.Typer(help="FastMCP Multi-Agent Content Production System")
console = Console()

# 全局控制器实例
master_controller: Optional[MasterController] = None


def init_controller():
    """初始化Master控制器"""
    global master_controller
    if not master_controller:
        # 配置日志
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # 初始化控制器
        master_controller = MasterController(max_concurrent_tasks=3)
        
        # 启动处理器 (在后台运行)
        loop = asyncio.get_event_loop()
        if not loop.is_running():
            asyncio.run(master_controller.start_processing())


@app.command()
def create_task(
    topic: str = typer.Argument(..., help="内容话题"),
    platforms: str = typer.Option("wechat,xiaohongshu", help="目标平台，逗号分隔"),
    depth: str = typer.Option("medium", help="研究深度: shallow, medium, deep"),
    versions: int = typer.Option(3, help="每平台生成版本数"),
    video: bool = typer.Option(True, help="是否包含视频内容"),
    wait: bool = typer.Option(False, help="是否等待任务完成")
):
    """创建内容生产任务"""
    try:
        init_controller()
        
        # 解析平台列表
        platform_list = [p.strip() for p in platforms.split(",")]
        
        # 验证平台
        valid_platforms = [p.value for p in Platform]
        for platform in platform_list:
            if platform not in valid_platforms:
                console.print(f"[red]不支持的平台: {platform}[/red]")
                console.print(f"支持的平台: {', '.join(valid_platforms)}")
                return
        
        console.print(Panel(
            f"创建内容任务\n\n"
            f"话题: {topic}\n"
            f"平台: {', '.join(platform_list)}\n"
            f"研究深度: {depth}\n"
            f"版本数: {versions}\n"
            f"包含视频: {'是' if video else '否'}",
            title="[bold blue]任务创建[/bold blue]",
            border_style="blue"
        ))
        
        # 创建任务
        async def create_async():
            result = await master_controller.create_content_task(
                topic=topic,
                platforms=platform_list,
                research_depth=depth,
                versions_per_platform=versions,
                include_video=video
            )
            return result
        
        result = asyncio.run(create_async())
        
        console.print(f"[green]✓[/green] 任务创建成功!")
        console.print(f"任务ID: [bold]{result['task_id']}[/bold]")
        console.print(f"预估时间: [yellow]{result['estimated_time']}秒[/yellow]")
        console.print(f"队列位置: {result['queue_position']}")
        
        if wait:
            console.print("\n[yellow]等待任务完成...[/yellow]")
            wait_for_completion(result['task_id'])
        else:
            console.print(f"\n使用 'content-factory status {result['task_id']}' 查看进度")
            console.print(f"使用 'content-factory result {result['task_id']}' 获取结果")
        
    except Exception as e:
        console.print(f"[red]创建任务失败: {str(e)}[/red]")


@app.command() 
def status(
    task_id: str = typer.Argument(..., help="任务ID")
):
    """查看任务状态"""
    try:
        init_controller()
        
        async def get_status():
            return await master_controller.get_task_status(task_id)
        
        status_data = asyncio.run(get_status())
        
        # 创建状态表格
        table = Table(title=f"任务状态 - {task_id[:8]}...")
        table.add_column("项目", style="cyan")
        table.add_column("值", style="white")
        
        table.add_row("任务ID", task_id)
        table.add_row("状态", _format_status(status_data['status']))
        table.add_row("进度", f"{status_data['progress']}%")
        table.add_row("当前阶段", status_data['current_stage'])
        table.add_row("创建时间", status_data['created_at'])
        
        if status_data['started_at']:
            table.add_row("开始时间", status_data['started_at'])
        
        if status_data['completed_at']:
            table.add_row("完成时间", status_data['completed_at'])
        
        if status_data['execution_time']:
            table.add_row("执行时间", f"{status_data['execution_time']:.1f}秒")
        
        if status_data['error_message']:
            table.add_row("错误信息", f"[red]{status_data['error_message']}[/red]")
        
        console.print(table)
        
        # 显示阶段进度
        if status_data['stages']:
            console.print("\n[bold]阶段进度:[/bold]")
            for stage, stage_status in status_data['stages'].items():
                emoji = _get_stage_emoji(stage_status)
                console.print(f"  {emoji} {stage}: {stage_status}")
        
    except Exception as e:
        console.print(f"[red]获取状态失败: {str(e)}[/red]")


@app.command()
def result(
    task_id: str = typer.Argument(..., help="任务ID"),
    output_file: Optional[str] = typer.Option(None, help="输出文件路径")
):
    """获取任务结果"""
    try:
        init_controller()
        
        async def get_result():
            return await master_controller.get_task_result(task_id)
        
        result_data = asyncio.run(get_result())
        
        if output_file:
            # 保存到文件
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            console.print(f"[green]✓[/green] 结果已保存到: {output_path}")
        else:
            # 在控制台显示
            console.print(Panel(
                JSON(json.dumps(result_data, ensure_ascii=False, indent=2)),
                title=f"[bold blue]任务结果 - {task_id[:8]}...[/bold blue]",
                border_style="blue"
            ))
        
        # 显示结果摘要
        if result_data.get('best_version'):
            best = result_data['best_version']
            console.print(f"\n[green]最佳版本:[/green]")
            console.print(f"  平台: {best['platform']}")
            console.print(f"  标题: {best['title']}")
            console.print(f"  类型: {best['content_type']}")
            console.print(f"  字数: {len(best['content'])}字")
        
    except Exception as e:
        console.print(f"[red]获取结果失败: {str(e)}[/red]")


@app.command()
def list_tasks():
    """列出所有任务"""
    try:
        init_controller()
        
        async def get_system_status():
            return await master_controller.get_system_status()
        
        system_status = asyncio.run(get_system_status())
        
        # 显示系统状态
        console.print(Panel(
            f"系统状态: {'运行中' if system_status['is_running'] else '已停止'}\n"
            f"队列任务: {system_status['queue_size']}\n"
            f"运行任务: {system_status['running_tasks']}/{system_status['max_concurrent_tasks']}\n"
            f"系统时间: {system_status['system_time']}",
            title="[bold green]系统状态[/bold green]",
            border_style="green"
        ))
        
        # 显示任务统计
        stats = system_status['task_statistics']
        table = Table(title="任务统计")
        table.add_column("状态", style="cyan")
        table.add_column("数量", justify="right", style="white")
        
        for status, count in stats.items():
            if status != 'total':
                table.add_row(_format_status(status), str(count))
        table.add_row("[bold]总计[/bold]", f"[bold]{stats['total']}[/bold]")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]获取任务列表失败: {str(e)}[/red]")


@app.command()
def platforms():
    """显示支持的平台"""
    table = Table(title="支持的平台")
    table.add_column("平台", style="cyan")
    table.add_column("说明", style="white")
    
    platform_info = {
        Platform.WECHAT.value: "微信公众号 - 专业深度内容",
        Platform.XIAOHONGSHU.value: "小红书 - 轻松活泼内容",
        Platform.BILIBILI.value: "B站 - 教育向视频内容",
        Platform.DOUYIN.value: "抖音 - 娱乐向短视频"
    }
    
    for platform, description in platform_info.items():
        table.add_row(platform, description)
    
    console.print(table)


def wait_for_completion(task_id: str):
    """等待任务完成"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn()
        ) as progress:
            
            task_progress = progress.add_task("处理中...", total=None)
            
            while True:
                async def check_status():
                    return await master_controller.get_task_status(task_id)
                
                status_data = asyncio.run(check_status())
                
                # 更新进度描述
                progress.update(
                    task_progress,
                    description=f"阶段: {status_data['current_stage']} ({status_data['progress']}%)"
                )
                
                if status_data['status'] in ['completed', 'failed']:
                    break
                
                asyncio.sleep(2)
            
            if status_data['status'] == 'completed':
                console.print(f"[green]✓[/green] 任务完成!")
                console.print(f"执行时间: {status_data['execution_time']:.1f}秒")
            else:
                console.print(f"[red]✗[/red] 任务失败: {status_data['error_message']}")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]任务继续在后台运行[/yellow]")


def _format_status(status: str) -> str:
    """格式化状态显示"""
    status_colors = {
        'created': '[cyan]已创建[/cyan]',
        'queued': '[yellow]队列中[/yellow]',
        'processing': '[blue]处理中[/blue]',
        'completed': '[green]已完成[/green]',
        'failed': '[red]失败[/red]'
    }
    return status_colors.get(status, status)


def _get_stage_emoji(status: str) -> str:
    """获取阶段状态emoji"""
    emoji_map = {
        'pending': '⏳',
        'processing': '🔄',
        'completed': '✅',
        'failed': '❌',
        'skipped': '⏭️'
    }
    return emoji_map.get(status, '❓')


def main():
    """主入口函数"""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
    except Exception as e:
        console.print(f"[red]程序错误: {str(e)}[/red]")


if __name__ == "__main__":
    main()
