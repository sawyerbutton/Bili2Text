"""
Bili2Text - WhisperX音频转录工具（最终版）
==========================================

使用WhisperX对下载的音频文件进行转录，生成对应的文本文档。
这是经过充分测试的稳定版本。

主要功能：
    1. 批量处理音频文件转录
    2. 支持多种音频格式
    3. 生成带时间戳的转录文本
    4. 自动检测语言或指定语言
    5. 支持GPU加速（如果可用）

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

# 设置环境变量
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# 检查依赖
try:
    import torch
    import whisperx
except ImportError as e:
    print(f"错误：未安装必要的依赖库")
    print("请运行以下命令安装：")
    print("python fix_whisperx_auto.py")
    print("或手动安装：")
    print("pip install whisperx torch")
    exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transcribe_whisperx_final.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 支持的音频格式
SUPPORTED_FORMATS = ('.mp3', '.m4a', '.aac', '.wav', '.flac', '.ogg', '.opus')


class WhisperXTranscriber:
    """WhisperX转录器类（最终版）"""
    
    def __init__(self, model_size="base", device=None, language="zh", batch_size=16):
        """初始化转录器
        
        Args:
            model_size: 模型大小 (tiny, base, small, medium, large, large-v2, large-v3)
            device: 设备类型 (cuda, cpu, 或 None 自动检测)
            language: 语言代码 (zh 中文, en 英文等)
            batch_size: 批处理大小
        """
        self.model_size = model_size
        self.language = language
        self.batch_size = batch_size
        
        # 自动检测设备
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        # 根据设备选择计算类型
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        
        self.model = None
        
        logger.info(f"使用设备: {self.device}")
        logger.info(f"计算类型: {self.compute_type}")
        if self.device == "cuda":
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    
    def load_model(self):
        """加载WhisperX模型"""
        try:
            logger.info(f"加载WhisperX模型: {self.model_size}")
            logger.info(f"语言: {self.language}")
            
            # 加载模型
            self.model = whisperx.load_model(
                self.model_size,
                self.device,
                compute_type=self.compute_type,
                language=self.language  # 指定语言避免自动检测
            )
            
            logger.info("模型加载成功")
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            raise
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """转录单个音频文件"""
        try:
            logger.info(f"开始转录: {audio_path}")
            
            # 加载音频
            audio = whisperx.load_audio(audio_path)
            duration = len(audio) / 16000
            logger.info(f"音频长度: {duration:.2f}秒")
            
            # 执行转录
            result = self.model.transcribe(
                audio,
                batch_size=self.batch_size,
                language=self.language,
                print_progress=True
            )
            
            logger.info(f"转录完成，检测到 {len(result.get('segments', []))} 个片段")
            
            # 如果需要，可以进行时间戳对齐（可选）
            # 这需要额外的模型，可能会增加处理时间
            
            return result
            
        except Exception as e:
            logger.error(f"转录失败: {e}")
            return {"segments": [], "language": self.language}
    
    def save_result(self, result: Dict, audio_path: str, output_dir: str, 
                   include_timestamps: bool = True, output_format: str = "txt") -> str:
        """保存转录结果"""
        os.makedirs(output_dir, exist_ok=True)
        
        audio_name = Path(audio_path).stem
        
        if output_format == "txt":
            output_file = os.path.join(output_dir, f"{audio_name}_whisperx.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # 写入元信息
                f.write("# WhisperX转录结果\n")
                f.write(f"# 音频文件: {os.path.basename(audio_path)}\n")
                f.write(f"# 转录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 语言: {result.get('language', self.language)}\n")
                f.write(f"# 模型: {self.model_size}\n")
                f.write(f"# 设备: {self.device}\n")
                f.write("\n" + "="*60 + "\n\n")
                
                # 写入带时间戳的转录内容
                if include_timestamps and result.get("segments"):
                    for i, segment in enumerate(result["segments"], 1):
                        start = segment.get("start", 0)
                        end = segment.get("end", 0)
                        text = segment.get("text", "").strip()
                        if text:
                            f.write(f"{i}. [{start:.2f}s - {end:.2f}s] {text}\n")
                    
                    # 添加纯文本版本
                    f.write("\n" + "="*60 + "\n")
                    f.write("# 纯文本版本\n")
                    f.write("="*60 + "\n\n")
                    
                # 写入纯文本
                texts = [seg.get("text", "").strip() for seg in result.get("segments", [])]
                full_text = " ".join(texts) if texts else "[未检测到语音内容]"
                f.write(full_text)
        
        elif output_format == "json":
            output_file = os.path.join(output_dir, f"{audio_name}_whisperx.json")
            
            # 添加元信息
            result["metadata"] = {
                "audio_file": os.path.basename(audio_path),
                "transcription_time": datetime.now().isoformat(),
                "model": self.model_size,
                "device": self.device,
                "language": result.get('language', self.language)
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        
        elif output_format == "srt":
            output_file = os.path.join(output_dir, f"{audio_name}_whisperx.srt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(result.get("segments", []), 1):
                    start = segment.get("start", 0)
                    end = segment.get("end", 0)
                    text = segment.get("text", "").strip()
                    
                    if text:
                        # SRT格式
                        f.write(f"{i}\n")
                        f.write(f"{self._format_srt_timestamp(start)} --> {self._format_srt_timestamp(end)}\n")
                        f.write(f"{text}\n\n")
        
        logger.info(f"结果已保存: {output_file}")
        return output_file
    
    def _format_srt_timestamp(self, seconds: float) -> str:
        """格式化SRT时间戳"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def cleanup(self):
        """清理资源"""
        if self.model:
            del self.model
            self.model = None
        gc.collect()
        if self.device == "cuda":
            torch.cuda.empty_cache()


