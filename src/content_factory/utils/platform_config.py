"""
平台配置管理
"""
from typing import Dict
from ..models import Platform, PlatformConfig, VideoSpec


# 平台内容配置 - 基于真实用户画像数据优化
PLATFORM_CONFIGS: Dict[Platform, PlatformConfig] = {
    Platform.WECHAT: PlatformConfig(
        name="微信公众号",
        word_count_range=(2000, 5000),  # 根据文档调整为2000-5000字
        style="理性权威，深度分析",  # 更精准的风格定位
        special_requirements=[
            "数据案例支撑",  # 70%一二线城市用户，喜欢数据
            "专业观点输出",  # 73%本科以上，需要专业性
            "逻辑结构清晰",  # 成熟用户群体需要逻辑性
            "社交分享价值",  # 微信天然社交属性
            "长期价值导向",  # 31-40岁主力用户追求长期价值
            "权威性表达",    # 适合中产阶级的表达方式
        ]
    ),
    Platform.XIAOHONGSHU: PlatformConfig(
        name="小红书",
        word_count_range=(500, 1500),  # 根据文档调整范围
        style="真诚分享，生活美学",  # 基于70%女性用户特点
        special_requirements=[
            "真实体验分享",  # 用户重视真实性
            "视觉美感要求",  # 女性用户占70%，视觉导向
            "实用教程导向",  # 种草决策链短，需要实用性
            "购物决策支持",  # 消费力强的用户群体
            "话题标签丰富",  # 5-10个标签，增加曝光
            "互动性设计",    # 评论区答疑重要
            "生活方式展示",  # 一二线城市75%，追求品质生活
        ]
    ),
    Platform.BILIBILI: PlatformConfig(
        name="B站",
        word_count_range=(1000, 2500),  # 5-15分钟视频对应字数
        style="专业有趣，知识传播",  # 45%年轻人+62%本科以上
        special_requirements=[
            "知识密度高",    # 学习提升是核心需求
            "专业性与趣味性结合",  # 既要专业又要有趣
            "弹幕文化融入",  # 弹幕互动是B站特色
            "章节结构化",    # 便于学习和回看
            "互动投票设计",  # 增加用户参与度
            "社区文化尊重",  # 避免过度商业化
            "深度内容导向",  # 日均96分钟高粘性用户
            "成长价值体现",  # 年轻用户的成长需求
        ]
    ),
    Platform.DOUYIN: PlatformConfig(
        name="抖音",
        word_count_range=(200, 500),    # 15-60秒短视频对应字数
        style="接地气娱乐，情感共鸣",  # 三四线城市55%，全民化
        special_requirements=[
            "黄金3秒抓人",   # 开头必须立即抓住注意力
            "情绪价值导向",  # 娱乐解压是核心需求
            "热点话题结合",  # 算法依赖强，需跟热点
            "视觉冲击力强",  # 女性54%，视觉敏感
            "快节奏剪辑",    # 碎片化浏览习惯
            "互动钩子设计",  # 评论、点赞、分享驱动
            "接地气表达",    # 三四线城市用户占多数
            "强烈情感调动",  # 冲动消费的用户特征
        ]
    ),
}


# 视频规格配置
VIDEO_SPECS: Dict[Platform, VideoSpec] = {
    Platform.BILIBILI: VideoSpec(
        platform=Platform.BILIBILI,
        duration_range=(180, 600),  # 3-10分钟
        resolution=(1920, 1080),
        orientation="horizontal",
        style="教育向"
    ),
    Platform.DOUYIN: VideoSpec(
        platform=Platform.DOUYIN,
        duration_range=(15, 60),  # 15-60秒
        resolution=(1080, 1920),
        orientation="vertical", 
        style="娱乐向"
    ),
    Platform.XIAOHONGSHU: VideoSpec(
        platform=Platform.XIAOHONGSHU,
        duration_range=(30, 90),  # 30-90秒
        resolution=(1080, 1920),
        orientation="vertical",
        style="生活化"
    ),
}


def get_platform_config(platform: Platform) -> PlatformConfig:
    """获取平台配置"""
    return PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS[Platform.WECHAT])


def get_video_spec(platform: Platform) -> VideoSpec:
    """获取视频规格"""
    return VIDEO_SPECS.get(platform)


