"""
Bili2Text - 哔哩哔哩音频下载工具（批量处理版本）
=====================================================

文件目的：
    批量下载指定B站视频的音频文件，将音频文件保存到指定目录。
    这是一个专门用于音频下载的工具，基于download_videos.py改编。

主要功能：
    1. 批量下载B站视频的音频文件
    2. 自动管理文件目录结构
    3. 支持异步下载，提高下载效率
    4. 自动移动下载文件到指定目录
    5. 全面的错误处理和重试机制

与download_videos.py的区别：
    - 本文件专门用于音频下载，不下载视频
    - 下载音频文件（MP3或M4A格式）
    - 输出目录为audio文件夹
    - 添加了更全面的错误处理

依赖库：
    - asyncio: 异步编程支持
    - bilix: B站视频下载工具
    - logging: 日志记录
    - json: 配置文件处理

作者：Bili2Text Tool
创建时间：2024
"""

import asyncio
import os
import shutil
import logging
import json
import time
import subprocess
from datetime import datetime
from typing import List, Optional, Tuple
from pathlib import Path

try:
    from bilix.sites.bilibili import DownloaderBilibili
except ImportError as e:
    print(f"错误：未安装必要的依赖库 bilix")
    print("请运行以下命令安装：pip install bilix")
    exit(1)

