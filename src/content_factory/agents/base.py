"""
基础Agent类定义
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
import asyncio


class BaseAgent(ABC):
    """
    基础Agent抽象类
    所有专门的Agent都应继承此类
    """
    
    def __init__(self, name: str, logger: Optional[logging.Logger] = None):
        self.name = name
        self.logger = logger or logging.getLogger(f"agent.{name}")
        self.is_busy = False
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理输入数据并返回结果
        
        Args:
            input_data: 输入数据字典
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        pass
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行Agent任务的入口方法
        
        Args:
            input_data: 输入数据
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        if self.is_busy:
            raise RuntimeError(f"Agent {self.name} is busy")
        
        try:
            self.is_busy = True
            self.logger.info(f"Agent {self.name} starting execution")
            
            result = await self.process(input_data)
            
            self.logger.info(f"Agent {self.name} completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Agent {self.name} failed: {str(e)}")
            raise
        finally:
            self.is_busy = False
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取Agent状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        return {
            "name": self.name,
            "is_busy": self.is_busy,
        }
