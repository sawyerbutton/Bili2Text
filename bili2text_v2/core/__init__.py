"""
Bili2Text 核心模块
提供统一的转录、下载、文件管理和Markdown生成功能
"""

from .whisper_transcriber import WhisperTranscriber, transcribe_single_file
from .bilibili_downloader import BilibiliDownloader, download_single_video, get_user_all_videos
from .markdown_generator import MarkdownGenerator, create_video_markdown_simple, create_text_file
from .file_manager import (
    FileManager, StatusTracker, VideoInfoManager,
    setup_project_directories, create_status_tracker, create_video_info_manager
)

__version__ = "2.0.0"
__author__ = "Bili2Text Team"

__all__ = [
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