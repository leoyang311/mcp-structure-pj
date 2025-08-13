"""
基于真实数据的平台用户画像配置
根据platform-analysis-doc.md的详细调研数据构建
"""

from dataclasses import dataclass
from typing import Dict, List, Any
from ..models import Platform

@dataclass
class UserDemographics:
    """用户人口统计学特征"""
    age_distribution: Dict[str, float]  # 年龄分布比例
    gender_ratio: Dict[str, float]      # 性别比例
    location_distribution: Dict[str, float]  # 地域分布
    education_level: Dict[str, float]   # 教育水平分布

@dataclass  
class UserBehavior:
    """用户行为特征"""
    interests: List[str]                # 兴趣标签
    behavior_traits: List[str]          # 行为特点
    core_needs: List[str]              # 核心需求
    consumption_habits: List[str]       # 消费习惯

@dataclass
class ContentPreferences:
    """内容偏好"""
    popular_categories: Dict[str, float]  # 热门类目及占比
    content_format: Dict[str, Any]        # 内容格式要求
    engagement_features: List[str]        # 互动特征要求

@dataclass
class PlatformStereotypes:
    """平台刻板印象"""
    positive_labels: List[str]          # 正面标签
    negative_labels: List[str]          # 负面标签
    creation_dos: List[str]             # 创作建议-应该做
    creation_donts: List[str]           # 创作建议-不应该做

@dataclass
class UserPersona:
    """完整用户画像"""
    platform: Platform
    demographics: UserDemographics
    behavior: UserBehavior
    content_preferences: ContentPreferences
    stereotypes: PlatformStereotypes
    daily_usage_minutes: int            # 日均使用时长
    monthly_active_users: str           # 月活用户数

