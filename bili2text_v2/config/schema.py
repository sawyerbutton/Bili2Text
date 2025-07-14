"""
配置模式定义
使用Pydantic进行配置验证
"""
from typing import Optional, List, Dict, Any, Literal
from pathlib import Path
from pydantic import BaseModel, Field, validator, root_validator


class WhisperConfig(BaseModel):
    """Whisper模型配置"""
    model_name: Literal["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"] = Field(
        default="medium",
        description="Whisper模型名称"
    )
    device: Optional[str] = Field(
        default=None,
        description="计算设备，None为自动选择"
    )
    language: str = Field(
        default="zh",
        description="转录语言"
    )
    initial_prompt: str = Field(
        default="简体中文,加上标点",
        description="转录提示文本"
    )
    cache_dir: str = Field(
        default=".cache/whisper",
        description="模型缓存目录"
    )
    
    @validator('cache_dir')
    def validate_cache_dir(cls, v):
        """确保缓存目录是有效路径"""
        Path(v).mkdir(parents=True, exist_ok=True)
        return v


class DownloadConfig(BaseModel):
    """下载配置"""
    proxy_url: Optional[str] = Field(
        default=None,
        description="代理URL"
    )
    concurrent_downloads: int = Field(
        default=3,
        ge=1,
        le=10,
        description="并发下载数"
    )
    timeout: int = Field(
        default=300,
        ge=60,
        description="下载超时时间（秒）"
    )
    retry_times: int = Field(
        default=3,
        ge=0,
        le=10,
        description="重试次数"
    )
    only_audio: bool = Field(
        default=True,
        description="仅下载音频"
    )
    audio_quality: str = Field(
        default="192k",
        description="音频质量"
    )


class StorageConfig(BaseModel):
    """存储配置"""
    base_dir: str = Field(
        default=".",
        description="基础工作目录"
    )
    audio_dir: str = Field(
        default="audio",
        description="音频目录"
    )
    video_dir: str = Field(
        default="video",
        description="视频目录"
    )
    result_dir: str = Field(
        default="result",
        description="结果目录"
    )
    temp_dir: str = Field(
        default="temp",
        description="临时目录"
    )
    status_dir: str = Field(
        default="status",
        description="状态目录"
    )
    
    @root_validator
    def create_directories(cls, values):
        """创建所有必要的目录"""
        base = Path(values.get('base_dir', '.'))
        for key in ['audio_dir', 'video_dir', 'result_dir', 'temp_dir', 'status_dir']:
            dir_path = base / values.get(key, key)
            dir_path.mkdir(parents=True, exist_ok=True)
        return values


class LoggingConfig(BaseModel):
    """日志配置"""
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="日志级别"
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    file_path: Optional[str] = Field(
        default=None,
        description="日志文件路径"
    )
    max_bytes: int = Field(
        default=10485760,  # 10MB
        description="日志文件最大大小"
    )
    backup_count: int = Field(
        default=5,
        description="日志文件备份数量"
    )


class WorkflowConfig(BaseModel):
    """工作流配置"""
    batch_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="批处理大小"
    )
    skip_downloaded: bool = Field(
        default=True,
        description="跳过已下载文件"
    )
    skip_transcribed: bool = Field(
        default=True,
        description="跳过已转录文件"
    )
    output_format: Literal["txt", "md", "json", "srt"] = Field(
        default="txt",
        description="输出格式"
    )
    save_segments: bool = Field(
        default=False,
        description="保存时间戳片段"
    )


class AppConfig(BaseModel):
    """应用主配置"""
    app_name: str = Field(
        default="Bili2Text",
        description="应用名称"
    )
    version: str = Field(
        default="3.1.0",
        description="版本号"
    )
    debug: bool = Field(
        default=False,
        description="调试模式"
    )
    
    # 子配置
    whisper: WhisperConfig = Field(
        default_factory=WhisperConfig,
        description="Whisper配置"
    )
    download: DownloadConfig = Field(
        default_factory=DownloadConfig,
        description="下载配置"
    )
    storage: StorageConfig = Field(
        default_factory=StorageConfig,
        description="存储配置"
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="日志配置"
    )
    workflow: WorkflowConfig = Field(
        default_factory=WorkflowConfig,
        description="工作流配置"
    )
    
    class Config:
        """Pydantic配置"""
        env_prefix = "BILI2TEXT_"
        env_nested_delimiter = "__"
        case_sensitive = False