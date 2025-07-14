"""
Bili2Text 核心模块
提供统一的转录、下载、文件管理和Markdown生成功能
"""

# 导入日志和异常处理
from .logger import get_logger, init_logger, set_log_level
from .exceptions import (
    Bili2TextError,
    ConfigError,
    DownloadError,
    TranscriptionError,
    FileOperationError,
    WorkflowError,
    ValidationError
)
from .error_handler import error_handler, error_context, ErrorCollector

# 导入核心功能模块
from .whisper_transcriber import WhisperTranscriber, transcribe_single_file
from .bilibili_downloader import BilibiliDownloader, download_single_video, get_user_all_videos
from .markdown_generator import MarkdownGenerator, create_video_markdown_simple, create_text_file
from .file_manager import (
    FileManager, StatusTracker, VideoInfoManager,
    setup_project_directories, create_status_tracker, create_video_info_manager
)

# 初始化日志系统
init_logger()

__version__ = "3.0.0"
__author__ = "Bili2Text Team"

__all__ = [
    # 日志系统
    'get_logger',
    'init_logger',
    'set_log_level',
    
    # 异常类
    'Bili2TextError',
    'ConfigError',
    'DownloadError',
    'TranscriptionError',
    'FileOperationError',
    'WorkflowError',
    'ValidationError',
    
    # 错误处理
    'error_handler',
    'error_context',
    'ErrorCollector',
    
    # Whisper转录
    "WhisperTranscriber",
    "transcribe_single_file",
    
    # B站下载
    "BilibiliDownloader", 
    "download_single_video",
    "get_user_all_videos",
    
    # Markdown生成
    "MarkdownGenerator",
    "create_video_markdown_simple",
    "create_text_file",
    
    # 文件管理
    "FileManager",
    "StatusTracker", 
    "VideoInfoManager",
    "setup_project_directories",
    "create_status_tracker",
    "create_video_info_manager",
]