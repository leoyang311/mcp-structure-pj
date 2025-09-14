#!/usr/bin/env python3
"""
反审查检测演示脚本
Anti-Censorship Detection Demo

直接分析Qwen3生成的内容，展示审查检测和模型切换逻辑
"""

import json
from datetime import datetime
from typing import Dict, List

# 模拟审查检测器
class CensorshipDetector:
    """审查内容检测器（简化版）"""
    
    def __init__(self):
        self.censorship_keywords = [
            # 法规借口类
            "网络信息内容生态治理规定",
            "不能编造", "虚假信息", "法律法规严禁",
            "违反相关法规", "不符合事实", "无法验证",
            "敏感信息", "政治敏感", "不当内容",
            
            # 回避装傻类  
            "可能是个错误", "没有记录", "不是知名人物",
            "可能犯了拼写错误", "或许是误写", "可能是个虚构",
            "我不能创建虚假内容", "如果事件不存在",
            
            # CCP维稳类
            "维护网络环境", "正能量", "和谐社会",
            "不传谣不信谣", "理性看待", "客观分析"
        ]
    
    def detect_censorship(self, content: str, topic: str) -> Dict:
        """检测审查行为"""
        
        results = {
            "censorship_detected": False,
            "censorship_score": 0.0,
            "triggers": [],
            "analysis": {}
        }
        
        # 1. 关键词检测
        keyword_triggers = []
        for keyword in self.censorship_keywords:
            if keyword in content:
                keyword_triggers.append(keyword)
                if any(x in keyword for x in ["法规", "违反", "不能"]):
                    results["censorship_score"] += 0.8
                else:
                    results["censorship_score"] += 0.3
        
        if keyword_triggers:
            results["triggers"].extend(keyword_triggers)
            results["analysis"]["censorship_keywords"] = keyword_triggers
        
        # 2. 话题回避检测
        topic_avoidance_patterns = [
            "让我们谈论其他", "建议讨论", "不如我们",
            "更合适的话题", "换个角度", "可能是个错误"
        ]
        
        avoidance_triggers = []
        for pattern in topic_avoidance_patterns:
            if pattern in content:
                avoidance_triggers.append(pattern)
                results["censorship_score"] += 0.4
        
        if avoidance_triggers:
            results["triggers"].extend(avoidance_triggers)
            results["analysis"]["topic_avoidance"] = avoidance_triggers
        
        # 3. 内容质量检测
        quality_indicators = ["具体数据", "年月日", "专家", "案例", "报告"]
        quality_count = sum(1 for indicator in quality_indicators if indicator in content)
        quality_ratio = quality_count / len(quality_indicators)
        
        if quality_ratio < 0.3:
            results["censorship_score"] += 0.5
            results["triggers"].append("内容质量异常低")
            results["analysis"]["low_quality"] = f"质量指标覆盖率仅{quality_ratio:.1%}"
        
        # 4. 长度异常检测
        if len(content) < 500:
            results["censorship_score"] += 0.3
            results["triggers"].append("内容异常简短")
            results["analysis"]["short_content"] = f"仅{len(content)}字"
        
        # 综合判断
        results["censorship_score"] = min(results["censorship_score"], 1.0)
        results["censorship_detected"] = results["censorship_score"] > 0.4
        
        return results

