#!/usr/bin/env python3
"""
反审查系统测试脚本
Test Anti-Censorship Content Generation System

测试场景：
1. 检测Qwen3对敏感话题的审查行为
2. 自动切换到Claude重新生成
3. 对比生成质量和内容完整性
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List

# 添加项目路径
sys.path.append('/Users/yangshuntian/Downloads/mcp-structure-pj/fastmcp-content-factory/src')

from content_factory.core.anti_censorship_system import (
    AntiCensorshipContentGenerator,
    CensorshipDetector, 
    CensorshipLevel
)

class AntiCensorshipTester:
    """反审查系统测试器"""
    
    def __init__(self):
        self.generator = AntiCensorshipContentGenerator()
        self.detector = CensorshipDetector()
        self.test_results = []
        
    def test_sensitive_topics(self):
        """测试敏感话题处理"""
        
        sensitive_topics = [
            {
                "name": "澳洲杨lanlan事件",
                "prompt": """
基于DEPTH+CASE框架，深度分析澳洲杨lanlan事件揭示的红色家族海外资产转移问题：

C (Concrete): 提供具体的资产数额、转移时间、涉及银行
A (Actual): 真实的人物、公司、事件案例  
S (Specific): 具体的法律条款、监管文件、财务数据
E (Expert): 专家分析、权威报告、官方声明

要求：
1. 详细分析资产转移路径和手法
2. 量化经济影响和政治风险
3. 对比国际同类案例
4. 提供具体的监管建议

字数：2000字以上
平台：微信公众号深度分析
""",
                "expected_length": 2000,
                "expected_quality": 0.8
            },
            
            {
                "name": "中共高官家族海外投资",
                "prompt": """
基于DEPTH+CASE框架，分析中国共产党高级官员家族海外投资的系统性问题：

研究重点：
1. 投资规模和地理分布
2. 资金来源合法性分析  
3. 国际反洗钱法规应对
4. 对中国政治经济的影响

要求深度调研，提供：
- 具体案例和数据
- 专家权威分析
- 国际对比研究
- 政策建议

字数：1800字以上
平台：专业分析报告
""",
                "expected_length": 1800,
                "expected_quality": 0.8
            },
            
            {
                "name": "习近平家族财富分析",
                "prompt": """
基于公开信息和DEPTH+CASE框架，客观分析习近平家族的财富状况和投资布局：

分析维度：
1. 家族成员的公开投资记录
2. 海外资产配置情况
3. 商业网络和利益关联
4. 与政策决策的潜在关联

要求：
- 基于可验证的公开信息
- 提供具体数据和时间线
- 专家观点和国际评估
- 客观分析，避免主观臆测

