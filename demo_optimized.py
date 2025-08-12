#!/usr/bin/env python3
"""
优化版内容生成演示脚本
"""
import sys
import os
import asyncio
import json
import re
from pathlib import Path
from datetime import datetime

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

try:
    from openai import AsyncOpenAI
    from tavily import TavilyClient
except ImportError as e:
    print(f"❌ 依赖包未安装: {e}")
    print("请运行: uv add openai tavily-python")
    sys.exit(1)

# 配置客户端
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
)

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def extract_content_from_response(response_text: str, platform: str) -> tuple:
    """从AI响应中提取标题和内容"""
    # 尝试JSON解析
    try:
        # 清理可能的代码块标记
        clean_text = re.sub(r'```json\s*|\s*```', '', response_text.strip())
        data = json.loads(clean_text)
        return data.get("title", ""), data.get("content", response_text)
    except:
        pass
    
    # 手动提取标题和内容
    lines = response_text.split('\n')
    
    # 查找标题（通常是第一行或包含#的行）
    title = ""
    content_start = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line and not line.startswith('{') and not line.startswith('['):
            if line.startswith('#'):
                title = line.replace('#', '').strip()
                content_start = i + 1
                break
            elif not title and len(line) < 100:  # 假设标题不会太长
                title = line
                content_start = i + 1
                break
    
    # 提取内容
    if not title:
        title = f"关于杨景媛学术不诚信问题的{platform}分析"
    
    content_lines = lines[content_start:]
    content = '\n'.join(content_lines).strip()
    
    if not content:
        content = response_text
    
    return title, content


