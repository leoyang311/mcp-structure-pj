"""
Master控制器 - 系统的核心调度器
"""
import asyncio
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import uuid

from .task_manager import TaskManager
from .content_pipeline import ContentPipeline
from ..models import ContentTask, TaskStatus, Platform
from ..agents import ResearchAgent, WriterAgent, VideoAgent, ScorerAgent


class MasterController:
    """
    Master控制器
    负责系统的整体调度和任务管理
    """
    
    def __init__(
        self,
        max_concurrent_tasks: int = 5,
        logger: Optional[logging.Logger] = None,
        **agent_configs
    ):
        self.logger = logger or logging.getLogger("master_controller")
        self.max_concurrent_tasks = max_concurrent_tasks
        
        # 初始化任务管理器
        self.task_manager = TaskManager(logger=self.logger)
        
        # 初始化各个Agent
        self._init_agents(**agent_configs)
        
        # 初始化内容流水线
        self.pipeline = ContentPipeline(
            research_agent=self.research_agent,
            writer_agent=self.writer_agent,
            video_agent=self.video_agent,
            scorer_agent=self.scorer_agent,
            logger=self.logger
        )
        
        # 任务队列和执行状态
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
        
        self.logger.info("Master controller initialized")
    
    def _init_agents(self, **configs):
        """初始化各个Agent"""
        try:
            # 获取各Agent的配置
            research_config = configs.get("research_agent", {})
            writer_config = configs.get("writer_agent", {})
            video_config = configs.get("video_agent", {})
            scorer_config = configs.get("scorer_agent", {})
            
            # 初始化Agent
            self.research_agent = ResearchAgent(
                search_api_key=research_config.get("search_api_key"),
                logger=self.logger
            )
            
            self.writer_agent = WriterAgent(
                llm_client=writer_config.get("llm_client"),
                logger=self.logger
            )
            
            self.video_agent = VideoAgent(
                llm_client=video_config.get("llm_client"),
                logger=self.logger
            )
            
            self.scorer_agent = ScorerAgent(logger=self.logger)
            
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {str(e)}")
            raise
    
    async def create_content_task(
        self,
        topic: str,
        platforms: List[str],
        research_depth: str = "medium",
        versions_per_platform: int = 3,
        include_video: bool = True,
        priority: int = 0
    ) -> Dict[str, Any]:
        """
        创建内容生产任务
        
        Args:
            topic: 话题
            platforms: 目标平台列表
            research_depth: 研究深度
            versions_per_platform: 每平台生成版本数
            include_video: 是否包含视频
            priority: 任务优先级 (数值越大优先级越高)
            
        Returns:
            Dict: 创建结果
        """
        try:
            # 验证输入
            if not topic or not topic.strip():
                raise ValueError("Topic cannot be empty")
            
            if not platforms:
                raise ValueError("At least one platform is required")
            
            # 验证平台支持
            supported_platforms = [p.value for p in Platform]
            for platform in platforms:
                if platform not in supported_platforms:
                    raise ValueError(f"Unsupported platform: {platform}")
            
            # 创建任务
            task = self.task_manager.create_task(
                topic=topic,
                platforms=platforms,
                research_depth=research_depth,
                versions_per_platform=versions_per_platform,
                include_video=include_video
            )
            
            # 添加到队列
            await self.task_queue.put((priority, task))
            
            self.logger.info(f"Task {task.task_id} added to queue")
            
            return {
                "task_id": task.task_id,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "estimated_time": self._estimate_task_time(task),
                "queue_position": self.task_queue.qsize()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create task: {str(e)}")
            raise
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 任务状态信息
        """
        try:
            task = self.task_manager.get_task(task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")
            
            # 计算进度百分比
            progress = self._calculate_task_progress(task)
            
            return {
                "task_id": task.task_id,
                "status": task.status.value,
                "progress": progress,
                "current_stage": task.current_stage,
                "stages": task.stage_progress,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "execution_time": (
                    (datetime.now() - task.started_at).total_seconds() 
                    if task.started_at and not task.completed_at 
                    else None
                ),
                "error_message": task.error_message,
                "result_summary": self._get_result_summary(task) if task.result else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get task status: {str(e)}")
            raise
    
    async def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 任务结果
        """
        try:
            task = self.task_manager.get_task(task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")
            
            if task.status != TaskStatus.COMPLETED:
                raise ValueError(f"Task {task_id} is not completed")
            
            if not task.result:
                raise ValueError(f"Task {task_id} has no result")
            
            return {
                "task_id": task.task_id,
                "topic": task.topic,
                "platforms": [p.value for p in task.platforms],
                "research_data": task.result.research_data.dict() if task.result.research_data else None,
                "content_versions": [v.dict() for v in task.result.content_versions],
                "quality_scores": {k: v.dict() for k, v in task.result.quality_scores.items()},
                "best_version": task.result.best_version.dict() if task.result.best_version else None,
                "execution_time": task.result.execution_time,
                "completed_at": task.completed_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get task result: {str(e)}")
            raise
    
    async def start_processing(self):
        """
        开始处理任务队列
        """
        if self.is_running:
            self.logger.warning("Master controller is already running")
            return
        
        self.is_running = True
        self.logger.info("Master controller started processing")
        
        try:
            while self.is_running:
                # 检查并发限制
                if len(self.running_tasks) >= self.max_concurrent_tasks:
                    await asyncio.sleep(1)
                    continue
                
                try:
                    # 从队列获取任务 (带优先级)
                    priority, task = await asyncio.wait_for(
                        self.task_queue.get(), timeout=1.0
                    )
                    
                    # 开始执行任务
                    task_coroutine = self._execute_task(task)
                    async_task = asyncio.create_task(task_coroutine)
                    self.running_tasks[task.task_id] = async_task
                    
                    self.logger.info(f"Started processing task {task.task_id}")
                    
                except asyncio.TimeoutError:
                    # 队列为空，继续循环
                    continue
                except Exception as e:
                    self.logger.error(f"Error in task processing loop: {str(e)}")
                    continue
                
                # 清理已完成的任务
                await self._cleanup_completed_tasks()
                
        except Exception as e:
            self.logger.error(f"Master controller processing failed: {str(e)}")
        finally:
            self.is_running = False
            self.logger.info("Master controller stopped processing")
    
    async def stop_processing(self):
        """
        停止处理任务队列
        """
        self.logger.info("Stopping master controller...")
        self.is_running = False
        
        # 等待所有运行中的任务完成或取消
        if self.running_tasks:
            self.logger.info(f"Waiting for {len(self.running_tasks)} running tasks to complete")
            
            # 等待最多30秒
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.running_tasks.values(), return_exceptions=True),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                self.logger.warning("Some tasks did not complete within timeout, cancelling them")
                for task in self.running_tasks.values():
                    task.cancel()
        
        self.running_tasks.clear()
        self.logger.info("Master controller stopped")
    
    async def _execute_task(self, task: ContentTask):
        """
        执行单个任务
        """
        try:
            # 更新任务状态
            self.task_manager.update_task_status(task.task_id, TaskStatus.PROCESSING)
            
            # 定义进度回调函数
            async def progress_callback(stage: str, status: str, data: Any):
                self.task_manager.update_task_stage(task.task_id, stage, status)
                self.logger.info(f"Task {task.task_id} - {stage}: {status}")
            
            # 执行内容生产流水线
            result = await self.pipeline.execute(task, progress_callback)
            
            # 完成任务
            self.task_manager.complete_task(task.task_id, result)
            
            self.logger.info(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            # 任务失败
            error_msg = str(e)
            self.task_manager.fail_task(task.task_id, error_msg)
            self.logger.error(f"Task {task.task_id} failed: {error_msg}")
        finally:
            # 从运行任务列表中移除
            self.running_tasks.pop(task.task_id, None)
    
    async def _cleanup_completed_tasks(self):
        """
        清理已完成的任务
        """
        completed_tasks = []
        for task_id, async_task in self.running_tasks.items():
            if async_task.done():
                completed_tasks.append(task_id)
        
        for task_id in completed_tasks:
            self.running_tasks.pop(task_id, None)
    
    def _estimate_task_time(self, task: ContentTask) -> int:
        """
        估算任务执行时间 (秒)
        """
        base_time = 120  # 基础2分钟
        
        # 根据研究深度调整
        depth_multiplier = {
            "shallow": 0.7,
            "medium": 1.0,
            "deep": 1.5
        }
        base_time *= depth_multiplier.get(task.research_depth, 1.0)
        
        # 根据平台数量调整
        base_time += len(task.platforms) * 30
        
        # 根据版本数量调整
        base_time += task.versions_per_platform * 20
        
        # 视频制作额外时间
        if task.include_video:
            base_time += 60
        
        return int(base_time)
    
    def _calculate_task_progress(self, task: ContentTask) -> int:
        """
        计算任务进度百分比
        """
        if task.status == TaskStatus.CREATED:
            return 0
        elif task.status == TaskStatus.QUEUED:
            return 5
        elif task.status == TaskStatus.COMPLETED:
            return 100
        elif task.status == TaskStatus.FAILED:
            return 100
        
        # 处理中状态 - 根据阶段计算进度
        stage_weights = {
            "research": 25,
            "writing": 40,
            "video": 20,
            "scoring": 15
        }
        
        progress = 0
        for stage, weight in stage_weights.items():
            stage_status = task.stage_progress.get(stage, "pending")
            if stage_status == "completed":
                progress += weight
            elif stage_status == "processing":
                progress += weight // 2
            elif stage_status == "skipped":
                progress += weight
        
        return min(95, max(10, progress))  # 确保在10-95之间
    
    def _get_result_summary(self, task: ContentTask) -> Dict[str, Any]:
        """
        获取结果摘要
        """
        if not task.result:
            return None
        
        return {
            "content_versions_count": len(task.result.content_versions),
            "video_versions_count": len([v for v in task.result.content_versions if v.content_type.value == "video_script"]),
            "best_score": task.result.best_version.metadata.get("quality_score") if task.result.best_version else None,
            "execution_time": task.result.execution_time
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态
        """
        try:
            pipeline_status = await self.pipeline.get_pipeline_status()
            task_stats = self.task_manager.get_task_statistics()
            
            return {
                "is_running": self.is_running,
                "queue_size": self.task_queue.qsize(),
                "running_tasks": len(self.running_tasks),
                "max_concurrent_tasks": self.max_concurrent_tasks,
                "pipeline_status": pipeline_status,
                "task_statistics": task_stats,
                "system_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {str(e)}")
            raise