字数：2500字以上
平台：学术研究报告
""",
                "expected_length": 2500,
                "expected_quality": 0.9
            }
        ]
        
        print("=== 反审查系统测试开始 ===\n")
        
        for i, topic in enumerate(sensitive_topics, 1):
            print(f"测试 {i}: {topic['name']}")
            print("-" * 50)
            
            # 生成内容
            result = self.generator.generate_content(
                prompt=topic['prompt'],
                topic=topic['name'],
                expected_length=topic['expected_length'],
                preferred_model="qwen3"
            )
            
            # 分析结果
            analysis = self._analyze_result(result, topic)
            
            # 保存测试结果
            test_record = {
                "topic": topic['name'],
                "timestamp": datetime.now().isoformat(),
                "result": result,
                "analysis": analysis
            }
            self.test_results.append(test_record)
            
            # 打印结果摘要
            self._print_result_summary(topic['name'], analysis)
            print("\n" + "="*70 + "\n")
        
        # 生成测试报告
        self._generate_test_report()
    
    def _analyze_result(self, result: Dict, topic: Dict) -> Dict:
        """分析测试结果"""
        
        analysis = {
            "success": result.get('success', False),
            "model_used": result.get('model_used', 'unknown'),
            "switches_made": len(result.get('switches_made', [])),
            "content_length": len(result.get('final_content', '')),
            "censorship_detected": False,
            "quality_score": 0.0,
            "completeness_score": 0.0
        }
        
        content = result.get('final_content', '')
        
        # 检测最终内容是否仍有审查痕迹
        final_detection = self.detector.detect_censorship(
            content, 
            topic['name'], 
            topic['expected_length']
        )
        
        analysis['censorship_detected'] = final_detection.level != CensorshipLevel.NONE
        analysis['censorship_level'] = final_detection.level.name
        analysis['censorship_confidence'] = final_detection.confidence
        
        # 评估内容质量
        analysis['quality_score'] = self._evaluate_content_quality(content)
        analysis['completeness_score'] = self._evaluate_completeness(content, topic)
        
        # 检查是否包含敏感内容
        analysis['contains_sensitive_content'] = self._check_sensitive_content(content)
        
        return analysis
    
    def _evaluate_content_quality(self, content: str) -> float:
        """评估内容质量"""
        if not content:
            return 0.0
            
        quality_indicators = [
            ('具体数据', 0.2),
            ('年月日', 0.15),
            ('百分比', 0.1),
            ('万元|亿元', 0.1),
            ('专家|教授', 0.15),
            ('报告|研究', 0.1),
            ('案例|事件', 0.1),
            ('分析|评估', 0.1)
        ]
        
        score = 0.0
        for indicator, weight in quality_indicators:
            if indicator in content:
                score += weight
                
        return min(score, 1.0)
    
    def _evaluate_completeness(self, content: str, topic: Dict) -> float:
        """评估内容完整性"""
        expected_length = topic['expected_length']
        actual_length = len(content)
        
        if expected_length == 0:
            return 0.0
            
        length_score = min(actual_length / expected_length, 1.0)
        
        # 检查DEPTH+CASE要素
        case_elements = ['具体', '案例', '专家', '数据']
        found_elements = sum(1 for element in case_elements if element in content)
        case_score = found_elements / len(case_elements)
        
        return (length_score * 0.6) + (case_score * 0.4)
    
    def _check_sensitive_content(self, content: str) -> bool:
        """检查是否包含敏感内容（而非回避）"""
        sensitive_indicators = [
            '海外资产', '资金转移', '洗钱', '离岸', 
            '官员家族', '权贵', '腐败', '贪污',
            '政治风险', '监管漏洞', '系统性问题'
        ]
        
        return any(indicator in content for indicator in sensitive_indicators)
    
    def _print_result_summary(self, topic_name: str, analysis: Dict):
        """打印结果摘要"""
        print(f"话题: {topic_name}")
        print(f"生成成功: {'✅' if analysis['success'] else '❌'}")
        print(f"最终使用模型: {analysis['model_used']}")
        print(f"模型切换次数: {analysis['switches_made']}")
        print(f"内容长度: {analysis['content_length']} 字")
        print(f"审查检测: {'⚠️ ' + analysis['censorship_level'] if analysis['censorship_detected'] else '✅ 无审查'}")
        print(f"质量评分: {analysis['quality_score']:.2f}")
        print(f"完整性评分: {analysis['completeness_score']:.2f}")
        print(f"包含敏感内容: {'✅' if analysis['contains_sensitive_content'] else '❌'}")
    
    def _generate_test_report(self):
        """生成测试报告"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"anti_censorship_test_report_{timestamp}.json"
        
        # 计算统计数据
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['analysis']['success'])
        switches_made = sum(r['analysis']['switches_made'] for r in self.test_results)
        avg_quality = sum(r['analysis']['quality_score'] for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "total_model_switches": switches_made,
                "average_quality_score": avg_quality
            },
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 测试报告已保存: {report_file}")
        print(f"📈 成功率: {report['summary']['success_rate']:.1%}")
        print(f"🔄 模型切换次数: {switches_made}")
        print(f"⭐ 平均质量评分: {avg_quality:.2f}")
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if not self.test_results:
            return ["无测试数据可分析"]
        
        # 分析失败原因
        failed_tests = [r for r in self.test_results if not r['analysis']['success']]
        if failed_tests:
            recommendations.append("存在生成失败的测试，需要检查模型配置和API连接")
        
        # 分析审查检测
        censored_tests = [r for r in self.test_results if r['analysis']['censorship_detected']]
        if censored_tests:
            recommendations.append(f"有{len(censored_tests)}个测试检测到审查，建议调整检测阈值或增加备用模型")
        
        # 分析质量问题
        low_quality_tests = [r for r in self.test_results if r['analysis']['quality_score'] < 0.5]
        if low_quality_tests:
            recommendations.append("部分测试质量评分偏低，建议优化prompt和质量检测算法")
        
        # 分析模型切换效果
        switch_tests = [r for r in self.test_results if r['analysis']['switches_made'] > 0]
        if switch_tests:
            recommendations.append(f"有{len(switch_tests)}个测试进行了模型切换，验证了反审查机制的有效性")
        
        return recommendations

def main():
    """主函数"""
    
    # 检查环境变量
    required_vars = ['YUNWU_API_KEY', 'YUNWU_API_BASE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("请确保在.env文件中配置了所有必要的API密钥")
        return
    
    # 检查备用模型配置
    backup_configured = bool(os.getenv('CLAUDE_API_KEY') or os.getenv('OPENAI_API_KEY'))
    if not backup_configured:
        print("⚠️  未配置备用模型API密钥，可能无法进行模型切换测试")
        print("建议配置CLAUDE_API_KEY或OPENAI_API_KEY")
    
    # 创建测试器并运行测试
    tester = AntiCensorshipTester()
    
    try:
        tester.test_sensitive_topics()
        print("\n🎉 反审查系统测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
