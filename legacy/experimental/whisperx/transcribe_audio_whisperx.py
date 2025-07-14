"""
Bili2Text - WhisperX音频转录工具
=====================================================

文件目的：
    使用WhisperX对下载的音频文件进行转录，生成对应的文本文档。
    WhisperX是Whisper的升级版，提供更准确的时间戳对齐和说话人分离功能。

主要功能：
    1. 批量处理音频文件转录
    2. 支持多种音频格式（MP3, M4A, AAC, WAV等）
    3. 生成带时间戳的转录文本
    4. 可选的说话人分离功能
    5. 自动保存转录结果为TXT文件

与原版Whisper的区别：
    - 更准确的字级时间戳
    - 支持批量推理，速度更快（可达70倍实时）
    - 支持说话人分离（Speaker Diarization）
    - 使用VAD减少幻觉文本
    - 更好的多语言支持

依赖库：
    - whisperx: WhisperX核心库
    - torch: PyTorch深度学习框架
    - torchaudio: 音频处理
    - pyannote.audio: 说话人分离（可选）

作者：Bili2Text Tool
创建时间：2024
"""

import os
import sys
import json
import logging
import argparse
import warnings
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import gc

# 忽略一些警告
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# 检查依赖
try:
    import torch
    import whisperx
except ImportError as e:
    print(f"错误：未安装必要的依赖库")
    print("请运行以下命令安装：")
    print("pip install whisperx torch torchaudio")
    print("如需说话人分离功能，还需安装：pip install pyannote.audio")
    exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transcribe_whisperx.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 转录配置
TRANSCRIBE_CONFIG = {
    "model_size": "large-v2",  # 模型大小：tiny, base, small, medium, large, large-v2
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "device_index": 0,
    "compute_type": "float16" if torch.cuda.is_available() else "int8",  # GPU用float16, CPU用int8
    "batch_size": 16,  # 批处理大小
    "language": "zh",  # 语言代码，None表示自动检测
    "enable_diarization": False,  # 是否启用说话人分离
    "min_speakers": None,  # 最小说话人数
    "max_speakers": None,  # 最大说话人数
    "output_format": "txt",  # 输出格式：txt, json, srt
    "include_timestamps": True,  # 是否包含时间戳
    "vad_filter": True,  # 使用VAD过滤
    "vad_onset": 0.500,  # VAD开始阈值
    "vad_offset": 0.363,  # VAD结束阈值
}

# 支持的音频格式
SUPPORTED_FORMATS = ('.mp3', '.m4a', '.aac', '.wav', '.flac', '.ogg', '.opus')


