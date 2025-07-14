"""
Bili2Text - Whisper音频转录工具（标准版）
=========================================

使用OpenAI Whisper进行音频转录，生成对应的文本文档。
这是一个更稳定的版本，使用标准Whisper而不是WhisperX。

主要功能：
    1. 批量处理音频文件转录
    2. 支持多种音频格式
    3. 生成带时间戳的转录文本
    4. 自动保存转录结果

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
from typing import List, Dict, Optional
from pathlib import Path
import gc

# 忽略警告
warnings.filterwarnings("ignore")

# 检查依赖
try:
    import torch
    import whisper
except ImportError as e:
    print(f"错误：未安装必要的依赖库")
    print("请运行以下命令安装：")
    print("pip install openai-whisper torch")
    exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transcribe_whisper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 转录配置
TRANSCRIBE_CONFIG = {
    "model_size": "medium",  # 模型大小：tiny, base, small, medium, large
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "language": "zh",  # 语言代码
    "task": "transcribe",  # transcribe 或 translate
    "output_format": "txt",  # 输出格式
    "include_timestamps": True,  # 是否包含时间戳
}

# 支持的音频格式
SUPPORTED_FORMATS = ('.mp3', '.m4a', '.aac', '.wav', '.flac', '.ogg', '.opus')


class WhisperTranscriber:
    """Whisper转录器类"""
    
    def __init__(self, config: dict = None):
        """初始化转录器"""
        self.config = config or TRANSCRIBE_CONFIG
        self.model = None
        self.device = self.config.get("device", "cuda" if torch.cuda.is_available() else "cpu")
        
        logger.info(f"使用设备: {self.device}")
        if self.device == "cuda":
            logger.info(f"GPU设备: {torch.cuda.get_device_name(0)}")
    
    def load_model(self):
        """加载Whisper模型"""
        try:
            model_size = self.config.get("model_size", "medium")
            
            logger.info(f"加载Whisper模型: {model_size}")
            self.model = whisper.load_model(model_size, device=self.device)
            logger.info("模型加载成功")
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            raise
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """转录单个音频文件"""
        try:
            logger.info(f"开始转录: {audio_path}")
            
            # 转录参数
            options = {
                "language": self.config.get("language", "zh"),
                "task": self.config.get("task", "transcribe"),
                "verbose": True,
                "temperature": 0,
                "compression_ratio_threshold": 2.4,
                "logprob_threshold": -1.0,
                "no_speech_threshold": 0.6,
                "initial_prompt": "以下是普通话的对话。",
            }
            
            # 执行转录
            result = self.model.transcribe(audio_path, **options)
            
            logger.info(f"转录完成，检测到语言: {result.get('language', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"转录失败: {e}")
            return {"segments": [], "text": "", "language": self.config.get("language", "zh")}
    
    def format_output(self, result: Dict, include_timestamps: bool = True) -> str:
        """格式化输出结果"""
        if not include_timestamps:
            return result.get("text", "").strip()
        
        output_lines = []
        segments = result.get("segments", [])
        
        for segment in segments:
            start_time = self._format_timestamp(segment.get("start", 0))
            end_time = self._format_timestamp(segment.get("end", 0))
            text = segment.get("text", "").strip()
            
            if text:
                line = f"[{start_time} --> {end_time}] {text}"
                output_lines.append(line)
        
        return "\n".join(output_lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """格式化时间戳"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
        else:
            return f"{minutes:02d}:{seconds:06.3f}"
    
    def save_result(self, result: Dict, audio_path: str, output_dir: str) -> str:
        """保存转录结果"""
        os.makedirs(output_dir, exist_ok=True)
        
        audio_name = Path(audio_path).stem
        output_format = self.config.get("output_format", "txt")
        include_timestamps = self.config.get("include_timestamps", True)
        
        if output_format == "txt":
            output_file = os.path.join(output_dir, f"{audio_name}_whisper.txt")
            content = self.format_output(result, include_timestamps)
            
            if not content:
                content = "[转录失败或音频中没有检测到语音内容]"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # 写入元信息
                f.write(f"# Whisper转录结果\n")
                f.write(f"# 音频文件: {os.path.basename(audio_path)}\n")
                f.write(f"# 转录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 语言: {result.get('language', 'zh')}\n")
                f.write(f"# 模型: {self.config.get('model_size', 'unknown')}\n")
                f.write("\n" + "="*50 + "\n\n")
                
                # 写入转录内容
                f.write(content)
                
                # 如果有完整文本，也添加一个纯文本版本
                if include_timestamps and result.get("text"):
                    f.write("\n\n" + "="*50 + "\n")
                    f.write("# 纯文本版本（无时间戳）\n")
                    f.write("="*50 + "\n\n")
                    f.write(result.get("text", "").strip())
        
        elif output_format == "json":
            output_file = os.path.join(output_dir, f"{audio_name}_whisper.json")
            
            # 添加元信息
            result["metadata"] = {
                "audio_file": os.path.basename(audio_path),
                "transcription_time": datetime.now().isoformat(),
                "model": self.config.get('model_size', 'unknown')
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"转录结果已保存: {output_file}")
        return output_file


