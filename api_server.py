"""
FastAPI服务器 - HTTP API接口
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
except ImportError:
    print("请先安装依赖: uv sync")
    exit(1)

from src.content_factory import MasterController, Platform, TaskStatus

# 初始化FastAPI应用
app = FastAPI(
    title="FastMCP Multi-Agent Content Production API",
    description="基于多Agent架构的智能内容生产系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局Master控制器
master_controller: Optional[MasterController] = None

# 请求/响应模型
class CreateTaskRequest(BaseModel):
    topic: str = Field(..., description="内容话题", min_length=1, max_length=200)
    platforms: List[str] = Field(default=["wechat", "xiaohongshu"], description="目标平台列表")
    research_depth: str = Field(default="medium", description="研究深度", regex="^(shallow|medium|deep)$")
    versions_per_platform: int = Field(default=3, description="每平台生成版本数", ge=1, le=10)
    include_video: bool = Field(default=True, description="是否包含视频内容")


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    estimated_time: Optional[int] = None
    queue_position: Optional[int] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    current_stage: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    stages: Optional[Dict[str, str]] = None


class TaskResultResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    best_version: Optional[Dict[str, Any]] = None
    all_versions: Optional[List[Dict[str, Any]]] = None
    research_data: Optional[Dict[str, Any]] = None
    execution_stats: Optional[Dict[str, Any]] = None


class SystemStatusResponse(BaseModel):
    is_running: bool
    queue_size: int
    running_tasks: int
    max_concurrent_tasks: int
    system_time: str
    task_statistics: Dict[str, int]


class PlatformInfo(BaseModel):
    platform: str
    description: str
    content_types: List[str]
    max_versions: int


# 依赖注入
def get_master_controller() -> MasterController:
    """获取Master控制器实例"""
    global master_controller
    if not master_controller:
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        master_controller = MasterController(max_concurrent_tasks=3)
        # 在后台启动处理器
        asyncio.create_task(master_controller.start_processing())
    return master_controller


# API端点
@app.get("/", response_model=Dict[str, str])
async def root():
    """API根端点"""
    return {
        "name": "FastMCP Content Factory API",
        "version": "1.0.0",
        "description": "Multi-Agent Content Production System",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """健康检查端点"""
    try:
        controller = get_master_controller()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "content-factory-api"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/platforms", response_model=List[PlatformInfo])
async def get_supported_platforms():
    """获取支持的平台列表"""
    platforms_info = [
        {
            "platform": Platform.WECHAT.value,
            "description": "微信公众号 - 专业深度内容",
            "content_types": ["article", "tutorial", "analysis"],
            "max_versions": 10
        },
        {
            "platform": Platform.XIAOHONGSHU.value, 
            "description": "小红书 - 轻松活泼内容",
            "content_types": ["lifestyle", "tips", "review"],
            "max_versions": 10
        },
        {
            "platform": Platform.BILIBILI.value,
            "description": "B站 - 教育向视频内容",
            "content_types": ["video_script", "tutorial", "explanation"],
            "max_versions": 5
        },
        {
            "platform": Platform.DOUYIN.value,
            "description": "抖音 - 娱乐向短视频",
            "content_types": ["short_video", "entertainment", "trend"],
            "max_versions": 5
        }
    ]
    return platforms_info


@app.post("/tasks", response_model=TaskResponse)
async def create_task(
    request: CreateTaskRequest,
    controller: MasterController = Depends(get_master_controller)
):
    """创建内容生产任务"""
    try:
        # 验证平台
        valid_platforms = [p.value for p in Platform]
        for platform in request.platforms:
            if platform not in valid_platforms:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的平台: {platform}. 支持的平台: {', '.join(valid_platforms)}"
                )
        
        # 创建任务
        result = await controller.create_content_task(
            topic=request.topic,
            platforms=request.platforms,
            research_depth=request.research_depth,
            versions_per_platform=request.versions_per_platform,
            include_video=request.include_video
        )
        
        return TaskResponse(
            task_id=result["task_id"],
            status="created",
            message="任务创建成功",
            estimated_time=result.get("estimated_time"),
            queue_position=result.get("queue_position")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    controller: MasterController = Depends(get_master_controller)
):
    """获取任务状态"""
    try:
        status_data = await controller.get_task_status(task_id)
        
        return TaskStatusResponse(**status_data)
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"任务不存在或获取失败: {str(e)}")


@app.get("/tasks/{task_id}/result", response_model=TaskResultResponse)
async def get_task_result(
    task_id: str,
    controller: MasterController = Depends(get_master_controller)
):
    """获取任务结果"""
    try:
        result_data = await controller.get_task_result(task_id)
        
        return TaskResultResponse(
            task_id=task_id,
            status=result_data.get("status", "unknown"),
            result=result_data,
            best_version=result_data.get("best_version"),
            all_versions=result_data.get("all_versions"),
            research_data=result_data.get("research_data"),
            execution_stats=result_data.get("execution_stats")
        )
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"任务结果不存在或获取失败: {str(e)}")


@app.delete("/tasks/{task_id}")
async def cancel_task(
    task_id: str,
    controller: MasterController = Depends(get_master_controller)
):
    """取消任务"""
    try:
        success = await controller.cancel_task(task_id)
        
        if success:
            return {"message": "任务已取消", "task_id": task_id}
        else:
            raise HTTPException(status_code=400, detail="无法取消任务 - 可能已完成或不存在")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")


@app.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status(
    controller: MasterController = Depends(get_master_controller)
):
    """获取系统状态"""
    try:
        status_data = await controller.get_system_status()
        return SystemStatusResponse(**status_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统状态失败: {str(e)}")


@app.get("/tasks", response_model=Dict[str, Any])
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    controller: MasterController = Depends(get_master_controller)
):
    """列出任务（带分页和过滤）"""
    try:
        # 这里简化实现，实际应该在MasterController中添加相应方法
        system_status = await controller.get_system_status()
        
        return {
            "tasks": [],  # TODO: 实现任务列表查询
            "total": system_status["task_statistics"]["total"],
            "limit": limit,
            "offset": offset,
            "filters": {"status": status} if status else {}
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")


@app.post("/system/start")
async def start_system(
    controller: MasterController = Depends(get_master_controller)
):
    """启动系统处理"""
    try:
        await controller.start_processing()
        return {"message": "系统处理已启动"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动系统失败: {str(e)}")


@app.post("/system/stop")
async def stop_system(
    controller: MasterController = Depends(get_master_controller)
):
    """停止系统处理"""
    try:
        await controller.stop_processing()
        return {"message": "系统处理已停止"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止系统失败: {str(e)}")


# 异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "内部服务器错误",
            "details": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print("🚀 FastMCP Content Factory API 启动中...")
    
    # 初始化Master控制器
    controller = get_master_controller()
    
    print("✅ API服务器已启动")
    print("📖 API文档: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("🛑 FastMCP Content Factory API 关闭中...")
    
    # 清理资源
    global master_controller
    if master_controller:
        await master_controller.stop_processing()
        master_controller = None
    
    print("✅ API服务器已关闭")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
