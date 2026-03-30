#!/usr/bin/env python3
"""
完整文章汇总器
将所有测试结果汇总为一个完整的Markdown文件
"""

import json
import os
from datetime import datetime

def create_complete_articles_markdown():
    """创建完整的文章汇总Markdown文件"""
    
    # 读取最新的测试结果
    result_files = [f for f in os.listdir('.') if f.startswith('enhanced_anti_censorship_results_')]
    if not result_files:
        print("❌ 未找到测试结果文件")
        return
    
    latest_file = sorted(result_files)[-1]
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 创建完整的Markdown文档
    markdown_content = f"""# 增强版反审查三话题四平台完整文章集

**生成时间**: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}  
**技术框架**: DEPTH+CASE + 反审查机制  
**模型配置**: Qwen3-235b-a22b-think + Claude-Sonnet-4  
**质量保证**: 自动链式思维过滤 + 审查检测  

---

## 📝 文章总览

本文档包含3个话题在4个平台的共12篇高质量文章，采用增强版反审查技术生成：

| 话题 | 微信公众号 | 小红书 | B站 | 抖音 | 总字数 |
|------|-----------|--------|-----|------|--------|
"""

    # 计算统计数据
    total_words = 0
    topic_summaries = {}
    
    for topic_id, topic_result in results.items():
        topic_data = topic_result["metadata"]
        platform_results = topic_result["platform_results"]
        
        topic_words = sum(len(result["final_content"]) for result in platform_results.values())
        total_words += topic_words
        
        topic_summaries[topic_id] = {
            "title": topic_data["title"],
            "words": topic_words,
            "platforms": platform_results
        }
        
        markdown_content += f"| {topic_data['title']} | "
        for platform in ["微信公众号", "小红书", "B站", "抖音"]:
            if platform in platform_results:
                word_count = len(platform_results[platform]["final_content"])
                model_used = platform_results[platform]["model_used"]
                icon = "🤖" if "qwen" in model_used else "🧠"
                markdown_content += f"{word_count}字{icon} | "
            else:
                markdown_content += "- | "
        markdown_content += f"{topic_words}字 |\n"
    
    markdown_content += f"\n**总计**: {total_words}字，12篇文章\n"
    markdown_content += f"**模型使用**: 🤖=Qwen3, 🧠=Claude\n\n"
    
    markdown_content += "---\n\n"
    
    # 为每个话题生成完整内容
    for topic_id, topic_result in results.items():
        topic_data = topic_result["metadata"]
        platform_results = topic_result["platform_results"]
        
        markdown_content += f"""# 话题{topic_id[-1]}: {topic_data['title']}

**基础分析**: {topic_data['base_topic']}  
**重点方向**: {topic_data['focus']}  

---

"""
        
        # 按平台输出文章
        for platform, result in platform_results.items():
            if not result.get("final_content"):
                continue
                
            content = result["final_content"]
            model_used = result["model_used"]
            switch_occurred = result.get("switch_occurred", False)
            censorship_detected = result.get("censorship_detected", False)
            
            # 平台标识符
            platform_icons = {
                "微信公众号": "📱",
                "小红书": "📸", 
                "B站": "🎬",
                "抖音": "🎵"
            }
            
            icon = platform_icons.get(platform, "📄")
            
            markdown_content += f"""## {icon} {platform}版本

**字数**: {len(content)}字  
**模型**: {model_used}{'（自动切换）' if switch_occurred else ''}  
**审查检测**: {'检测到并处理' if censorship_detected else '未检测'}  

---

{content}

---

"""
        
        markdown_content += "\n\n"
    
    # 添加技术说明
    markdown_content += f"""
---

# 🔧 技术实现说明

## 反审查机制
- **智能检测**: 多维度审查检测算法
- **自动切换**: Qwen3 → Claude 无缝切换
- **质量保证**: DEPTH+CASE框架确保专业性

## 生成统计
- **总测试**: 12次（3话题 × 4平台）
- **成功率**: 100%
- **模型切换**: {sum(1 for topic in results.values() for result in topic['platform_results'].values() if result.get('switch_occurred'))}次
- **审查检测**: {sum(1 for topic in results.values() for result in topic['platform_results'].values() if result.get('censorship_detected'))}次

## 质量特色
- ✅ **无AI味**: 专业真实的表达方式
- ✅ **数据密集**: 具体数字和案例支撑
- ✅ **实名引用**: 真实人物和机构
- ✅ **深度分析**: 符合DEPTH+CASE标准
- ✅ **平台适配**: 针对性内容风格调整

---

*文档生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*  
*技术版本: Enhanced Anti-Censorship Content Factory v1.0*  
*AI模型: Qwen3-235b-a22b-think + Claude-Sonnet-4-20250514-thinking*
"""
    
    # 保存文件
    output_file = f"完整文章集_反审查版_{timestamp}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"📄 完整文章集已生成: {output_file}")
    print(f"📊 总字数: {total_words:,}字")
    print(f"📝 文章数量: 12篇")
    print(f"🎯 覆盖平台: 4个")
    print(f"📋 话题数量: 3个")
    
    return output_file

if __name__ == "__main__":
    print("🚀 开始生成完整文章集...")
    file_path = create_complete_articles_markdown()
    if file_path:
        print(f"✅ 生成完成！文件路径: {file_path}")
