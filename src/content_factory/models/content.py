"""
内容相关数据模型
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .task import Platform, ContentType


class ContentTemplate(BaseModel):
    """内容模板"""
    platform: Platform
    content_type: ContentType
    template: str
    variables: List[str] = Field(default_factory=list)
    style_guide: str = ""


class VideoSpec(BaseModel):
    """视频规格"""
    platform: Platform
    duration_range: tuple[int, int]  # 秒
    resolution: tuple[int, int]  # (width, height)
    orientation: str  # horizontal, vertical
    style: str
    
    class Config:
        frozen = True


class SEOKeywords(BaseModel):
    """SEO关键词"""
    primary_keywords: List[str] = Field(default_factory=list)
    secondary_keywords: List[str] = Field(default_factory=list)
    long_tail_keywords: List[str] = Field(default_factory=list)
    search_volume: Dict[str, int] = Field(default_factory=dict)


class ContentAnalytics(BaseModel):
    """内容分析"""
    readability_score: float = 0.0
    keyword_density: Dict[str, float] = Field(default_factory=dict)
    sentiment_score: float = 0.0
    engagement_prediction: float = 0.0
    seo_score: float = 0.0


class PublishedContent(BaseModel):
    """已发布内容"""
    content_id: str
    platform: Platform
    title: str
    content: str
    published_at: datetime
    url: Optional[str] = None
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    analytics: Optional[ContentAnalytics] = None
