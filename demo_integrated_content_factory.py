#!/usr/bin/env python3
"""
图片生成功能快速演示
展示如何将图片生成集成到现有的内容工厂流程中
"""
import asyncio
import json
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.content_factory.agents.image_agent import (
    create_image_agent,
    quick_image_generation,
    multi_platform_generation
)


class ContentFactoryWithImages:
    """
    集成图片生成功能的内容工厂演示类
    """
    
    def __init__(self):
        self.image_agent = create_image_agent()
        print("✅ 图片生成Agent初始化完成")
    
    async def produce_complete_content(self, topic: str, platforms: list = None):
        """
        生产完整的内容包（文案+图片）
        
        Args:
            topic: 内容主题
            platforms: 目标平台列表
        """
        if platforms is None:
            platforms = ["xiaohongshu", "wechat"]
        
        print(f"\n🎯 开始为主题「{topic}」生产内容...")
        
        # 1. 模拟文案生成（这里用预设文案代替）
        content = self._generate_mock_content(topic)
        print(f"📝 文案生成完成 ({len(content)} 字符)")
        
        # 2. 为每个平台生成图片
        results = {}
        for platform in platforms:
            print(f"\n📱 为 {platform} 平台生成图片...")
            
            image_result = await self.image_agent.execute({
                "text": content,
                "platform": platform,
                "num_images": 2 if platform == "xiaohongshu" else 1,
                "use_cache": True
            })
            
            results[platform] = {
                "content": content,
                "images": image_result
            }
            
            if image_result['success']:
                print(f"  ✅ 成功生成 {image_result['num_generated']} 张图片")
            else:
                print(f"  ❌ 生成失败: {image_result['error']}")
        
        return results
    
    def _generate_mock_content(self, topic: str) -> str:
        """生成模拟文案内容"""
        content_templates = {
            "时间管理": """
⏰ 高效时间管理秘籍分享！

作为一个每天都在和时间赛跑的打工人，我终于找到了让效率翻倍的方法！今天必须和大家分享这个超实用的时间管理技巧 ✨

🍅 番茄工作法真的yyds：
• 25分钟专注工作，绝不分心
• 5分钟短休息，放松大脑
• 每4个番茄钟休息15-30分钟

实践了一个月，工作效率提升了至少50%！再也不用加班到深夜了 🎉

💡 小贴士：
- 选择一个安静的环境
- 准备一杯咖啡或茶
- 手机调成勿扰模式
- 列出当天要完成的任务

#时间管理 #效率提升 #职场技巧 #番茄工作法
            """,
            
            "咖啡探店": """
☕ 发现宝藏咖啡店！治愈系下午茶时光 ✨

今天偶然路过这家超有氛围感的小咖啡店，瞬间就被温暖的灯光和咖啡香气征服了 🥰

📍 店铺信息：
• 地址：市中心文艺街区
• 营业时间：9:00-22:00
• 人均消费：35-50元

🎯 必点推荐：
• 招牌拿铁 ★★★★★
  奶泡绵密，咖啡香浓，拉花超美
• 提拉米苏 ★★★★☆
  入口即化，甜度刚好
• 手冲单品 ★★★★★
  酸甜平衡，回味悠长

环境真的太舒服了！木质装修配上暖色灯光，还有慵懒的小猫咪，简直是都市中的世外桃源 🌸

#咖啡探店 #下午茶时光 #治愈系 #城市漫步
            """,
            
            "护肤分享": """
✨ 换季护肤心得分享！告别敏感肌困扰

最近天气变化大，皮肤又开始闹脾气了 😭 作为一个资深敏感肌，今天来分享我的护肤心得～

🌿 我的护肤步骤：
1️⃣ 温和洁面（氨基酸洁面乳）
2️⃣ 舒缓爽肤水（无酒精配方）
3️⃣ 保湿精华（玻尿酸成分）
4️⃣ 面霜锁水（含神经酰胺）
5️⃣ 防晒隔离（SPF30+）

💡 敏感肌小贴士：
• 新产品一定要先试用
• 换季时减少刺激性成分
• 多喝水，保持作息规律
• 选择温和无添加的产品

坚持这个routine一个月，皮肤状态稳定了很多！希望对同样是敏感肌的姐妹有帮助 💕

#护肤心得 #敏感肌 #换季护肤 #美容分享
            """
        }
        
        return content_templates.get(topic, f"关于{topic}的精彩内容分享...")
    
    async def batch_production_demo(self):
        """批量生产演示"""
        print("\n" + "="*60)
        print("🚀 批量内容生产演示")
        print("="*60)
        
        topics = ["时间管理", "咖啡探店", "护肤分享"]
        platforms = ["xiaohongshu", "wechat"]
        
        all_results = {}
        
        for topic in topics:
            results = await self.produce_complete_content(topic, platforms)
            all_results[topic] = results
            
            # 显示结果摘要
            print(f"\n📊 {topic} 内容包生产完成:")
            for platform, result in results.items():
                success = result['images']['success']
                count = result['images'].get('num_generated', 0) if success else 0
                print(f"  {platform}: {'✅' if success else '❌'} {count}张图片")
        
        return all_results
    
    def export_results(self, results: dict, filename: str = None):
        """导出结果到文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"content_production_results_{timestamp}.json"
        
        # 清理结果数据（移除不可序列化的部分）
        clean_results = {}
        for topic, topic_results in results.items():
            clean_results[topic] = {}
            for platform, platform_result in topic_results.items():
                clean_results[topic][platform] = {
                    "content_length": len(platform_result['content']),
                    "image_success": platform_result['images']['success'],
                    "image_count": platform_result['images'].get('num_generated', 0),
                    "image_urls": [img['url'] for img in platform_result['images'].get('images', [])],
                    "platform_config": platform_result['images'].get('platform_description', platform)
                }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(clean_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到: {filename}")


async def main():
    """主演示函数"""
    print("🎨 内容工厂图片生成功能演示")
    print("=" * 50)
    print("📋 演示内容:")
    print("  1. 单个内容包生产（文案+图片）")
    print("  2. 批量内容生产")
    print("  3. 结果导出")
    print("=" * 50)
    
    try:
        # 1. 初始化内容工厂
        factory = ContentFactoryWithImages()
        
        # 2. 单个内容包演示
        print("\n🎯 单个内容包生产演示")
        single_result = await factory.produce_complete_content(
            topic="时间管理",
            platforms=["xiaohongshu", "wechat", "douyin"]
        )
        
        # 3. 批量生产演示
        batch_results = await factory.batch_production_demo()
        
        # 4. 导出结果
        print("\n💾 导出结果...")
        factory.export_results(batch_results)
        
        # 5. 显示最终统计
        print("\n" + "="*60)
        print("📈 最终统计")
        print("="*60)
        
        total_topics = len(batch_results)
        total_platforms = sum(len(topic_results) for topic_results in batch_results.values())
        total_images = sum(
            platform_result['images'].get('num_generated', 0)
            for topic_results in batch_results.values()
            for platform_result in topic_results.values()
        )
        
        print(f"📝 处理主题数: {total_topics}")
        print(f"📱 目标平台次数: {total_platforms}")
        print(f"🖼️  生成图片总数: {total_images}")
        print(f"✅ 演示完成!")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