def get_content_prompt_template(platform: Platform) -> str:
    """获取平台内容生成提示词模板 - 基于真实用户画像优化"""
    config = get_platform_config(platform)
    
    # 平台特定的用户画像和内容要求
    user_personas = {
        Platform.WECHAT: {
            "user_profile": "主要用户：31-40岁(50%)，70%一二线城市，73%本科以上，中产阶级为主",
            "reading_habit": "深度阅读习惯，社交分享动机强，知识付费意愿高",
            "content_preferences": "时事热点、职场成长、财经理财类内容最受欢迎"
        },
        Platform.XIAOHONGSHU: {
            "user_profile": "主要用户：18-30岁(75%)，70%女性，75%一二线城市，70%本科以上",
            "reading_habit": "种草决策链短，视觉导向强，真实体验重视，品质生活追求",
            "content_preferences": "美妆护肤、穿搭时尚、美食探店、家居生活类内容"
        },
        Platform.BILIBILI: {
            "user_profile": "主要用户：18-24岁(45%)，57%男性，65%一二线城市，62%本科以上", 
            "reading_habit": "深度内容消费，弹幕互动活跃，创作欲强，付费意愿高",
            "content_preferences": "知识学习、科技游戏、生活技能类教育内容"
        },
        Platform.DOUYIN: {
            "user_profile": "主要用户：25-40岁(59%)，54%女性，55%三四线城市，58%大专以下",
            "reading_habit": "碎片化浏览，算法依赖强，冲动消费，跟风模仿",
            "content_preferences": "搞笑娱乐、生活技巧、美食探店、情感故事类内容"
        }
    }
    
    persona = user_personas.get(platform, user_personas[Platform.WECHAT])
    
    base_template = f"""
请为{config.name}平台创作内容，基于真实用户画像优化：

## 目标用户画像
{persona['user_profile']}

## 用户行为特征  
{persona['reading_habit']}

## 内容偏好
{persona['content_preferences']}

## 创作要求
1. 字数范围：{config.word_count_range[0]}-{config.word_count_range[1]}字
2. 风格特点：{config.style}
3. 平台特定要求：
"""
    
    for req in config.special_requirements:
        base_template += f"   - {req}\n"
    
    base_template += """
## 内容结构要求：
   - 标题：符合平台用户心理，激发点击欲望
   - 开头：快速抓住目标用户注意力，符合其浏览习惯
   - 主体：内容深度和表达方式匹配用户教育背景和兴趣
   - 结尾：符合用户行为特征的引导设计（分享/收藏/关注等）

请基于以下研究材料创作内容：
{research_data}

话题：{topic}
"""
    
    return base_template


def get_title_generation_prompt(platform: Platform) -> str:
    """获取标题生成提示词 - 基于真实用户画像优化"""
    config = get_platform_config(platform)
    
    # 各平台爆款标题特征
    title_strategies = {
        Platform.WECHAT: {
            "techniques": ["悬念式", "数字式", "反问式", "观点式"],
            "psychology": "成熟理性用户，追求深度价值和社交分享性",
            "examples": "深度解析：为什么90%的人都错了｜5个数据告诉你真相｜你真的了解...吗？"
        },
        Platform.XIAOHONGSHU: {
            "techniques": ["结果导向", "真实体验", "避坑指南", "干货总结"],
            "psychology": "年轻女性用户，追求实用价值和视觉美感",
            "examples": "30天瘦10斤！我的详细食谱｜超全避坑指南！｜姐妹们这个真的有用！"
        },
        Platform.BILIBILI: {
            "techniques": ["知识点悬念", "教程式", "揭秘式", "成长式"],
            "psychology": "学习导向用户，追求知识获取和能力提升",
            "examples": "这个方法让我效率提升300%｜深度揭秘...背后的原理｜从0到1教你..."
        },
        Platform.DOUYIN: {
            "techniques": ["情绪冲击", "对比反差", "好奇心钩子", "争议话题"],
            "psychology": "娱乐消费用户，追求情感共鸣和快速消费",
            "examples": "看到最后我哭了...｜你绝对想不到...｜这个真相震惊了所有人"
        }
    }
    
    strategy = title_strategies.get(platform, title_strategies[Platform.WECHAT])
    
    return f"""
请为{config.name}平台生成3个吸引人的标题，基于真实用户画像：

## 平台特色
{config.name} - 风格：{config.style}

## 标题策略
适用技巧：{', '.join(strategy['techniques'])}
用户心理：{strategy['psychology']}
优秀案例：{strategy['examples']}

## 具体要求
1. 符合{config.name}用户心理和浏览习惯
2. 字数控制在10-30字之间
3. 能激发用户点击和分享欲望
4. 体现平台文化特色

话题：{{topic}}
关键要点：{{key_points}}

请直接返回3个标题，每行一个。
"""
