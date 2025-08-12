"""
内容生产流水线 - 协调各个Agent执行完整的内容生产流程
"""
import asyncio
from typing import Dict, Any, Optional
import logging
import time

from ..agents import ResearchAgent, WriterAgent, VideoAgent, ScorerAgent
from ..models import ContentTask, TaskResult, TaskStatus


class ContentPipeline:
    """
    内容生产流水线
    协调研究、写作、视频、评分等环节，完成完整的内容生产流程
    """
    
    def __init__(
        self,
        research_agent: Optional[ResearchAgent] = None,
        writer_agent: Optional[WriterAgent] = None,
        video_agent: Optional[VideoAgent] = None,
        scorer_agent: Optional[ScorerAgent] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.logger = logger or logging.getLogger("content_pipeline")
        
        # 初始化各个Agent
        self.research_agent = research_agent or ResearchAgent(logger=self.logger)
        self.writer_agent = writer_agent or WriterAgent(logger=self.logger)
        self.video_agent = video_agent or VideoAgent(logger=self.logger)
        self.scorer_agent = scorer_agent or ScorerAgent(logger=self.logger)
    
    async def execute(
        self, 
        task: ContentTask, 
        progress_callback: Optional[callable] = None
    ) -> TaskResult:
        """
        执行完整的内容生产流程
        
        Args:
            task: 内容任务
            progress_callback: 进度回调函数 (stage, status, data)
            
        Returns:
            TaskResult: 生产结果
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting content pipeline for task {task.task_id}")
            
            # 创建结果对象
            result = TaskResult()
            
            # Stage 1: 研究阶段
            await self._notify_progress(progress_callback, "research", "processing", None)
            research_result = await self._execute_research(task)
            result.research_data = research_result["research_data"]
            await self._notify_progress(progress_callback, "research", "completed", result.research_data)
            
            # Stage 2: 写作阶段  
            await self._notify_progress(progress_callback, "writing", "processing", None)
            writing_result = await self._execute_writing(task, result.research_data)
            result.content_versions = writing_result["content_versions"]
            await self._notify_progress(progress_callback, "writing", "completed", result.content_versions)
            
            # Stage 3: 视频制作阶段 (如果需要)
            video_versions = []
            if task.include_video:
                await self._notify_progress(progress_callback, "video", "processing", None)
                video_result = await self._execute_video_production(task, result.research_data, result.content_versions)
                video_versions = video_result["video_versions"]
                await self._notify_progress(progress_callback, "video", "completed", video_versions)
            else:
                await self._notify_progress(progress_callback, "video", "skipped", None)
            
            # Stage 4: 评分阶段
            await self._notify_progress(progress_callback, "scoring", "processing", None)
            scoring_result = await self._execute_scoring(
                task, 
                result.research_data, 
                result.content_versions, 
                video_versions
            )
            result.quality_scores = scoring_result["quality_scores"]
            result.best_version = self._select_overall_best_version(scoring_result["ranking"])
            await self._notify_progress(progress_callback, "scoring", "completed", scoring_result)
            
            # 计算执行时间
            result.execution_time = time.time() - start_time
            
            self.logger.info(
                f"Content pipeline completed for task {task.task_id} "
                f"in {result.execution_time:.2f} seconds"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Content pipeline failed for task {task.task_id}: {str(e)}")
            await self._notify_progress(progress_callback, "error", "failed", {"error": str(e)})
            raise
    
    async def _execute_research(self, task: ContentTask) -> Dict[str, Any]:
        """
        执行研究阶段
        """
        try:
            self.logger.info(f"Starting research phase for task {task.task_id}")
            
            research_input = {
                "topic": task.topic,
                "depth": task.research_depth,
                "platforms": [p.value for p in task.platforms]
            }
            
            result = await self.research_agent.execute(research_input)
            
            self.logger.info(f"Research phase completed for task {task.task_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Research phase failed for task {task.task_id}: {str(e)}")
            raise
    
    async def _execute_writing(self, task: ContentTask, research_data) -> Dict[str, Any]:
        """
        执行写作阶段
        """
        try:
            self.logger.info(f"Starting writing phase for task {task.task_id}")
            
            writing_input = {
                "research_data": research_data,
                "platforms": task.platforms,
                "versions_per_platform": task.versions_per_platform
            }
            
            result = await self.writer_agent.execute(writing_input)
            
            self.logger.info(
                f"Writing phase completed for task {task.task_id}, "
                f"generated {len(result['content_versions'])} versions"
            )
            return result
            
        except Exception as e:
            self.logger.error(f"Writing phase failed for task {task.task_id}: {str(e)}")
            raise
    
    async def _execute_video_production(
        self, 
        task: ContentTask, 
        research_data,
        content_versions
    ) -> Dict[str, Any]:
        """
        执行视频制作阶段
        """
        try:
            self.logger.info(f"Starting video production phase for task {task.task_id}")
            
            video_input = {
                "research_data": research_data,
                "platforms": task.platforms,
                "content_versions": content_versions
            }
            
            result = await self.video_agent.execute(video_input)
            
            self.logger.info(
                f"Video production phase completed for task {task.task_id}, "
                f"generated {len(result['video_versions'])} video versions"
            )
            return result
            
        except Exception as e:
            self.logger.error(f"Video production phase failed for task {task.task_id}: {str(e)}")
            raise
    
    async def _execute_scoring(
        self, 
        task: ContentTask, 
        research_data, 
        content_versions, 
        video_versions
    ) -> Dict[str, Any]:
        """
        执行评分阶段
        """
        try:
            self.logger.info(f"Starting scoring phase for task {task.task_id}")
            
            scoring_input = {
                "content_versions": content_versions,
                "video_versions": video_versions,
                "research_data": research_data
            }
            
            result = await self.scorer_agent.execute(scoring_input)
            
            total_versions = len(content_versions) + len(video_versions)
            self.logger.info(
                f"Scoring phase completed for task {task.task_id}, "
                f"scored {total_versions} versions"
            )
            return result
            
        except Exception as e:
            self.logger.error(f"Scoring phase failed for task {task.task_id}: {str(e)}")
            raise
    
    def _select_overall_best_version(self, ranking):
        """
        选择总体最佳版本
        """
        if not ranking:
            return None
        
        # 返回得分最高的版本
        best_version, best_score = ranking[0]
        
        self.logger.info(
            f"Selected best version {best_version.version_id} "
            f"with score {best_score.total_score:.2f}"
        )
        
        return best_version
    
    async def _notify_progress(
        self, 
        callback: Optional[callable], 
        stage: str, 
        status: str, 
        data: Any
    ) -> None:
        """
        通知进度更新
        """
        if callback:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(stage, status, data)
                else:
                    callback(stage, status, data)
            except Exception as e:
                self.logger.warning(f"Progress callback failed: {str(e)}")
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """
        获取流水线状态
        """
        return {
            "research_agent_busy": self.research_agent.is_busy,
            "writer_agent_busy": self.writer_agent.is_busy,
            "video_agent_busy": self.video_agent.is_busy,
            "scorer_agent_busy": self.scorer_agent.is_busy,
        }
    
    async def health_check(self) -> Dict[str, bool]:
        """
        健康检查
        """
        try:
            # 简单的健康检查 - 确保所有Agent都可用
            health = {
                "research_agent": True,
                "writer_agent": True, 
                "video_agent": True,
                "scorer_agent": True,
                "overall": True
            }
            
            return health
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "research_agent": False,
                "writer_agent": False,
                "video_agent": False, 
                "scorer_agent": False,
                "overall": False
            }
