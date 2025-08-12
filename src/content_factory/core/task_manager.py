"""
任务管理器 - 负责任务的创建、存储和状态管理
"""
import uuid
from typing import Dict, List, Optional
from datetime import datetime
import logging

from ..models import ContentTask, TaskStatus, Platform


class TaskManager:
    """
    任务管理器
    负责任务的生命周期管理
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("task_manager")
        self.tasks: Dict[str, ContentTask] = {}
        self.task_history: List[ContentTask] = []
    
    def create_task(
        self,
        topic: str,
        platforms: List[str],
        research_depth: str = "medium",
        versions_per_platform: int = 3,
        include_video: bool = True
    ) -> ContentTask:
        """
        创建新任务
        
        Args:
            topic: 话题
            platforms: 目标平台列表
            research_depth: 研究深度 (shallow, medium, deep)
            versions_per_platform: 每平台生成版本数
            include_video: 是否包含视频内容
            
        Returns:
            ContentTask: 创建的任务对象
        """
        try:
            # 验证平台
            platform_enums = []
            for platform in platforms:
                if isinstance(platform, str):
                    try:
                        platform_enums.append(Platform(platform))
                    except ValueError:
                        raise ValueError(f"Unsupported platform: {platform}")
                else:
                    platform_enums.append(platform)
            
            # 生成任务ID
            task_id = str(uuid.uuid4())
            
            # 创建任务对象
            task = ContentTask(
                task_id=task_id,
                topic=topic,
                platforms=platform_enums,
                research_depth=research_depth,
                versions_per_platform=versions_per_platform,
                include_video=include_video,
                status=TaskStatus.CREATED,
                created_at=datetime.now()
            )
            
            # 初始化阶段进度
            task.stage_progress = {
                "research": "pending",
                "writing": "pending", 
                "video": "pending" if include_video else "skipped",
                "scoring": "pending"
            }
            
            # 存储任务
            self.tasks[task_id] = task
            
            self.logger.info(f"Created task {task_id} for topic: {topic}")
            
            return task
            
        except Exception as e:
            self.logger.error(f"Failed to create task: {str(e)}")
            raise
    
    def get_task(self, task_id: str) -> Optional[ContentTask]:
        """
        获取任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[ContentTask]: 任务对象或None
        """
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 新状态
            
        Returns:
            bool: 更新是否成功
        """
        try:
            task = self.tasks.get(task_id)
            if not task:
                self.logger.warning(f"Task {task_id} not found")
                return False
            
            old_status = task.status
            task.status = status
            
            # 更新时间戳
            if status == TaskStatus.PROCESSING and not task.started_at:
                task.started_at = datetime.now()
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                task.completed_at = datetime.now()
            
            self.logger.info(f"Task {task_id} status changed: {old_status} -> {status}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update task status: {str(e)}")
            return False
    
    def update_task_stage(self, task_id: str, stage: str, status: str = "processing") -> bool:
        """
        更新任务执行阶段
        
        Args:
            task_id: 任务ID
            stage: 阶段名称
            status: 阶段状态
            
        Returns:
            bool: 更新是否成功
        """
        try:
            task = self.tasks.get(task_id)
            if not task:
                return False
            
            task.update_stage(stage, status)
            
            self.logger.debug(f"Task {task_id} stage updated: {stage} -> {status}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update task stage: {str(e)}")
            return False
    
    def complete_task(self, task_id: str, result) -> bool:
        """
        完成任务
        
        Args:
            task_id: 任务ID
            result: 任务结果
            
        Returns:
            bool: 操作是否成功
        """
        try:
            task = self.tasks.get(task_id)
            if not task:
                return False
            
            task.set_completed(result)
            
            # 添加到历史记录
            self.task_history.append(task)
            
            self.logger.info(f"Task {task_id} completed successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to complete task: {str(e)}")
            return False
    
    def fail_task(self, task_id: str, error_message: str) -> bool:
        """
        标记任务失败
        
        Args:
            task_id: 任务ID
            error_message: 错误消息
            
        Returns:
            bool: 操作是否成功
        """
        try:
            task = self.tasks.get(task_id)
            if not task:
                return False
            
            task.set_failed(error_message)
            
            # 添加到历史记录
            self.task_history.append(task)
            
            self.logger.error(f"Task {task_id} failed: {error_message}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to fail task: {str(e)}")
            return False
    
    def get_active_tasks(self) -> List[ContentTask]:
        """
        获取活跃任务列表
        
        Returns:
            List[ContentTask]: 活跃任务列表
        """
        active_statuses = [TaskStatus.CREATED, TaskStatus.QUEUED, TaskStatus.PROCESSING]
        return [task for task in self.tasks.values() if task.status in active_statuses]
    
    def get_completed_tasks(self) -> List[ContentTask]:
        """
        获取已完成任务列表
        
        Returns:
            List[ContentTask]: 已完成任务列表
        """
        return [task for task in self.task_history if task.status == TaskStatus.COMPLETED]
    
    def get_task_statistics(self) -> Dict[str, int]:
        """
        获取任务统计信息
        
        Returns:
            Dict[str, int]: 统计信息
        """
        all_tasks = list(self.tasks.values()) + self.task_history
        
        stats = {
            "total": len(all_tasks),
            "created": 0,
            "queued": 0, 
            "processing": 0,
            "completed": 0,
            "failed": 0
        }
        
        for task in all_tasks:
            if task.status == TaskStatus.CREATED:
                stats["created"] += 1
            elif task.status == TaskStatus.QUEUED:
                stats["queued"] += 1
            elif task.status == TaskStatus.PROCESSING:
                stats["processing"] += 1
            elif task.status == TaskStatus.COMPLETED:
                stats["completed"] += 1
            elif task.status == TaskStatus.FAILED:
                stats["failed"] += 1
        
        return stats
    
    def cleanup_old_tasks(self, max_history_size: int = 1000) -> int:
        """
        清理旧任务记录
        
        Args:
            max_history_size: 最大历史记录数量
            
        Returns:
            int: 清理的任务数量
        """
        if len(self.task_history) <= max_history_size:
            return 0
        
        # 保留最新的记录
        sorted_history = sorted(self.task_history, key=lambda x: x.created_at, reverse=True)
        kept_history = sorted_history[:max_history_size]
        
        removed_count = len(self.task_history) - len(kept_history)
        self.task_history = kept_history
        
        self.logger.info(f"Cleaned up {removed_count} old task records")
        
        return removed_count
