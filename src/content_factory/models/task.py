"""
数据模型定义
"""
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态枚举"""
    CREATED = "created"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ContentType(str, Enum):
    """内容类型枚举"""
    ARTICLE = "article"
    VIDEO_SCRIPT = "video_script"
    SOCIAL_POST = "social_post"


class Platform(str, Enum):
    """平台枚举"""
    WECHAT = "wechat"
    XIAOHONGSHU = "xiaohongshu"
    BILIBILI = "bilibili"
    DOUYIN = "douyin"


class PlatformConfig(BaseModel):
    """平台配置"""
    name: str
    word_count_range: tuple[int, int]
    style: str
    special_requirements: List[str] = Field(default_factory=list)
    
    class Config:
        frozen = True


class ResearchData(BaseModel):
    """研究数据"""
    topic: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    key_points: List[str] = Field(default_factory=list)
    trends: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)
    summary: str = ""
    created_at: datetime = Field(default_factory=datetime.now)


class ContentVersion(BaseModel):
    """内容版本"""
    version_id: str
    platform: Platform
    content_type: ContentType
    title: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class QualityScore(BaseModel):
    """质量评分"""
    content_quality: float = Field(ge=0, le=100)
    platform_adaptation: float = Field(ge=0, le=100)
    engagement_potential: float = Field(ge=0, le=100)
    technical_quality: float = Field(ge=0, le=100)
    total_score: float = Field(ge=0, le=100)
    
    def calculate_total(self) -> float:
        """计算总分"""
        self.total_score = (
            self.content_quality * 0.3 +
            self.platform_adaptation * 0.25 +
            self.engagement_potential * 0.25 +
            self.technical_quality * 0.2
        )
        return self.total_score


class TaskResult(BaseModel):
    """任务结果"""
    research_data: Optional[ResearchData] = None
    content_versions: List[ContentVersion] = Field(default_factory=list)
    quality_scores: Dict[str, QualityScore] = Field(default_factory=dict)
    best_version: Optional[ContentVersion] = None
    image_results: Dict[str, Any] = Field(default_factory=dict)    # platform -> image generation result
    seedance_results: Dict[str, Any] = Field(default_factory=dict) # platform -> {video_url, prompt, ...}
    execution_time: float = 0.0


class ContentTask(BaseModel):
    """内容生产任务"""
    task_id: str
    topic: str
    platforms: List[Platform]
    research_depth: str = "medium"  # shallow, medium, deep
    versions_per_platform: int = 3
    include_video: bool = True
    include_image: bool = False           # 图片生成默认关闭（需要额外API配额）
    include_seedance_video: bool = False  # Seedance真实视频生成默认关闭（需要FAL_KEY）
    
    # 任务状态
    status: TaskStatus = TaskStatus.CREATED
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 执行阶段
    current_stage: str = "created"
    stage_progress: Dict[str, str] = Field(default_factory=dict)
    
    # 结果数据
    result: Optional[TaskResult] = None
    error_message: Optional[str] = None
    
    def update_stage(self, stage: str, status: str = "processing") -> None:
        """更新执行阶段"""
        self.current_stage = stage
        self.stage_progress[stage] = status
        
    def set_completed(self, result: TaskResult) -> None:
        """设置任务完成"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        
    def set_failed(self, error: str) -> None:
        """设置任务失败"""
        self.status = TaskStatus.FAILED
        self.error_message = error
        self.completed_at = datetime.now()
