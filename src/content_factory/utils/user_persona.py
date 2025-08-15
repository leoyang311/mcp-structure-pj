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
    psychological_pain_points: List[str] # 心理痛点（新增）
    addiction_patterns: List[str]        # 成瘾模式（新增）
    social_comparison_triggers: List[str] # 社交比较触发点（新增）@dataclass
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
            interests=["二次元文化", "ACG内容", "知识学习", "科技数码", "游戏动漫"],
            behavior_traits=["虚拟逃避", "假学习现象", "弹幕依赖", "数字囤积", "社交焦虑"],
            core_needs=["情感避难所", "身份认同", "虚拟陪伴", "知识焦虑缓解"],
            consumption_habits=["免费内容优先", "精神消费", "周边收集", "会员充值"],
            psychological_pain_points=["现实适应困难", "成人责任恐惧", "社交缺失", "学习焦虑", "抑郁倾向"],
            addiction_patterns=["准社会关系依赖", "弹幕参与感", "连续观看", "收藏不看"],
            social_comparison_triggers=["学历能力", "二次元知识深度", "弹幕机智程度", "创作才能"]
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
                "style": "专业性与趣味性结合，避免说教"
            },
            engagement_features=["弹幕互动", "知识彩蛋", "二次元梗", "温暖治愈"]
        ),
        stereotypes=PlatformStereotypes(
            positive_labels=["有深度", "有文化", "创造力强", "情感丰富"],
            negative_labels=["脆弱一代", "逃避现实", "躺平文化", "毒性饭圈"],
            creation_dos=["提供情感价值", "构建虚拟陪伴", "满足求知欲", "创造安全空间"],
            creation_donts=["强调现实残酷", "成人化说教", "过度商业化", "批判二次元文化"]
        ),
        daily_usage_minutes=150,  # 重度使用
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
            interests=["即时娱乐", "成功故事", "财富炫耀", "网红生活", "消费种草"],
            behavior_traits=["即时满足", "冲动消费", "算法依赖", "多巴胺循环", "从众跟风"],
            core_needs=["娱乐刺激", "成功幻想", "虚荣满足", "社交认同"],
            consumption_habits=["直播冲动购买", "KOL推荐跟买", "挑战参与", "炫耀消费"],
            psychological_pain_points=["FOMO恐惧", "相对剥夺感", "自控力下降", "现实扭曲", "社会焦虑"],
            addiction_patterns=["无限滚动", "算法推送依赖", "KOL准社会关系", "挑战参与"],
            social_comparison_triggers=["财富成功", "外貌身材", "生活方式", "社交影响力"]
        ),
        content_preferences=ContentPreferences(
            popular_categories={
                "搞笑娱乐": 0.30, "成功励志": 0.20, "美食探店": 0.15, "情感故事": 0.12,
                "财富炫耀": 0.10, "才艺展示": 0.08, "萌宠": 0.03, "游戏": 0.02
            },
            content_format={
                "optimal_duration": "15-30秒",
                "golden_rule": "黄金3秒抓眼球",
                "visual_style": "快节奏剪辑，强视觉冲击"
            },
            engagement_features=["反转剧情", "情绪刺激", "成功暗示", "参与挑战"]
        ),
        stereotypes=PlatformStereotypes(
            positive_labels=["有活力", "敢表达", "接地气", "传播力强"],
            negative_labels=["容易上瘾", "冲动消费", "跟风盲目", "认知下降"],
            creation_dos=["制造多巴胺循环", "暗示成功可能", "提供即时满足", "利用从众心理"],
            creation_donts=["内容过于复杂", "节奏缓慢", "缺乏刺激点", "否定成功梦想"]
        ),
        daily_usage_minutes=150,  # 2.5小时+
        monthly_active_users="7.3亿"
    ),
    
    Platform.WECHAT: UserPersona(
        platform=Platform.WECHAT,
        demographics=UserDemographics(
            age_distribution={"25-30": 0.20, "31-40": 0.35, "41-50": 0.30, "50+": 0.15},
            gender_ratio={"男性": 0.48, "女性": 0.52},
            location_distribution={"一二线城市": 0.60, "其他": 0.40},
            education_level={"大专及以上": 0.65, "其他": 0.35}
        ),
        behavior=UserBehavior(
            interests=["权威信息", "健康养生", "家庭教育", "财富保值", "国家大事"],
            behavior_traits=["权威崇拜", "健康焦虑", "转发分享", "群体认同", "确认偏见"],
            core_needs=["权威认可", "健康保障", "社会地位", "家庭责任"],
            consumption_habits=["保健品购买", "保险理财", "教育投资", "权威推荐"],
            psychological_pain_points=["健康恐慌", "技术焦虑", "社会边缘化", "权威依赖", "信息焦虑"],
            addiction_patterns=["转发成就感", "群聊参与", "权威信息依赖", "健康信息收集"],
            social_comparison_triggers=["健康状况", "家庭成就", "社会地位", "财富积累"]
        ),
        content_preferences=ContentPreferences(
            popular_categories={
                "健康养生": 0.30, "家庭教育": 0.20, "时事政治": 0.15, "财经理财": 0.15,
                "情感鸡汤": 0.10, "传统文化": 0.05, "科技知识": 0.05
            },
            content_format={
                "optimal_length": "1500-2500字",
                "title_style": "权威性、恐慌性、数字化标题",
                "structure": "权威引用+案例证明+行动建议"
            },
            engagement_features=["权威背书", "健康提醒", "家庭关爱", "转发价值"]
        ),
        stereotypes=PlatformStereotypes(
            positive_labels=["有责任心", "关爱家人", "社会经验", "传播正能量"],
            negative_labels=["易信谣言", "焦虑传播", "技术焦虑", "固化思维"],
            creation_dos=["提供权威依据", "关注健康话题", "强调家庭价值", "缓解中年焦虑"],
            creation_donts=["挑战权威", "忽视健康", "复杂技术", "制造对立"]
        ),
        daily_usage_minutes=90,
        monthly_active_users="12.9亿"
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
            interests=["精致消费", "外貌提升", "生活方式", "社交展示", "品牌种草"],
            behavior_traits=["种草拔草", "精致贫穷", "视觉导向", "社交比较", "消费冲动"],
            core_needs=["外貌焦虑缓解", "生活方式认同", "消费指导", "社交价值"],
            consumption_habits=["冲动购买", "品牌跟风", "医美消费", "精致生活投资"],
            psychological_pain_points=["容貌焦虑", "社交比较压力", "消费主义陷阱", "身份认同困惑", "经济负担"],
            addiction_patterns=["种草循环", "理想化内容依赖", "消费展示", "社交验证需求"],
            social_comparison_triggers=["外貌颜值", "生活品质", "消费能力", "社交地位"]
        ),
        content_preferences=ContentPreferences(
            popular_categories={
                "美妆护肤": 0.35, "穿搭时尚": 0.25, "生活方式": 0.20, "美食探店": 0.10,
                "旅行攻略": 0.05, "健身塑形": 0.03, "学习成长": 0.02
            },
            content_format={
                "image_count": "6-9张精修图片",
                "content_style": "精致生活展示+详细攻略",
                "tag_count": "8-12个热门标签"
            },
            engagement_features=["精致视觉", "前后对比", "详细教程", "价格透明"]
        ),
        stereotypes=PlatformStereotypes(
            positive_labels=["审美品味", "生活精致", "消费理性", "分享精神"],
            negative_labels=["虚荣攀比", "消费主义", "容貌焦虑", "精致贫穷"],
            creation_dos=["提供美丽方案", "展示精致生活", "给出消费指导", "缓解外貌焦虑"],
            creation_donts=["过度滤镜", "不切实际消费", "制造容貌焦虑", "忽视经济现实"]
        ),
        daily_usage_minutes=85,
        monthly_active_users="3.2亿"
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
