"""
基于真实用户画像的内容策略优化器
根据platform-analysis-doc.md构建精准的内容适配策略
"""

from typing import Dict, List, Any, Optional
from ..models import Platform
from .user_persona import get_user_persona, get_platform_algorithm_weights

class PersonaBasedContentOptimizer:
    """基于用户画像的内容优化器"""
    
    def __init__(self):
        self.personas = {platform: get_user_persona(platform) for platform in Platform}
        self.algorithm_weights = {platform: get_platform_algorithm_weights(platform) for platform in Platform}
    
    def optimize_content_for_persona(self, content: str, platform: Platform, topic: str) -> Dict[str, Any]:
        """基于用户画像优化内容"""
        persona = self.personas[platform]
        
        optimization_suggestions = {
            "platform": platform.value,
            "user_profile": self._get_user_profile_summary(persona),
            "content_adjustments": self._get_content_adjustments(content, persona, topic),
            "title_suggestions": self._get_title_suggestions(topic, persona),
            "engagement_optimization": self._get_engagement_optimization(persona),
            "algorithm_tips": self._get_algorithm_tips(platform),
            "demographic_matching": self._check_demographic_matching(content, persona)
        }
        
        return optimization_suggestions
    
    def _get_user_profile_summary(self, persona) -> Dict[str, Any]:
        """获取用户画像摘要"""
        demographics = persona.demographics
        behavior = persona.behavior
        
        # 找到主要用户群体
        main_age_group = max(demographics.age_distribution.items(), key=lambda x: x[1])
        main_gender = max(demographics.gender_ratio.items(), key=lambda x: x[1])
        main_location = max(demographics.location_distribution.items(), key=lambda x: x[1])
        main_education = max(demographics.education_level.items(), key=lambda x: x[1])
        
        return {
            "primary_demographics": {
                "age": f"{main_age_group[0]} ({main_age_group[1]*100:.0f}%)",
                "gender": f"{main_gender[0]} ({main_gender[1]*100:.0f}%)", 
                "location": f"{main_location[0]} ({main_location[1]*100:.0f}%)",
                "education": f"{main_education[0]} ({main_education[1]*100:.0f}%)"
            },
            "key_interests": behavior.interests[:3],
            "core_behaviors": behavior.behavior_traits[:3],
            "main_needs": behavior.core_needs
        }
    
    def _get_content_adjustments(self, content: str, persona, topic: str) -> List[str]:
        """获取内容调整建议"""
        adjustments = []
        preferences = persona.content_preferences
        behavior = persona.behavior
        
        # 基于平台特定建议
        if persona.platform == Platform.BILIBILI:
            if "学习" not in content and "教程" not in content:
                adjustments.append("增加学习价值和教程元素，符合B站用户的学习导向")
            if len(content) < 1000:
                adjustments.append("内容深度不足，B站用户偏好深度内容(建议1000-2500字)")
            adjustments.append("添加章节划分和知识点总结，便于用户学习和回看")
            
        elif persona.platform == Platform.DOUYIN:
            if len(content) > 500:
                adjustments.append("内容过长，抖音用户习惯快速消费(建议200-500字)")
            adjustments.append("增强情绪价值，添加能引起共鸣的情感元素")
            adjustments.append("优化开头3秒，确保立即抓住注意力")
            
        elif persona.platform == Platform.WECHAT:
            if len(content) < 2000:
                adjustments.append("内容深度不够，微信用户期待深度分析(建议2000-5000字)")
            adjustments.append("添加数据支撑和权威引用，提升专业性")
            adjustments.append("优化分享价值，增加社交讨论性")
            
        elif persona.platform == Platform.XIAOHONGSHU:
            adjustments.append("增加真实体验分享和使用心得")
            adjustments.append("添加实用教程和步骤说明")
            adjustments.append("考虑视觉呈现，规划高质量配图需求")
        
        return adjustments
    
    def _get_title_suggestions(self, topic: str, persona) -> List[str]:
        """获取标题建议"""
        suggestions = []
        
        if persona.platform == Platform.BILIBILI:
            suggestions.extend([
                f"深度解析：{topic}背后的原理",
                f"从0到1教你掌握{topic}",
                f"这个{topic}方法让我效率提升300%"
            ])
            
        elif persona.platform == Platform.DOUYIN:
            suggestions.extend([
                f"关于{topic}，你绝对想不到的真相",
                f"看完这个{topic}，我整个人都不好了",
                f"{topic}？这个操作太绝了！"
            ])
            
        elif persona.platform == Platform.WECHAT:
            suggestions.extend([
                f"深度分析：{topic}的5个关键趋势",
                f"为什么90%的人对{topic}的理解都错了",
                f"关于{topic}，这些数据告诉我们真相"
            ])
            
        elif persona.platform == Platform.XIAOHONGSHU:
            suggestions.extend([
                f"超全{topic}攻略！姐妹们收藏好",
                f"30天{topic}实战经验，避坑指南来了",
                f"{topic}真实体验分享+详细教程"
            ])
            
        return suggestions
    
    def _get_engagement_optimization(self, persona) -> Dict[str, List[str]]:
        """获取互动优化建议"""
        engagement_features = persona.content_preferences.engagement_features
        
        optimization = {
            "interaction_design": [],
            "call_to_action": [],
            "community_building": []
        }
        
        if persona.platform == Platform.BILIBILI:
            optimization["interaction_design"] = ["设置弹幕互动点", "添加投票问题", "设计彩蛋环节"]
            optimization["call_to_action"] = ["引导三连(点赞投币收藏)", "鼓励弹幕讨论", "提供补充资料"]
            optimization["community_building"] = ["回复优质弹幕", "定期总结讨论", "建立学习群组"]
            
        elif persona.platform == Platform.DOUYIN:
            optimization["interaction_design"] = ["结尾提出问题", "设计争议点", "使用热门音乐"]
            optimization["call_to_action"] = ["引导点赞评论", "鼓励分享转发", "关注后续内容"]
            optimization["community_building"] = ["积极回复评论", "参与话题挑战", "与粉丝互动"]
            
        elif persona.platform == Platform.WECHAT:
            optimization["interaction_design"] = ["文末讨论话题", "投票互动", "问题征集"]
            optimization["call_to_action"] = ["引导转发分享", "鼓励在看点赞", "留言讨论"]
            optimization["community_building"] = ["建立读者群", "定期互动", "内容共创"]
            
        elif persona.platform == Platform.XIAOHONGSHU:
            optimization["interaction_design"] = ["评论区答疑", "私信福利", "话题标签"]
            optimization["call_to_action"] = ["引导收藏点赞", "鼓励分享体验", "关注更新"]
            optimization["community_building"] = ["真诚回复评论", "分享更多心得", "建立信任关系"]
            
        return optimization
    
    def _get_algorithm_tips(self, platform: Platform) -> Dict[str, str]:
        """获取算法优化建议"""
        weights = self.algorithm_weights[platform]
        tips = {}
        
        for metric, weight in weights.items():
            if platform == Platform.BILIBILI:
                if metric == "完播率":
                    tips[metric] = f"权重{weight*100:.0f}% - 设置章节，控制节奏，避免注水内容"
                elif metric == "互动率":
                    tips[metric] = f"权重{weight*100:.0f}% - 弹幕互动点，投票卡片，积极回复"
                elif metric == "收藏率":
                    tips[metric] = f"权重{weight*100:.0f}% - 提供干货价值，制作总结清单"
                elif metric == "点赞率":
                    tips[metric] = f"权重{weight*100:.0f}% - 情感共鸣，价值认同"
                    
            elif platform == Platform.DOUYIN:
                if metric == "完播率":
                    tips[metric] = f"权重{weight*100:.0f}% - 控制时长，黄金3秒钩子，结尾悬念"
                elif metric == "点赞率":
                    tips[metric] = f"权重{weight*100:.0f}% - 情绪价值，视觉冲击，共鸣内容"
                elif metric == "评论率":
                    tips[metric] = f"权重{weight*100:.0f}% - 争议话题，互动问题，引发讨论"
                elif metric == "转发率":
                    tips[metric] = f"权重{weight*100:.0f}% - 实用价值，社交货币，分享动机"
                    
            elif platform == Platform.WECHAT:
                if metric == "阅读完成率":
                    tips[metric] = f"权重{weight*100:.0f}% - 段落精简，配图丰富，结构清晰"
                elif metric == "分享率":
                    tips[metric] = f"权重{weight*100:.0f}% - 观点独特，社交价值，讨论性强"
                elif metric == "在看率":
                    tips[metric] = f"权重{weight*100:.0f}% - 引发共鸣，话题性强，价值认同"
                elif metric == "收藏率":
                    tips[metric] = f"权重{weight*100:.0f}% - 实用干货，长期价值，工具属性"
                    
            elif platform == Platform.XIAOHONGSHU:
                if metric == "互动率":
                    tips[metric] = f"权重{weight*100:.0f}% - 真实分享，详细回复，建立信任"
                elif metric == "收藏率":
                    tips[metric] = f"权重{weight*100:.0f}% - 实用教程，购物清单，保存价值"
                elif metric == "点赞率":
                    tips[metric] = f"权重{weight*100:.0f}% - 视觉美感，内容价值，情感认同"
                elif metric == "浏览时长":
                    tips[metric] = f"权重{weight*100:.0f}% - 图文并茂，信息丰富，层次分明"
                    
        return tips
    
    def _check_demographic_matching(self, content: str, persona) -> Dict[str, Any]:
        """检查内容与人口统计特征的匹配度"""
        demographics = persona.demographics
        behavior = persona.behavior
        
        matching_analysis = {
            "age_appropriateness": self._check_age_matching(content, demographics.age_distribution),
            "gender_sensitivity": self._check_gender_matching(content, demographics.gender_ratio),
            "education_level_match": self._check_education_matching(content, demographics.education_level),
            "location_relevance": self._check_location_matching(content, demographics.location_distribution),
            "interest_alignment": self._check_interest_matching(content, behavior.interests)
        }
        
        return matching_analysis
    
    def _check_age_matching(self, content: str, age_dist: Dict[str, float]) -> Dict[str, Any]:
        """检查年龄匹配度"""
        main_age = max(age_dist.items(), key=lambda x: x[1])
        
        age_indicators = {
            "18-24": ["年轻", "学生", "校园", "毕业", "求职", "恋爱"],
            "25-30": ["职场", "晋升", "买房", "结婚", "创业", "技能"],
            "31-40": ["管理", "投资", "教育", "家庭", "健康", "理财"],
            "40+": ["养生", "子女", "退休", "经验", "智慧", "传承"]
        }
        
        main_age_group = main_age[0]
        relevant_keywords = age_indicators.get(main_age_group, [])
        
        matching_score = sum(1 for keyword in relevant_keywords if keyword in content) / len(relevant_keywords)
        
        return {
            "main_age_group": main_age_group,
            "percentage": f"{main_age[1]*100:.0f}%",
            "matching_score": matching_score,
            "suggestions": f"针对{main_age_group}年龄段，建议更多使用相关场景词汇"
        }
    
    def _check_gender_matching(self, content: str, gender_ratio: Dict[str, float]) -> Dict[str, Any]:
        """检查性别敏感度"""
        main_gender = max(gender_ratio.items(), key=lambda x: x[1])
        
        return {
            "main_gender": main_gender[0],
            "percentage": f"{main_gender[1]*100:.0f}%",
            "suggestions": f"内容表达考虑{main_gender[0]}用户的偏好和表达习惯"
        }
    
    def _check_education_matching(self, content: str, edu_level: Dict[str, float]) -> Dict[str, Any]:
        """检查教育水平匹配"""
        main_education = max(edu_level.items(), key=lambda x: x[1])
        
        complexity_indicators = {
            "本科及以上": ["分析", "逻辑", "数据", "理论", "研究", "专业"],
            "其他": ["实用", "简单", "直接", "例子", "体验", "感受"]
        }
        
        education_group = main_education[0]
        relevant_keywords = complexity_indicators.get(education_group, [])
        
        matching_score = sum(1 for keyword in relevant_keywords if keyword in content) / len(relevant_keywords)
        
        return {
            "main_education": education_group,
            "percentage": f"{main_education[1]*100:.0f}%",
            "matching_score": matching_score,
            "suggestions": f"根据{education_group}背景，调整内容复杂度和表达方式"
        }
    
    def _check_location_matching(self, content: str, location_dist: Dict[str, float]) -> Dict[str, Any]:
        """检查地域相关性"""
        main_location = max(location_dist.items(), key=lambda x: x[1])
        
        return {
            "main_location": main_location[0],
            "percentage": f"{main_location[1]*100:.0f}%",
            "suggestions": f"考虑{main_location[0]}用户的消费水平和生活方式"
        }
    
    def _check_interest_matching(self, content: str, interests: List[str]) -> Dict[str, Any]:
        """检查兴趣匹配度"""
        interest_score = sum(1 for interest in interests if interest in content) / len(interests)
        
        return {
            "main_interests": interests[:3],
            "matching_score": interest_score,
            "suggestions": f"结合用户主要兴趣：{', '.join(interests[:3])}来增强内容吸引力"
        }

def get_content_optimization_report(content: str, platform: Platform, topic: str) -> Dict[str, Any]:
    """获取内容优化报告"""
    optimizer = PersonaBasedContentOptimizer()
    return optimizer.optimize_content_for_persona(content, platform, topic)
