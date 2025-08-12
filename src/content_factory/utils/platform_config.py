"""
平台配置管理
"""
from typing import Dict
from ..models import Platform, PlatformConfig, VideoSpec


# 平台内容配置
PLATFORM_CONFIGS: Dict[Platform, PlatformConfig] = {
    Platform.WECHAT: PlatformConfig(
        name="微信公众号",
        word_count_range=(2000, 3000),
        style="专业深度",
        special_requirements=[
            "SEO优化",
            "长篇深度分析",
            "专业术语解释",
            "引用数据支撑",
        ]
    ),
    Platform.XIAOHONGSHU: PlatformConfig(
        name="小红书",
        word_count_range=(500, 800),
        style="轻松活泼",
        special_requirements=[
            "emoji表情丰富",
            "话题标签",
            "互动性强",
            "视觉化描述",
            "分段明确",
        ]
    ),
    Platform.BILIBILI: PlatformConfig(
        name="B站",
        word_count_range=(1000, 1500),
        style="教育向",
        special_requirements=[
            "结构化内容",
            "知识点清晰",
            "互动引导",
            "弹幕友好",
        ]
    ),
    Platform.DOUYIN: PlatformConfig(
        name="抖音",
        word_count_range=(200, 400),
        style="娱乐向",
        special_requirements=[
            "节奏感强",
            "冲突吸引",
            "情感共鸣",
            "热门话题",
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
    """获取平台内容生成提示词模板"""
    config = get_platform_config(platform)
    
    base_template = f"""
请为{config.name}平台创作内容，要求：

1. 字数范围：{config.word_count_range[0]}-{config.word_count_range[1]}字
2. 风格特点：{config.style}
3. 特殊要求：
"""
    
    for req in config.special_requirements:
        base_template += f"   - {req}\n"
    
    base_template += """
4. 内容要求：
   - 标题吸引人，能激发点击欲望
   - 开头要有吸引力，快速抓住读者注意
   - 内容结构清晰，逻辑连贯
   - 结尾有总结或行动引导

请基于以下研究材料创作内容：
{research_data}

话题：{topic}
"""
    
    return base_template


def get_title_generation_prompt(platform: Platform) -> str:
    """获取标题生成提示词"""
    config = get_platform_config(platform)
    
    return f"""
请为{config.name}平台生成3个吸引人的标题，要求：

1. 符合{config.name}平台特色
2. 风格：{config.style}
3. 能激发用户点击欲望
4. 字数控制在10-30字之间

话题：{{topic}}
关键要点：{{key_points}}

请直接返回3个标题，每行一个。
"""