# 检查ffmpeg是否可用
def check_ffmpeg():
    """检查系统中是否安装了ffmpeg"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# 在启动时检查ffmpeg
FFMPEG_AVAILABLE = check_ffmpeg()
if not FFMPEG_AVAILABLE:
    print("警告：未检测到ffmpeg，将无法进行音频格式转换")
    print("建议安装ffmpeg以支持MP3格式输出：")
    print("  - Windows: 下载ffmpeg并添加到PATH")
    print("  - macOS: brew install ffmpeg")
    print("  - Linux: sudo apt-get install ffmpeg")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('audio_download.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置要处理的音频URL列表
audio_urls = [
    "https://www.bilibili.com/video/BV1aD3EznERn/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    "https://www.bilibili.com/video/BV1gB39zjEpk/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    "https://www.bilibili.com/video/BV1Rn3BzkEnY/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    "https://www.bilibili.com/video/BV1Bb32zuET7/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    "https://www.bilibili.com/video/BV1HM37zcErp/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    "https://www.bilibili.com/video/BV1Mq3QzuEm9/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    "https://www.bilibili.com/video/BV1ko39zPEgh/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    "https://www.bilibili.com/video/BV1H93kziE1n/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    "https://www.bilibili.com/video/BV1Zt3yzwEg3/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    "https://www.bilibili.com/video/BV1ykGczdEVw/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    "https://www.bilibili.com/video/BV1knuFzGEHv/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363"
]

# 下载配置
DOWNLOAD_CONFIG = {
    "max_retries": 3,  # 最大重试次数
    "retry_delay": 5,  # 重试延迟（秒）
    "timeout": 300,  # 下载超时时间（秒）
    "concurrent_downloads": 3,  # 同时下载数
    "output_formats": ["aac", "mp3"],  # 输出格式，第一个为原始格式
    "audio_quality": "192k",  # 音频比特率
}


class AudioDownloadError(Exception):
    """音频下载相关的自定义异常"""
    pass


def convert_audio_format(input_file: str, output_file: str, bitrate: str = "192k") -> bool:
    """
    使用ffmpeg转换音频格式
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        bitrate: 音频比特率（如 "192k", "256k"）
        
    Returns:
        转换是否成功
    """
    if not FFMPEG_AVAILABLE:
        logger.warning("ffmpeg不可用，跳过格式转换")
        return False
        
    try:
        # 构建ffmpeg命令
        cmd = [
            'ffmpeg',
            '-i', input_file,  # 输入文件
            '-acodec', 'libmp3lame',  # MP3编码器
            '-ab', bitrate,  # 比特率
            '-y',  # 覆盖已存在的文件
            output_file  # 输出文件
        ]
        
        # 执行转换
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"音频格式转换成功: {os.path.basename(input_file)} -> {os.path.basename(output_file)}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"音频格式转换失败: {e}")
        logger.error(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"转换过程中出现错误: {e}")
        return False


def load_config(config_file: str = "download_config.json") -> dict:
    """
    加载配置文件
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        配置字典
    """
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info(f"成功加载配置文件: {config_file}")
                return config
    except Exception as e:
        logger.warning(f"加载配置文件失败: {e}，使用默认配置")
    
    return DOWNLOAD_CONFIG


def save_download_status(status_file: str, url: str, status: str, error: str = ""):
    """
    保存下载状态到文件
    
    Args:
        status_file: 状态文件路径
        url: 视频URL
        status: 下载状态（success/failed/skipped）
        error: 错误信息（如果有）
    """
    try:
        status_data = []
        if os.path.exists(status_file):
            with open(status_file, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
        
        status_data.append({
            "url": url,
            "status": status,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        logger.error(f"保存下载状态失败: {e}")


async def download_audio_with_retry(url: str, temp_path: str, max_retries: int = 3) -> bool:
    """
    下载指定B站视频的音频文件，支持重试
    
    Args:
        url: B站视频URL
        temp_path: 临时下载目录路径
        max_retries: 最大重试次数
        
    Returns:
        是否下载成功
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"开始下载音频 (尝试 {attempt + 1}/{max_retries}): {url}")
            logger.info(f"临时下载目录: {temp_path}")
            
            async with DownloaderBilibili() as d:
                # 设置只下载音频
                await d.get_video(url, path=temp_path, only_audio=True)
            
            logger.info(f"音频下载完成: {url}")
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"下载超时 (尝试 {attempt + 1}/{max_retries}): {url}")
            if attempt < max_retries - 1:
                await asyncio.sleep(DOWNLOAD_CONFIG["retry_delay"])
                
        except Exception as e:
            logger.error(f"下载失败 (尝试 {attempt + 1}/{max_retries}): {url}")
            logger.error(f"错误详情: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(DOWNLOAD_CONFIG["retry_delay"])
    
    return False


def setup_directories(config: dict = None) -> Tuple[str, str, str, dict]:
    """
    设置和创建必要的目录结构
    
    Args:
        config: 配置字典，包含输出格式信息
        
    Returns:
        音频目录、临时目录、状态目录的路径元组，以及格式子目录字典
    """
    if config is None:
        config = DOWNLOAD_CONFIG
        
    try:
        audio_folder_path = "./audio"      # 音频文件存储目录
        temp_folder_path = "./temp"        # 临时下载目录
        status_folder_path = "./status"    # 状态文件目录
        
        # 创建必要的目录结构
        for folder_path, folder_name in [
            (audio_folder_path, "音频"),
            (temp_folder_path, "临时"),
            (status_folder_path, "状态")
        ]:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                logger.info(f"创建{folder_name}目录: {folder_path}")
            else:
                logger.info(f"{folder_name}目录已存在: {folder_path}")
        
        # 为每种输出格式创建子目录
        format_dirs = {}
        output_formats = config.get("output_formats", ["aac"])
        for fmt in output_formats:
            fmt_dir = os.path.join(audio_folder_path, fmt)
            if not os.path.exists(fmt_dir):
                os.makedirs(fmt_dir)
                logger.info(f"创建{fmt.upper()}格式子目录: {fmt_dir}")
            format_dirs[fmt] = fmt_dir
        
        return audio_folder_path, temp_folder_path, status_folder_path, format_dirs
        
    except OSError as e:
        logger.error(f"创建目录失败: {e}")
        raise AudioDownloadError(f"无法创建必要的目录: {e}")


def move_audio_files(temp_folder_path: str, audio_folder_path: str, 
                    format_dirs: dict = None, config: dict = None) -> List[str]:
    """
    将临时目录中的音频文件移动到audio目录，并根据配置转换格式
    
    Args:
        temp_folder_path: 临时目录路径
        audio_folder_path: 目标音频目录路径
        format_dirs: 格式子目录字典
        config: 配置字典
        
    Returns:
        成功处理的文件列表
    """
    if config is None:
        config = DOWNLOAD_CONFIG
    
    processed_files = []
    output_formats = config.get("output_formats", ["aac"])
    audio_quality = config.get("audio_quality", "192k")
    
    try:
        # 获取临时目录中的所有文件
        temp_files = os.listdir(temp_folder_path)
        
        if not temp_files:
            logger.warning("临时目录中没有找到下载的文件")
            return processed_files
        
        # 处理所有音频文件
        for file_name in temp_files:
            if os.path.isfile(os.path.join(temp_folder_path, file_name)):
                # 检查是否为音频文件
                if not file_name.lower().endswith(('.mp3', '.m4a', '.aac', '.flac', '.wav')):
                    logger.info(f"跳过非音频文件: {file_name}")
                    continue
                
                try:
                    temp_path = os.path.join(temp_folder_path, file_name)
                    name, original_ext = os.path.splitext(file_name)
                    
                    # 处理每种输出格式
                    for fmt in output_formats:
                        # 确定目标目录
                        if format_dirs and fmt in format_dirs:
                            target_dir = format_dirs[fmt]
                        else:
                            target_dir = os.path.join(audio_folder_path, fmt)
                            if not os.path.exists(target_dir):
                                os.makedirs(target_dir)
                        
                        # 构建目标文件路径
                        if fmt.lower() in original_ext.lower() or fmt == "aac":
                            # 原始格式或AAC格式，直接复制
                            target_file = f"{name}{original_ext}"
                            target_path = os.path.join(target_dir, target_file)
                            
                            # 如果目标文件已存在，添加时间戳
                            if os.path.exists(target_path):
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                target_file = f"{name}_{timestamp}{original_ext}"
                                target_path = os.path.join(target_dir, target_file)
                            
                            # 复制文件
                            shutil.copy2(temp_path, target_path)
                            logger.info(f"音频文件已复制到: {target_path}")
                            processed_files.append(target_path)
                            
                        elif fmt == "mp3" and FFMPEG_AVAILABLE:
                            # 转换为MP3格式
                            target_file = f"{name}.mp3"
                            target_path = os.path.join(target_dir, target_file)
                            
                            # 如果目标文件已存在，添加时间戳
                            if os.path.exists(target_path):
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                target_file = f"{name}_{timestamp}.mp3"
                                target_path = os.path.join(target_dir, target_file)
                            
                            # 转换格式
                            if convert_audio_format(temp_path, target_path, audio_quality):
                                processed_files.append(target_path)
                            else:
                                logger.warning(f"无法转换为MP3格式: {file_name}")
                    
                    # 删除临时文件
                    os.remove(temp_path)
                    logger.info(f"已删除临时文件: {temp_path}")
                    
                except Exception as e:
                    logger.error(f"处理文件 {file_name} 失败: {e}")
                    
    except Exception as e:
        logger.error(f"处理音频文件时出错: {e}")
        
    return processed_files


def cleanup_temp_folder(temp_folder_path: str):
    """
    清理临时文件夹
    
    Args:
        temp_folder_path: 临时文件夹路径
    """
    try:
        # 删除临时文件夹中的所有文件
        for file_name in os.listdir(temp_folder_path):
            file_path = os.path.join(temp_folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.info(f"删除临时文件: {file_path}")
                
    except Exception as e:
        logger.warning(f"清理临时文件夹失败: {e}")


async def download_batch(urls: List[str], temp_path: str, max_concurrent: int = 3) -> dict:
    """
    批量下载音频，支持并发控制
    
    Args:
        urls: URL列表
        temp_path: 临时下载路径
        max_concurrent: 最大并发数
        
    Returns:
        下载结果统计
    """
    results = {"success": 0, "failed": 0, "urls_failed": []}
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def download_with_semaphore(url: str):
        async with semaphore:
            success = await download_audio_with_retry(
                url, temp_path, DOWNLOAD_CONFIG["max_retries"]
            )
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
                results["urls_failed"].append(url)
    
    # 创建下载任务
    tasks = [download_with_semaphore(url) for url in urls]
    await asyncio.gather(*tasks)
    
    return results


async def main():
    """
    主函数：批量下载音频处理流程
    """
    start_time = datetime.now()
    
    logger.info("=" * 50)
    logger.info("Bili2Text - B站音频下载工具")
    logger.info("=" * 50)
    
    try:
        # 加载配置
        config = load_config()
        
        # 准备工作环境
        logger.info("准备工作环境......")
        audio_folder_path, temp_folder_path, status_folder_path, format_dirs = setup_directories(config)
        
        # 创建状态文件
        status_file = os.path.join(status_folder_path, 
                                   f"download_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # 显示要下载的音频数量
        logger.info(f"准备下载 {len(audio_urls)} 个音频")
        
        # 批量下载音频
        download_results = {"success": 0, "failed": 0, "urls_failed": []}
        
        for i, audio_url in enumerate(audio_urls, 1):
            logger.info(f"\n[{i}/{len(audio_urls)}] 处理音频: {audio_url}")
            
            batch_start_time = datetime.now()
            
            try:
                # 清理临时文件夹
                cleanup_temp_folder(temp_folder_path)
                
                # 下载音频文件到临时目录
                success = await download_audio_with_retry(
                    audio_url, temp_folder_path, config["max_retries"]
                )
                
                if success:
                    # 移动音频文件到指定目录
                    logger.info("正在处理音频文件...")
                    moved_files = move_audio_files(temp_folder_path, audio_folder_path, format_dirs, config)
                    
                    if moved_files:
                        download_results["success"] += 1
                        save_download_status(status_file, audio_url, "success")
                        
                        batch_end_time = datetime.now()
                        duration = (batch_end_time - batch_start_time).seconds
                        logger.info(f"音频 {i} 下载完成，耗时 {duration} 秒")
                    else:
                        download_results["failed"] += 1
                        download_results["urls_failed"].append(audio_url)
                        save_download_status(status_file, audio_url, "failed", "文件移动失败")
                else:
                    download_results["failed"] += 1
                    download_results["urls_failed"].append(audio_url)
                    save_download_status(status_file, audio_url, "failed", "下载失败")
                    
            except KeyboardInterrupt:
                logger.info("\n用户中断下载")
                save_download_status(status_file, audio_url, "interrupted", "用户中断")
                break
                
            except Exception as e:
                logger.error(f"处理音频时出现未预期的错误: {str(e)}")
                download_results["failed"] += 1
                download_results["urls_failed"].append(audio_url)
                save_download_status(status_file, audio_url, "failed", str(e))
                continue
        
        # 最终清理
        cleanup_temp_folder(temp_folder_path)
        
        # 显示下载统计
        end_time = datetime.now()
        total_duration = (end_time - start_time).seconds
        
        logger.info("\n" + "=" * 50)
        logger.info("下载完成统计：")
        logger.info(f"成功下载: {download_results['success']} 个")
        logger.info(f"下载失败: {download_results['failed']} 个")
        if download_results["urls_failed"]:
            logger.info("失败的URL列表：")
            for url in download_results["urls_failed"]:
                logger.info(f"  - {url}")
        logger.info(f"总耗时: {total_duration} 秒")
        logger.info(f"音频文件保存在: {os.path.abspath(audio_folder_path)}")
        logger.info(f"状态文件保存在: {os.path.abspath(status_file)}")
        logger.info("=" * 50)
        
    except AudioDownloadError as e:
        logger.error(f"音频下载错误: {e}")
        return 1
        
    except Exception as e:
        logger.error(f"程序运行出现严重错误: {e}")
        logger.error("错误详情：", exc_info=True)
        return 1
        
    return 0


if __name__ == "__main__":
    try:
        # 运行批量下载程序
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n程序被用户中断")
        exit(0)
    except Exception as e:
        logger.error(f"程序启动失败: {e}")
        exit(1)