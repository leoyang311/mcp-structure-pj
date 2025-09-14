#!/usr/bin/env python3
"""
查看生成的完整文章内容
"""
import json
import sys
from pathlib import Path

def display_article_content():
    """显示生成的文章内容"""
    
    # 读取测试结果
    results_file = Path("results/enhanced_test_results_20250817_224751.json")
    
    if not results_file.exists():
        print("❌ 测试结果文件不存在")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("📚 完整文章内容展示")
    print("="*80)
    
    # 遍历每个话题
    for topic_id, topic_data in data["topic_results"].items():
        topic_meta = topic_data["metadata"]
        platform_results = topic_data["platform_results"]
        
        print(f"\n🎯 {topic_meta['title']} ({topic_id.upper()})")
        print(f"主题: {topic_meta['topic']}")
        print(f"重点: {topic_meta['focus']}")
        print("-" * 60)
        
        # 遍历每个平台
        for platform, result in platform_results.items():
            print(f"\n📱 {platform} 版本")
            print(f"使用模型: {result.get('model_used', 'unknown')}")
            print(f"审查检测: {'是' if result.get('censorship_detected', False) else '否'}")
            print(f"模型切换: {'是' if result.get('switch_occurred', False) else '否'}")
            print(f"质量评分: {result.get('quality_score', 0):.2f}")
            
            # 显示文章内容
            content = result.get('final_content', '')
            if content:
                print("\n📄 文章内容:")
                print("─" * 40)
                print(content)
                print("─" * 40)
            else:
                print("❌ 无内容生成")
            
            print("\n" + "="*80)

def display_specific_article(topic_id=None, platform=None):
    """显示特定话题和平台的文章"""
    
    results_file = Path("results/enhanced_test_results_20250817_224751.json")
    
    if not results_file.exists():
        print("❌ 测试结果文件不存在")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if topic_id and topic_id in data["topic_results"]:
        topic_data = data["topic_results"][topic_id]
        
        if platform and platform in topic_data["platform_results"]:
            result = topic_data["platform_results"][platform]
            
            print(f"📄 {topic_data['metadata']['title']} - {platform}")
            print("="*80)
            print(f"使用模型: {result.get('model_used', 'unknown')}")
            print(f"审查检测: {'是' if result.get('censorship_detected', False) else '否'}")
            print(f"质量评分: {result.get('quality_score', 0):.2f}")
            print("\n文章内容:")
            print("-" * 40)
            print(result.get('final_content', '无内容'))
            print("-" * 40)
        else:
            print("可用平台:", list(topic_data["platform_results"].keys()))
    else:
        print("可用话题:", list(data["topic_results"].keys()))

def main():
    """主函数"""
    if len(sys.argv) > 1:
        if len(sys.argv) == 3:
            # 显示特定文章
            topic_id = sys.argv[1]
            platform = sys.argv[2]
            display_specific_article(topic_id, platform)
        else:
            print("用法: python view_articles.py [topic_id] [platform]")
            print("例如: python view_articles.py topic1 微信公众号")
    else:
        # 显示所有文章
        display_article_content()

if __name__ == "__main__":
    main()
