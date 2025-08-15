#!/usr/bin/env python3
"""
基于用户心理特征的真实化内容创作策略
完全摒弃AI味，回归真实人类表达
"""

from typing import Dict, Any

class PlatformSpecificPrompts:
    """去AI化的平台内容创作策略"""
    
    def __init__(self):
        # 基于用户心理痛点的真实化策略
        self.platform_configs = {
            "bilibili": {
                "psychological_core": "虚拟逃避与知识焦虑的脆弱一代",
                "pain_points": ["现实适应困难", "成人责任恐惧", "学习焦虑", "社交缺失"],
                "writing_voice": "理解包容，专业陪伴，温暖治愈",
                "forbidden_phrases": [
                    "让我们一起探讨", "引发了广泛关注", "深入研究发现", 
                    "通过分析", "为读者提供", "共同努力", "值得深思"
                ],
                "authentic_starters": [
                    "说个可能扎心的事实", "我发现一个有意思的现象", 
                    "最近刷到的数据把我震惊了", "分享个冷门但重要的观察"
                ]
            },
            "douyin": {
                "psychological_core": "即时满足与虚荣经济的成瘾机制",
                "pain_points": ["FOMO恐惧", "相对剥夺感", "现实扭曲", "冲动消费"],
                "writing_voice": "直接犀利，情绪共鸣，制造紧迫感",
                "forbidden_phrases": [
                    "让我们深入了解", "经过研究表明", "综合分析来看",
                    "为大家详细解释", "希望能够帮助", "值得关注"
                ],
                "authentic_starters": [
                    "这个真相绝了", "你绝对想不到", "刚刚被这个数据震撼了",
                    "必须曝光这件事", "看完你就明白了", "这才是真实情况"
                ]
            },
            "wechat": {
                "psychological_core": "权威崇拜与焦虑传播的中年群体",
                "pain_points": ["健康恐慌", "技术焦虑", "权威依赖", "社会边缘化"],
                "writing_voice": "权威专业，关怀理解，缓解焦虑",
                "forbidden_phrases": [
                    "年轻人都知道", "很简单的道理", "显而易见", 
                    "大家都明白", "这个时代", "互联网思维"
                ],
                "authentic_starters": [
                    "最近很多朋友问我", "作为过来人想说几句", 
                    "从专业角度分析", "这件事关系到每个家庭"
                ]
            },
            "xiaohongshu": {
                "psychological_core": "精致贫穷与容貌焦虑的消费陷阱",
                "pain_points": ["容貌焦虑", "社交比较压力", "消费主义陷阱", "经济负担"],
                "writing_voice": "理解同情，实用建议，缓解焦虑",
                "forbidden_phrases": [
                    "建议大家", "我们需要", "深入思考", "全面分析",
                    "理性看待", "客观来说", "综合考虑"
                ],
                "authentic_starters": [
                    "说个真心话", "分享个踩坑经历", "真的要提醒姐妹们",
                    "亲测有效的方法", "花了好多学费才明白"
                ]
            }
        }
    
    def get_writing_style_guide(self, platform: str) -> str:
        """获取去AI化的写作风格指南"""
        config = self.platform_configs.get(platform, self.platform_configs["wechat"])
        
        if platform == "bilibili":
            return f"""
# B站内容创作：治愈脆弱一代的真实表达

## 用户心理洞察
{config['psychological_core']}
核心痛点：{', '.join(config['pain_points'])}

## 写作原则
1. **拒绝说教**：不要告诉他们"应该怎样"，而是"我是这样做的"
2. **承认困难**：正视现实的复杂性，不回避问题的难度
3. **提供陪伴**：像朋友一样分享，而不是像老师一样教导
4. **温暖治愈**：在残酷现实中给予温暖，但不虚假安慰

## 语言特征
- 用"我发现"代替"研究表明"
- 用"可能"代替"一定"、"必须"
- 用具体故事代替抽象概念
- 用个人体验代替权威论断

## 开头方式（选择其一）
{chr(10).join([f'- {starter}' for starter in config['authentic_starters']])}

## 绝对禁用
{chr(10).join([f'❌ {phrase}' for phrase in config['forbidden_phrases']])}

## 情绪调性
理解 → 陪伴 → 温暖 → 希望（但不虚假）
"""

        elif platform == "douyin":
            return f"""
# 抖音内容：打破虚荣经济的直击表达

## 用户心理洞察  
{config['psychological_core']}
核心痛点：{', '.join(config['pain_points'])}

## 创作策略
1. **制造反差**：用数据和事实打破用户的固有认知
2. **直击痛点**：不绕弯子，直接说出用户不敢面对的真相
3. **制造紧迫感**：利用FOMO心理，但提供真实价值
4. **情绪共鸣**：理解用户的焦虑，但不放大恐惧

## 黄金3秒开场
{chr(10).join([f'- {starter}' for starter in config['authentic_starters']])}

## 内容结构
- 钩子（3秒内抓住注意力）
- 反转（打破预期）
- 揭秘（提供新信息）
- 行动（给出明确建议）

## 语言特色
- 短句，快节奏
- 数字对比，制造冲击
- 反问句引发思考
- 结尾留悬念或给建议

## 禁用套路
{chr(10).join([f'❌ {phrase}' for phrase in config['forbidden_phrases']])}
"""

        elif platform == "xiaohongshu":
            return f"""
# 小红书：缓解容貌焦虑的贴心分享

## 用户心理洞察
{config['psychological_core']}
核心痛点：{', '.join(config['pain_points'])}

## 分享原则
1. **真实体验**：分享真实的使用感受，包括失败经历
2. **成本透明**：诚实说明时间成本、金钱成本、机会成本
3. **降低门槛**：提供适合不同预算的选择方案
4. **心理疏导**：在变美的同时，缓解容貌焦虑

## 开场方式
{chr(10).join([f'- {starter}' for starter in config['authentic_starters']])}

## 内容要素
- 前后对比（真实不过度）
- 详细步骤（可操作性强）
- 成本说明（时间+金钱）
- 失败经验（避坑指南）
- 替代方案（不同预算）

## 情感温度
姐妹 → 理解 → 建议 → 陪伴

## 避免踩雷  
{chr(10).join([f'❌ {phrase}' for phrase in config['forbidden_phrases']])}
- 避免过度滤镜和不切实际的效果展示
- 不制造新的容貌焦虑
"""

        else:  # wechat
            return f"""
# 微信公众号：缓解中年焦虑的专业陪伴

## 用户心理洞察
{config['psychological_core']}  
核心痛点：{', '.join(config['pain_points'])}

## 写作策略
1. **权威但不高冷**：专业分析但语言温和
2. **理解中年困境**：不站在道德高地指责
3. **提供确定性**：在不确定的世界给出相对确定的建议
4. **家庭视角**：从家庭责任和下一代角度思考问题

## 开场方式
{chr(10).join([f'- {starter}' for starter in config['authentic_starters']])}

## 文章结构
- 现象观察（身边的真实案例）
- 深度分析（专业视角解读）
- 多方观点（平衡呈现）
- 实用建议（可操作的方案）

## 语言特点
- 成熟稳重，不急不躁
- 数据支撑，逻辑清晰
- 考虑周全，风险可控
- 温暖关怀，理解包容

## 表达禁忌
{chr(10).join([f'❌ {phrase}' for phrase in config['forbidden_phrases']])}
"""

    def get_topic_strategy(self, platform: str, topic: str) -> str:
        """针对具体话题的创作策略"""
        config = self.platform_configs.get(platform, self.platform_configs["wechat"])
        
        return f"""
# 话题策略：{topic}

## 平台用户心理
{config['psychological_core']}

## 内容角度选择
根据用户痛点，从以下角度切入：
{chr(10).join([f'- {pain}相关的具体影响' for pain in config['pain_points']])}

## 真实化表达
- 用具体数据代替模糊表述
- 用真实案例代替理论分析  
- 用个人观点代替官腔套话
- 用情感共鸣代替理性说教

## 避免AI化表达
{chr(10).join([f'- 不要说：{phrase}' for phrase in config['forbidden_phrases']])}

## 推荐开场
从这些方式中选择一个：
{chr(10).join([f'- {starter}' for starter in config['authentic_starters']])}
"""

    def get_research_integration_prompt(self, platform: str) -> str:
        """获取研究数据整合提示"""
        if platform == "bilibili":
            return """
研究数据使用策略（B站）：
- 不要直接引用"研究表明"，而是说"我看到一个数据"
- 用具体数字制造冲击："你知道吗，72%的中国女性对外貌不满意"
- 承认数据局限性："虽然这个调查可能有局限，但..."
- 结合个人观察："这跟我身边的情况很像"
"""
        elif platform == "douyin":
            return """
数据冲击策略（抖音）：
- 用对比制造震撼："你以为X，但实际上是Y"  
- 数字要具体："不是'很多人'，而是'2000万中国人'"
- 制造紧迫感："这个趋势正在加速"
- 联系个人："这可能就发生在你身上"
"""
        elif platform == "xiaohongshu":
            return """
数据温情化策略（小红书）：
- 数据要关联到个人体验："难怪我总觉得..."
- 提供解决方案："知道这个数据后，我们可以..."
- 降低焦虑："虽然数据看起来可怕，但我们有办法"
- 姐妹视角："姐妹们，这个数据我们得重视"
"""
        else:  # wechat
            return """
权威数据呈现（微信）：
- 引用权威来源但不过度崇拜
- 数据要服务于分析逻辑
- 承认复杂性："情况比数据显示的更复杂"
- 提供多角度解读："从不同角度看这个数据"
"""
