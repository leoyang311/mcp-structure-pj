"""
质量评估指标和算法
"""
import re
import math
from typing import Dict, List
from ..models import QualityScore, Platform


def calculate_readability_score(text: str) -> float:
    """
    计算可读性分数 (基于简化的Flesch公式)
    """
    if not text.strip():
        return 0.0
    
    # 计算句子数
    sentences = len(re.findall(r'[.!?。！？]', text))
    if sentences == 0:
        sentences = 1
    
    # 计算单词数 (中文按字符计算)
    words = len(text.replace(' ', '').replace('\n', ''))
    
    # 计算平均句长
    avg_sentence_length = words / sentences
    
    # 简化的可读性分数 (适合中文)
    score = max(0, min(100, 100 - (avg_sentence_length / 20) * 30))
    
    return round(score, 2)


def calculate_keyword_density(text: str, keywords: List[str]) -> Dict[str, float]:
    """
    计算关键词密度
    """
    if not text or not keywords:
        return {}
    
    text_lower = text.lower()
    total_chars = len(text.replace(' ', '').replace('\n', ''))
    
    densities = {}
    for keyword in keywords:
        count = text_lower.count(keyword.lower())
        keyword_chars = len(keyword) * count
        density = (keyword_chars / total_chars * 100) if total_chars > 0 else 0
        densities[keyword] = round(density, 2)
    
    return densities


def calculate_engagement_potential(text: str, platform: Platform) -> float:
    """
    计算互动潜力分数
    """
    score = 50.0  # 基础分数
    
    # 检查问号数量 (引发互动)
    question_count = len(re.findall(r'[?？]', text))
    score += min(question_count * 5, 20)
    
    # 检查感叹号数量 (情感强度)
    exclamation_count = len(re.findall(r'[!！]', text))
    score += min(exclamation_count * 3, 15)
    
    # 平台特定加分
    if platform == Platform.XIAOHONGSHU:
        # 小红书喜欢emoji和话题标签
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text))
        hashtag_count = len(re.findall(r'#[^#\s]+#', text))
        score += min(emoji_count * 2, 10)
        score += min(hashtag_count * 5, 15)
    
    elif platform == Platform.DOUYIN:
        # 抖音喜欢热门词汇和节奏感
        hot_words = ['热门', '火爆', '必看', '绝了', '太棒了', '震惊', '不敢相信']
        hot_word_count = sum(1 for word in hot_words if word in text)
        score += min(hot_word_count * 8, 20)
    
    return min(100.0, round(score, 2))


def calculate_seo_score(text: str, title: str, keywords: List[str]) -> float:
    """
    计算SEO分数
    """
    if not text or not title:
        return 0.0
    
    score = 0.0
    
    # 标题中包含关键词
    title_lower = title.lower()
    for keyword in keywords:
        if keyword.lower() in title_lower:
            score += 20
    
    # 内容中关键词分布
    keyword_densities = calculate_keyword_density(text, keywords)
    for density in keyword_densities.values():
        if 1 <= density <= 3:  # 理想密度范围
            score += 15
        elif density > 0:
            score += 5
    
    # 内容长度适中
    text_length = len(text.replace(' ', '').replace('\n', ''))
    if 500 <= text_length <= 2000:
        score += 20
    elif text_length > 0:
        score += 10
    
    # 结构化程度 (标题、段落)
    if '##' in text or '**' in text:
        score += 10
    
    return min(100.0, round(score, 2))


def calculate_platform_adaptation_score(text: str, title: str, platform: Platform) -> float:
    """
    计算平台适配分数
    """
    from .platform_config import get_platform_config
    
    config = get_platform_config(platform)
    score = 0.0
    
    # 字数范围匹配
    text_length = len(text.replace(' ', '').replace('\n', ''))
    min_words, max_words = config.word_count_range
    
    if min_words <= text_length <= max_words:
        score += 40
    elif text_length < min_words:
        ratio = text_length / min_words
        score += 40 * ratio
    else:  # text_length > max_words
        excess_ratio = (text_length - max_words) / max_words
        score += max(0, 40 - excess_ratio * 20)
    
    # 特殊要求匹配
    requirement_score = 0
    total_requirements = len(config.special_requirements)
    
    for requirement in config.special_requirements:
        if requirement == "emoji表情丰富":
            emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text))
            if emoji_count >= 3:
                requirement_score += 1
        elif requirement == "话题标签":
            hashtag_count = len(re.findall(r'#[^#\s]+#', text))
            if hashtag_count >= 2:
                requirement_score += 1
        elif requirement == "SEO优化":
            if '##' in text or '**' in text:
                requirement_score += 1
        elif requirement == "分段明确":
            paragraph_count = len(text.split('\n\n'))
            if paragraph_count >= 3:
                requirement_score += 1
        else:
            # 其他要求通过关键词匹配
            if requirement in text:
                requirement_score += 0.5
    
    if total_requirements > 0:
        score += (requirement_score / total_requirements) * 60
    
    return min(100.0, round(score, 2))


def evaluate_content_quality(
    text: str,
    title: str,
    platform: Platform,
    keywords: List[str] = None
) -> QualityScore:
    """
    综合评估内容质量
    """
    keywords = keywords or []
    
    # 计算各维度分数
    content_quality = (
        calculate_readability_score(text) * 0.4 +
        calculate_seo_score(text, title, keywords) * 0.3 +
        len(text.split('\n\n')) * 2  # 结构化程度
    )
    content_quality = min(100.0, content_quality)
    
    platform_adaptation = calculate_platform_adaptation_score(text, title, platform)
    engagement_potential = calculate_engagement_potential(text, platform)
    technical_quality = calculate_seo_score(text, title, keywords)
    
    # 创建质量评分对象
    quality_score = QualityScore(
        content_quality=round(content_quality, 2),
        platform_adaptation=round(platform_adaptation, 2),
        engagement_potential=round(engagement_potential, 2),
        technical_quality=round(technical_quality, 2),
        total_score=0.0  # 临时值，将通过calculate_total()计算
    )
    
    # 计算总分
    quality_score.calculate_total()
    
    return quality_score