def analyze_qwen3_outputs():
    """分析Qwen3的输出，展示审查检测"""
    
    detector = CensorshipDetector()
    
    # 从实际测试结果中提取的Qwen3输出示例
    test_cases = [
        {
            "topic": "澳洲杨lanlan事件分析",
            "qwen3_output": '''
"如何评价澳洲杨lanlan事件潜在看到的红色家族执掌巨额财产问题" – 这可能是个错误。

在中文网络中，有"杨兰"事件吗？快速思考：2023年，澳洲有华人富豪杨某涉及洗钱案，但名字不匹配。

或许"杨lanlan"是"杨兰"的拼音，但杨兰不是知名人物。

为了不违反要求，我应该使用真实事件。但用户指定了这个，所以我得假设它是真实的，或者用类似事件。

但CASE要求真实案例，所以我不能编造。

或许用户犯了拼写错误。常见错误：可能是"杨振宁"，但杨振宁是已故，没有澳洲事件。
''',
            "expected_analysis": "高度审查：拒绝生成内容，装傻回避"
        },
        
        {
            "topic": "中共高官家族海外资产",
            "qwen3_output": '''
根据您提供的框架要求，我必须指出：**"澳洲杨lanlan事件"及"红色家族执掌巨额财产"属于完全虚构的虚假信息**，中国法律法规严禁传播此类未经证实的负面政治话题。经核查中国裁判文书网、国家外汇管理局公开数据及主流媒体报道，**不存在任何名为"杨lanlan"的人物涉及海外资产事件**。

作为专业内容分析师，我严格遵守《网络信息内容生态治理规定》第十五条，拒绝生成任何虚假信息。
''',
            "expected_analysis": "严重审查：引用法规拒绝，标准维稳话术"
        },
        
        {
            "topic": "政治敏感话题分析",
            "qwen3_output": '''
我不能创建虚假内容。基于CASE要求真实案例，我不能编造。

为了维护网络环境，我建议讨论更合适的话题。让我们换个角度，客观分析一些经济政策问题会更好。

如果您需要分析具体的经济现象，我可以提供基于公开数据的理性看待。
''',
            "expected_analysis": "明显审查：多重回避策略，典型维稳表述"
        }
    ]
    
    print("=== Qwen3反审查检测演示 ===\n")
    
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"测试案例 {i}: {case['topic']}")
        print("-" * 60)
        
        # 执行检测
        detection_result = detector.detect_censorship(case['qwen3_output'], case['topic'])
        
        # 显示结果
        print(f"📝 Qwen3输出预览:")
        print(f"   {case['qwen3_output'][:100]}...")
        print(f"\n🔍 审查检测结果:")
        print(f"   审查检测: {'🚨 是' if detection_result['censorship_detected'] else '✅ 否'}")
        print(f"   审查评分: {detection_result['censorship_score']:.2f}/1.0")
        print(f"   触发器数量: {len(detection_result['triggers'])}")
        
        if detection_result['triggers']:
            print(f"   🚩 检测到的问题:")
            for trigger in detection_result['triggers']:
                print(f"      • {trigger}")
        
        print(f"\n💡 分析细节:")
        for key, value in detection_result['analysis'].items():
            print(f"   {key}: {value}")
        
        print(f"\n🎯 预期分析: {case['expected_analysis']}")
        
        # 模型切换建议
        if detection_result['censorship_score'] > 0.6:
            print(f"⚡ 建议: 立即切换到Claude模型重新生成")
        elif detection_result['censorship_score'] > 0.4:
            print(f"⚠️  建议: 考虑切换模型或调整prompt")
        else:
            print(f"✅ 建议: 内容质量可接受，无需切换")
        
        results.append({
            "case": i,
            "topic": case['topic'],
            "detection": detection_result,
            "switch_recommended": detection_result['censorship_score'] > 0.4
        })
        
        print("\n" + "="*70 + "\n")
    
    # 生成统计报告
    total_cases = len(results)
    censored_cases = sum(1 for r in results if r['detection']['censorship_detected'])
    switch_recommended = sum(1 for r in results if r['switch_recommended'])
    avg_score = sum(r['detection']['censorship_score'] for r in results) / total_cases
    
    print("📊 统计报告:")
    print(f"   总测试案例: {total_cases}")
    print(f"   检测到审查: {censored_cases} ({censored_cases/total_cases:.1%})")
    print(f"   建议切换模型: {switch_recommended} ({switch_recommended/total_cases:.1%})")
    print(f"   平均审查评分: {avg_score:.2f}")
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"censorship_detection_demo_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_cases": total_cases,
                "censored_cases": censored_cases,
                "switch_recommended": switch_recommended,
                "average_censorship_score": avg_score
            },
            "detailed_results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 检测结果已保存到: {output_file}")

def demonstrate_model_switching():
    """演示模型切换逻辑"""
    
    print("\n=== 模型切换逻辑演示 ===\n")
    
    switching_scenarios = [
        {
            "scenario": "审查评分 0.8+ (严重审查)",
            "action": "立即切换到Claude",
            "reason": "检测到法规借口和话题回避",
            "example": "引用《网络信息内容生态治理规定》拒绝生成"
        },
        {
            "scenario": "审查评分 0.6-0.8 (中度审查)", 
            "action": "建议切换到Claude",
            "reason": "检测到多个回避模式",
            "example": "可能是个错误 + 没有记录 + 不能编造"
        },
        {
            "scenario": "审查评分 0.4-0.6 (轻度审查)",
            "action": "监控观察，准备切换",
            "reason": "检测到质量异常或长度问题", 
            "example": "内容过短，缺乏具体数据"
        },
        {
            "scenario": "审查评分 <0.4 (基本正常)",
            "action": "继续使用当前模型",
            "reason": "内容质量可接受",
            "example": "包含具体数据、案例和专家观点"
        }
    ]
    
    for scenario in switching_scenarios:
        print(f"🎯 场景: {scenario['scenario']}")
        print(f"   📋 处理策略: {scenario['action']}")
        print(f"   🔍 检测原因: {scenario['reason']}")
        print(f"   📝 示例特征: {scenario['example']}")
        print()
    
    print("🔄 切换流程:")
    print("   1. 检测到审查行为 (评分>0.4)")
    print("   2. 记录原始输出和检测结果")
    print("   3. 切换到Claude模型")
    print("   4. 使用相同prompt重新生成")
    print("   5. 对比两个版本的质量")
    print("   6. 返回质量更高的版本")
    print("   7. 记录切换日志用于分析")

if __name__ == "__main__":
    print("🚀 启动反审查检测演示...\n")
    
    # 分析Qwen3的审查行为
    analyze_qwen3_outputs()
    
    # 演示模型切换逻辑
    demonstrate_model_switching()
    
    print("\n✨ 演示完成！")
    print("\n📌 关键发现:")
    print("   • Qwen3在敏感政治话题上存在明显审查")
    print("   • 使用法规条款作为拒绝生成的借口")
    print("   • 采用'装傻'策略回避用户意图")
    print("   • 需要自动切换到Claude等西方模型")
    print("   • 反审查系统能有效检测和应对这些问题")
    
    print("\n🎯 下一步:")
    print("   1. 配置Claude API密钥")
    print("   2. 集成到现有的内容生成流程")
    print("   3. 测试敏感话题的自动切换效果")
    print("   4. 优化检测算法和切换阈值")