# 基于真实调研数据的用户画像配置
USER_PERSONAS: Dict[Platform, UserPersona] = {
    Platform.BILIBILI: UserPersona(
        platform=Platform.BILIBILI,
        demographics=UserDemographics(
            age_distribution={"18-24": 0.45, "25-30": 0.28, "31-35": 0.15, "其他": 0.12},
            gender_ratio={"男性": 0.57, "女性": 0.43},
            location_distribution={"一二线城市": 0.65, "其他": 0.35},
            education_level={"本科及以上": 0.62, "其他": 0.38}
        ),
        behavior=UserBehavior(
            interests=["二次元文化", "游戏", "科技", "学习知识", "争议话题"],
            behavior_traits=["深度内容消费", "弹幕互动活跃", "幻想倾向", "寻求刺激", "经济拮据"],
            core_needs=["知识获取", "娱乐刺激", "社交认同", "逃避现实"],
            consumption_habits=["免费内容优先", "少量付费支持", "白嫖心理"]
        ),
        content_preferences=ContentPreferences(
            popular_categories={
                "生活区": 0.25, "游戏区": 0.18, "知识区": 0.15, "动画区": 0.12,
                "科技区": 0.10, "音乐区": 0.08, "影视区": 0.05, "美食区": 0.04,
                "时尚区": 0.02, "运动区": 0.01
            },
            content_format={
                "optimal_duration": "5-15分钟",
                "pacing": "信息密度高，剪辑紧凑", 
                "style": "专业性与趣味性结合"
            },
            engagement_features=["弹幕梗", "彩蛋", "互动投票", "章节划分"]
        ),
        stereotypes=PlatformStereotypes(
            positive_labels=["学习热情", "思维活跃", "创造力强", "互动性高"],
            negative_labels=["经济拮据", "好高骛远", "寻求刺激", "容易被煽动"],
            creation_dos=["提供免费价值", "满足好奇心", "设置互动点", "迎合幻想需求"],
            creation_donts=["过度收费", "内容平淡", "忽视互动", "过于现实残酷"]
        ),
        daily_usage_minutes=96,
        monthly_active_users="3.3亿"
    ),
    
    Platform.DOUYIN: UserPersona(
        platform=Platform.DOUYIN,
        demographics=UserDemographics(
            age_distribution={"18-24": 0.22, "25-30": 0.28, "31-40": 0.31, "40+": 0.19},
            gender_ratio={"男性": 0.46, "女性": 0.54},
            location_distribution={"三四线城市": 0.55, "一二线城市": 0.45},
            education_level={"大专及以下": 0.58, "本科及以上": 0.42}
        ),
        behavior=UserBehavior(
            interests=["娱乐", "美食", "生活", "情感"],
            behavior_traits=["碎片化浏览", "算法依赖强", "冲动消费", "跟风模仿"],
            core_needs=["娱乐解压", "获取资讯", "社交互动"],
            consumption_habits=["直播带货", "冲动消费", "热点跟随"]
        ),
        content_preferences=ContentPreferences(
            popular_categories={
                "搞笑娱乐": 0.30, "生活技巧": 0.20, "美食探店": 0.15, "情感故事": 0.12,
                "知识科普": 0.10, "才艺展示": 0.08, "萌宠": 0.03, "游戏": 0.02
            },
            content_format={
                "optimal_duration": "15-30秒",
                "golden_rule": "黄金3秒开头抓人",
                "visual_style": "画面变化快，特效丰富"
            },
            engagement_features=["反转情节", "情绪价值", "互动钩子", "热点话题"]
        ),
        stereotypes=PlatformStereotypes(
            positive_labels=["接地气真实", "娱乐性强", "传播速度快", "全民参与"],
            negative_labels=["内容低俗", "容易上瘾", "带货太多", "同质化严重"],
            creation_dos=["紧跟热点话题", "使用流行音乐和特效", "真人出镜增加信任", "设置互动钩子"],
            creation_donts=["内容过于复杂", "节奏拖沓", "画质模糊", "违规擦边"]
        ),
        daily_usage_minutes=115,
        monthly_active_users="7.3亿"
    ),
    
    Platform.WECHAT: UserPersona(
        platform=Platform.WECHAT,
        demographics=UserDemographics(
            age_distribution={"25-30": 0.24, "31-35": 0.28, "36-40": 0.22, "40+": 0.26},
            gender_ratio={"男性": 0.48, "女性": 0.52},
            location_distribution={"一二线城市": 0.70, "其他": 0.30},
            education_level={"本科及以上": 0.73, "其他": 0.27}
        ),
        behavior=UserBehavior(
            interests=["职场焦虑", "财经理财", "情感生活", "育儿教育", "国家政策"],
            behavior_traits=["深度阅读习惯", "社交压力大", "知识付费意愿", "爱国情怀强烈", "中年危机焦虑"],
            core_needs=["缓解焦虑", "社会认同", "财富增值", "家庭责任"],
            consumption_habits=["理性消费", "品质追求", "知识付费", "保险理财"]
        ),
        content_preferences=ContentPreferences(
            popular_categories={
                "时事热点": 0.25, "职场成长": 0.20, "情感生活": 0.18, "财经理财": 0.15,
                "教育育儿": 0.10, "健康养生": 0.07, "科技互联网": 0.05
            },
            content_format={
                "optimal_length": "2000-3000字",
                "title_style": "悬念式、数字式、反问式",
                "structure": "总分总、递进式、并列式"
            },
            engagement_features=["深度分析", "数据支撑", "观点独特", "分享价值"]
        ),
        stereotypes=PlatformStereotypes(
            positive_labels=["深度思考", "理性分析", "专业权威", "社会责任感"],
            negative_labels=["焦虑传播", "标题党", "贩卖焦虑", "民族主义倾向"],
            creation_dos=["提供深度分析", "数据支撑观点", "缓解中年焦虑", "体现家国情怀"],
            creation_donts=["过度贩卖焦虑", "缺乏事实依据", "忽视情感需求", "政治敏感话题"]
        ),
        daily_usage_minutes=0,  # 公众号无单独统计
        monthly_active_users="4亿+"
    ),
    
    Platform.XIAOHONGSHU: UserPersona(
        platform=Platform.XIAOHONGSHU,
        demographics=UserDemographics(
            age_distribution={"18-24": 0.35, "25-30": 0.40, "31-35": 0.18, "其他": 0.07},
            gender_ratio={"男性": 0.30, "女性": 0.70},
            location_distribution={"一二线城市": 0.75, "其他": 0.25},
            education_level={"本科及以上": 0.70, "其他": 0.30}
        ),
        behavior=UserBehavior(
            interests=["美妆时尚", "品质生活", "社交展示", "女性权益", "精致消费"],
            behavior_traits=["种草决策链短", "视觉导向强", "从众心理", "虚荣心理", "女权意识"],
            core_needs=["社交认同", "美丽追求", "生活品质", "自我价值实现"],
            consumption_habits=["冲动消费", "品牌种草", "跟风购买", "精致生活"]
        ),
        content_preferences=ContentPreferences(
            popular_categories={
                "美妆护肤": 0.28, "穿搭时尚": 0.22, "美食探店": 0.18, "家居生活": 0.12,
                "旅行攻略": 0.10, "健身瘦身": 0.05, "学习成长": 0.05
            },
            content_format={
                "image_count": "4-9张高质量配图",
                "content_style": "真实使用体验+详细步骤教程",
                "tag_count": "5-10个精准标签"
            },
            engagement_features=["真人体验", "前后对比", "详细教程", "评论区答疑"]
        ),
        stereotypes=PlatformStereotypes(
            positive_labels=["精致生活", "审美品味", "消费能力", "社交活跃"],
            negative_labels=["虚荣攀比", "跟风从众", "过度滤镜", "女拳倾向"],
            creation_dos=["展示精致生活", "提供实用价值", "迎合审美需求", "体现女性力量"],
            creation_donts=["过于商业化", "缺乏真实感", "忽视实用性", "性别对立言论"]
        ),
        daily_usage_minutes=0,  # 文档中70%用户每日打开但未提供具体时长
        monthly_active_users="2.6亿"
    )
}

def get_user_persona(platform: Platform) -> UserPersona:
    """获取平台用户画像"""
    return USER_PERSONAS.get(platform, USER_PERSONAS[Platform.WECHAT])

def get_platform_algorithm_weights(platform: Platform) -> Dict[str, float]:
    """获取各平台算法权重（基于文档中的算法优化策略）"""
    algorithm_weights = {
        Platform.BILIBILI: {
            "完播率": 0.35,
            "互动率": 0.30, 
            "收藏率": 0.20,
            "点赞率": 0.15
        },
        Platform.DOUYIN: {
            "完播率": 0.40,
            "点赞率": 0.25,
            "评论率": 0.20,
            "转发率": 0.15
        },
        Platform.WECHAT: {
            "阅读完成率": 0.35,
            "分享率": 0.30,
            "在看率": 0.20,
            "收藏率": 0.15
        },
        Platform.XIAOHONGSHU: {
            "互动率": 0.30,
            "收藏率": 0.30,
            "点赞率": 0.20,
            "浏览时长": 0.20
        }
    }
    
    return algorithm_weights.get(platform, algorithm_weights[Platform.WECHAT])