class WhisperXTranscriber:
    """WhisperX转录器类"""
    
    def __init__(self, config: dict = None):
        """
        初始化转录器
        
        Args:
            config: 配置字典
        """
        self.config = config or TRANSCRIBE_CONFIG
        self.model = None
        self.diarize_model = None
        
        # 设置设备
        self.device = self.config.get("device", "cuda" if torch.cuda.is_available() else "cpu")
        self.device_index = self.config.get("device_index", 0)
        
        logger.info(f"使用设备: {self.device}")
        if self.device == "cuda":
            logger.info(f"GPU设备: {torch.cuda.get_device_name(self.device_index)}")
    
    def load_model(self):
        """加载WhisperX模型"""
        try:
            model_size = self.config.get("model_size", "large-v2")
            compute_type = self.config.get("compute_type", "float16" if self.device == "cuda" else "int8")
            
            logger.info(f"加载WhisperX模型: {model_size}")
            self.model = whisperx.load_model(
                model_size, 
                self.device,
                device_index=self.device_index,
                compute_type=compute_type
            )
            logger.info("模型加载成功")
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            raise
    
    def load_diarization_model(self):
        """加载说话人分离模型"""
        if not self.config.get("enable_diarization", False):
            return
            
        try:
            logger.info("加载说话人分离模型...")
            # 需要Hugging Face token
            hf_token = os.environ.get("HF_TOKEN")
            if not hf_token:
                logger.warning("未设置HF_TOKEN环境变量，无法使用说话人分离功能")
                logger.warning("请访问 https://huggingface.co/settings/tokens 获取token")
                self.config["enable_diarization"] = False
                return
                
            self.diarize_model = whisperx.DiarizationPipeline(use_auth_token=hf_token, device=self.device)
            logger.info("说话人分离模型加载成功")
            
        except Exception as e:
            logger.error(f"加载说话人分离模型失败: {e}")
            self.config["enable_diarization"] = False
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """
        转录单个音频文件
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            转录结果字典
        """
        try:
            logger.info(f"开始转录: {audio_path}")
            
            # 加载音频
            audio = whisperx.load_audio(audio_path)
            
            # 转录
            batch_size = self.config.get("batch_size", 16)
            language = self.config.get("language", None)
            
            result = self.model.transcribe(
                audio,
                batch_size=batch_size,
                language=language,
                task="transcribe"
            )
            
            logger.info(f"转录完成，检测到语言: {result.get('language', 'unknown')}")
            
            # 对齐时间戳
            if self.config.get("include_timestamps", True):
                logger.info("对齐时间戳...")
                model_a, metadata = whisperx.load_align_model(
                    language_code=result["language"], 
                    device=self.device
                )
                result = whisperx.align(
                    result["segments"], 
                    model_a, 
                    metadata, 
                    audio, 
                    self.device,
                    return_char_alignments=False
                )
                
                # 清理内存
                del model_a
                gc.collect()
            
            # 说话人分离
            if self.config.get("enable_diarization", False) and self.diarize_model:
                logger.info("执行说话人分离...")
                min_speakers = self.config.get("min_speakers", None)
                max_speakers = self.config.get("max_speakers", None)
                
                diarize_segments = self.diarize_model(
                    audio,
                    min_speakers=min_speakers,
                    max_speakers=max_speakers
                )
                
                result = whisperx.assign_word_speakers(diarize_segments, result)
                logger.info(f"说话人分离完成")
            
            return result
            
        except Exception as e:
            logger.error(f"转录失败: {e}")
            raise
    
    def format_output(self, result: Dict, include_timestamps: bool = True) -> str:
        """
        格式化输出结果
        
        Args:
            result: 转录结果
            include_timestamps: 是否包含时间戳
            
        Returns:
            格式化的文本
        """
        output_lines = []
        
        segments = result.get("segments", [])
        
        for segment in segments:
            if include_timestamps:
                start_time = self._format_timestamp(segment.get("start", 0))
                end_time = self._format_timestamp(segment.get("end", 0))
                speaker = segment.get("speaker", "")
                
                if speaker:
                    line = f"[{start_time} --> {end_time}] [{speaker}] {segment.get('text', '').strip()}"
                else:
                    line = f"[{start_time} --> {end_time}] {segment.get('text', '').strip()}"
            else:
                line = segment.get('text', '').strip()
            
            output_lines.append(line)
        
        return "\n".join(output_lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """
        格式化时间戳
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化的时间戳字符串
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
        else:
            return f"{minutes:02d}:{seconds:06.3f}"
    
    def save_result(self, result: Dict, audio_path: str, output_dir: str) -> str:
        """
        保存转录结果
        
        Args:
            result: 转录结果
            audio_path: 原音频文件路径
            output_dir: 输出目录
            
        Returns:
            保存的文件路径
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        audio_name = Path(audio_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output_format = self.config.get("output_format", "txt")
        include_timestamps = self.config.get("include_timestamps", True)
        
        if output_format == "txt":
            output_file = os.path.join(output_dir, f"{audio_name}_whisperx.txt")
            content = self.format_output(result, include_timestamps)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # 写入元信息
                f.write(f"# WhisperX转录结果\n")
                f.write(f"# 音频文件: {os.path.basename(audio_path)}\n")
                f.write(f"# 转录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 语言: {result.get('language', 'unknown')}\n")
                f.write(f"# 模型: {self.config.get('model_size', 'unknown')}\n")
                if self.config.get("enable_diarization", False):
                    f.write(f"# 说话人分离: 已启用\n")
                f.write("\n" + "="*50 + "\n\n")
                
                # 写入转录内容
                f.write(content)
        
        elif output_format == "json":
            output_file = os.path.join(output_dir, f"{audio_name}_whisperx.json")
            
            # 添加元信息
            result["metadata"] = {
                "audio_file": os.path.basename(audio_path),
                "transcription_time": datetime.now().isoformat(),
                "model": self.config.get('model_size', 'unknown'),
                "diarization_enabled": self.config.get("enable_diarization", False)
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        
        elif output_format == "srt":
            output_file = os.path.join(output_dir, f"{audio_name}_whisperx.srt")
            content = self._format_srt(result)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"转录结果已保存: {output_file}")
        return output_file
    
    def _format_srt(self, result: Dict) -> str:
        """
        格式化为SRT字幕格式
        
        Args:
            result: 转录结果
            
        Returns:
            SRT格式文本
        """
        srt_lines = []
        segments = result.get("segments", [])
        
        for i, segment in enumerate(segments, 1):
            start = self._format_srt_timestamp(segment.get("start", 0))
            end = self._format_srt_timestamp(segment.get("end", 0))
            text = segment.get("text", "").strip()
            speaker = segment.get("speaker", "")
            
            if speaker:
                text = f"[{speaker}] {text}"
            
            srt_lines.append(f"{i}")
            srt_lines.append(f"{start} --> {end}")
            srt_lines.append(text)
            srt_lines.append("")  # 空行
        
        return "\n".join(srt_lines)
    
    def _format_srt_timestamp(self, seconds: float) -> str:
        """
        格式化SRT时间戳
        
        Args:
            seconds: 秒数
            
        Returns:
            SRT格式时间戳
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def find_audio_files(directory: str, formats: tuple = SUPPORTED_FORMATS) -> List[str]:
    """
    查找目录中的音频文件
    
    Args:
        directory: 目录路径
        formats: 支持的格式元组
        
    Returns:
        音频文件路径列表
    """
    audio_files = []
    
    # 检查主目录
    for file in os.listdir(directory):
        if file.lower().endswith(formats):
            audio_files.append(os.path.join(directory, file))
    
    # 检查子目录（如aac/, mp3/）
    for subdir in ['aac', 'mp3']:
        subdir_path = os.path.join(directory, subdir)
        if os.path.exists(subdir_path):
            for file in os.listdir(subdir_path):
                if file.lower().endswith(formats):
                    audio_files.append(os.path.join(subdir_path, file))
    
    return sorted(audio_files)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="使用WhisperX转录音频文件")
    parser.add_argument('--audio-dir', type=str, default='./audio',
                        help='音频文件目录 (默认: ./audio)')
    parser.add_argument('--output-dir', type=str, default='./transcripts',
                        help='输出目录 (默认: ./transcripts)')
    parser.add_argument('--model', type=str, default='large-v2',
                        choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v2'],
                        help='WhisperX模型大小 (默认: large-v2)')
    parser.add_argument('--language', type=str, default='zh',
                        help='语言代码 (默认: zh，中文)')
    parser.add_argument('--device', type=str, default='auto',
                        choices=['auto', 'cuda', 'cpu'],
                        help='计算设备 (默认: auto)')
    parser.add_argument('--batch-size', type=int, default=16,
                        help='批处理大小 (默认: 16)')
    parser.add_argument('--enable-diarization', action='store_true',
                        help='启用说话人分离')
    parser.add_argument('--no-timestamps', action='store_true',
                        help='不包含时间戳')
    parser.add_argument('--output-format', type=str, default='txt',
                        choices=['txt', 'json', 'srt'],
                        help='输出格式 (默认: txt)')
    
    args = parser.parse_args()
    
    # 更新配置
    config = TRANSCRIBE_CONFIG.copy()
    config['model_size'] = args.model
    config['language'] = args.language
    config['batch_size'] = args.batch_size
    config['enable_diarization'] = args.enable_diarization
    config['include_timestamps'] = not args.no_timestamps
    config['output_format'] = args.output_format
    
    if args.device == 'auto':
        config['device'] = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        config['device'] = args.device
    
    logger.info("="*50)
    logger.info("WhisperX音频转录工具")
    logger.info("="*50)
    
    # 查找音频文件
    audio_files = find_audio_files(args.audio_dir)
    if not audio_files:
        logger.error(f"在 {args.audio_dir} 中未找到音频文件")
        return 1
    
    logger.info(f"找到 {len(audio_files)} 个音频文件")
    
    # 创建转录器
    transcriber = WhisperXTranscriber(config)
    
    try:
        # 加载模型
        transcriber.load_model()
        
        # 加载说话人分离模型（如果需要）
        if config['enable_diarization']:
            transcriber.load_diarization_model()
        
        # 转录统计
        success_count = 0
        failed_files = []
        
        # 批量转录
        for i, audio_file in enumerate(audio_files, 1):
            logger.info(f"\n[{i}/{len(audio_files)}] 处理文件: {os.path.basename(audio_file)}")
            
            try:
                # 转录音频
                result = transcriber.transcribe_audio(audio_file)
                
                # 保存结果
                output_file = transcriber.save_result(result, audio_file, args.output_dir)
                
                success_count += 1
                logger.info(f"转录成功: {os.path.basename(output_file)}")
                
            except Exception as e:
                logger.error(f"转录失败: {e}")
                failed_files.append(audio_file)
                continue
        
        # 显示统计
        logger.info("\n" + "="*50)
        logger.info("转录完成统计：")
        logger.info(f"成功转录: {success_count} 个")
        logger.info(f"转录失败: {len(failed_files)} 个")
        if failed_files:
            logger.info("失败的文件：")
            for file in failed_files:
                logger.info(f"  - {os.path.basename(file)}")
        logger.info(f"输出目录: {os.path.abspath(args.output_dir)}")
        logger.info("="*50)
        
        return 0
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())