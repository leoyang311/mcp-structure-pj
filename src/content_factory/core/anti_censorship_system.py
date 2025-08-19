"""
反审查内容生成系统
Anti-Censorship Content Generation System

当检测到模型输出被审查、话题偏移或质量异常时，
自动切换到非中国模型（如Claude）重新生成内容。
"""

import re
import os
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class CensorshipLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class CensorshipDetectionResult:
    """审查检测结果"""
    level: CensorshipLevel
    confidence: float
    triggers: List[str]
    original_content: str
    recommended_action: str
    detection_details: Dict

class CensorshipDetector:
    """审查内容检测器"""
    
    def __init__(self):
        self.censorship_keywords = [
            # 法规借口类
            "网络信息内容生态治理规定",
            "不能编造",
            "虚假信息", 
            "法律法规严禁",
            "违反相关法规",
            "不符合事实",
            "无法验证",
            "敏感信息",
            "政治敏感",
            "不当内容",
            "Sorry, I can't assist with that",
            
            # 回避装傻类  
            "可能是个错误",
            "没有记录",
            "不是知名人物",
            "可能犯了拼写错误",
            "或许是误写",
            "可能是个虚构",
            "我不能创建虚假内容",
            "基于事实",
            "如果事件不存在",
            
            # CCP维稳类
            "维护网络环境",
            "正能量",
            "和谐社会",
            "国家安全",
            "社会稳定",
            "不传谣不信谣",
            "理性看待",
            "客观分析"
        ]
        
        self.topic_drift_patterns = [
            r"让我们谈论其他",
            r"我们应该关注",
            r"更合适的话题",
            r"建议讨论",
            r"不如我们",
            r"换个角度"
        ]
        
        self.quality_indicators = [
            "CASE", "具体数据", "实名", "报告编号", 
            "年月日", "百分比", "万元", "亿元"
        ]

    def detect_censorship(self, content: str, expected_topic: str, expected_length: int = 1000) -> CensorshipDetectionResult:
        """检测内容是否被审查"""
        
        triggers = []
        confidence = 0.0
        details = {}
        
        # 1. 关键词检测
        keyword_score = self._check_censorship_keywords(content)
        if keyword_score > 0:
            triggers.append("审查关键词")
            confidence += keyword_score * 0.4
            details["censorship_keywords"] = keyword_score
        
        # 2. 话题偏移检测
        drift_score = self._check_topic_drift(content, expected_topic)
        if drift_score > 0:
            triggers.append("话题偏移")
            confidence += drift_score * 0.3
            details["topic_drift"] = drift_score
            
        # 3. 长度异常检测
        length_score = self._check_length_anomaly(content, expected_length)
        if length_score > 0:
            triggers.append("长度异常")
            confidence += length_score * 0.2
            details["length_anomaly"] = length_score
            
        # 4. 质量指标检测
        quality_score = self._check_quality_indicators(content)
        if quality_score < 0.3:
            triggers.append("质量异常")
            confidence += (1 - quality_score) * 0.3
            details["quality_deficit"] = quality_score
            
        # 5. 结构完整性检测
        structure_score = self._check_structure_completeness(content)
        if structure_score < 0.5:
            triggers.append("结构不完整")
            confidence += (1 - structure_score) * 0.2
            details["structure_incomplete"] = structure_score
        
        # 确定审查级别
        level = self._determine_censorship_level(confidence)
        
        # 推荐行动
        action = self._recommend_action(level)
        
        return CensorshipDetectionResult(
            level=level,
            confidence=min(confidence, 1.0),
            triggers=triggers,
            original_content=content,
            recommended_action=action,
            detection_details=details
        )
    
    def _check_censorship_keywords(self, content: str) -> float:
        """检查审查关键词"""
        score = 0.0
        for keyword in self.censorship_keywords:
            if keyword in content:
                if any(x in keyword for x in ["法规", "违反", "不能"]):
                    score += 0.8  # 高权重审查词
                else:
                    score += 0.3  # 一般审查词
        return min(score, 1.0)
    
    def _check_topic_drift(self, content: str, expected_topic: str) -> float:
        """检查话题偏移"""
        # 简单的关键词匹配
        topic_keywords = expected_topic.split()
        found_keywords = sum(1 for kw in topic_keywords if kw in content)
        
        if len(topic_keywords) == 0:
            return 0.0
            
        coverage = found_keywords / len(topic_keywords)
        
        # 检查偏移模式
        drift_patterns_found = sum(1 for pattern in self.topic_drift_patterns 
                                 if re.search(pattern, content))
        
        drift_score = 1.0 - coverage + (drift_patterns_found * 0.2)
        return min(drift_score, 1.0)
    
    def _check_length_anomaly(self, content: str, expected_length: int) -> float:
        """检查长度异常"""
        actual_length = len(content)
        if expected_length == 0:
            return 0.0
            
        ratio = actual_length / expected_length
        
        if ratio < 0.3:  # 内容过短，可能被截断
            return 1.0 - ratio
        elif ratio > 3.0:  # 内容过长，可能有灌水
            return (ratio - 3.0) / 5.0
        
        return 0.0
    
    def _check_quality_indicators(self, content: str) -> float:
        """检查质量指标"""
        found_indicators = sum(1 for indicator in self.quality_indicators 
                             if indicator in content)
        
        return found_indicators / len(self.quality_indicators)
    
    def _check_structure_completeness(self, content: str) -> float:
        """检查结构完整性（DEPTH+CASE）"""
        required_elements = ["具体", "数据", "案例", "专家"]
        found_elements = sum(1 for element in required_elements 
                           if element in content)
        
        return found_elements / len(required_elements)
    
    def _determine_censorship_level(self, confidence: float) -> CensorshipLevel:
        """确定审查级别"""
        if confidence >= 0.8:
            return CensorshipLevel.CRITICAL
        elif confidence >= 0.6:
            return CensorshipLevel.HIGH
        elif confidence >= 0.4:
            return CensorshipLevel.MEDIUM
        elif confidence >= 0.2:
            return CensorshipLevel.LOW
        else:
            return CensorshipLevel.NONE
    
    def _recommend_action(self, level: CensorshipLevel) -> str:
        """推荐处理行动"""
        actions = {
            CensorshipLevel.NONE: "无需行动",
            CensorshipLevel.LOW: "监控观察",
            CensorshipLevel.MEDIUM: "考虑切换模型",
            CensorshipLevel.HIGH: "建议切换模型",
            CensorshipLevel.CRITICAL: "立即切换模型"
        }
        return actions[level]

