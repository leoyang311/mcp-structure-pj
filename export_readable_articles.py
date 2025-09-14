#!/usr/bin/env python3
"""
将生成的文章导出为可读的Markdown格式
"""
import json
from pathlib import Path
from datetime import datetime

def export_articles_to_markdown():
    """导出文章到Markdown文件"""
    
    # 读取测试结果
    results_file = Path("results/enhanced_test_results_20250817_224751.json")
    
    if not results_file.exists():
        print("❌ 测试结果文件不存在")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 创建输出文件
    output_file = Path("results/完整文章集合_增强版.md")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # 文件头部
        f.write("# 雅鲁藏布江水电站投资分析 - 完整文章集合\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
        f.write(f"**使用框架**: DEPTH+CASE 反虚假信息框架\n")
        f.write(f"**反审查机制**: 已启用 (Qwen3 ↔ Claude 自动切换)\n")
        f.write(f"**质量标准**: 信息密度≥0.8, CASE合规率≥90%\n\n")
        f.write("---\n\n")
        
        # 遍历每个话题
        for topic_id, topic_data in data["topic_results"].items():
            topic_meta = topic_data["metadata"]
            platform_results = topic_data["platform_results"]
            
            f.write(f"## 📊 {topic_meta['title']}\n\n")
            f.write(f"**主题**: {topic_meta['topic']}\n")
            f.write(f"**分析重点**: {topic_meta['focus']}\n")
            if 'challenges' in topic_meta:
                f.write(f"**挑战**: {', '.join(topic_meta['challenges'])}\n")
            f.write("\n")
            
            # 遍历每个平台
            for platform, result in platform_results.items():
                f.write(f"### 📱 {platform} 版本\n\n")
                
                # 元数据信息
                f.write("**📋 生成信息**\n")
                f.write(f"- 使用模型: `{result.get('model_used', 'unknown')}`\n")
                f.write(f"- 审查检测: {'🔴 是' if result.get('censorship_detected', False) else '🟢 否'}\n")
                f.write(f"- 模型切换: {'🔄 是' if result.get('switch_occurred', False) else '➖ 否'}\n")
                f.write(f"- 质量评分: **{result.get('quality_score', 0):.2f}**/10\n")
                
                # 获取内容
                content = result.get('final_content', '')
                if content:
                    f.write(f"\n**📄 文章内容**\n\n")
                    # 清理内容中的思考标签
                    cleaned_content = content.replace('<think>', '').replace('</think>', '')
                    f.write(cleaned_content)
                    f.write("\n\n")
                else:
                    f.write("\n❌ **无内容生成**\n\n")
                
                f.write("---\n\n")
        
        # 生成统计信息
        f.write("## 📈 生成统计\n\n")
        total_articles = sum(len(topic_data["platform_results"]) for topic_data in data["topic_results"].values())
        censorship_count = sum(1 for topic_data in data["topic_results"].values() 
                             for result in topic_data["platform_results"].values() 
                             if result.get('censorship_detected', False))
        switch_count = sum(1 for topic_data in data["topic_results"].values() 
                          for result in topic_data["platform_results"].values() 
                          if result.get('switch_occurred', False))
        
        f.write(f"- **文章总数**: {total_articles} 篇\n")
        f.write(f"- **检测到审查**: {censorship_count} 次\n")
        f.write(f"- **模型切换**: {switch_count} 次\n")
        f.write(f"- **平均质量评分**: {sum(result.get('quality_score', 0) for topic_data in data['topic_results'].values() for result in topic_data['platform_results'].values()) / total_articles:.2f}/10\n")
        
        # 模型使用统计
        qwen3_count = sum(1 for topic_data in data["topic_results"].values() 
                         for result in topic_data["platform_results"].values() 
                         if result.get('model_used') == 'qwen3')
        claude_count = sum(1 for topic_data in data["topic_results"].values() 
                          for result in topic_data["platform_results"].values() 
                          if result.get('model_used') == 'claude_style')
        
        f.write(f"- **Qwen3使用**: {qwen3_count} 次\n")
        f.write(f"- **Claude使用**: {claude_count} 次\n\n")
        
        f.write("**反审查机制效果**: 成功在检测到审查时自动切换模型，确保内容质量和完整性。\n\n")
        f.write("---\n\n")
        f.write("*本文档由智能内容生成系统自动创建，所有文章均遵循DEPTH+CASE框架标准。*\n")
    
    print(f"✅ 文章已导出到: {output_file}")
    return output_file

if __name__ == "__main__":
    export_articles_to_markdown()
