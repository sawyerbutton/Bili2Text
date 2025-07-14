"""
Bili2Text - WhisperX音频转录工具（v2版本）
===========================================

使用WhisperX对下载的音频文件进行转录，生成对应的文本文档。
修复了参数兼容性问题。

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
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import gc
import torch

# 忽略警告
warnings.filterwarnings("ignore")

# 设置环境变量以避免某些错误
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# 检查依赖
try:
    import whisperx
    import torchaudio
except ImportError as e:
    print(f"错误：未安装必要的依赖库")
    print("请运行以下命令安装：")
    print("pip install whisperx torch torchaudio")
    exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transcribe_whisperx_v2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 转录配置
TRANSCRIBE_CONFIG = {
    "model_size": "base",  # 模型大小
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "device_index": 0,
    "compute_type": "float16" if torch.cuda.is_available() else "int8",
    "batch_size": 16,  # 批处理大小
    "language": "zh",  # 指定语言避免自动检测
    "enable_diarization": False,  # 默认关闭说话人分离
    "output_format": "txt",
    "include_timestamps": True,
}

# 支持的音频格式
SUPPORTED_FORMATS = ('.mp3', '.m4a', '.aac', '.wav', '.flac', '.ogg', '.opus')


class WhisperXTranscriber:
    """WhisperX转录器类（v2版本）"""
    
    def __init__(self, config: dict = None):
        """初始化转录器"""
        self.config = config or TRANSCRIBE_CONFIG
        self.model = None
        self.device = self.config.get("device", "cuda" if torch.cuda.is_available() else "cpu")
        self.device_index = self.config.get("device_index", 0)
        
        logger.info(f"使用设备: {self.device}")
        if self.device == "cuda":
            logger.info(f"GPU设备: {torch.cuda.get_device_name(self.device_index)}")
            # 清理GPU缓存
            torch.cuda.empty_cache()
    
    def load_model(self):
        """加载WhisperX模型"""
        try:
            model_size = self.config.get("model_size", "base")
            compute_type = self.config.get("compute_type", "float16" if self.device == "cuda" else "int8")
            language = self.config.get("language", "zh")
            
            logger.info(f"加载WhisperX模型: {model_size}")
            logger.info(f"计算类型: {compute_type}")
            logger.info(f"指定语言: {language}")
            
            # 加载模型时指定语言
            self.model = whisperx.load_model(
                model_size, 
                self.device,
                device_index=self.device_index if self.device == "cuda" else None,
                compute_type=compute_type,
                language=language,  # 预先指定语言
                asr_options={
                    "beam_size": 5,
                    "best_of": 5,
                    "patience": 1,
                    "length_penalty": 1,
                    "temperatures": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                    "compression_ratio_threshold": 2.4,
                    "log_prob_threshold": -1.0,
                    "no_speech_threshold": 0.6,
                    "initial_prompt": "以下是普通话的对话。"  # 中文提示
                }
            )
            logger.info("模型加载成功")
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            raise
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """转录单个音频文件（带错误恢复）"""
        try:
            logger.info(f"开始转录: {audio_path}")
            
            # 加载音频
            try:
                audio = whisperx.load_audio(audio_path)
                logger.info(f"音频加载成功，长度: {len(audio)/16000:.2f}秒")
            except Exception as e:
                logger.error(f"音频加载失败: {e}")
                # 尝试使用torchaudio加载
                import torchaudio
                waveform, sample_rate = torchaudio.load(audio_path)
                if sample_rate != 16000:
                    resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                    waveform = resampler(waveform)
                audio = waveform.squeeze().numpy()
                logger.info("使用备用方法加载音频成功")
            
            # 设置批处理大小
            batch_size = self.config.get("batch_size", 16)
            language = self.config.get("language", "zh")
            
            # 执行转录 - 不使用chunk_length参数
            logger.info("执行转录...")
            result = self.model.transcribe(
                audio,
                batch_size=batch_size,
                language=language,
                task="transcribe",
                print_progress=True
            )
            
            logger.info(f"转录完成，语言: {result.get('language', language)}")
            
            # 简化结果处理，避免对齐步骤的问题
            if self.config.get("include_timestamps", True):
                try:
                    # 尝试对齐时间戳
                    logger.info("尝试对齐时间戳...")
                    model_a, metadata = whisperx.load_align_model(
                        language_code=result.get("language", language), 
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
                    logger.info("时间戳对齐成功")
                    
                    # 清理对齐模型
                    del model_a
                    gc.collect()
                    if self.device == "cuda":
                        torch.cuda.empty_cache()
                        
                except Exception as e:
                    logger.warning(f"时间戳对齐失败，使用原始时间戳: {e}")
                    # 保持原始结果
            
            return result
            
        except Exception as e:
            logger.error(f"转录失败: {e}")
            # 返回空结果而不是抛出异常
            return {"segments": [], "language": self.config.get("language", "zh")}
    
    def format_output(self, result: Dict, include_timestamps: bool = True) -> str:
        """格式化输出结果"""
        output_lines = []
        
        segments = result.get("segments", [])
        
        for segment in segments:
            text = segment.get('text', '').strip()
            if not text:
                continue
                
            if include_timestamps and 'start' in segment:
                start_time = self._format_timestamp(segment.get("start", 0))
                end_time = self._format_timestamp(segment.get("end", 0))
                line = f"[{start_time} --> {end_time}] {text}"
            else:
                line = text
            
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
            output_file = os.path.join(output_dir, f"{audio_name}_whisperx.txt")
            content = self.format_output(result, include_timestamps)
            
            # 如果没有转录内容，添加说明
            if not content:
                content = "[转录失败或音频中没有检测到语音内容]"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # 写入元信息
                f.write(f"# WhisperX转录结果\n")
                f.write(f"# 音频文件: {os.path.basename(audio_path)}\n")
                f.write(f"# 转录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 语言: {result.get('language', 'zh')}\n")
                f.write(f"# 模型: {self.config.get('model_size', 'unknown')}\n")
                f.write("\n" + "="*50 + "\n\n")
                f.write(content)
                
                # 如果segments存在但没有格式化内容，尝试提取纯文本
                if not content and result.get("segments"):
                    texts = [seg.get("text", "").strip() for seg in result["segments"]]
                    if texts:
                        f.write("\n\n" + "="*50 + "\n")
                        f.write("# 纯文本版本\n")
                        f.write("="*50 + "\n\n")
                        f.write(" ".join(texts))
        
        elif output_format == "json":
            output_file = os.path.join(output_dir, f"{audio_name}_whisperx.json")
            result["metadata"] = {
                "audio_file": os.path.basename(audio_path),
                "transcription_time": datetime.now().isoformat(),
                "model": self.config.get('model_size', 'unknown')
            }
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"转录结果已保存: {output_file}")
        return output_file
    
    def cleanup(self):
        """清理资源"""
        if self.model:
            del self.model
            self.model = None
        gc.collect()
        if self.device == "cuda":
            torch.cuda.empty_cache()


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
    parser = argparse.ArgumentParser(description="使用WhisperX转录音频文件（v2版本）")
    parser.add_argument('--audio-dir', type=str, default='./audio',
                        help='音频文件目录 (默认: ./audio)')
    parser.add_argument('--output-dir', type=str, default='./transcripts',
                        help='输出目录 (默认: ./transcripts)')
    parser.add_argument('--model', type=str, default='base',
                        choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'],
                        help='WhisperX模型大小 (默认: base)')
    parser.add_argument('--language', type=str, default='zh',
                        help='语言代码 (默认: zh，中文)')
    parser.add_argument('--device', type=str, default='auto',
                        choices=['auto', 'cuda', 'cpu'],
                        help='计算设备 (默认: auto)')
    parser.add_argument('--batch-size', type=int, default=16,
                        help='批处理大小 (默认: 16)')
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
    config['batch_size'] = args.batch_size
    config['include_timestamps'] = not args.no_timestamps
    config['output_format'] = args.output_format
    
    if args.device == 'auto':
        config['device'] = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        config['device'] = args.device
    
    logger.info("="*50)
    logger.info("WhisperX音频转录工具（v2版本）")
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
                if result.get("segments"):
                    output_file = transcriber.save_result(result, audio_file, args.output_dir)
                    success_count += 1
                    logger.info(f"转录成功: {os.path.basename(output_file)}")
                else:
                    logger.warning(f"音频文件没有检测到语音内容: {os.path.basename(audio_file)}")
                    failed_files.append(audio_file)
                
                # 定期清理内存
                if i % 5 == 0:
                    gc.collect()
                    if config['device'] == 'cuda':
                        torch.cuda.empty_cache()
                    
            except Exception as e:
                logger.error(f"处理文件失败: {e}")
                failed_files.append(audio_file)
                continue
        
        # 清理资源
        transcriber.cleanup()
        
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
    finally:
        # 确保清理资源
        if 'transcriber' in locals():
            transcriber.cleanup()


if __name__ == "__main__":
    sys.exit(main())