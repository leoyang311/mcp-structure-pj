"""
基于心理洞察的质量评估指标
聚焦真实性、心理价值和去AI化
"""
import re
import math
from typing import Dict, List, Tuple
from ..models import QualityScore, Platform


def calculate_authenticity_score(text: str) -> Tuple[float, List[str]]:
    """
    计算真实性分数 - 检测AI味道和套话
    """
    if not text.strip():
        return 0.0, ["内容为空"]
    
    # AI套话检测
    ai_phrases = [
        "让我们一起探讨", "引发了广泛关注", "深入研究发现",
        "通过分析我们可以看出", "值得我们深思", "为读者提供",
        "综合来看", "总的来说", "从某种意义上说",
        "需要我们共同努力", "相信大家都", "希望能够帮助",
        "在这个快速发展的", "随着社会的进步", "在当今这个时代"
    ]
    
    ai_count = 0
    found_phrases = []
    for phrase in ai_phrases:
        if phrase in text:
            ai_count += text.count(phrase)
            found_phrases.append(phrase)
    
    # 真实性特征检测
    authenticity_features = 0
    authenticity_indicators = []
    
    # 检测个人化表达
    personal_patterns = [
        r"我发现", r"我觉得", r"在我看来", r"我的理解是", 
        r"说实话", r"让我震惊的是", r"我也困惑",
        r"可能我想多了", r"也许我太", r"我之前也是"
    ]
    
    for pattern in personal_patterns:
        if re.search(pattern, text):
            authenticity_features += len(re.findall(pattern, text))
            authenticity_indicators.append(f"使用个人化表达: {pattern}")
    
    # 检测情感表达
    emotion_patterns = [
        r"让我担心", r"我被震撼", r"说实话我也", r"这让我很",
        r"我有点困惑", r"让我意外的是", r"我没想到"
    ]
    
    for pattern in emotion_patterns:
        if re.search(pattern, text):
            authenticity_features += len(re.findall(pattern, text))
            authenticity_indicators.append(f"表达真实情感: {pattern}")
    
    # 检测质疑和不确定性
    uncertainty_patterns = [
        r"可能不完整", r"也许", r"可能", r"不确定", r"我也不知道",
        r"需要进一步", r"还有待研究", r"这个问题很复杂"
    ]
    
    for pattern in uncertainty_patterns:
        if re.search(pattern, text):
            authenticity_features += len(re.findall(pattern, text))
            authenticity_indicators.append(f"承认不确定性: {pattern}")
    
    # 计算分数
    base_score = 70.0
    ai_penalty = min(ai_count * 5, 40)  # AI套话扣分
    authenticity_bonus = min(authenticity_features * 3, 30)  # 真实性加分
    
    final_score = max(0, min(100, base_score - ai_penalty + authenticity_bonus))
    
    issues = []
    if ai_count > 0:
        issues.append(f"发现{ai_count}处AI套话: {', '.join(found_phrases[:3])}")
    if authenticity_features == 0:
        issues.append("缺乏个人化和情感表达")
    
    return round(final_score, 2), issues


