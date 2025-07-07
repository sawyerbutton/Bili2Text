#!/usr/bin/env python3
"""
Bili2Text - 视频文件转录工具
=============================

文件目的：
    将 storage/video 目录中的视频文件转录为文本，使用Whisper模型进行语音识别，
    结果保存到 storage/results/result 目录中。

主要功能：
    1. 扫描 storage/video 目录中的所有视频文件
    2. 自动检测并使用GPU或CPU进行转录
    3. 使用Whisper模型进行语音转录
    4. 标点符号标准化处理
    5. 保存转录结果为文本文件
    6. 支持多种视频格式（mp4, avi, mkv, mov等）

依赖库：
    - whisper: OpenAI语音转录模型
    - torch: PyTorch深度学习框架
    - tqdm: 进度条显示
    - pathlib: 路径处理
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
import logging

# 初始化项目路径管理  
from src.utils import setup_project_paths
path_manager = setup_project_paths()
project_root = path_manager.project_root

try:
    import torch
    import whisper
    from tqdm import tqdm
    WHISPER_AVAILABLE = True
except ImportError as e:
    WHISPER_AVAILABLE = False
    print(f"警告: 无法导入Whisper相关库: {e}")
    print("请安装相关依赖: pip install openai-whisper torch tqdm")

# 支持的视频文件格式
SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/transcribe_videos.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def setup_directories():
    """创建必要的目录结构"""
    directories = [
        project_root / 'storage' / 'video',
        project_root / 'storage' / 'results' / 'result',
        project_root / 'logs',
        project_root / '.cache' / 'whisper'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"确保目录存在: {directory}")


def detect_device():
    """检测并选择计算设备（GPU优先）"""
    if not WHISPER_AVAILABLE:
        return None, "模拟模式"
    
    if torch.cuda.is_available():
        device = torch.device("cuda")
        gpu_name = torch.cuda.get_device_name(0)
        logger.info(f"检测到GPU: {gpu_name}")
        return device, f"GPU ({gpu_name})"
    else:
        device = torch.device("cpu")
        logger.info("使用CPU进行推理")
        return device, "CPU"


def load_whisper_model(model_name="medium", device=None):
    """加载Whisper模型"""
    if not WHISPER_AVAILABLE:
        logger.warning("Whisper不可用，使用模拟模式")
        return None
    
    try:
        logger.info(f"正在加载Whisper模型: {model_name}")
        start_time = datetime.now()
        
        model = whisper.load_model(
            name=model_name,
            device=device,
            download_root=str(project_root / '.cache' / 'whisper')
        )
        
        end_time = datetime.now()
        load_time = (end_time - start_time).total_seconds()
        logger.info(f"模型加载完成，耗时 {load_time:.2f} 秒")
        
        return model
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        return None


def find_video_files(video_dir):
    """查找视频目录中的所有视频文件"""
    video_files = []
    
    for file_path in Path(video_dir).rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_VIDEO_FORMATS:
            video_files.append(file_path)
    
    logger.info(f"找到 {len(video_files)} 个视频文件")
    return video_files


def normalize_punctuation(text):
    """标点符号标准化（英文标点转中文标点）"""
    replacements = {
        ',': '，',      # 逗号
        '?': '？',      # 问号
        '!': '！',      # 感叹号
        ':': '：',      # 冒号
        ';': '；',      # 分号
        '(': '（',      # 左括号
        ')': '）',      # 右括号
    }
    
    for en_punct, zh_punct in replacements.items():
        text = text.replace(en_punct, zh_punct)
    
    return text


def transcribe_video(model, video_path, output_dir, device_info):
    """转录单个视频文件"""
    try:
        logger.info(f"开始转录: {video_path.name}")
        start_time = datetime.now()
        
        if model is None:
            # 模拟模式
            logger.info("使用模拟模式进行转录")
            text = f"这是来自视频 {video_path.name} 的模拟转录文本。实际使用时需要安装Whisper库。"
        else:
            # 实际转录
            result = model.transcribe(
                str(video_path),
                verbose=False,
                initial_prompt='简体中文，加上标点符号。',
                language='zh'
            )
            text = result["text"]
        
        # 标点符号标准化
        text = normalize_punctuation(text)
        
        # 生成输出文件路径
        output_filename = f"{video_path.stem}_transcript.txt"
        output_path = output_dir / output_filename
        
        # 保存转录结果
        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入文件头信息
            f.write(f"视频文件: {video_path.name}\n")
            f.write(f"转录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"使用设备: {device_info}\n")
            f.write(f"文件路径: {video_path}\n")
            f.write("-" * 50 + "\n\n")
            f.write(text)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"转录完成: {video_path.name} -> {output_path.name} (耗时: {duration:.2f}秒)")
        return True, output_path, duration
        
    except Exception as e:
        logger.error(f"转录失败 {video_path.name}: {e}")
        return False, None, 0


def main(args=None):
    """主函数"""
    # 如果没有传入args或者传入的是命令行参数列表，则进行解析
    if args is None or isinstance(args, list):
        parser = argparse.ArgumentParser(
            description='转录storage/video目录中的视频文件',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例用法:
  # 使用默认设置转录所有视频文件
  python transcribe_videos.py
  
  # 指定Whisper模型
  python transcribe_videos.py --model large-v3
  
  # 指定输入和输出目录
  python transcribe_videos.py --input-dir /path/to/videos --output-dir /path/to/results
            """
        )
        
        parser.add_argument(
            '--model', 
            default='medium',
            choices=['tiny', 'base', 'medium', 'large-v3'],
            help='Whisper模型选择 (默认: medium)'
        )
        parser.add_argument(
            '--input-dir',
            default=str(project_root / 'storage' / 'video'),
            help='视频文件输入目录 (默认: storage/video)'
        )
        parser.add_argument(
            '--output-dir',
            default=str(project_root / 'storage' / 'results' / 'result'),
            help='转录结果输出目录 (默认: storage/results/result)'
        )
        parser.add_argument(
            '--force-cpu',
            action='store_true',
            help='强制使用CPU (即使有GPU可用)'
        )
        
        parsed_args = parser.parse_args(args)
    else:
        # 如果传入的是已经解析的args对象，直接使用
        parsed_args = args
    
    logger.info("=" * 60)
    logger.info("Bili2Text 视频转录工具启动")
    logger.info("=" * 60)
    
    # 设置目录
    setup_directories()
    
    input_dir = Path(parsed_args.input_dir)
    output_dir = Path(parsed_args.output_dir)
    
    if not input_dir.exists():
        logger.error(f"输入目录不存在: {input_dir}")
        return 1
    
    # 查找视频文件
    video_files = find_video_files(input_dir)
    
    if not video_files:
        logger.warning(f"在目录 {input_dir} 中未找到支持的视频文件")
        logger.info(f"支持的格式: {', '.join(SUPPORTED_VIDEO_FORMATS)}")
        return 0
    
    # 检测设备
    if parsed_args.force_cpu:
        device = torch.device("cpu") if WHISPER_AVAILABLE else None
        device_info = "CPU (强制)"
    else:
        device, device_info = detect_device()
    
    # 加载模型
    model = load_whisper_model(parsed_args.model, device)
    
    # 开始批量转录
    logger.info(f"开始批量转录 {len(video_files)} 个视频文件")
    logger.info(f"使用模型: {parsed_args.model}")
    logger.info(f"使用设备: {device_info}")
    logger.info(f"输出目录: {output_dir}")
    
    success_count = 0
    total_duration = 0
    failed_files = []
    
    # 使用进度条处理每个文件
    with tqdm(video_files, desc="转录进度", unit="文件") as pbar:
        for video_file in pbar:
            pbar.set_description(f"转录: {video_file.name}")
            
            success, _, duration = transcribe_video(
                model, video_file, output_dir, device_info
            )
            
            if success:
                success_count += 1
                total_duration += duration
            else:
                failed_files.append(video_file.name)
            
            pbar.set_postfix({
                '成功': success_count,
                '失败': len(failed_files)
            })
    
    # 输出统计结果
    logger.info("=" * 60)
    logger.info("转录完成统计")
    logger.info("=" * 60)
    logger.info(f"总文件数: {len(video_files)}")
    logger.info(f"成功转录: {success_count}")
    logger.info(f"失败数量: {len(failed_files)}")
    logger.info(f"总耗时: {total_duration:.2f} 秒")
    
    if failed_files:
        logger.warning("失败的文件:")
        for failed_file in failed_files:
            logger.warning(f"  - {failed_file}")
    
    logger.info(f"转录结果保存在: {output_dir}")
    logger.info("转录任务完成")
    
    return 0 if success_count > 0 else 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序异常: {e}")
        sys.exit(1)