#!/usr/bin/env python3
"""
简化的内容生成测试脚本
测试题目：杨景媛的学术不诚信问题，以及武大潜在的措施
"""
import sys
import os
import asyncio
import json
from pathlib import Path
from datetime import datetime

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 导入OpenAI
try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    print("❌ OpenAI未安装，请运行: uv add openai")
    sys.exit(1)

# 导入Tavily
try:
    from tavily import TavilyClient
except ImportError:
    print("❌ Tavily未安装，请运行: uv add tavily-python")
    sys.exit(1)

# 配置OpenAI客户端
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
)

# 配置Tavily客户端
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


async def research_topic(topic: str) -> dict:
    """研究话题"""
    print(f"🔍 研究话题: {topic}")
    
    try:
        # 使用Tavily搜索最新信息
        search_result = tavily.search(
            query=topic,
            search_depth="basic",
            max_results=5
        )
        
        # 提取关键信息
        sources = []
        content_pieces = []
        
        for result in search_result.get("results", []):
            sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "published_date": result.get("published_date", "")
            })
            content_pieces.append(result.get("content", ""))
        
        # 使用GPT分析和总结
        analysis_prompt = f"""
基于以下关于"{topic}"的搜索资料，请进行深入分析：

搜索资料：
{chr(10).join(content_pieces[:3])}

请提供：
1. 事件核心要点（3-5个关键点）
2. 可能的影响和后果
3. 相关方的立场和反应
4. 潜在的解决措施
5. 事件的深层次意义

请以JSON格式返回，包含以下字段：
- key_points: 关键要点列表
- impacts: 影响分析
- stakeholder_positions: 各方立场
- potential_measures: 潜在措施
- significance: 深层意义
- summary: 整体总结
"""
        
        response = await client.chat.completions.create(
            model=os.getenv("RESEARCH_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "你是一个专业的研究分析师，擅长分析复杂事件和社会现象。请基于提供的资料进行客观、全面的分析。"},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        analysis_text = response.choices[0].message.content
        
        # 尝试解析JSON，如果失败则使用文本格式
        try:
            analysis = json.loads(analysis_text)
        except:
            analysis = {
                "key_points": ["事件分析", "影响评估", "解决方案"],
                "impacts": "社会关注度高，影响学术声誉",
                "stakeholder_positions": "多方关注",
                "potential_measures": "加强学术诚信教育",
                "significance": "反映学术诚信问题的重要性",
                "summary": analysis_text[:500],
                "raw_analysis": analysis_text
            }
        
        research_data = {
            "topic": topic,
            "sources": sources,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ 研究完成，获得 {len(sources)} 个信息源")
        return research_data
        
    except Exception as e:
        print(f"❌ 研究失败: {str(e)}")
        return {
            "topic": topic,
            "sources": [],
            "analysis": {
                "key_points": ["学术不诚信问题", "机构责任", "制度改进"],
                "summary": f"关于{topic}的研究分析",
                "error": str(e)
            },
            "timestamp": datetime.now().isoformat()
        }


async def generate_content(research_data: dict, platform: str = "wechat") -> dict:
    """生成内容"""
    print(f"✍️ 为 {platform} 平台生成内容...")
    
    analysis = research_data.get("analysis", {})
    topic = research_data.get("topic", "")
    
    # 平台特定的提示词
    platform_prompts = {
        "wechat": {
            "style": "专业深度，适合微信公众号的长文章格式",
            "length": "2000-3000字",
            "tone": "专业、客观、深入分析"
        },
        "xiaohongshu": {
            "style": "轻松易懂，适合小红书的图文风格",
            "length": "500-800字",
            "tone": "通俗易懂、有观点、引人思考"
        },
        "bilibili": {
            "style": "教育性强，适合B站视频脚本",
            "length": "1500-2500字",
            "tone": "知识性、逻辑清晰、有层次"
        },
        "douyin": {
            "style": "简洁有力，适合短视频脚本",
            "length": "300-500字",
            "tone": "简洁、有冲击力、易传播"
        }
    }
    
    platform_config = platform_prompts.get(platform, platform_prompts["wechat"])
    
    content_prompt = f"""
基于以下研究分析，为{platform}平台创作关于"{topic}"的内容：

研究分析：
关键要点：{analysis.get('key_points', [])}
影响分析：{analysis.get('impacts', '')}
各方立场：{analysis.get('stakeholder_positions', '')}
潜在措施：{analysis.get('potential_measures', '')}
深层意义：{analysis.get('significance', '')}
总结：{analysis.get('summary', '')}

平台要求：
- 风格：{platform_config['style']}
- 长度：{platform_config['length']}
- 语调：{platform_config['tone']}

请创作包含以下内容：
1. 吸引人的标题
2. 引人入胜的开头
3. 结构清晰的正文（包含关键要点分析）
4. 有见地的结论
5. 适合该平台的格式和风格

请以JSON格式返回，包含title和content字段。
"""
    
    try:
        response = await client.chat.completions.create(
            model=os.getenv("WRITER_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": f"你是一个专业的内容创作者，擅长为不同平台创作高质量的内容。请根据平台特点调整写作风格。"},
                {"role": "user", "content": content_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        content_text = response.choices[0].message.content
        
        # 尝试解析JSON
        try:
            content_data = json.loads(content_text)
            title = content_data.get("title", f"{topic} - 深度分析")
            content = content_data.get("content", content_text)
        except:
            # JSON解析失败，手动提取标题和内容
            lines = content_text.split('\n')
            title = lines[0].replace('#', '').strip() if lines else f"{topic} - 深度分析"
            content = content_text
        
        # 计算内容统计
        word_count = len(content.replace(' ', '').replace('\n', ''))
        
        result = {
            "platform": platform,
            "title": title,
            "content": content,
            "word_count": word_count,
            "created_at": datetime.now().isoformat(),
            "source_topic": topic
        }
        
        print(f"✅ {platform} 内容生成完成，标题：{title[:30]}...")
        print(f"📊 字数统计：{word_count}字")
        
        return result
        
    except Exception as e:
        print(f"❌ {platform} 内容生成失败: {str(e)}")
        return {
            "platform": platform,
            "title": f"{topic} - 分析报告",
            "content": f"关于{topic}的分析内容生成遇到问题：{str(e)}",
            "word_count": 0,
            "created_at": datetime.now().isoformat(),
            "source_topic": topic,
            "error": str(e)
        }


async def main():
    """主函数"""
    print("🎉 FastMCP Content Factory 测试演示")
    print("=" * 50)
    
    # 测试话题
    topic = "杨景媛的学术不诚信问题，以及武大潜在的措施"
    
    print(f"📋 测试话题: {topic}")
    print()
    
    try:
        # 1. 研究阶段
        research_result = await research_topic(topic)
        
        # 2. 内容生成阶段
        platforms = ["wechat", "xiaohongshu"]
        
        all_content = []
        for platform in platforms:
            content = await generate_content(research_result, platform)
            all_content.append(content)
        
        # 3. 结果展示
        print("\n" + "="*50)
        print("📝 生成结果")
        print("="*50)
        
        for content in all_content:
            print(f"\n🎯 {content['platform'].upper()} 平台内容：")
            print(f"📰 标题: {content['title']}")
            print(f"📊 字数: {content['word_count']}")
            print(f"📄 内容预览:")
            print("-" * 30)
            print(content['content'][:300] + "..." if len(content['content']) > 300 else content['content'])
            print("-" * 30)
        
        # 4. 保存结果
        output_file = f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        result_data = {
            "topic": topic,
            "research": research_result,
            "content": all_content,
            "generated_at": datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 完整结果已保存到: {output_file}")
        print("✨ 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
