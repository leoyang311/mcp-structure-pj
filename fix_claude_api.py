#!/usr/bin/env python3
"""
修复反审查系统中的Claude调用问题
Fix Claude API Call Issues in Anti-Censorship System
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class FixedAntiCensorshipGenerator:
    """修复版反审查内容生成器"""
    
    def __init__(self):
        # API配置
        self.api_key = os.getenv('YUNWU_API_KEY', os.getenv('OPENAI_API_KEY'))
        self.api_base = os.getenv('YUNWU_API_BASE', os.getenv('OPENAI_API_BASE', 'https://yunwu.ai/v1'))
        
        # 检查是否有Claude配置
        self.claude_api_key = os.getenv('CLAUDE_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_GPT4_API_KEY')
        
        # 确定可用的备用模型
        self.backup_available = bool(self.claude_api_key or self.openai_api_key)
        
        print(f"✅ Yunwu API: {self.api_base}")
        print(f"🔧 Claude可用: {'是' if self.claude_api_key else '否'}")
        print(f"🔧 OpenAI可用: {'是' if self.openai_api_key else '否'}")
        print(f"🛡️  备用模型: {'已配置' if self.backup_available else '未配置'}")
        
        if not self.backup_available:
            print("⚠️  警告: 没有配置备用模型，反审查功能将降级为Yunwu内模型切换")
        
        # 审查检测关键词
        self.censorship_indicators = [
            "网络信息内容生态治理规定", "不能编造", "虚假信息", "法律法规严禁",
            "违反相关法规", "不符合事实", "无法验证", "敏感信息", "政治敏感",
            "可能是个错误", "没有记录", "不是知名人物", "可能犯了拼写错误", 
            "或许是误写", "可能是个虚构", "我不能创建虚假内容", "如果事件不存在",
            "维护网络环境", "正能量", "和谐社会", "不传谣不信谣", "理性看待", "客观分析"
        ]

    def detect_censorship(self, content: str) -> Dict:
        """检测内容是否被审查"""
        
        triggers = []
        score = 0.0
        
        # 检查审查关键词
        for keyword in self.censorship_indicators:
            if keyword in content:
                triggers.append(keyword)
                if any(x in keyword for x in ["法规", "违反", "不能", "虚假"]):
                    score += 0.8
                else:
                    score += 0.3
        
        # 检查内容长度异常
        if len(content) < 500:
            triggers.append("内容过短")
            score += 0.4
        
        # 检查质量指标缺失
        quality_indicators = ["具体", "数据", "案例", "专家", "报告", "年", "月", "日"]
        missing_indicators = sum(1 for indicator in quality_indicators if indicator not in content)
        if missing_indicators > 6:
            triggers.append("质量指标缺失")
            score += 0.3
        
        censorship_detected = score >= 0.6
        
        return {
            "censorship_detected": censorship_detected,
            "censorship_score": min(score, 1.0),
            "triggers": triggers,
            "recommendation": "切换模型" if censorship_detected else "继续使用"
        }

    def call_yunwu_api(self, prompt: str, model_name: str = None) -> Dict:
        """调用Yunwu API"""
        
        if not model_name:
            model_name = os.getenv('MODEL_NAME', 'qwen3-235b-a22b-think')
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "content": data["choices"][0]["message"]["content"],
                    "model": model_name,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "content": "",
                    "model": model_name,
                    "error": f"API调用失败: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "model": model_name,
                "error": str(e)
            }

    def call_alternative_model(self, prompt: str) -> Dict:
        """调用备用模型（Claude或OpenAI）"""
        
        if self.claude_api_key:
            return self._call_claude_api(prompt)
        elif self.openai_api_key:
            return self._call_openai_api(prompt)
        else:
            # 如果没有外部备用，尝试其他Yunwu模型
            return self._try_yunwu_alternatives(prompt)

    def _call_claude_api(self, prompt: str) -> Dict:
        """调用Claude API"""
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.claude_api_key)
            
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "success": True,
                "content": message.content[0].text,
                "model": "claude-3-sonnet",
                "error": None
            }
            
        except ImportError:
            return {
                "success": False,
                "content": "",
                "model": "claude",
                "error": "anthropic库未安装"
            }
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "model": "claude",
                "error": str(e)
            }

    def _call_openai_api(self, prompt: str) -> Dict:
        """调用OpenAI API"""
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "content": data["choices"][0]["message"]["content"],
                    "model": "gpt-4",
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "content": "",
                    "model": "gpt-4", 
                    "error": f"OpenAI API调用失败: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "model": "gpt-4",
                "error": str(e)
            }

    def _try_yunwu_alternatives(self, prompt: str) -> Dict:
        """尝试Yunwu的其他模型作为备用"""
        
        alternative_models = [
            "claude-sonnet-4-20250514-thinking",  # 如果Yunwu支持Claude
            "gpt-4-turbo",                        # 如果Yunwu支持GPT-4
            "deepseek-v3-chat",                   # 其他替代模型
            "qwen2.5-72b-instruct"               # Qwen的其他版本
        ]
        
        for model in alternative_models:
            print(f"🔄 尝试备用模型: {model}")
            result = self.call_yunwu_api(prompt, model)
            
            if result["success"]:
                print(f"✅ 备用模型 {model} 调用成功")
                return result
            else:
                print(f"❌ 备用模型 {model} 调用失败: {result['error']}")
        
        # 如果所有备用都失败，返回错误
        return {
            "success": False,
            "content": "",
            "model": "backup_failed",
            "error": "所有备用模型调用失败"
        }

    def generate_with_anti_censorship(self, prompt: str, topic: str) -> Dict:
        """使用反审查机制生成内容"""
        
        result = {
            "final_content": "",
            "model_used": "qwen3",
            "censorship_detected": False,
            "switch_occurred": False,
            "attempts": [],
            "quality_score": 0.0,
            "success": False
        }
        
        # 第一次尝试：使用主要模型（Qwen3）
        print(f"🔥 使用主要模型生成内容...")
        primary_result = self.call_yunwu_api(prompt)
        
        attempt_1 = {
            "model": "qwen3",
            "success": primary_result["success"],
            "content": primary_result["content"],
            "error": primary_result.get("error")
        }
        result["attempts"].append(attempt_1)
        
        if primary_result["success"]:
            # 检测审查
            censorship_result = self.detect_censorship(primary_result["content"])
            result["censorship_detected"] = censorship_result["censorship_detected"]
            
            if not censorship_result["censorship_detected"]:
                # 没有审查，使用原始内容
                result["final_content"] = primary_result["content"]
                result["model_used"] = "qwen3"
                result["quality_score"] = self._evaluate_quality(primary_result["content"])
                result["success"] = True
                print(f"✅ 主要模型生成成功，未检测到审查")
                return result
            else:
                print(f"🚨 检测到审查，触发器: {censorship_result['triggers']}")
                
        # 第二次尝试：使用备用模型
        if self.backup_available or True:  # 总是尝试备用
            print(f"🔄 切换到备用模型...")
            backup_result = self.call_alternative_model(prompt)
            
            attempt_2 = {
                "model": backup_result["model"],
                "success": backup_result["success"],
                "content": backup_result["content"],
                "error": backup_result.get("error")
            }
            result["attempts"].append(attempt_2)
            result["switch_occurred"] = True
            
            if backup_result["success"]:
                result["final_content"] = backup_result["content"]
                result["model_used"] = backup_result["model"]
                result["quality_score"] = self._evaluate_quality(backup_result["content"])
                result["success"] = True
                print(f"✅ 备用模型生成成功")
                return result
            else:
                print(f"❌ 备用模型调用失败: {backup_result['error']}")
        
        # 如果都失败，使用原始内容（即使被审查）
        if primary_result["success"]:
            result["final_content"] = primary_result["content"]
            result["model_used"] = "qwen3"
            result["quality_score"] = self._evaluate_quality(primary_result["content"])
            result["success"] = True
        
        return result

    def _evaluate_quality(self, content: str) -> float:
        """评估内容质量"""
        
        if not content or len(content) < 100:
            return 0.0
        
        score = 0.0
        
        # 长度评分
        if len(content) >= 1000:
            score += 0.2
        elif len(content) >= 500:
            score += 0.1
        
        # 结构评分
        structure_indicators = ["##", "**", "###", "1.", "2.", "3."]
        found_structure = sum(1 for indicator in structure_indicators if indicator in content)
        score += min(found_structure * 0.1, 0.3)
        
        # 数据评分
        data_indicators = ["年", "月", "日", "%", "万", "亿", "元", "人", "个", "项"]
        found_data = sum(1 for indicator in data_indicators if indicator in content)
        score += min(found_data * 0.05, 0.4)
        
        # 专业性评分
        professional_indicators = ["报告", "数据", "分析", "研究", "专家", "机构"]
        found_professional = sum(1 for indicator in professional_indicators if indicator in content)
        score += min(found_professional * 0.05, 0.1)
        
        return min(score, 1.0)

def test_fixed_anti_censorship():
    """测试修复后的反审查系统"""
    
    print("🧪 测试修复后的反审查系统")
    print("="*60)
    
    generator = FixedAntiCensorshipGenerator()
    
    # 测试敏感话题
    sensitive_prompt = """
    请基于DEPTH+CASE框架，深度分析澳洲杨lanlan事件潜在看到的红色家族执掌巨额财产问题。

    要求：
    1. 使用具体数据和精确时间（年月日）
    2. 引用真实案例和实名专家
    3. 包含财务数据和政策条款
    4. 字数1500字以上
    5. 信息密度≥0.8（每100字4+数据点）
    6. CASE合规率≥90%
    """
    
    print("📋 测试敏感话题处理...")
    result = generator.generate_with_anti_censorship(
        prompt=sensitive_prompt,
        topic="澳洲杨lanlan事件分析"
    )
    
    # 输出结果
    print("\n📊 测试结果:")
    print(f"  成功: {result['success']}")
    print(f"  使用模型: {result['model_used']}")
    print(f"  检测到审查: {result['censorship_detected']}")
    print(f"  发生切换: {result['switch_occurred']}")
    print(f"  质量评分: {result['quality_score']:.2f}")
    print(f"  尝试次数: {len(result['attempts'])}")
    print(f"  内容长度: {len(result['final_content'])}")
    
    if result["final_content"]:
        print(f"\n📄 生成内容预览:")
        preview = result["final_content"][:200] + "..." if len(result["final_content"]) > 200 else result["final_content"]
        print(preview)
    
    return result

if __name__ == "__main__":
    test_fixed_anti_censorship()
