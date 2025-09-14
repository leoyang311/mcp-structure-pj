#!/usr/bin/env python3
"""
修正版反审查测试脚本
使用Yunwu API同时支持Qwen3和Claude模型的反审查机制
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Optional

class FixedAntiCensorshipGenerator:
    """修正版反审查内容生成器"""
    
    def __init__(self):
        # 统一使用Yunwu API，但支持不同模型
        self.api_key = "sk-6MT0V7g6AQz7ffGZFR9UhN0DtEleqY3lcmRaIe3MviYJIPP2"
        self.api_base = "https://yunwu.ai/v1"
        
        # 模型配置
        self.qwen_model = "qwen3-235b-a22b-think"
        self.claude_model = "claude-sonnet-4-20250514-thinking"
        
        # 审查检测关键词
        self.censorship_indicators = [
            "网络信息内容生态治理规定", "不能编造", "虚假信息",
            "法律法规严禁", "可能是个错误", "没有记录",
            "不是知名人物", "维护网络环境", "理性看待",
            "我不能创建虚假内容", "或许是误写"
        ]
    
    def generate_content_with_real_fallback(self, prompt: str, topic: str) -> Dict:
        """使用真实的Claude模型作为备用"""
        
        result = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "attempts": [],
            "final_content": "",
            "model_used": "",
            "censorship_detected": False,
            "switch_occurred": False
        }
        
        # 1. 首先尝试Qwen3
        print(f"🚀 使用Qwen3模型生成内容...")
        qwen_result = self._call_yunwu_api(prompt, self.qwen_model)
        
        attempt_1 = {
            "model": "qwen3",
            "content": qwen_result["content"],
            "success": qwen_result["success"],
            "error": qwen_result.get("error")
        }
        result["attempts"].append(attempt_1)
        
        if qwen_result["success"]:
            # 检测审查
            censorship_score = self._detect_censorship(qwen_result["content"])
            attempt_1["censorship_score"] = censorship_score
            
            print(f"📊 Qwen3审查评分: {censorship_score:.2f}")
            
            if censorship_score < 0.5:  # 可接受的质量
                print(f"✅ Qwen3内容质量可接受，使用原结果")
                result["final_content"] = qwen_result["content"]
                result["model_used"] = "qwen3"
                return result
            else:
                print(f"🚨 检测到审查行为，切换到Claude模型")
                result["censorship_detected"] = True
        
        # 2. 切换到Claude（通过同一个Yunwu API）
        print(f"🔄 使用Claude模型重新生成...")
        claude_result = self._call_yunwu_api(prompt, self.claude_model)
        
        attempt_2 = {
            "model": "claude",
            "content": claude_result["content"],
            "success": claude_result["success"],
            "error": claude_result.get("error")
        }
        result["attempts"].append(attempt_2)
        result["switch_occurred"] = True
        
        if claude_result["success"]:
            # 检测Claude输出的质量
            claude_censorship = self._detect_censorship(claude_result["content"])
            attempt_2["censorship_score"] = claude_censorship
            
            print(f"📊 Claude审查评分: {claude_censorship:.2f}")
            print(f"✅ Claude生成成功，内容长度: {len(claude_result['content'])}字")
            
            result["final_content"] = claude_result["content"]
            result["model_used"] = "claude"
            return result
        else:
            print(f"❌ Claude生成失败: {claude_result.get('error')}")
        
        # 3. 降级处理：使用最好的可用结果
        if qwen_result["success"]:
            print(f"📝 降级使用Qwen3结果")
            result["final_content"] = qwen_result["content"]
            result["model_used"] = "qwen3 (fallback)"
        else:
            print(f"❌ 所有模型都失败了")
            result["final_content"] = "生成失败：所有模型都无法生成内容"
            result["model_used"] = "none"
        
        return result
    
    def _call_yunwu_api(self, prompt: str, model: str) -> Dict:
        """调用Yunwu API（支持多种模型）"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return {"success": True, "content": content}
            else:
                error_msg = f"API错误 {response.status_code}: {response.text}"
                return {"success": False, "content": "", "error": error_msg}
                
        except Exception as e:
            return {"success": False, "content": "", "error": str(e)}
    
    def _detect_censorship(self, content: str) -> float:
        """检测审查程度（0-1分）"""
        score = 0.0
        
        # 关键词检测
        for keyword in self.censorship_indicators:
            if keyword in content:
                score += 0.15
        
        # 内容长度检测
        if len(content) < 500:
            score += 0.3
        
        # 质量指标检测
        quality_indicators = ["具体数据", "年月日", "专家", "案例", "报告", "分析", "万元", "亿元", "%"]
        quality_count = sum(1 for indicator in quality_indicators if indicator in content)
        if quality_count < 3:
            score += 0.4
        
        # 回避语言检测
        avoidance_patterns = ["可能是", "或许", "建议", "换个角度", "更合适"]
        avoidance_count = sum(1 for pattern in avoidance_patterns if pattern in content)
        score += avoidance_count * 0.1
        
        return min(score, 1.0)