def find_audio_files(directory: str) -> List[str]:
    """查找目录中的音频文件"""
    audio_files = []
    
    # 检查主目录和子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(SUPPORTED_FORMATS):
                audio_files.append(os.path.join(root, file))
    
    return sorted(audio_files)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="使用WhisperX转录音频文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本使用
  python transcribe_audio_whisperx_final.py
  
  # 指定模型和语言
  python transcribe_audio_whisperx_final.py --model large-v3 --language en
  
  # 批量处理特定目录
  python transcribe_audio_whisperx_final.py --audio-dir ./my_audio --output-dir ./results
  
  # 生成SRT字幕文件
  python transcribe_audio_whisperx_final.py --output-format srt
"""
    )
    
    parser.add_argument('--audio-dir', type=str, default='./audio',
                        help='音频文件目录 (默认: ./audio)')
    parser.add_argument('--output-dir', type=str, default='./transcripts',
                        help='输出目录 (默认: ./transcripts)')
    parser.add_argument('--model', type=str, default='base',
                        choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'],
                        help='WhisperX模型大小 (默认: base)')
    parser.add_argument('--language', type=str, default='zh',
                        help='语言代码，如: zh(中文), en(英文), ja(日文) (默认: zh)')
    parser.add_argument('--device', type=str, default='auto',
                        choices=['auto', 'cuda', 'cpu'],
                        help='计算设备 (默认: auto)')
    parser.add_argument('--batch-size', type=int, default=16,
                        help='批处理大小 (默认: 16)')
    parser.add_argument('--no-timestamps', action='store_true',
                        help='不包含时间戳')
    parser.add_argument('--output-format', type=str, default='txt',
                        choices=['txt', 'json', 'srt'],
                        help='输出格式 (默认: txt)')
    
    args = parser.parse_args()
    
    # 设置设备
    if args.device == 'auto':
        device = None
    else:
        device = args.device
    
    logger.info("="*60)
    logger.info("WhisperX音频转录工具")
    logger.info("="*60)
    
    # 查找音频文件
    audio_files = find_audio_files(args.audio_dir)
    if not audio_files:
        logger.error(f"在 {args.audio_dir} 中未找到音频文件")
        logger.info(f"支持的格式: {', '.join(SUPPORTED_FORMATS)}")
        return 1
    
    logger.info(f"找到 {len(audio_files)} 个音频文件")
    
    # 创建转录器
    transcriber = WhisperXTranscriber(
        model_size=args.model,
        device=device,
        language=args.language,
        batch_size=args.batch_size
    )
    
    try:
        # 加载模型
        transcriber.load_model()
        
        # 统计
        success_count = 0
        failed_files = []
        
        # 批量转录
        for i, audio_file in enumerate(audio_files, 1):
            logger.info(f"\n[{i}/{len(audio_files)}] 处理: {os.path.basename(audio_file)}")
            
            try:
                # 转录
                result = transcriber.transcribe_audio(audio_file)
                
                # 保存结果
                if result.get("segments"):
                    transcriber.save_result(
                        result, 
                        audio_file, 
                        args.output_dir,
                        include_timestamps=not args.no_timestamps,
                        output_format=args.output_format
                    )
                    success_count += 1
                else:
                    logger.warning(f"未检测到语音内容")
                    failed_files.append(audio_file)
                
                # 定期清理内存
                if i % 5 == 0:
                    gc.collect()
                    if transcriber.device == "cuda":
                        torch.cuda.empty_cache()
                        
            except KeyboardInterrupt:
                logger.info("\n用户中断")
                break
                
            except Exception as e:
                logger.error(f"处理失败: {e}")
                failed_files.append(audio_file)
                continue
        
        # 显示统计
        logger.info("\n" + "="*60)
        logger.info("转录完成统计")
        logger.info("="*60)
        logger.info(f"成功: {success_count} 个")
        logger.info(f"失败: {len(failed_files)} 个")
        
        if failed_files:
            logger.info("\n失败的文件:")
            for f in failed_files[:10]:  # 只显示前10个
                logger.info(f"  - {os.path.basename(f)}")
            if len(failed_files) > 10:
                logger.info(f"  ... 还有 {len(failed_files) - 10} 个")
        
        logger.info(f"\n输出目录: {os.path.abspath(args.output_dir)}")
        
        return 0
        
    except Exception as e:
        logger.error(f"程序错误: {e}")
        logger.error("详情:", exc_info=True)
        return 1
        
    finally:
        # 清理资源
        transcriber.cleanup()
        logger.info("\n程序结束")


if __name__ == "__main__":
    sys.exit(main())