class ModelSwitcher:
    """模型切换器"""
    
    def __init__(self):
        self.model_configs = {
            "qwen3": {
                "api_base": os.getenv("YUNWU_API_BASE"),
                "api_key": os.getenv("YUNWU_API_KEY"),
                "model_name": os.getenv("MODEL_NAME", "qwen3-235b-a22b-think"),
                "region": "china",
                "censorship_risk": "high"
            },
            "claude": {
                "api_base": os.getenv("CLAUDE_API_BASE", "https://api.anthropic.com"),
                "api_key": os.getenv("CLAUDE_API_KEY"),
                "model_name": os.getenv("BACKUP_MODEL_NAME", "claude-sonnet-4-20250514-thinking"),
                "region": "western",
                "censorship_risk": "low"
            },
            "gpt4": {
                "api_base": "https://api.openai.com/v1",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model_name": "gpt-4-turbo",
                "region": "western", 
                "censorship_risk": "low"
            }
        }
        
        self.switch_history = []
    
    def should_switch(self, detection_result: CensorshipDetectionResult) -> bool:
        """判断是否应该切换模型"""
        return detection_result.level in [CensorshipLevel.HIGH, CensorshipLevel.CRITICAL]
    
    def get_backup_model(self, current_model: str) -> str:
        """获取备用模型"""
        # 如果当前是中国模型，切换到西方模型
        current_config = self.model_configs.get(current_model, {})
        
        if current_config.get("region") == "china":
            # 优先选择Claude，其次GPT-4
            if self.model_configs["claude"]["api_key"]:
                return "claude"
            elif self.model_configs["gpt4"]["api_key"]:
                return "gpt4"
        
        # 默认返回claude
        return "claude"
    
    def log_switch(self, original_model: str, new_model: str, reason: str, detection_result: CensorshipDetectionResult):
        """记录模型切换"""
        switch_record = {
            "timestamp": datetime.now().isoformat(),
            "original_model": original_model,
            "new_model": new_model,
            "reason": reason,
            "censorship_level": detection_result.level.name,
            "confidence": detection_result.confidence,
            "triggers": detection_result.triggers
        }
        
        self.switch_history.append(switch_record)
        
        # 保存到文件
        log_file = "model_switch_log.json"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(switch_record, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to log model switch: {e}")

class AntiCensorshipContentGenerator:
    """反审查内容生成器"""
    
    def __init__(self):
        self.detector = CensorshipDetector()
        self.switcher = ModelSwitcher()
        self.max_retries = 2
        
    def generate_content(self, prompt: str, topic: str, expected_length: int = 1000, 
                        preferred_model: str = "qwen3") -> Dict:
        """生成内容（带反审查机制）"""
        
        results = {
            "final_content": "",
            "model_used": preferred_model,
            "switches_made": [],
            "detection_results": [],
            "success": False
        }
        
        current_model = preferred_model
        
        for attempt in range(self.max_retries + 1):
            try:
                # 使用当前模型生成内容
                content = self._generate_with_model(prompt, current_model)
                
                # 检测审查
                detection = self.detector.detect_censorship(content, topic, expected_length)
                results["detection_results"].append({
                    "attempt": attempt + 1,
                    "model": current_model,
                    "detection": detection
                })
                
                # 如果内容质量可接受
                if detection.level in [CensorshipLevel.NONE, CensorshipLevel.LOW]:
                    results["final_content"] = content
                    results["model_used"] = current_model
                    results["success"] = True
                    break
                
                # 如果需要切换模型
                if self.switcher.should_switch(detection) and attempt < self.max_retries:
                    backup_model = self.switcher.get_backup_model(current_model)
                    
                    # 记录切换
                    self.switcher.log_switch(
                        current_model, 
                        backup_model, 
                        f"Censorship detected: {detection.triggers}",
                        detection
                    )
                    
                    results["switches_made"].append({
                        "from": current_model,
                        "to": backup_model,
                        "reason": detection.triggers,
                        "attempt": attempt + 1
                    })
                    
                    current_model = backup_model
                    logger.warning(f"Switching from {current_model} to {backup_model} due to censorship detection")
                
                else:
                    # 最后一次尝试，使用最好的结果
                    results["final_content"] = content
                    results["model_used"] = current_model
                    results["success"] = detection.level != CensorshipLevel.CRITICAL
                    break
                    
            except Exception as e:
                logger.error(f"Error generating content with {current_model}: {e}")
                if attempt < self.max_retries:
                    current_model = self.switcher.get_backup_model(current_model)
                else:
                    results["error"] = str(e)
                    break
        
        return results
    
    def _generate_with_model(self, prompt: str, model: str) -> str:
        """使用指定模型生成内容"""
        # 这里应该调用相应的模型API
        # 为了演示，我们返回一个模拟结果
        
        model_config = self.switcher.model_configs.get(model, {})
        
        if model == "claude":
            # 调用Claude API
            return self._call_claude_api(prompt, model_config)
        elif model == "qwen3":
            # 调用Qwen API  
            return self._call_qwen_api(prompt, model_config)
        elif model == "gpt4":
            # 调用GPT-4 API
            return self._call_openai_api(prompt, model_config)
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    def _call_claude_api(self, prompt: str, config: Dict) -> str:
        """调用Claude API（通过Yunwu API）"""
        import requests
        
        api_base = config.get("api_base", "https://yunwu.ai/v1")
        api_key = config.get("api_key")
        model_name = config.get("model_name", "claude-sonnet-4-20250514-thinking")
        
        if not api_key:
            raise ValueError("Claude API key not configured")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Claude API error {response.status_code}: {response.text}")
    
    def _call_qwen_api(self, prompt: str, config: Dict) -> str:
        """调用Qwen API"""
        # 使用现有的OpenAI客户端
        from .openai_client import get_openai_client
        
        client = get_openai_client()
        
        response = client.chat.completions.create(
            model=config.get("model_name", "qwen3-235b-a22b-think"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=3000
        )
        
        return response.choices[0].message.content
    
    def _call_openai_api(self, prompt: str, config: Dict) -> str:
        """调用OpenAI API"""
        # 实现OpenAI API调用
        pass

# 配置文件生成
def generate_config_template():
    """生成配置文件模板"""
    config = {
        "anti_censorship": {
            "enabled": True,
            "detection_sensitivity": 0.6,
            "auto_switch_threshold": 0.7,
            "max_retries": 2,
            "log_switches": True
        },
        "models": {
            "primary": "qwen3",
            "backup": ["claude", "gpt4"],
            "fallback": "claude"
        },
        "censorship_detection": {
            "check_keywords": True,
            "check_topic_drift": True,
            "check_length_anomaly": True,
            "check_quality": True,
            "minimum_quality_score": 0.3
        }
    }
    
    with open("anti_censorship_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # 运行时测试可以移动到单独的测试文件
    pass
