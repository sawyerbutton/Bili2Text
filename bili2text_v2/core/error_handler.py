"""
错误处理工具
提供统一的错误处理机制
"""
import functools
import traceback
from typing import Optional, Type, Callable, Any, Union, Tuple
from contextlib import contextmanager

from .logger import get_logger
from .exceptions import (
    Bili2TextError,
    NetworkError,
    TranscriptionError,
    handle_exception
)


def error_handler(
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    default_return: Any = None,
    logger_name: Optional[str] = None,
    raise_on_error: bool = True,
    error_message: Optional[str] = None
):
    """
    错误处理装饰器
    
    Args:
        exceptions: 要捕获的异常类型
        default_return: 出错时的默认返回值
        logger_name: 日志器名称
        raise_on_error: 是否重新抛出异常
        error_message: 自定义错误消息
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            
            try:
                return func(*args, **kwargs)
            
            except exceptions as e:
                # 处理异常
                error_dict = handle_exception(e, logger)
                
                # 自定义错误消息
                if error_message:
                    logger.error(error_message, extra=error_dict)
                
                # 是否重新抛出
                if raise_on_error:
                    raise
                
                # 返回默认值
                return default_return
        
        return wrapper
    return decorator


def safe_execute(
    func: Callable,
    *args,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    default: Any = None,
    logger_name: Optional[str] = None,
    **kwargs
) -> Any:
    """
    安全执行函数
    
    Args:
        func: 要执行的函数
        *args: 函数参数
        exceptions: 要捕获的异常类型
        default: 出错时的默认返回值
        logger_name: 日志器名称
        **kwargs: 函数关键字参数
        
    Returns:
        函数返回值或默认值
    """
    logger = get_logger(logger_name or func.__module__)
    
    try:
        return func(*args, **kwargs)
    except exceptions as e:
        handle_exception(e, logger)
        return default


@contextmanager
def error_context(
    message: str,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    logger_name: Optional[str] = None,
    raise_on_error: bool = True
):
    """
    错误处理上下文管理器
    
    Args:
        message: 上下文描述
        exceptions: 要捕获的异常类型
        logger_name: 日志器名称
        raise_on_error: 是否重新抛出异常
    """
    logger = get_logger(logger_name or __name__)
    logger.debug(f"进入上下文: {message}")
    
    try:
        yield
        logger.debug(f"成功完成: {message}")
    
    except exceptions as e:
        logger.error(f"失败: {message}")
        handle_exception(e, logger)
        
        if raise_on_error:
            raise
    
    finally:
        logger.debug(f"退出上下文: {message}")


class ErrorCollector:
    """错误收集器"""
    
    def __init__(self, logger_name: Optional[str] = None):
        """
        初始化错误收集器
        
        Args:
            logger_name: 日志器名称
        """
        self.errors = []
        self.logger = get_logger(logger_name or __name__)
    
    def add_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """
        添加错误
        
        Args:
            error: 异常对象
            context: 错误上下文
        """
        error_info = {
            "error": error,
            "context": context or {},
            "traceback": traceback.format_exc()
        }
        self.errors.append(error_info)
        
        # 记录日志
        self.logger.error(
            f"收集到错误: {error}",
            exc_info=True,
            extra={"context": context}
        )
    
    def has_errors(self) -> bool:
        """是否有错误"""
        return len(self.errors) > 0
    
    def get_errors(self) -> list:
        """获取所有错误"""
        return self.errors
    
    def clear(self):
        """清空错误"""
        self.errors.clear()
    
    def raise_if_errors(self, message: Optional[str] = None):
        """如果有错误则抛出异常"""
        if self.has_errors():
            error_count = len(self.errors)
            msg = message or f"收集到 {error_count} 个错误"
            
            # 创建包含所有错误信息的异常
            details = {
                "error_count": error_count,
                "errors": [
                    {
                        "type": type(e["error"]).__name__,
                        "message": str(e["error"]),
                        "context": e["context"]
                    }
                    for e in self.errors
                ]
            }
            
            raise Bili2TextError(msg, details=details)
    
    def __enter__(self):
        """进入上下文"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if exc_type is not None:
            self.add_error(exc_val)
            return True  # 抑制异常
        return False


def graceful_shutdown(cleanup_func: Optional[Callable] = None):
    """
    优雅关闭装饰器
    
    Args:
        cleanup_func: 清理函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            
            try:
                return func(*args, **kwargs)
            
            except KeyboardInterrupt:
                logger.info("接收到中断信号，正在优雅关闭...")
                if cleanup_func:
                    try:
                        cleanup_func()
                    except Exception as e:
                        logger.error(f"清理过程出错: {e}")
                raise
            
            except Exception as e:
                logger.error(f"程序异常退出: {e}", exc_info=True)
                if cleanup_func:
                    try:
                        cleanup_func()
                    except Exception as cleanup_error:
                        logger.error(f"清理过程出错: {cleanup_error}")
                raise
        
        return wrapper
    return decorator