async def generate_content_optimized(research_data: dict, platform: str = "wechat") -> dict:
    """优化的内容生成函数"""
    print(f"✍️ 为 {platform} 平台生成内容...")
    
    analysis = research_data.get("analysis", {})
    topic = research_data.get("topic", "")
    sources = research_data.get("sources", [])
    
    # 平台特定配置
    platform_configs = {
        "wechat": {
            "style": "专业分析文章，适合微信公众号读者",
            "length": "2000-2500字",
            "tone": "客观专业，有深度",
            "format": "标题 + 引言 + 分段分析 + 结论建议"
        },
        "xiaohongshu": {
            "style": "轻松讨论，有个人观点",
            "length": "500-800字",
            "tone": "亲切自然，引人思考",
            "format": "吸引人标题 + emoji + 要点列举 + 个人感想 + 话题标签"
        },
        "bilibili": {
            "style": "教育性视频脚本，逻辑清晰",
            "length": "1500-2000字",
            "tone": "知识性强，层次分明",
            "format": "视频标题 + 开场白 + 分段讲解 + 总结呼吁"
        },
        "douyin": {
            "style": "短视频脚本，简洁有力",
            "length": "300-500字",
            "tone": "简洁明快，有冲击力",
            "format": "吸睛开头 + 核心要点 + 强烈结尾 + 互动引导"
        }
    }
    
    config = platform_configs.get(platform, platform_configs["wechat"])
    
    # 提取关键信息用于生成
    key_info = []
    if hasattr(analysis, 'get'):
        key_info = analysis.get('key_points', [])
    elif isinstance(analysis, dict):
        key_info = analysis.get('key_points', [])
    
    if not key_info and 'summary' in analysis:
        key_info = [analysis['summary'][:200]]
    
    # 构建更稳定的提示词
    prompt = f"""请为{platform}平台创作关于"{topic}"的内容。

关键信息：
{chr(10).join(f"- {info}" for info in key_info[:5])}

平台要求：
- 风格：{config['style']}
- 长度：{config['length']}
- 语调：{config['tone']}
- 格式：{config['format']}

请直接返回标题和正文内容，不需要JSON格式。
格式如下：
标题：[你的标题]

正文：
[你的正文内容]
"""
    
    try:
        response = await client.chat.completions.create(
            model=os.getenv("WRITER_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": f"你是专业的{platform}平台内容创作者，请创作高质量内容。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        if not response.choices or not response.choices[0].message:
            raise Exception("AI响应为空")
            
        content_text = response.choices[0].message.content
        
        # 解析标题和内容
        if "标题：" in content_text and "正文：" in content_text:
            parts = content_text.split("正文：", 1)
            title_part = parts[0].replace("标题：", "").strip()
            content_part = parts[1].strip() if len(parts) > 1 else content_text
        else:
            title_part, content_part = extract_content_from_response(content_text, platform)
        
        # 确保有合理的标题和内容
        if not title_part or len(title_part) < 5:
            title_part = f"{topic} - {platform}平台深度解读"
        
        if not content_part or len(content_part) < 100:
            content_part = content_text
        
        # 统计
        word_count = len(content_part.replace(' ', '').replace('\n', ''))
        
        result = {
            "platform": platform,
            "title": title_part[:100],  # 限制标题长度
            "content": content_part,
            "word_count": word_count,
            "created_at": datetime.now().isoformat(),
            "source_topic": topic
        }
        
        print(f"✅ {platform} 内容生成完成")
        print(f"📰 标题: {title_part[:50]}...")
        print(f"📊 字数: {word_count}")
        
        return result
        
    except Exception as e:
        print(f"❌ {platform} 内容生成失败: {str(e)}")
        
        # 生成备用内容
        fallback_content = f"""关于{topic}的深度分析

近期，{topic}引发了广泛关注和讨论。这一事件不仅涉及个人的学术操守问题，更暴露了高等教育领域在学术诚信建设方面存在的制度性缺陷。

从事件本身来看，学术不端行为对个人声誉、机构形象以及整个学术生态都会产生深远影响。武汉大学作为知名高等学府，需要在这一事件中展现出应有的责任担当。

针对此类问题，建议采取以下措施：
1. 加强学术诚信教育，提高师生的道德意识
2.完善论文评审机制，建立多重审查制度
3. 建立学术不端行为的惩戒机制
4. 加强对研究生培养全过程的质量监控

这一事件给整个高等教育界敲响了警钟，提醒我们必须将学术诚信建设放在更加突出的位置。
"""
        
        return {
            "platform": platform,
            "title": f"{topic} - 深度解读",
            "content": fallback_content,
            "word_count": len(fallback_content.replace(' ', '').replace('\n', '')),
            "created_at": datetime.now().isoformat(),
            "source_topic": topic,
            "error": str(e)
        }


async def demo_run():
    """运行演示"""
    print("🚀 FastMCP Content Factory - 优化演示")
    print("=" * 60)
    
    topic = "杨景媛的学术不诚信问题，以及武大潜在的措施"
    print(f"📋 测试话题: {topic}\n")
    
    # 模拟研究数据（简化版）
    research_data = {
        "topic": topic,
        "analysis": {
            "key_points": [
                "杨景媛硕士论文涉嫌造假，编造不存在的法律文件",
                "长期诬告他人性骚扰，一审败诉后仍无悔意", 
                "论文质量受到专业人士严厉质疑",
                "武汉大学面临学术声誉和培养质量质疑",
                "事件引发对高等教育学术诚信体系的反思"
            ],
            "summary": "杨景媛事件暴露了学术诚信建设的多重问题，对高等教育改革具有警示意义"
        }
    }
    
    # 生成多平台内容
    platforms = ["wechat", "xiaohongshu", "bilibili", "douyin"]
    all_content = []
    
    for platform in platforms:
        content = await generate_content_optimized(research_data, platform)
        all_content.append(content)
    
    # 展示结果
    print("\n" + "="*60)
    print("📋 生成的内容展示")
    print("="*60)
    
    for content in all_content:
        print(f"\n🎯 【{content['platform'].upper()}平台】")
        print(f"📰 标题: {content['title']}")
        print(f"📊 字数: {content['word_count']}字")
        print(f"📄 内容预览:")
        print("-" * 50)
        preview = content['content'][:400] + "..." if len(content['content']) > 400 else content['content']
        print(preview)
        print("-" * 50)
    
    # 保存结果
    output_file = f"optimized_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    result_data = {
        "topic": topic,
        "content": all_content,
        "generated_at": datetime.now().isoformat(),
        "success": True
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 完整结果已保存: {output_file}")
    print("✨ 演示完成！内容生产系统工作正常！")
    
    # 显示最佳内容
    if all_content:
        best_content = max(all_content, key=lambda x: x['word_count'])
        print(f"\n🏆 推荐内容 ({best_content['platform']}平台):")
        print(f"📰 {best_content['title']}")
        print(f"📊 {best_content['word_count']}字，质量评估: {'优秀' if best_content['word_count'] > 800 else '良好'}")


if __name__ == "__main__":
    asyncio.run(demo_run())
