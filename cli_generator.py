#!/usr/bin/env python3
"""
FastMCP Content Factory - 命令行版本
快速生成多平台内容，无需GUI
"""
import asyncio
import sys
import os
from datetime import datetime
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.content_factory.core.anti_censorship_system import AntiCensorshipGenerator
    HAS_CONTENT_FACTORY = True
    print("✅ FastMCP Content Factory 已加载")
except ImportError:
    HAS_CONTENT_FACTORY = False
    print("⚠️  使用模拟模式")

class CLIGenerator:
    """命令行内容生成器"""
    
    def __init__(self):
        self.generator = None
        if HAS_CONTENT_FACTORY:
            try:
                self.generator = AntiCensorshipGenerator()
                print("✅ 反审查生成器初始化成功")
            except Exception as e:
                print(f"⚠️  生成器初始化失败，使用模拟模式: {e}")
    
    def get_platform_info(self):
        """获取平台信息"""
        return {
            "1": {"key": "wechat", "name": "微信公众号", "desc": "深度分析，专业权威，2000-5000字"},
            "2": {"key": "xiaohongshu", "name": "小红书", "desc": "生活分享，真实体验，500-1500字"},
            "3": {"key": "bilibili", "name": "B站", "desc": "知识科普，专业有趣，1000-2500字"},
            "4": {"key": "douyin", "name": "抖音", "desc": "短视频脚本，情感共鸣，200-500字"}
        }
    
    def display_menu(self):
        """显示主菜单"""
        print("\n" + "="*60)
        print("🚀 FastMCP Content Factory - 命令行版")
        print("="*60)
        print("📝 请选择目标平台（可多选，用逗号分隔）:")
        
        platforms = self.get_platform_info()
        for num, info in platforms.items():
            print(f"  {num}. {info['name']} - {info['desc']}")
        
        print(f"  5. 全部平台")
        print(f"  0. 退出")
        print("-"*60)
    
    def get_user_input(self):
        """获取用户输入"""
        try:
            # 选择平台
            self.display_menu()
            platform_choice = input("🎯 选择平台 (例: 1,2 或 5): ").strip()
            
            if platform_choice == "0":
                return None, None, None
            
            # 解析平台选择
            platforms_info = self.get_platform_info()
            selected_platforms = []
            
            if platform_choice == "5":
                # 选择全部平台
                selected_platforms = [info["key"] for info in platforms_info.values()]
            else:
                # 解析用户选择
                choices = [c.strip() for c in platform_choice.split(",")]
                for choice in choices:
                    if choice in platforms_info:
                        selected_platforms.append(platforms_info[choice]["key"])
            
            if not selected_platforms:
                print("❌ 请选择有效的平台!")
                return self.get_user_input()
            
            # 获取主题
            print("\n📝 内容主题:")
            topic = input("请输入主题 (例: 小米汽车市场竞争分析): ").strip()
            
            if not topic:
                print("❌ 请输入主题!")
                return self.get_user_input()
            
            # 选择模式
            print("\n⚙️ 生成模式:")
            print("1. 标准模式")
            print("2. 反审查模式 (推荐，处理敏感话题)")
            mode_choice = input("选择模式 (1-2, 默认2): ").strip() or "2"
            
            anti_censorship = mode_choice == "2"
            
            # 显示选择的平台
            platform_names = [platforms_info[k]["name"] for k, v in platforms_info.items() 
                             if v["key"] in selected_platforms]
            print(f"\n✅ 将为以下平台生成内容: {', '.join(platform_names)}")
            print(f"✅ 主题: {topic}")
            print(f"✅ 模式: {'反审查模式' if anti_censorship else '标准模式'}")
            
            confirm = input("\n确认开始生成? (Y/n): ").strip().lower()
            if confirm in ['n', 'no']:
                return self.get_user_input()
            
            return topic, selected_platforms, anti_censorship
            
        except KeyboardInterrupt:
            print("\n\n👋 用户取消，退出程序")
            return None, None, None
    
    async def generate_content_async(self, topic, platforms, anti_censorship=True):
        """异步生成内容"""
        results = {}
        total = len(platforms)
        
        platform_names = {
            "wechat": "微信公众号",
            "xiaohongshu": "小红书",
            "bilibili": "B站", 
            "douyin": "抖音"
        }
        
        print(f"\n🔄 开始生成内容...")
        print("-"*60)
        
        for i, platform in enumerate(platforms, 1):
            platform_name = platform_names.get(platform, platform)
            print(f"[{i}/{total}] 正在为 {platform_name} 生成内容...")
            
            try:
                if self.generator and HAS_CONTENT_FACTORY and anti_censorship:
                    # 使用真实的反审查生成器
                    result = await self.generator.generate_with_fallback(
                        prompt=f"请为{platform}平台写一篇关于{topic}的专业文章",
                        topic=topic,
                        platform=platform
                    )
                    
                    content_result = {
                        "content": result.get("final_content", ""),
                        "model_used": result.get("model_used", "unknown"),
                        "quality_score": result.get("quality_score", 0),
                        "word_count": len(result.get("final_content", "")),
                        "generated_at": datetime.now().isoformat()
                    }
                else:
                    # 使用模拟生成
                    content_result = await self.generate_mock_content(topic, platform)
                
                results[platform] = content_result
                print(f"✅ {platform_name} - {content_result['word_count']}字 (质量分: {content_result['quality_score']})")
                
            except Exception as e:
                print(f"❌ {platform_name} 生成失败: {e}")
                results[platform] = {"error": str(e)}
        
        return results
    
    async def generate_mock_content(self, topic, platform):
        """生成模拟内容"""
        await asyncio.sleep(1)  # 模拟API延迟
        
        templates = {
            "wechat": f"""# {topic} - 深度分析报告

## 市场现状分析

根据最新市场数据显示，{topic}在当前经济环境下展现出强劲的发展势头。从宏观经济指标来看，相关行业的增长率保持在15-20%的健康区间。

## 核心竞争优势分析

### 1. 技术创新能力
- 研发投入占比持续提升至12.5%
- 核心技术专利数量同比增长35%
- 产品迭代周期缩短至6个月

### 2. 市场响应机制
- 用户反馈处理时间缩短至24小时内
- 市场占有率提升至23.8%
- 客户满意度达到92.3%

## 未来发展趋势预测

基于当前市场数据和行业发展规律，预计未来3-5年{topic}将呈现以下发展特征：

1. **市场规模持续扩大**：年复合增长率预计保持在18-25%
2. **技术迭代加速**：新技术应用周期将缩短30%以上  
3. **用户需求多样化**：个性化需求占比将超过60%

## 结论与建议

综合分析显示，{topic}具备良好的发展前景和投资价值。建议相关企业和投资者关注以下关键节点：

- 技术突破的时间窗口期
- 政策红利的释放节奏
- 市场竞争格局的变化

*数据来源：行业研究报告，截至{datetime.now().strftime('%Y年%m月')}*""",

            "xiaohongshu": f"""✨ {topic}全解析！姐妹们必看攻略来啦～

哈喽小仙女们！今天要给大家分享超级干货的{topic}深度解析💕

🔥 核心要点抢先看：
✅ 市场现状：发展势头强劲，增长率达20%+
✅ 关键优势：技术创新+用户体验双重加持  
✅ 未来趋势：个性化需求将成主流

💡 深度分析：

🌟 **技术实力篇**
研发投入真的很给力，占比12.5%，专利数量暴涨35%！这个数据真的太亮眼了～

🌟 **用户体验篇**  
24小时内响应用户反馈，满意度高达92.3%！这服务态度必须点赞👍

🌟 **发展前景篇**
未来3-5年复合增长率18-25%，个性化需求占比超60%，这个赛道真的很有潜力！

📝 **小贴士**：
关注技术突破窗口期，抓住政策红利，这些都是关键节点哦～

记得收藏起来慢慢研究！有问题评论区见💕

#内容创作 #{topic.replace(' ', '')} #干货分享 #投资理财 #市场分析 #科技趋势""",

            "bilibili": f"""【{topic}】2024最新深度解析 - 这可能是最全面的介绍

大家好，我是UP主。今天给大家带来{topic}的全方位解读。

🎯 本期目录：
00:00 开场介绍
01:30 市场现状分析  
03:45 核心优势解读
06:20 未来趋势预测
08:15 投资建议总结

📊 **市场数据解析**

从最新的行业报告来看，{topic}相关领域确实展现出了强劲的发展动力：

- 整体增长率：20%+ (远超行业平均水平)
- 技术专利增长：35% (创新能力显著提升)
- 市场占有率：23.8% (稳居第一梯队)
- 用户满意度：92.3% (口碑表现优秀)

💡 **核心竞争力分析**

1. **技术创新能力突出**
   - R&D投入占营收12.5%，远超同行
   - 产品迭代周期从12个月缩短至6个月
   - 核心技术壁垒不断加深

2. **市场响应机制完善**
   - 用户反馈24小时内处理完成
   - 个性化服务覆盖率达85%
   - 客户留存率持续提升

🔮 **未来发展预测**

基于当前趋势分析，未来3-5年{topic}将迎来黄金发展期：

- 市场规模CAGR预计18-25%
- 个性化需求占比将超过60%  
- 技术应用周期缩短30%+

如果这期视频对你有帮助，别忘了三连支持！我们评论区见～

下期预告：深度解析相关产业链投资机会，记得关注！""",

            "douyin": f"""🔥 {topic}的秘密，99%的人不知道！

【开场3秒抓眼球】
你知道{topic}今年发生了什么吗？数据太震撼了！

【核心内容15-45秒】
💥 重点1：增长率竟然达到20%+！
这个数据比90%的行业都要高，太疯狂了！

⚡ 重点2：用户满意度92.3%！  
24小时内解决问题，这服务绝了！

🚀 重点3：未来5年复合增长18-25%！
现在入局还不晚，机会就在眼前！

【结尾冲刺45-60秒】
关注我，每天分享赚钱密码！
下一期更精彩，不要错过！

#赚钱 #{topic.replace(' ', '')} #投资 #创业 #商机 #财经 #干货"""
        }
        
        content = templates.get(platform, f"基于{topic}的{platform}内容...")
        
        return {
            "content": content,
            "model_used": "mock-gpt-4",
            "quality_score": 88,
            "word_count": len(content),
            "generated_at": datetime.now().isoformat()
        }
    
    def display_results(self, results):
        """显示生成结果"""
        platform_names = {
            "wechat": "微信公众号",
            "xiaohongshu": "小红书",
            "bilibili": "B站",
            "douyin": "抖音"
        }
        
        print("\n" + "="*60)
        print("📋 生成结果")
        print("="*60)
        
        for platform, result in results.items():
            platform_name = platform_names.get(platform, platform)
            print(f"\n🎯 {platform_name}")
            print("-" * 40)
            
            if "error" in result:
                print(f"❌ 生成失败: {result['error']}")
                continue
            
            print(f"✅ 模型: {result['model_used']}")
            print(f"✅ 质量分: {result['quality_score']}")
            print(f"✅ 字数: {result['word_count']}")
            print(f"✅ 生成时间: {result['generated_at'][:16]}")
            print("\n📝 内容预览:")
            print("-" * 40)
            
            # 显示内容前300字
            content = result.get('content', '')
            preview = content[:300] + "..." if len(content) > 300 else content
            print(preview)
            print("-" * 40)
    
    def save_results(self, topic, results):
        """保存结果到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"generated_content_{timestamp}.json"
        
        save_data = {
            "topic": topic,
            "generated_at": datetime.now().isoformat(),
            "results": results
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 结果已保存到: {filename}")
            
            # 同时保存文本版本
            txt_filename = f"generated_content_{timestamp}.txt"
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(f"主题: {topic}\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                platform_names = {
                    "wechat": "微信公众号",
                    "xiaohongshu": "小红书", 
                    "bilibili": "B站",
                    "douyin": "抖音"
                }
                
                for platform, result in results.items():
                    platform_name = platform_names.get(platform, platform)
                    f.write(f"\n=== {platform_name} ===\n")
                    f.write(f"模型: {result.get('model_used', 'N/A')}\n")
                    f.write(f"质量分: {result.get('quality_score', 'N/A')}\n")
                    f.write(f"字数: {result.get('word_count', 'N/A')}\n")
                    f.write("-" * 40 + "\n")
                    f.write(result.get('content', '') + "\n\n")
            
            print(f"💾 文本版本已保存到: {txt_filename}")
            return True
            
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False
    
    async def run(self):
        """运行主程序"""
        print("🚀 启动 FastMCP Content Factory CLI...")
        
        try:
            while True:
                # 获取用户输入
                topic, platforms, anti_censorship = self.get_user_input()
                
                if topic is None:
                    break
                
                # 生成内容
                results = await self.generate_content_async(topic, platforms, anti_censorship)
                
                # 显示结果
                self.display_results(results)
                
                # 询问是否保存
                save_choice = input("\n💾 是否保存结果? (Y/n): ").strip().lower()
                if save_choice != 'n':
                    self.save_results(topic, results)
                
                # 询问是否继续
                continue_choice = input("\n🔄 是否继续生成其他内容? (Y/n): ").strip().lower()
                if continue_choice == 'n':
                    break
        
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，程序退出")
        except Exception as e:
            print(f"❌ 程序运行错误: {e}")
        
        print("\n感谢使用 FastMCP Content Factory！")

def main():
    """主函数"""
    generator = CLIGenerator()
    asyncio.run(generator.run())

if __name__ == "__main__":
    main()