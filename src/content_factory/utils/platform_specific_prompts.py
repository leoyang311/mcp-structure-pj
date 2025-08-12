#!/usr/bin/env python3
"""
平台特定用户画像和内容策略
基于不同平台的监管环境和用户特征调整内容深度
"""

from typing import Dict, Any

class PlatformSpecificPrompts:
    """平台特定内容策略和用户画像"""
    
    def __init__(self):
        self.platform_configs = {
            "wechat": {
                "user_profile": "中产阶级，30-45岁，关注深度分析，风险厌恶",
                "content_style": "严谨专业，数据驱动，保守稳健",
                "sensitivity_level": "HIGH_CONSERVATIVE",
                "truth_depth": "SURFACE_ANALYTICAL",
                "risk_tolerance": "LOW"
            },
            "xiaohongshu": {
                "user_profile": "年轻女性，20-35岁，追求实用性，社交分享",
                "content_style": "亲和易懂，实用导向，适度谨慎",
                "sensitivity_level": "MEDIUM_CAUTIOUS", 
                "truth_depth": "PRACTICAL_ORIENTED",
                "risk_tolerance": "MEDIUM"
            },
            "bilibili": {
                "user_profile": "年轻用户，18-30岁，追求真相，敢于质疑",
                "content_style": "深度挖掘，批判思维，勇于探讨",
                "sensitivity_level": "MEDIUM_BOLD",
                "truth_depth": "DEEP_INVESTIGATIVE", 
                "risk_tolerance": "HIGH"
            },
            "douyin": {
                "user_profile": "大众用户，全年龄段，追求热点，快速消费",
                "content_style": "直接犀利，热点导向，适度挑战",
                "sensitivity_level": "MEDIUM_DIRECT",
                "truth_depth": "PROVOCATIVE_INSIGHT",
                "risk_tolerance": "MEDIUM_HIGH"
            }
        }
    
    def get_sensitive_topic_prompt(self, platform: str, topic: str) -> str:
        """获取敏感话题的平台特定处理策略"""
        config = self.platform_configs.get(platform, self.platform_configs["wechat"])
        
        if platform == "bilibili":
            return f"""
## B站深度分析策略 - {topic}

用户画像: {config['user_profile']}
内容要求: 深度挖掘，理性质疑，追求真相

### 内容原则:
1. **深度分析**: 不回避敏感点，但基于事实和逻辑
2. **批判思维**: 质疑官方叙事，探讨多元视角  
3. **信息透明**: 明确区分已证实事实、合理推测、个人观点
4. **理性讨论**: 鼓励深度思考，避免情绪化煽动

### 分析框架:
- 事实层面: 哪些是可以验证的硬事实?
- 信息缺口: 哪些关键信息被隐瞒或模糊处理?
- 利益分析: 各方的动机和利益考量是什么?
- 深层逻辑: 事件背后的结构性问题是什么?

### 表达策略:
- 使用"据可获得信息显示"、"从公开资料分析"等限定词
- 提出尖锐问题但给出分析路径
- 承认分析局限性，但不放弃深度思考
- 鼓励观众独立思考和进一步调研

注意: 追求真相但避免阴谋论，质疑但不诽谤，深度但负责任
"""
        
        elif platform == "douyin":
            return f"""
## 抖音直击策略 - {topic}  

用户画像: {config['user_profile']}
内容要求: 直接犀利，快速切中要害

### 内容原则:
1. **直击痛点**: 快速点出事件的核心问题
2. **数据说话**: 用硬数据揭示真相
3. **常识判断**: 运用常识逻辑质疑疑点
4. **引发思考**: 提出关键问题让用户自己判断

### 表达策略:
- 开门见山，直接提出核心疑问
- 用对比数据揭示不合理之处  
- "你们有没有想过..."、"这里有个问题..."的引导式提问
- 避免下结论，但提供判断工具

### 内容特色:
- 节奏快，信息密度高
- 重点信息重复强调
- 用反问句引发思考
- 结尾留下关键问题

注意: 犀利但不恶意，质疑但提供依据，引导思考但不代替判断
"""
        
        elif platform == "xiaohongshu":
            return f"""
## 小红书理性分享策略 - {topic}

用户画像: {config['user_profile']}  
内容要求: 理性分析，实用指导，适度深入

### 内容原则:
1. **理性态度**: 保持冷静客观，避免情绪化
2. **实用导向**: 重点关注对个人的实际影响
3. **信息素养**: 教授辨识信息真伪的方法
4. **适度质疑**: 提出合理质疑但不过度解读

### 分析方向:
- 个人影响: 这个事件对普通人意味着什么?
- 信息判断: 如何在复杂信息中保持理性?
- 实用建议: 面对类似情况应该怎么做?
- 长期思考: 这类事件的深层影响是什么?

注意: 深度适中，避免过于激进或过于保守
"""
        
        else:  # wechat 默认
            return f"""
## 微信深度分析策略 - {topic}

用户画像: {config['user_profile']}
内容要求: 专业严谨，数据驱动，深度分析

### 内容原则:
1. **专业分析**: 基于扎实的信息基础进行分析
2. **多角度视角**: 呈现不同立场和观点
3. **风险评估**: 充分评估各种可能性和风险
4. **理性建议**: 提供基于分析的理性建议

### 分析框架:
- 背景分析: 事件的历史和现实背景
- 多方观点: 各利益相关方的立场分析  
- 深层逻辑: 事件反映的深层次问题
- 发展趋势: 可能的发展方向和影响

注意: 保持专业性和客观性，避免偏激表达
"""
    
    def get_industry_analysis_prompt(self, platform: str) -> str:
        """获取产业分析的平台特定策略"""
        config = self.platform_configs.get(platform, self.platform_configs["wechat"])
        
        if platform == "bilibili":
            return """
### B站产业分析 - 深度挖掘真相

**分析重点**:
1. **数据深挖**: 不只看表面数字，挖掘数据背后的真实含义
2. **利益链条**: 分析产业链各方的利益分配和博弈
3. **技术真相**: 剥离营销包装，探讨真实的技术实力
4. **市场逻辑**: 质疑过度炒作，探讨真实的商业逻辑

**内容策略**:
- 对比分析官方数据和第三方数据的差异
- 深入分析财报数字背后的真实情况
- 质疑过度乐观的预测和承诺
- 探讨行业内部人士的真实看法
"""
        
        elif platform == "douyin":
            return """
### 抖音产业分析 - 直击要害

**核心策略**:
1. **数据对比**: 用对比数据快速揭示问题
2. **常识判断**: 用常识逻辑质疑不合理现象  
3. **关键问题**: 直接提出核心疑问
4. **实用建议**: 给出明确的行动指导

**表达特点**:
- "你知道真实情况吗?"开场
- 用数据对比制造反差
- 直接指出问题所在
- 结尾给出明确建议
"""
        
        return "标准产业分析策略"
    
    def get_policy_analysis_prompt(self, platform: str) -> str:
        """获取政策解读的平台特定策略"""
        config = self.platform_configs.get(platform, self.platform_configs["wechat"])
        
        if platform == "bilibili":
            return """
### B站政策解读 - 深度分析

**分析维度**:
1. **政策逻辑**: 政策出台的真实动机和背景
2. **利益格局**: 政策受益者和受损者分析
3. **执行现实**: 政策理想与执行现实的差距
4. **长远影响**: 政策的深层影响和潜在风险

**质疑角度**:
- 官方表述与实际效果的差距
- 政策时机选择的深层考量
- 不同利益集团的博弈情况
- 政策可能的意外后果
"""
        
        elif platform == "douyin":
            return """
### 抖音政策解读 - 直击核心

**核心策略**:
1. **直击痛点**: 政策对普通人的真实影响
2. **数据说话**: 用数据揭示政策效果  
3. **常识判断**: 用常识质疑政策逻辑
4. **实用指导**: 告诉用户应该怎么做

**表达重点**:
- "这个政策真正影响的是..."
- "数据告诉我们真相是..."
- "你需要知道的关键点是..."
- "普通人应该..."
"""
        
        return "标准政策分析策略"
