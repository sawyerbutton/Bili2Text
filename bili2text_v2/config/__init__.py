"""
配置管理模块
提供统一的配置管理功能
"""
from .schema import (
    AppConfig,
    WhisperConfig,
    DownloadConfig,
    StorageConfig,
    LoggingConfig,
    WorkflowConfig
)
from .config_manager import (
    ConfigManager,
    get_config_manager,
    get_config,
    init_config
)

__all__ = [
    # 配置模式
    'AppConfig',
    'WhisperConfig',
    'DownloadConfig',
    'StorageConfig',
    'LoggingConfig',
    'WorkflowConfig',
    
    # 配置管理
    'ConfigManager',
    'get_config_manager',
    'get_config',
    'init_config'
]