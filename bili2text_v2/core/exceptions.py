"""
自定义异常类
提供统一的错误处理机制
"""
from typing import Optional, Dict, Any


class Bili2TextError(Exception):
    """Bili2Text基础异常类"""
    
    def __init__(self, 
                 message: str,
                 error_code: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 额外的错误详情
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


# ==================== 配置相关异常 ====================
class ConfigError(Bili2TextError):
    """配置错误"""
    pass


class ConfigFileNotFoundError(ConfigError):
    """配置文件未找到"""
    pass


class ConfigValidationError(ConfigError):
    """配置验证失败"""
    pass


# ==================== 下载相关异常 ====================
class DownloadError(Bili2TextError):
    """下载错误"""
    pass


class VideoNotFoundError(DownloadError):
    """视频未找到"""
    def __init__(self, video_id: str, **kwargs):
        super().__init__(f"视频未找到: {video_id}", **kwargs)
        self.details["video_id"] = video_id


class NetworkError(DownloadError):
    """网络错误"""
    pass


class ProxyError(NetworkError):
    """代理错误"""
    pass


# ==================== 转录相关异常 ====================
class TranscriptionError(Bili2TextError):
    """转录错误"""
    pass


class ModelNotFoundError(TranscriptionError):
    """模型未找到"""
    def __init__(self, model_name: str, **kwargs):
        super().__init__(f"模型未找到: {model_name}", **kwargs)
        self.details["model_name"] = model_name


class AudioProcessingError(TranscriptionError):
    """音频处理错误"""
    pass


class WhisperError(TranscriptionError):
    """Whisper相关错误"""
    pass


# ==================== 文件操作相关异常 ====================
class FileOperationError(Bili2TextError):
    """文件操作错误"""
    pass


class FileNotFoundError(FileOperationError):
    """文件未找到"""
    def __init__(self, file_path: str, **kwargs):
        super().__init__(f"文件未找到: {file_path}", **kwargs)
        self.details["file_path"] = file_path


class PermissionError(FileOperationError):
    """权限错误"""
    pass


class DiskSpaceError(FileOperationError):
    """磁盘空间不足"""
    pass


# ==================== 工作流相关异常 ====================
class WorkflowError(Bili2TextError):
    """工作流错误"""
    pass


class TaskFailedError(WorkflowError):
    """任务失败"""
    def __init__(self, task_id: str, reason: str, **kwargs):
        super().__init__(f"任务 {task_id} 失败: {reason}", **kwargs)
        self.details["task_id"] = task_id
        self.details["reason"] = reason


class DependencyError(WorkflowError):
    """依赖错误"""
    pass


# ==================== 验证相关异常 ====================
class ValidationError(Bili2TextError):
    """验证错误"""
    pass


class URLValidationError(ValidationError):
    """URL验证错误"""
    def __init__(self, url: str, **kwargs):
        super().__init__(f"无效的URL: {url}", **kwargs)
        self.details["url"] = url


class ParameterError(ValidationError):
    """参数错误"""
    pass


# ==================== 异常处理工具函数 ====================
def handle_exception(exc: Exception, logger=None) -> Dict[str, Any]:
    """
    统一的异常处理函数
    
    Args:
        exc: 异常对象
        logger: 日志记录器
        
    Returns:
        错误信息字典
    """
    if isinstance(exc, Bili2TextError):
        error_dict = exc.to_dict()
    else:
        # 处理非自定义异常
        error_dict = {
            "error": exc.__class__.__name__,
            "message": str(exc),
            "details": {}
        }
    
    # 记录日志
    if logger:
        logger.error(f"{error_dict['error']}: {error_dict['message']}", 
                    exc_info=True,
                    extra={"error_details": error_dict['details']})
    
    return error_dict


def retry_on_error(
    exceptions: tuple = (NetworkError, TranscriptionError),
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    logger=None
):
    """
    错误重试装饰器
    
    Args:
        exceptions: 需要重试的异常类型
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟倍数
        logger: 日志记录器
    """
    import time
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        if logger:
                            logger.warning(
                                f"{func.__name__} 失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}",
                                extra={"attempt": attempt + 1, "delay": current_delay}
                            )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        if logger:
                            logger.error(
                                f"{func.__name__} 最终失败: {e}",
                                exc_info=True
                            )
            
            raise last_exception
        
        return wrapper
    return decorator