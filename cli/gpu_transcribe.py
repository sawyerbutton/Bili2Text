#!/usr/bin/env python3
"""
Bili2Text - GPU加速转录工具
===========================

功能：使用GPU加速的Whisper模型进行音频/视频转录
特性：
    - 支持B站视频URL和本地文件
    - 自动检测GPU并优化配置
    - 支持混合精度推理(FP16)
    - GPU内存管理和监控
    - 批量处理支持
    - 自动fallback到CPU
"""

import os
import sys
import time
import argparse
import asyncio
from datetime import datetime
from pathlib import Path
import json
import logging
from typing import Dict, List, Optional, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GPUTranscriber:
    """GPU加速的Whisper转录器"""
    
    # 模型显存需求（GB）
    MODEL_VRAM_REQUIREMENTS = {
        'tiny': 1.5,
        'base': 1.5,
        'small': 2.5,
        'medium': 5.0,
        'large': 10.0,
        'large-v3': 10.0
    }
    
    def __init__(self, model_name: str = "medium", device: str = "auto", 
                 compute_type: str = "float16", num_workers: int = 1):
        """
        初始化GPU转录器
        
        Args:
            model_name: Whisper模型名称 (tiny, base, small, medium, large, large-v3)
            device: 设备选择 (auto, cuda, cpu)
            compute_type: 计算精度 (float16, float32)
            num_workers: 并行处理线程数
        """
        self.model_name = model_name
        self.device_choice = device
        self.compute_type = compute_type
        self.num_workers = num_workers
        self.model = None
        self.device = None
        
        # 初始化设备和模型
        self._initialize()
    
    def _initialize(self):
        """初始化设备和模型"""
        try:
            import torch
            import whisper
            
            # 检测设备
            self.device = self._detect_device(torch)
            logger.info(f"使用设备: {self.device}")
            
            # GPU内存信息
            if self.device.type == 'cuda':
                gpu_props = torch.cuda.get_device_properties(0)
                total_memory = gpu_props.total_memory / 1024**3  # GB
                available_memory = (gpu_props.total_memory - torch.cuda.memory_allocated(0)) / 1024**3
                logger.info(f"GPU: {gpu_props.name}")
                logger.info(f"显存: {total_memory:.1f} GB (可用: {available_memory:.1f} GB)")
                
                # 检查显存是否足够
                required_vram = self.MODEL_VRAM_REQUIREMENTS.get(self.model_name, 5.0)
                if self.compute_type == 'float16':
                    required_vram *= 0.6  # FP16大约减少40%显存需求
                
                if available_memory < required_vram * 0.9:  # 留10%余量
                    logger.warning(f"警告: {self.model_name}模型需要约{required_vram:.1f}GB显存，但只有{available_memory:.1f}GB可用")
                    
                    # 推荐合适的模型
                    for model, vram in self.MODEL_VRAM_REQUIREMENTS.items():
                        if self.compute_type == 'float16':
                            vram *= 0.6
                        if available_memory >= vram * 0.9:
                            logger.info(f"建议使用 {model} 模型（需要 {vram:.1f}GB）")
                            if model != self.model_name:
                                logger.info(f"自动切换到 {model} 模型")
                                self.model_name = model
                            break
                    else:
                        logger.error("显存不足，无法加载任何模型")
                        raise RuntimeError(f"显存不足: 需要{required_vram:.1f}GB，只有{available_memory:.1f}GB")
                
                # 设置GPU内存分配策略
                # 为large模型优化内存分配
                if self.model_name in ['large', 'large-v3']:
                    torch.cuda.set_per_process_memory_fraction(0.95)  # large模型使用95%
                    torch.cuda.empty_cache()  # 清理缓存
                    # 设置更保守的内存分配策略
                    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
                else:
                    torch.cuda.set_per_process_memory_fraction(0.9)  # 其他模型使用90%
                
                torch.backends.cudnn.benchmark = True  # 优化卷积操作
            
            # 加载模型
            logger.info(f"正在加载Whisper模型: {self.model_name}")
            start_time = time.time()
            
            # 模型缓存目录
            cache_dir = project_root / '.cache' / 'whisper'
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # 加载模型
            self.model = whisper.load_model(
                name=self.model_name,
                device=self.device,
                download_root=str(cache_dir)
            )
            
            # 如果使用GPU且支持FP16，转换模型
            if self.device.type == 'cuda' and self.compute_type == 'float16':
                logger.info("启用FP16混合精度推理")
                # 只转换模型到half，不转换输入
                # Whisper内部会处理输入类型转换
                self.model = self.model.half()
            
            load_time = time.time() - start_time
            logger.info(f"模型加载完成，耗时: {load_time:.1f} 秒")
            
            # 显示GPU内存使用
            if self.device.type == 'cuda':
                self._log_gpu_memory(torch)
            
        except ImportError as e:
            logger.error(f"缺少必要的依赖: {e}")
            logger.error("请安装: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
            logger.error("以及: pip install openai-whisper")
            sys.exit(1)
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise
    
    def _detect_device(self, torch) -> 'torch.device':
        """检测并选择最佳设备"""
        if self.device_choice == 'cpu':
            return torch.device('cpu')
        
        if torch.cuda.is_available():
            # 检查CUDA版本兼容性
            cuda_version = torch.version.cuda
            logger.info(f"PyTorch CUDA版本: {cuda_version}")
            
            # 选择GPU
            if self.device_choice == 'auto' or self.device_choice == 'cuda':
                return torch.device('cuda:0')
        else:
            logger.warning("未检测到可用的GPU，使用CPU")
            return torch.device('cpu')
        
        return torch.device('cpu')
    
    def _log_gpu_memory(self, torch):
        """记录GPU内存使用情况"""
        if self.device.type == 'cuda':
            allocated = torch.cuda.memory_allocated(0) / 1024**3
            cached = torch.cuda.memory_reserved(0) / 1024**3
            logger.info(f"GPU内存使用: {allocated:.1f} GB 已分配, {cached:.1f} GB 已缓存")
    
    def transcribe(self, audio_path: str, **kwargs) -> Dict:
        """
        转录音频文件
        
        Args:
            audio_path: 音频文件路径
            **kwargs: 其他Whisper参数
            
        Returns:
            转录结果字典
        """
        if not self.model:
            raise RuntimeError("模型未初始化")
        
        logger.info(f"开始转录: {Path(audio_path).name}")
        start_time = time.time()
        
        # 默认参数
        default_params = {
            'language': 'zh',
            'initial_prompt': '以下是普通话的句子。',
            'beam_size': 5,
            'best_of': 5,
            'temperature': [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            'compression_ratio_threshold': 2.4,
            'logprob_threshold': -1.0,
            'no_speech_threshold': 0.6,
            'condition_on_previous_text': True,
            'verbose': True
        }
        
        # FP16参数处理 - Whisper会自动处理类型转换
        # 不需要显式设置fp16参数，模型已经是half类型
        
        # 合并用户参数
        params = {**default_params, **kwargs}
        
        try:
            # 执行转录
            result = self.model.transcribe(str(audio_path), **params)
            
            # 记录时间和内存
            transcribe_time = time.time() - start_time
            logger.info(f"转录完成，耗时: {transcribe_time:.1f} 秒")
            
            if self.device.type == 'cuda':
                import torch
                self._log_gpu_memory(torch)
            
            return result
            
        except Exception as e:
            logger.error(f"转录失败: {e}")
            raise
    
    def transcribe_batch(self, audio_paths: List[str], **kwargs) -> List[Dict]:
        """
        批量转录音频文件
        
        Args:
            audio_paths: 音频文件路径列表
            **kwargs: Whisper参数
            
        Returns:
            转录结果列表
        """
        results = []
        total_files = len(audio_paths)
        
        logger.info(f"开始批量转录 {total_files} 个文件")
        start_time = time.time()
        
        for i, audio_path in enumerate(audio_paths, 1):
            logger.info(f"[{i}/{total_files}] 处理: {Path(audio_path).name}")
            
            try:
                result = self.transcribe(audio_path, **kwargs)
                results.append({
                    'file': audio_path,
                    'success': True,
                    'result': result
                })
            except Exception as e:
                logger.error(f"文件 {audio_path} 转录失败: {e}")
                results.append({
                    'file': audio_path,
                    'success': False,
                    'error': str(e)
                })
            
            # GPU内存清理
            if self.device.type == 'cuda' and i % 5 == 0:
                import torch
                torch.cuda.empty_cache()
                logger.info("清理GPU缓存")
        
        total_time = time.time() - start_time
        avg_time = total_time / total_files
        logger.info(f"批量转录完成，总耗时: {total_time:.1f} 秒，平均: {avg_time:.1f} 秒/文件")
        
        return results


async def download_audio_from_url(url: str, output_dir: Path) -> Path:
    """从B站URL下载音频文件"""
    logger.info(f"开始下载音频: {url}")
    
    # 创建临时目录
    temp_dir = output_dir.parent / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        from bilix.sites.bilibili import DownloaderBilibili
        
        # 使用bilix下载音频
        async with DownloaderBilibili() as d:
            await d.get_video(url, path=str(temp_dir), only_audio=True)
        
        # 查找下载的音频文件
        audio_extensions = ['*.mp4', '*.m4a', '*.aac', '*.mp3']
        audio_files = []
        for ext in audio_extensions:
            audio_files.extend(list(temp_dir.glob(ext)))
        
        if not audio_files:
            all_files = list(temp_dir.glob("*"))
            logger.error(f"临时目录中的文件: {[f.name for f in all_files]}")
            raise Exception("未找到下载的音频文件")
        
        # 移动到输出目录
        audio_file = audio_files[0]
        target_path = output_dir / audio_file.name
        
        import shutil
        shutil.move(str(audio_file), str(target_path))
        
        logger.info(f"音频下载完成: {target_path.name}")
        return target_path
        
    except ImportError:
        logger.error("bilix未安装，请安装: pip install bilix")
        raise
    except Exception as e:
        logger.error(f"下载失败: {e}")
        raise
    finally:
        # 清理临时目录
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='GPU加速的Whisper转录工具')
    
    # 基础参数 - 支持URL或本地文件
    parser.add_argument('--url', '-u', help='B站视频URL')
    parser.add_argument('--input', '-i', help='本地文件或目录')
    parser.add_argument('--output', '-o', default='./storage/results', help='输出目录')
    parser.add_argument('--model', '-m', default='medium', 
                      choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v3'],
                      help='Whisper模型大小')
    
    # 设备参数
    parser.add_argument('--device', '-d', default='auto',
                      choices=['auto', 'cuda', 'cpu'],
                      help='计算设备选择')
    parser.add_argument('--compute-type', default='float16',
                      choices=['float16', 'float32'],
                      help='计算精度（仅GPU有效）')
    
    # 高级参数
    parser.add_argument('--language', default='zh', help='音频语言')
    parser.add_argument('--beam-size', type=int, default=5, help='Beam搜索大小')
    parser.add_argument('--batch', action='store_true', help='批量处理模式')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 验证输入参数
    if not args.url and not args.input:
        logger.error("错误: 必须提供 --url 或 --input 参数之一")
        parser.print_help()
        return 1
    
    if args.url and args.input:
        logger.error("错误: --url 和 --input 参数不能同时使用")
        return 1
    
    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 如果是URL，先下载音频
    if args.url:
        logger.info("=== 从URL下载音频 ===")
        try:
            # 创建音频存储目录
            audio_dir = output_dir.parent / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)
            
            # 异步下载音频
            audio_path = asyncio.run(download_audio_from_url(args.url, audio_dir))
            audio_files = [audio_path]
        except Exception as e:
            logger.error(f"下载音频失败: {e}")
            return 1
    else:
        # 处理本地文件
        input_path = Path(args.input)
        if input_path.is_file():
            audio_files = [input_path]
        elif input_path.is_dir():
            # 支持的音频/视频格式
            supported_formats = {'.mp4', '.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.avi', '.mkv', '.mov'}
            audio_files = [f for f in input_path.rglob('*') if f.suffix.lower() in supported_formats]
            logger.info(f"找到 {len(audio_files)} 个音视频文件")
        else:
            logger.error(f"输入路径无效: {input_path}")
            return 1
    
    # 初始化转录器
    transcriber = GPUTranscriber(
        model_name=args.model,
        device=args.device,
        compute_type=args.compute_type
    )
    
    if not audio_files:
        logger.error("未找到可处理的文件")
        return 1
    
    # 执行转录
    if args.batch or len(audio_files) > 1:
        # 批量模式
        results = transcriber.transcribe_batch(
            [str(f) for f in audio_files],
            language=args.language,
            beam_size=args.beam_size,
            verbose=args.verbose
        )
        
        # 保存结果
        for item in results:
            if item['success']:
                audio_path = Path(item['file'])
                result = item['result']
                
                # 标准化标点
                text = result['text']
                text = normalize_punctuation(text)
                
                # 保存文件
                output_file = output_dir / f"{audio_path.stem}_GPU转录结果.txt"
                save_transcription(output_file, text, args.model, audio_path, args.url)
                logger.info(f"保存结果: {output_file}")
        
        # 统计信息
        success_count = sum(1 for r in results if r['success'])
        logger.info(f"批量处理完成: {success_count}/{len(results)} 成功")
        
    else:
        # 单文件模式
        audio_file = audio_files[0]
        result = transcriber.transcribe(
            str(audio_file),
            language=args.language,
            beam_size=args.beam_size,
            verbose=args.verbose
        )
        
        # 处理结果
        text = result['text']
        text = normalize_punctuation(text)
        
        # 保存文件
        output_file = output_dir / f"{audio_file.stem}_GPU转录结果.txt"
        save_transcription(output_file, text, args.model, audio_file, args.url)
        logger.info(f"转录结果已保存: {output_file}")
    
    return 0


def normalize_punctuation(text: str) -> str:
    """标点符号标准化"""
    replacements = {
        ',': '，', '?': '？', '!': '！', ':': '：',
        ';': '；', '(': '（', ')': '）'
    }
    for en, zh in replacements.items():
        text = text.replace(en, zh)
    return text


def save_transcription(output_file: Path, text: str, model: str, source_file: Path, url: str = None):
    """保存转录结果"""
    with open(output_file, 'w', encoding='utf-8') as f:
        if url:
            f.write(f"视频URL: {url}\n")
        f.write(f"源文件: {source_file.name}\n")
        f.write(f"转录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"使用模型: Whisper {model}\n")
        f.write(f"处理模式: GPU加速\n")
        f.write("=" * 50 + "\n\n")
        f.write(text)


if __name__ == '__main__':
    sys.exit(main())