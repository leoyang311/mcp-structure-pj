#!/usr/bin/env python3
"""
FastMCP Content Factory 使用示例
演示如何使用多Agent内容生产系统
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

# 导入系统组件
from content_factory import (
    MasterController, 
    Platform, 
    TaskStatus,
    ContentTask,
    ResearchData,
    ContentVersion,
    QualityScore
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def example_basic_usage():
    """基础使用示例"""
    print("🚀 FastMCP Content Factory 基础使用示例")
    print("=" * 50)
    
    # 1. 创建Master控制器
    print("1. 初始化Master控制器...")
    master = MasterController(max_concurrent_tasks=2)
    
    # 2. 启动处理器
    print("2. 启动系统处理...")
    await master.start_processing()
    
    # 3. 创建内容任务
    print("3. 创建内容生产任务...")
    task_result = await master.create_content_task(
        topic="人工智能在教育领域的应用与前景",
        platforms=["wechat", "xiaohongshu"],
        research_depth="medium",
        versions_per_platform=2,
        include_video=True
    )
    
    task_id = task_result["task_id"]
    print(f"   ✅ 任务创建成功: {task_id[:8]}...")
    print(f"   📊 预估时间: {task_result['estimated_time']}秒")
    print(f"   📋 队列位置: {task_result['queue_position']}")
    
    # 4. 监控任务进度
    print("4. 监控任务进度...")
    while True:
        status = await master.get_task_status(task_id)
        print(f"   📈 进度: {status['progress']}% - {status['current_stage']}")
        
        if status['status'] in ['completed', 'failed']:
            break
        
        await asyncio.sleep(5)  # 等待5秒再检查
    
    # 5. 获取任务结果
    if status['status'] == 'completed':
        print("5. 获取任务结果...")
        result = await master.get_task_result(task_id)
        
        print(f"   ✅ 任务执行成功!")
        print(f"   ⏱️  执行时间: {result['execution_stats']['total_time']:.1f}秒")
        print(f"   📝 生成版本数: {len(result['all_versions'])}")
        
        # 显示最佳版本信息
        best = result['best_version']
        print(f"   🏆 最佳版本: {best['platform']} - {best['content_type']}")
        print(f"   📊 质量分数: {best['quality_score']:.2f}")
        print(f"   📖 标题: {best['title'][:50]}...")
        
        # 保存结果到文件
        output_file = f"example_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"   💾 结果已保存到: {output_file}")
    
    else:
        print(f"❌ 任务失败: {status['error_message']}")
    
    # 6. 停止处理器
    print("6. 停止系统处理...")
    await master.stop_processing()
    
    print("✨ 示例完成!")


async def example_advanced_usage():
    """高级使用示例"""
    print("\n🎯 FastMCP Content Factory 高级使用示例")
    print("=" * 50)
    
    master = MasterController(max_concurrent_tasks=3)
    await master.start_processing()
    
    # 1. 批量创建任务
    print("1. 批量创建多个任务...")
    topics = [
        "区块链技术在供应链管理中的创新应用",
        "可持续发展目标下的绿色能源转型",
        "元宇宙时代的数字身份与隐私保护"
    ]
    
    task_ids = []
    for i, topic in enumerate(topics, 1):
        print(f"   创建任务 {i}: {topic[:30]}...")
        result = await master.create_content_task(
            topic=topic,
            platforms=["wechat", "xiaohongshu", "bilibili"],
            research_depth="deep" if i == 1 else "medium",
            versions_per_platform=3,
            include_video=True
        )
        task_ids.append(result["task_id"])
        print(f"   ✅ 任务ID: {result['task_id'][:8]}...")
    
    # 2. 系统状态监控
    print("2. 系统状态监控...")
    system_status = await master.get_system_status()
    print(f"   📊 队列任务: {system_status['queue_size']}")
    print(f"   🏃 运行任务: {system_status['running_tasks']}/{system_status['max_concurrent_tasks']}")
    print(f"   📈 任务统计: {system_status['task_statistics']}")
    
    # 3. 等待所有任务完成
    print("3. 等待所有任务完成...")
    completed_tasks = []
    
    while len(completed_tasks) < len(task_ids):
        for task_id in task_ids:
            if task_id not in completed_tasks:
                status = await master.get_task_status(task_id)
                if status['status'] in ['completed', 'failed']:
                    completed_tasks.append(task_id)
                    print(f"   ✅ 任务完成: {task_id[:8]}... ({status['status']})")
                else:
                    print(f"   🔄 任务进行中: {task_id[:8]}... ({status['progress']}%)")
        
        if len(completed_tasks) < len(task_ids):
            await asyncio.sleep(10)
    
    # 4. 结果分析
    print("4. 结果分析...")
    all_results = []
    total_versions = 0
    
    for task_id in task_ids:
        try:
            result = await master.get_task_result(task_id)
            all_results.append(result)
            total_versions += len(result.get('all_versions', []))
        except Exception as e:
            print(f"   ❌ 获取结果失败 {task_id[:8]}...: {str(e)}")
    
    print(f"   📊 总共生成版本: {total_versions}")
    print(f"   ✅ 成功任务: {len(all_results)}")
    
    # 5. 找出最佳内容
    best_contents = []
    for result in all_results:
        if result.get('best_version'):
            best_contents.append({
                'task_id': result.get('task_id', 'unknown'),
                'topic': result.get('topic', 'unknown'),
                'best_version': result['best_version']
            })
    
    # 按质量分数排序
    best_contents.sort(key=lambda x: x['best_version']['quality_score'], reverse=True)
    
    print("\n🏆 质量排行榜:")
    for i, content in enumerate(best_contents[:3], 1):
        best = content['best_version']
        print(f"   {i}. {best['platform']} - 分数: {best['quality_score']:.2f}")
        print(f"      主题: {content['topic'][:40]}...")
        print(f"      标题: {best['title'][:40]}...")
        print()
    
    await master.stop_processing()
    print("✨ 高级示例完成!")


async def example_platform_specific():
    """平台特定内容示例"""
    print("\n📱 平台特定内容生产示例")
    print("=" * 50)
    
    master = MasterController(max_concurrent_tasks=4)
    await master.start_processing()
    
    # 不同平台的内容配置
    platform_configs = [
        {
            "platforms": ["wechat"],
            "topic": "深度学习算法原理与实践应用",
            "depth": "deep",
            "versions": 1
        },
        {
            "platforms": ["xiaohongshu"],
            "topic": "AI绘画工具使用技巧分享",
            "depth": "shallow",
            "versions": 3
        },
        {
            "platforms": ["bilibili"],
            "topic": "Python机器学习入门教程",
            "depth": "medium",
            "versions": 1
        },
        {
            "platforms": ["douyin"],
            "topic": "ChatGPT趣味玩法大揭秘",
            "depth": "shallow",
            "versions": 2
        }
    ]
    
    results = {}
    
    # 为每个平台创建专门的任务
    for i, config in enumerate(platform_configs, 1):
        platform = config["platforms"][0]
        print(f"{i}. 为{platform}创建专门内容...")
        
        result = await master.create_content_task(
            topic=config["topic"],
            platforms=config["platforms"],
            research_depth=config["depth"],
            versions_per_platform=config["versions"],
            include_video=(platform in ["bilibili", "douyin"])
        )
        
        task_id = result["task_id"]
        
        # 等待任务完成
        while True:
            status = await master.get_task_status(task_id)
            if status['status'] in ['completed', 'failed']:
                break
            await asyncio.sleep(3)
        
        if status['status'] == 'completed':
            task_result = await master.get_task_result(task_id)
            results[platform] = task_result
            print(f"   ✅ {platform}内容生成完成")
        else:
            print(f"   ❌ {platform}内容生成失败")
    
    # 展示不同平台的内容特点
    print("\n📊 各平台内容特点分析:")
    for platform, result in results.items():
        if result.get('best_version'):
            best = result['best_version']
            print(f"\n{platform.upper()}:")
            print(f"  内容类型: {best['content_type']}")
            print(f"  标题风格: {best['title'][:50]}...")
            print(f"  内容长度: {len(best['content'])}字")
            print(f"  质量分数: {best['quality_score']:.2f}")
    
    await master.stop_processing()
    print("\n✨ 平台特定内容示例完成!")


async def run_all_examples():
    """运行所有示例"""
    print("🎉 FastMCP Content Factory 完整示例演示")
    print("=" * 60)
    
    try:
        # 基础示例
        await example_basic_usage()
        
        # 高级示例
        await example_advanced_usage()
        
        # 平台特定示例
        await example_platform_specific()
        
        print("\n🎊 所有示例运行完成!")
        print("💡 更多用法请参考CLI工具和API文档")
        
    except Exception as e:
        logger.error(f"示例运行出错: {str(e)}")
        print(f"❌ 示例运行失败: {str(e)}")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(run_all_examples())
