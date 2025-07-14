"""
Bili2Text - 下载并转录工具（WhisperX版）
=====================================================

文件目的：
    整合音频下载和WhisperX转录功能，提供一站式的B站视频转文字解决方案。
    
主要功能：
    1. 下载B站视频的音频文件
    2. 使用WhisperX进行高质量转录
    3. 支持批量处理
    4. 自动管理文件和目录
    5. 提供完整的处理流程

作者：Bili2Text Tool
创建时间：2024
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime
from pathlib import Path

# 添加当前目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入下载和转录模块
try:
    from download_audio import (
        download_audio_with_retry, 
        setup_directories, 
        move_audio_files,
        cleanup_temp_folder,
        load_config,
        DOWNLOAD_CONFIG
    )
    from transcribe_audio_whisperx import WhisperXTranscriber, find_audio_files
except ImportError as e:
    print(f"错误：无法导入必要的模块: {e}")
    print("请确保 download_audio.py 和 transcribe_audio_whisperx.py 在同一目录下")
    exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('download_and_transcribe_whisperx.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 默认URL列表
DEFAULT_URLS = [
    "https://www.bilibili.com/video/BV1aD3EznERn/",
    # 可以在这里添加更多URL
]


async def download_single_audio(url: str, temp_path: str, audio_path: str, format_dirs: dict, config: dict) -> list:
    """
    下载单个音频并处理
    
    Args:
        url: B站视频URL
        temp_path: 临时目录
        audio_path: 音频目录
        format_dirs: 格式子目录
        config: 配置字典
        
    Returns:
        处理后的音频文件路径列表
    """
    # 清理临时文件夹
    cleanup_temp_folder(temp_path)
    
    # 下载音频
    success = await download_audio_with_retry(url, temp_path, config.get("max_retries", 3))
    
    if success:
        # 移动并处理音频文件
        processed_files = move_audio_files(temp_path, audio_path, format_dirs, config)
        return processed_files
    
    return []


def transcribe_downloaded_audio(audio_files: list, transcriber: WhisperXTranscriber, output_dir: str) -> dict:
    """
    转录下载的音频文件
    
    Args:
        audio_files: 音频文件路径列表
        transcriber: WhisperX转录器实例
        output_dir: 输出目录
        
    Returns:
        转录结果统计
    """
    results = {"success": 0, "failed": 0, "failed_files": []}
    
    for audio_file in audio_files:
        try:
            logger.info(f"转录文件: {os.path.basename(audio_file)}")
            
            # 转录音频
            result = transcriber.transcribe_audio(audio_file)
            
            # 保存结果
            output_file = transcriber.save_result(result, audio_file, output_dir)
            
            results["success"] += 1
            logger.info(f"转录成功: {os.path.basename(output_file)}")
            
        except Exception as e:
            logger.error(f"转录失败 {audio_file}: {e}")
            results["failed"] += 1
            results["failed_files"].append(audio_file)
    
    return results


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="下载B站视频音频并使用WhisperX转录")
    parser.add_argument('--urls', nargs='+', help='B站视频URL列表')
    parser.add_argument('--urls-file', type=str, help='包含URL列表的文件')
    parser.add_argument('--output-dir', type=str, default='./transcripts',
                        help='转录输出目录 (默认: ./transcripts)')
    parser.add_argument('--model', type=str, default='large-v2',
                        choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v2'],
                        help='WhisperX模型大小 (默认: large-v2)')
    parser.add_argument('--language', type=str, default='zh',
                        help='语言代码 (默认: zh)')
    parser.add_argument('--enable-diarization', action='store_true',
                        help='启用说话人分离')
    parser.add_argument('--download-only', action='store_true',
                        help='仅下载音频，不进行转录')
    parser.add_argument('--transcribe-only', action='store_true',
                        help='仅转录已下载的音频')
    parser.add_argument('--output-format', type=str, default='txt',
                        choices=['txt', 'json', 'srt'],
                        help='转录输出格式 (默认: txt)')
    
    args = parser.parse_args()
    
    # 准备URL列表
    urls = []
    if args.urls:
        urls = args.urls
    elif args.urls_file and os.path.exists(args.urls_file):
        with open(args.urls_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        urls = DEFAULT_URLS
    
    if not urls and not args.transcribe_only:
        logger.error("没有提供URL")
        return 1
    
    logger.info("="*50)
    logger.info("Bili2Text - 下载并转录工具（WhisperX版）")
    logger.info("="*50)
    
    try:
        # 加载配置
        config = load_config()
        
        # 设置目录
        audio_folder_path, temp_folder_path, status_folder_path, format_dirs = setup_directories(config)
        
        # 下载阶段
        if not args.transcribe_only:
            logger.info(f"准备下载 {len(urls)} 个音频")
            
            all_downloaded_files = []
            
            for i, url in enumerate(urls, 1):
                logger.info(f"\n[{i}/{len(urls)}] 处理URL: {url}")
                
                try:
                    # 下载单个音频
                    downloaded_files = await download_single_audio(
                        url, temp_folder_path, audio_folder_path, format_dirs, config
                    )
                    
                    if downloaded_files:
                        all_downloaded_files.extend(downloaded_files)
                        logger.info(f"下载成功，生成 {len(downloaded_files)} 个文件")
                    else:
                        logger.error(f"下载失败: {url}")
                        
                except Exception as e:
                    logger.error(f"处理URL时出错: {e}")
                    continue
            
            if args.download_only:
                logger.info(f"\n下载完成，共生成 {len(all_downloaded_files)} 个音频文件")
                return 0
        
        # 转录阶段
        logger.info("\n开始转录阶段...")
        
        # 查找所有音频文件
        audio_files = find_audio_files(audio_folder_path)
        if not audio_files:
            logger.error("未找到可转录的音频文件")
            return 1
        
        logger.info(f"找到 {len(audio_files)} 个音频文件待转录")
        
        # 准备WhisperX配置
        whisperx_config = {
            "model_size": args.model,
            "language": args.language,
            "enable_diarization": args.enable_diarization,
            "output_format": args.output_format,
            "include_timestamps": True,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
        }
        
        # 创建转录器
        import torch
        transcriber = WhisperXTranscriber(whisperx_config)
        
        # 加载模型
        logger.info("加载WhisperX模型...")
        transcriber.load_model()
        
        if args.enable_diarization:
            transcriber.load_diarization_model()
        
        # 批量转录
        transcribe_results = transcribe_downloaded_audio(audio_files, transcriber, args.output_dir)
        
        # 显示最终统计
        logger.info("\n" + "="*50)
        logger.info("处理完成统计：")
        if not args.transcribe_only:
            logger.info(f"下载的音频文件: {len(audio_files)} 个")
        logger.info(f"成功转录: {transcribe_results['success']} 个")
        logger.info(f"转录失败: {transcribe_results['failed']} 个")
        if transcribe_results['failed_files']:
            logger.info("转录失败的文件：")
            for file in transcribe_results['failed_files']:
                logger.info(f"  - {os.path.basename(file)}")
        logger.info(f"音频文件目录: {os.path.abspath(audio_folder_path)}")
        logger.info(f"转录结果目录: {os.path.abspath(args.output_dir)}")
        logger.info("="*50)
        
        return 0
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        logger.error("错误详情：", exc_info=True)
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序启动失败: {e}")
        sys.exit(1)