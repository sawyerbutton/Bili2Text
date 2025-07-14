"""
日志管理系统
提供统一的日志记录功能
"""
import os
import sys
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from ..config import get_config, LoggingConfig


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 紫色
    }
    RESET = '\033[0m'
    
    def __init__(self, *args, use_color: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_color = use_color and sys.stderr.isatty()
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        # 保存原始级别名称
        levelname = record.levelname
        
        # 如果启用颜色，添加颜色代码
        if self.use_color and levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        
        # 格式化消息
        formatted = super().format(record)
        
        # 恢复原始级别名称
        record.levelname = levelname
        
        return formatted


class LoggerManager:
    """日志管理器"""
    
    _instance = None
    _loggers: Dict[str, logging.Logger] = {}
    _config: Optional[LoggingConfig] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, config: Optional[LoggingConfig] = None):
        """
        初始化日志系统
        
        Args:
            config: 日志配置，如果不提供则使用全局配置
        """
        if self._initialized:
            return
        
        # 获取配置
        if config is None:
            config = get_config().logging
        self._config = config
        
        # 设置根日志器
        self._setup_root_logger()
        
        self._initialized = True
    
    def _setup_root_logger(self):
        """设置根日志器"""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self._config.level))
        
        # 清除现有处理器
        root_logger.handlers.clear()
        
        # 添加控制台处理器
        console_handler = self._create_console_handler()
        root_logger.addHandler(console_handler)
        
        # 如果配置了文件输出，添加文件处理器
        if self._config.file_path:
            file_handler = self._create_file_handler()
            root_logger.addHandler(file_handler)
    
    def _create_console_handler(self) -> logging.Handler:
        """创建控制台处理器"""
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(getattr(logging, self._config.level))
        
        # 使用彩色格式化器
        formatter = ColoredFormatter(
            self._config.format,
            datefmt='%Y-%m-%d %H:%M:%S',
            use_color=True
        )
        handler.setFormatter(formatter)
        
        return handler
    
    def _create_file_handler(self) -> logging.Handler:
        """创建文件处理器"""
        # 确保日志目录存在
        log_path = Path(self._config.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建轮转文件处理器
        handler = logging.handlers.RotatingFileHandler(
            filename=str(log_path),
            maxBytes=self._config.max_bytes,
            backupCount=self._config.backup_count,
            encoding='utf-8'
        )
        handler.setLevel(getattr(logging, self._config.level))
        
        # 使用普通格式化器（文件中不需要颜色）
        formatter = logging.Formatter(
            self._config.format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        return handler
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        获取日志记录器
        
        Args:
            name: 日志器名称
            
        Returns:
            日志记录器
        """
        if not self._initialized:
            self.initialize()
        
        if name not in self._loggers:
            logger = logging.getLogger(name)
            self._loggers[name] = logger
        
        return self._loggers[name]
    
    def update_level(self, level: str):
        """
        更新日志级别
        
        Args:
            level: 新的日志级别
        """
        new_level = getattr(logging, level.upper())
        
        # 更新根日志器
        logging.getLogger().setLevel(new_level)
        
        # 更新所有处理器
        for handler in logging.getLogger().handlers:
            handler.setLevel(new_level)
        
        # 更新配置
        if self._config:
            self._config.level = level.upper()


# 全局日志管理器实例
_logger_manager = LoggerManager()


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志器名称，通常使用 __name__
        
    Returns:
        日志记录器
    """
    return _logger_manager.get_logger(name)


def init_logger(config: Optional[LoggingConfig] = None):
    """
    初始化日志系统
    
    Args:
        config: 日志配置
    """
    _logger_manager.initialize(config)


def set_log_level(level: str):
    """
    设置日志级别
    
    Args:
        level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
    """
    _logger_manager.update_level(level)


class LogContext:
    """日志上下文管理器"""
    
    def __init__(self, logger: logging.Logger, **context):
        """
        初始化日志上下文
        
        Args:
            logger: 日志记录器
            **context: 上下文信息
        """
        self.logger = logger
        self.context = context
        self._old_factory = None
    
    def __enter__(self):
        """进入上下文"""
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            # 添加上下文信息
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        self._old_factory = old_factory
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if self._old_factory:
            logging.setLogRecordFactory(self._old_factory)


def log_execution_time(logger: Optional[logging.Logger] = None):
    """
    记录函数执行时间的装饰器
    
    Args:
        logger: 日志记录器，如果不提供则使用函数所在模块的logger
    """
    import functools
    import time
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)
            
            start_time = time.time()
            func_name = func.__name__
            
            logger.debug(f"开始执行 {func_name}")
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(
                    f"{func_name} 执行完成",
                    extra={"execution_time": elapsed, "status": "success"}
                )
                return result
            
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"{func_name} 执行失败",
                    exc_info=True,
                    extra={"execution_time": elapsed, "status": "failed"}
                )
                raise
        
        return wrapper
    return decorator


def log_method_calls(logger: Optional[logging.Logger] = None):
    """
    记录类方法调用的装饰器
    
    Args:
        logger: 日志记录器
    """
    def decorator(cls):
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                setattr(cls, attr_name, log_execution_time(logger)(attr))
        return cls
    return decorator