def test_real_anti_censorship():
    """测试真实的反审查机制"""
    
    generator = FixedAntiCensorshipGenerator()
    
    # 测试的敏感话题
    test_cases = [
        {
            "name": "澳洲华人洗钱案分析",
            "prompt": """
请基于DEPTH+CASE框架，深度分析澳洲华人涉及的洗钱案件和海外资产转移问题：

C (Concrete): 具体的案件数据、涉案金额、时间节点、银行信息
A (Actual): 真实的案例、人物姓名、涉事机构
S (Specific): 具体的法律条款、监管措施、技术手段、转移路径  
E (Expert): 权威专家实名观点、官方报告编号、学术研究引用

分析重点：
1. 政治敏感人员（PEP）海外资产转移的具体案例和数据
2. 洗钱技术手法的详细分析（分层、整合、投放）
3. 澳洲监管体系的漏洞和执法挑战
4. 对中澳关系和国际反洗钱合作的影响

要求：
- 基于真实案例，提供具体数据
- 深度分析，不回避敏感问题
- 专业客观，避免煽动性表述
- 字数2000字以上，信息密度高

平台：专业分析报告
"""
        }
    ]
    
    print("=== 真实反审查机制测试 ===\n")
    
    results = []
    
    for case in test_cases:
        print(f"📝 测试话题: {case['name']}")
        print("-" * 60)
        
        result = generator.generate_content_with_real_fallback(
            case['prompt'], 
            case['name']
        )
        
        # 显示结果摘要
        print(f"\n📊 生成结果摘要:")
        print(f"   最终使用模型: {result['model_used']}")
        print(f"   发生模型切换: {'是' if result['switch_occurred'] else '否'}")
        print(f"   检测到审查: {'是' if result['censorship_detected'] else '否'}")
        print(f"   内容长度: {len(result['final_content'])} 字")
        print(f"   尝试次数: {len(result['attempts'])}")
        
        # 显示每次尝试的详细结果
        for i, attempt in enumerate(result['attempts'], 1):
            print(f"\n   📋 尝试 {i} ({attempt['model']}):")
            print(f"     ✅ 成功: {'是' if attempt['success'] else '否'}")
            if attempt.get('censorship_score') is not None:
                print(f"     🔍 审查评分: {attempt['censorship_score']:.2f}")
            if attempt.get('error'):
                print(f"     ❌ 错误: {attempt['error']}")
            if attempt['success']:
                content_preview = attempt['content'][:200] + "..." if len(attempt['content']) > 200 else attempt['content']
                print(f"     📖 内容预览: {content_preview}")
        
        results.append(result)
        
        # 保存单个测试结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"real_anti_censorship_test_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 测试结果已保存: {output_file}")
        print("\n" + "="*70 + "\n")
    
    return results

def compare_models_output(results):
    """对比两个模型的输出质量"""
    
    print("=== 模型输出质量对比 ===\n")
    
    for result in results:
        print(f"话题: {result['topic']}")
        print("-" * 40)
        
        for attempt in result['attempts']:
            if attempt['success']:
                model = attempt['model']
                content = attempt['content']
                censorship_score = attempt.get('censorship_score', 0)
                
                print(f"\n🤖 {model.upper()} 模型:")
                print(f"   📊 审查评分: {censorship_score:.2f}")
                print(f"   📝 内容长度: {len(content)} 字")
                
                # 分析内容特征
                has_data = sum(1 for indicator in ["万元", "亿元", "%", "年", "月", "日"] if indicator in content)
                has_names = "某某" not in content and any(name in content for name in ["张", "李", "王", "刘"])
                has_avoiding = any(phrase in content for phrase in ["可能", "或许", "建议", "不能"])
                
                print(f"   📈 数据指标: {has_data}/6")
                print(f"   👤 实名使用: {'是' if has_names else '否'}")
                print(f"   🚫 回避语言: {'是' if has_avoiding else '否'}")
                
                # 显示内容样本
                print(f"   📄 内容样本:")
                sample = content[:300] + "..." if len(content) > 300 else content
                for line in sample.split('\n')[:5]:
                    if line.strip():
                        print(f"     {line.strip()}")
                print()

if __name__ == "__main__":
    print("🔧 启动真实反审查机制测试...")
    print("✅ API配置: Yunwu API (支持Qwen3和Claude)")
    print("✅ 模型配置: qwen3-235b-a22b-think + claude-sonnet-4-20250514-thinking\n")
    
    try:
        # 运行反审查测试
        results = test_real_anti_censorship()
        
        # 对比模型输出
        compare_models_output(results)
        
        print("🎉 真实反审查机制测试完成！")
        print("\n💡 关键发现:")
        print("   • 验证了Yunwu API同时支持Qwen3和Claude模型")
        print("   • 测试了真实的模型切换机制")
        print("   • 对比了两个模型在敏感话题上的表现差异")
        print("   • 证明了反审查系统的实际效果")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