def calculate_psychological_value_score(text: str, platform: Platform) -> Tuple[float, List[str]]:
    """
    计算心理价值分数 - 基于用户心理需求
    """
    if not text.strip():
        return 0.0, ["内容为空"]
    
    score = 0.0
    insights = []
    
    # 平台特定心理需求检测
    if platform == Platform.WECHAT:
        # 微信：缓解中年焦虑
        anxiety_relief_patterns = [
            r"不用担心", r"其实没那么可怕", r"专业的角度", r"给大家安心",
            r"从父母角度", r"为了孩子", r"家庭责任", r"可靠的建议"
        ]
        
        for pattern in anxiety_relief_patterns:
            count = len(re.findall(pattern, text))
            if count > 0:
                score += count * 8
                insights.append(f"缓解中年焦虑: {pattern}")
        
        # 权威背书检测
        authority_patterns = [
            r"专家", r"研究", r"数据", r"官方", r"权威", r"科学"
        ]
        
        authority_count = sum(len(re.findall(pattern, text)) for pattern in authority_patterns)
        if authority_count > 0:
            score += min(authority_count * 3, 20)
            insights.append(f"提供权威背书: {authority_count}处")
    
    elif platform == Platform.XIAOHONGSHU:
        # 小红书：缓解容貌焦虑和消费理性
        beauty_support_patterns = [
            r"不要给自己太大压力", r"每个人都有自己的美", r"适合自己的最重要",
            r"踩过坑", r"学费", r"理性消费", r"预算有限", r"性价比"
        ]
        
        for pattern in beauty_support_patterns:
            count = len(re.findall(pattern, text))
            if count > 0:
                score += count * 10
                insights.append(f"缓解容貌焦虑/消费理性: {pattern}")
        
        # 姐妹感检测
        sisterhood_patterns = [
            r"姐妹", r"宝贝", r"亲测", r"真心推荐", r"替你们踩坑",
            r"我们一起", r"理解你们的"
        ]
        
        for pattern in sisterhood_patterns:
            count = len(re.findall(pattern, text))
            if count > 0:
                score += count * 5
                insights.append(f"营造姐妹感: {pattern}")
    
    elif platform == Platform.BILIBILI:
        # B站：治愈成长焦虑
        healing_patterns = [
            r"你不是一个人", r"慢慢来", r"每个人的节奏不同", r"不要着急",
            r"理解你的困惑", r"这很正常", r"允许自己", r"给自己时间"
        ]
        
        for pattern in healing_patterns:
            count = len(re.findall(pattern, text))
            if count > 0:
                score += count * 10
                insights.append(f"提供治愈价值: {pattern}")
        
        # 陪伴感检测
        companion_patterns = [
            r"我也经历过", r"一起面对", r"我懂你的", r"陪伴你"
        ]
        
        for pattern in companion_patterns:
            count = len(re.findall(pattern, text))
            if count > 0:
                score += count * 8
                insights.append(f"营造陪伴感: {pattern}")
    
    elif platform == Platform.DOUYIN:
        # 抖音：打破认知误区，缓解FOMO
        reality_check_patterns = [
            r"真相是", r"实际上", r"别被骗了", r"事实是", r"真实情况",
            r"你以为.*实际", r"打破幻想", r"不要被表面"
        ]
        
        for pattern in reality_check_patterns:
            count = len(re.findall(pattern, text))
            if count > 0:
                score += count * 8
                insights.append(f"提供现实认知: {pattern}")
        
        # 数据震撼检测
        data_impact_patterns = [
            r"\d+%", r"\d+万", r"\d+倍", r"居然", r"竟然", r"震撼"
        ]
        
        data_count = sum(len(re.findall(pattern, text)) for pattern in data_impact_patterns)
        if data_count > 0:
            score += min(data_count * 3, 15)
            insights.append(f"数据震撼效果: {data_count}处")
    
    # 通用心理价值检测
    empathy_patterns = [
        r"理解", r"感同身受", r"我懂", r"知道你的", r"体会到"
    ]
    
    empathy_count = sum(len(re.findall(pattern, text)) for pattern in empathy_patterns)
    if empathy_count > 0:
        score += min(empathy_count * 4, 20)
        insights.append(f"表达理解和共情: {empathy_count}处")
    
    final_score = min(100, score)
    
    return round(final_score, 2), insights


def calculate_actionability_score(text: str) -> Tuple[float, List[str]]:
    """
    计算可操作性分数
    """
    if not text.strip():
        return 0.0, ["内容为空"]
    
    score = 0.0
    actions = []
    
    # 具体建议检测
    action_patterns = [
        r"建议.*：", r"可以试试", r"推荐", r"方法是", r"步骤.*：",
        r"首先.*其次.*最后", r"第一.*第二.*第三", r"具体做法"
    ]
    
    for pattern in action_patterns:
        count = len(re.findall(pattern, text))
        if count > 0:
            score += count * 15
            actions.append(f"提供具体建议: {pattern}")
    
    # 数字化指导检测
    number_patterns = [
        r"\d+分钟", r"\d+次", r"\d+天", r"\d+步", r"\d+个方法"
    ]
    
    for pattern in number_patterns:
        count = len(re.findall(pattern, text))
        if count > 0:
            score += count * 10
            actions.append(f"量化指导: {pattern}")
    
    # 时间成本透明
    cost_patterns = [
        r"需要.*时间", r"花费.*分钟", r"大约.*小时", r"每天.*分钟"
    ]
    
    for pattern in cost_patterns:
        count = len(re.findall(pattern, text))
        if count > 0:
            score += count * 8
            actions.append(f"时间成本透明: {pattern}")
    
    final_score = min(100, score)
    
    return round(final_score, 2), actions