def find_audio_files(directory: str, formats: tuple = SUPPORTED_FORMATS) -> List[str]:
    """查找目录中的音频文件"""
    audio_files = []
    
    # 检查主目录
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.lower().endswith(formats):
                audio_files.append(os.path.join(directory, file))
    
    # 检查子目录
    for subdir in ['aac', 'mp3']:
        subdir_path = os.path.join(directory, subdir)
        if os.path.exists(subdir_path):
            for file in os.listdir(subdir_path):
                if file.lower().endswith(formats):
                    audio_files.append(os.path.join(subdir_path, file))
    
    return sorted(audio_files)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="使用Whisper转录音频文件")
    parser.add_argument('--audio-dir', type=str, default='./audio',
                        help='音频文件目录 (默认: ./audio)')
    parser.add_argument('--output-dir', type=str, default='./transcripts',
                        help='输出目录 (默认: ./transcripts)')
    parser.add_argument('--model', type=str, default='medium',
                        choices=['tiny', 'base', 'small', 'medium', 'large'],
                        help='Whisper模型大小 (默认: medium)')
    parser.add_argument('--language', type=str, default='zh',
                        help='语言代码 (默认: zh，中文)')
    parser.add_argument('--device', type=str, default='auto',
                        choices=['auto', 'cuda', 'cpu'],
                        help='计算设备 (默认: auto)')
    parser.add_argument('--no-timestamps', action='store_true',
                        help='不包含时间戳')
    parser.add_argument('--output-format', type=str, default='txt',
                        choices=['txt', 'json'],
                        help='输出格式 (默认: txt)')
    
    args = parser.parse_args()
    
    # 更新配置
    config = TRANSCRIBE_CONFIG.copy()
    config['model_size'] = args.model
    config['language'] = args.language
    config['include_timestamps'] = not args.no_timestamps
    config['output_format'] = args.output_format
    
    if args.device == 'auto':
        config['device'] = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        config['device'] = args.device
    
    logger.info("="*50)
    logger.info("Whisper音频转录工具")
    logger.info("="*50)
    
    # 查找音频文件
    audio_files = find_audio_files(args.audio_dir)
    if not audio_files:
        logger.error(f"在 {args.audio_dir} 中未找到音频文件")
        return 1
    
    logger.info(f"找到 {len(audio_files)} 个音频文件")
    
    # 创建转录器
    transcriber = WhisperTranscriber(config)
    
    try:
        # 加载模型
        transcriber.load_model()
        
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
                if result.get("text") or result.get("segments"):
                    output_file = transcriber.save_result(result, audio_file, args.output_dir)
                    success_count += 1
                    logger.info(f"转录成功: {os.path.basename(output_file)}")
                else:
                    logger.warning(f"音频文件没有检测到语音内容: {os.path.basename(audio_file)}")
                    failed_files.append(audio_file)
                
                # 清理内存
                if i % 5 == 0:
                    gc.collect()
                    if config['device'] == 'cuda':
                        torch.cuda.empty_cache()
                    
            except Exception as e:
                logger.error(f"处理文件失败: {e}")
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
        logger.error("错误详情：", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())