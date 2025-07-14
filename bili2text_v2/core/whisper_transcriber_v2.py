#!/usr/bin/env python3
"""
Whisper转录核心模块 - 使用配置系统的版本
"""

import os
import re
from datetime import datetime
from typing import Optional, Dict, Any

import torch
import whisper

from ..config import get_config, WhisperConfig


class WhisperTranscriber:
    """Whisper转录器类 - 集成配置系统"""
    
    def __init__(self, 
                 config: Optional[WhisperConfig] = None,
                 model_name: Optional[str] = None,
                 device: Optional[str] = None,
                 cache_dir: Optional[str] = None):
        """
        初始化Whisper转录器
        
        Args:
            config: Whisper配置对象，如果不提供则使用全局配置
            model_name: 模型名称（会覆盖配置中的值）
            device: 设备（会覆盖配置中的值）
            cache_dir: 缓存目录（会覆盖配置中的值）
        """
        # 获取配置
        if config is None:
            config = get_config().whisper
        self.config = config
        
        # 覆盖配置值（如果提供了参数）
        self.model_name = model_name or config.model_name
        self.cache_dir = cache_dir or config.cache_dir
        
        # 设备选择
        if device:
            self.device = device
        elif config.device:
            self.device = config.device
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载Whisper模型"""
        print(f"使用Whisper模型: {self.model_name}")
        print(f"使用设备: {self.device}")
        print("正在加载模型......")
        
        start_time = datetime.now()
        
        try:
            self.model = whisper.load_model(
                name=self.model_name,
                device=self.device,
                download_root=self.cache_dir,
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).seconds
            print(f"模型加载完成，耗时 {duration} 秒")
            
        except Exception as e:
            print(f"模型加载失败: {e}")
            raise
    
    def transcribe_audio(self, 
                        audio_path: str,
                        initial_prompt: Optional[str] = None,
                        verbose: bool = True) -> Dict[str, Any]:
        """
        转录音频文件
        
        Args:
            audio_path: 音频文件路径
            initial_prompt: 转录提示文本（覆盖配置）
            verbose: 是否显示详细进度
            
        Returns:
            转录结果字典，包含原始结果和处理后的文本
        """
        if not self.model:
            raise RuntimeError("模型未加载，请先调用_load_model()")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        # 使用配置中的默认值
        if initial_prompt is None:
            initial_prompt = self.config.initial_prompt
        
        print(f"\n开始转录音频文件: {audio_path}")
        
        # 转录音频
        result = self.model.transcribe(
            audio_path,
            language=self.config.language,
            initial_prompt=initial_prompt,
            verbose=verbose
        )
        
        # 处理转录文本
        processed_text = self.process_text(result["text"])
        
        return {
            "original_result": result,
            "text": result["text"],
            "processed_text": processed_text,
            "segments": result.get("segments", []),
            "language": result.get("language", self.config.language)
        }
    
    def transcribe_audio_data(self, 
                            audio_data,
                            language: Optional[str] = None,
                            initial_prompt: Optional[str] = None,
                            verbose: bool = False) -> Dict[str, Any]:
        """
        转录音频数据（numpy数组）
        
        Args:
            audio_data: 音频数据（numpy数组）
            language: 语言代码（覆盖配置）
            initial_prompt: 转录提示文本（覆盖配置）
            verbose: 是否显示详细进度
            
        Returns:
            转录结果字典
        """
        if not self.model:
            raise RuntimeError("模型未加载")
        
        # 使用配置中的默认值
        language = language or self.config.language
        initial_prompt = initial_prompt or self.config.initial_prompt
        
        # 转录
        result = self.model.transcribe(
            audio_data,
            language=language,
            initial_prompt=initial_prompt,
            verbose=verbose
        )
        
        # 处理转录文本
        processed_text = self.process_text(result["text"])
        
        return {
            "original_result": result,
            "text": result["text"],
            "processed_text": processed_text,
            "segments": result.get("segments", []),
            "language": result.get("language", language)
        }
    
    def process_text(self, text: str) -> str:
        """
        处理转录文本，进行标点符号标准化等
        
        Args:
            text: 原始转录文本
            
        Returns:
            处理后的文本
        """
        if not text:
            return ""
        
        # 移除开头和结尾的空白
        text = text.strip()
        
        # 标点符号标准化
        # 将全角标点转换为半角
        replacements = {
            '，': ',',
            '。': '.',
            '！': '!',
            '？': '?',
            '；': ';',
            '：': ':',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '（': '(',
            '）': ')',
            '【': '[',
            '】': ']',
            '《': '<',
            '》': '>',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # 处理多余的空格
        text = re.sub(r'\s+', ' ', text)
        
        # 确保句子结尾有标点
        if text and text[-1] not in '.!?':
            text += '.'
        
        return text
    
    def save_segments(self, segments: list, output_path: str, format: str = "srt"):
        """
        保存时间戳片段
        
        Args:
            segments: 片段列表
            output_path: 输出路径
            format: 格式 (srt/vtt)
        """
        if format == "srt":
            content = self._segments_to_srt(segments)
        elif format == "vtt":
            content = self._segments_to_vtt(segments)
        else:
            raise ValueError(f"不支持的格式: {format}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _segments_to_srt(self, segments: list) -> str:
        """转换片段为SRT格式"""
        lines = []
        for i, seg in enumerate(segments, 1):
            start = self._format_timestamp(seg['start'], 'srt')
            end = self._format_timestamp(seg['end'], 'srt')
            text = seg['text'].strip()
            
            lines.append(f"{i}")
            lines.append(f"{start} --> {end}")
            lines.append(text)
            lines.append("")
        
        return '\n'.join(lines)
    
    def _segments_to_vtt(self, segments: list) -> str:
        """转换片段为WebVTT格式"""
        lines = ["WEBVTT", ""]
        
        for seg in segments:
            start = self._format_timestamp(seg['start'], 'vtt')
            end = self._format_timestamp(seg['end'], 'vtt')
            text = seg['text'].strip()
            
            lines.append(f"{start} --> {end}")
            lines.append(text)
            lines.append("")
        
        return '\n'.join(lines)
    
    def _format_timestamp(self, seconds: float, format: str) -> str:
        """格式化时间戳"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        
        if format == 'srt':
            return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')
        else:  # vtt
            return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"