def calculate_readability_score(text: str) -> float:
    """
    计算可读性分数 (基于句子长度和结构)
    """
    if not text.strip():
        return 0.0
    
    # 计算句子数
    sentences = len(re.findall(r'[.!?。！？]', text))
    if sentences == 0:
        sentences = 1
    
    # 计算字符数 (去除空格和换行)
    chars = len(text.replace(' ', '').replace('\n', ''))
    
    # 计算平均句长
    avg_sentence_length = chars / sentences
    
    # 可读性分数 (中文句子15-25字为最佳)
    if 15 <= avg_sentence_length <= 25:
        score = 100
    elif avg_sentence_length < 15:
        score = 70 + (avg_sentence_length / 15) * 30
    else:
        score = max(40, 100 - (avg_sentence_length - 25) * 2)
    
    # 段落结构加分
    paragraph_count = len(text.split('\n\n'))
    if paragraph_count >= 3:
        score = min(100, score + 10)
    
    return round(score, 2)


def calculate_platform_adaptation_score(text: str, title: str, platform: Platform) -> Tuple[float, List[str]]:
    """
    计算平台适配分数
    """
    from .platform_config import get_platform_config
    
    config = get_platform_config(platform)
    score = 0.0
    adaptations = []
    
    # 字数范围匹配
    text_length = len(text.replace(' ', '').replace('\n', ''))
    min_words, max_words = config.word_count_range
    
    if min_words <= text_length <= max_words:
        score += 40
        adaptations.append(f"字数适配: {text_length}字在合理范围内")
    else:
        ratio = min(text_length / min_words, max_words / text_length) if text_length > 0 else 0
        score += 40 * ratio
        adaptations.append(f"字数偏差: {text_length}字，建议{min_words}-{max_words}字")
    
    # 平台特定格式检测
    format_score = 0
    
    if platform == Platform.XIAOHONGSHU:
        # emoji检测
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text))
        if emoji_count >= 3:
            format_score += 15
            adaptations.append(f"emoji表情: {emoji_count}个")
        
        # 话题标签检测
        hashtag_count = len(re.findall(r'#[^#\s]+#', text))
        if hashtag_count >= 2:
            format_score += 15
            adaptations.append(f"话题标签: {hashtag_count}个")
    
    elif platform == Platform.BILIBILI:
        # 视频脚本结构检测
        time_markers = len(re.findall(r'\d+分钟|\d+秒|开场|结尾', text))
        if time_markers > 0:
            format_score += 20
            adaptations.append(f"视频结构标记: {time_markers}处")
    
    elif platform == Platform.DOUYIN:
        # 短视频特征检测
        hook_patterns = [r'^.{0,20}绝了', r'^.{0,20}震撼', r'^.{0,20}必须', r'^.{0,20}真相']
        hook_found = any(re.search(pattern, text) for pattern in hook_patterns)
        if hook_found:
            format_score += 20
            adaptations.append("强力开场hook")
    
    score += format_score
    final_score = min(100.0, score)
    
    return round(final_score, 2), adaptations


def evaluate_content_quality(
    text: str,
    title: str,
    platform: Platform,
    keywords: List[str] = None
) -> Tuple[QualityScore, Dict[str, List[str]]]:
    """
    综合评估内容质量 - 基于心理洞察
    """
    keywords = keywords or []
    
    # 计算各维度分数和详细反馈
    authenticity_score, authenticity_issues = calculate_authenticity_score(text)
    psychological_value, psychological_insights = calculate_psychological_value_score(text, platform)
    actionability_score, actionability_actions = calculate_actionability_score(text)
    readability_score = calculate_readability_score(text)
    platform_score, platform_adaptations = calculate_platform_adaptation_score(text, title, platform)
    
    # 创建质量评分对象
    quality_score = QualityScore(
        content_quality=round((authenticity_score * 0.4 + psychological_value * 0.3 + actionability_score * 0.3), 2),
        platform_adaptation=platform_score,
        engagement_potential=round((psychological_value + readability_score) / 2, 2),
        technical_quality=readability_score,
        total_score=0.0  # 临时值，将通过calculate_total()计算
    )
    
    # 计算总分
    quality_score.calculate_total()
    
    # 详细反馈
    feedback = {
        "真实性问题": authenticity_issues,
        "心理价值": psychological_insights,
        "可操作性": actionability_actions,
        "平台适配": platform_adaptations
    }
    
    return quality_score, feedback
