"""
Bili2Text - 哔哩哔哩视频下载工具（批量处理版本）
=====================================================

文件目的：
    批量下载指定B站视频的MP4文件，将视频文件保存到指定目录。
    这是一个专门用于视频下载的简化工具。

主要功能：
    1. 批量下载B站视频的MP4文件
    2. 自动管理文件目录结构
    3. 支持异步下载，提高下载效率
    4. 自动移动下载文件到指定目录

与main.py的区别：
    - 本文件专门用于视频下载，不包含音频转录功能
    - 下载完整的MP4视频文件，而非仅音频
    - 输出目录为storage目录下的video文件夹
    - 适用于需要保存完整视频文件的场景

依赖库：
    - asyncio: 异步编程支持
    - bilix: B站视频下载工具

作者：Bili2Text Tool
创建时间：2024
"""

import asyncio
import os
import shutil
from datetime import datetime

from bilix.sites.bilibili import DownloaderBilibili

# 配置要处理的视频URL列表
video_urls = [
    # "https://www.bilibili.com/video/BV14hNbzpEjx/?spm_id_from=333.337.search-card.all.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    # "https://www.bilibili.com/video/BV1PdTMzYEmb/?spm_id_from=333.337.search-card.all.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    # "https://www.bilibili.com/video/BV1p4MuzNEkK/?spm_id_from=333.337.search-card.all.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    # "https://www.bilibili.com/video/BV1H2qLY7EcK/?spm_id_from=333.337.search-card.all.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    # "https://www.bilibili.com/video/BV1KvKtzREkV/?spm_id_from=333.337.search-card.all.click&vd_source=41395574d05172f2bcc7dfec3acf5363"
    # # "https://www.bilibili.com/video/BV1LCM3zwEH9/?spm_id_from=333.1391.0.0",
    # "https://www.bilibili.com/video/BV1mzNxzJEB8/?spm_id_from=333.1391.top_right_bar_window_default_collection.content.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    # "https://www.bilibili.com/video/BV1tbKAzQEQM/?spm_id_from=333.1391.top_right_bar_window_default_collection.content.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    # "https://www.bilibili.com/video/BV1fsKwzvECu/?spm_id_from=333.1391.top_right_bar_window_default_collection.content.click&vd_source=41395574d05172f2bcc7dfec3acf5363"
    # 可以在这里添加更多视频URL
    # "https://www.bilibili.com/video/BVXXXXXXX",
    # "https://www.bilibili.com/video/BVXXXXXXX",
    # "https://www.bilibili.com/video/BV1Mv7pzzEy5/?spm_id_from=333.1007.top_right_bar_window_history.content.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    # "https://www.bilibili.com/video/BV13b7pzCEeK/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    # "https://www.bilibili.com/video/BV1ssTqzjECD/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363"
    "https://www.bilibili.com/video/BV1xz3KzgEX1/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    "https://www.bilibili.com/video/BV15AgyzxEhr/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363",
    "https://www.bilibili.com/video/BV1g43szwEVL/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41395574d05172f2bcc7dfec3acf5363"
]


async def download_video(url, temp_path):
    """
    下载指定B站视频的MP4文件
    
    Args:
        url (str): B站视频URL
        temp_path (str): 临时下载目录路径
        
    功能：
        - 使用bilix库异步下载完整视频文件
        - 保存到指定的临时目录
        - 下载MP4格式的视频文件
        
    注意：
        - 需要在异步环境中调用
        - 下载的文件会先保存在temp目录中，然后移动到video目录
    """
    print(f"开始下载视频: {url}")
    print(f"临时下载目录: {temp_path}")
    async with DownloaderBilibili() as d:
        await d.get_video(url, path=temp_path)  # 使用配置的临时目录路径
    print(f"视频下载完成: {url}")


def setup_directories():
    """
    设置和创建必要的目录结构
    """
    video_folder_path = "./storage/video"      # 视频文件存储目录
    temp_folder_path = "./storage/temp"        # 临时下载目录
    
    # 创建必要的目录结构
    if not os.path.exists(video_folder_path):
        os.makedirs(video_folder_path)
        print(f"创建视频目录: {video_folder_path}")
    
    if not os.path.exists(temp_folder_path):
        os.makedirs(temp_folder_path)
        print(f"创建临时目录: {temp_folder_path}")
    
    return video_folder_path, temp_folder_path


def move_video_files(temp_folder_path, video_folder_path):
    """
    将临时目录中的视频文件移动到video目录
    
    Args:
        temp_folder_path (str): 临时目录路径
        video_folder_path (str): 目标视频目录路径
    """
    # 获取临时目录中的所有文件
    temp_files = os.listdir(temp_folder_path)
    
    if not temp_files:
        print("临时目录中没有找到下载的文件")
        return
    
    # 移动所有文件到video目录
    for file_name in temp_files:
        if os.path.isfile(os.path.join(temp_folder_path, file_name)):
            temp_path = os.path.join(temp_folder_path, file_name)
            video_path = os.path.join(video_folder_path, file_name)
            
            # 如果目标文件已存在，添加时间戳避免覆盖
            if os.path.exists(video_path):
                name, ext = os.path.splitext(file_name)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                video_path = os.path.join(video_folder_path, f"{name}_{timestamp}{ext}")
            
            shutil.move(temp_path, video_path)
            print(f"视频文件已移动到: {video_path}")


async def batch_main():
    """
    主函数：批量下载视频处理流程（用于直接运行脚本）
    """
    print("Bili2Text - B站视频下载工具")
    print("=" * 50)
    
    # 准备工作环境
    print("准备工作环境......")
    video_folder_path, temp_folder_path = setup_directories()
    
    # 显示要下载的视频数量
    print(f"准备下载 {len(video_urls)} 个视频")
    
    # 批量下载视频
    for i, video_url in enumerate(video_urls, 1):
        print(f"\n[{i}/{len(video_urls)}] 处理视频: {video_url}")
        
        start_time = datetime.now()
        
        try:
            # 下载视频文件到临时目录
            await download_video(video_url, temp_folder_path)
            
            # 移动视频文件到指定目录
            print("正在移动文件到video目录...")
            move_video_files(temp_folder_path, video_folder_path)
            
            end_time = datetime.now()
            duration = (end_time - start_time).seconds
            print(f"视频 {i} 下载完成，耗时 {duration} 秒")
            
        except Exception as e:
            print(f"下载视频时出现错误: {str(e)}")
            continue
    
    print(f"\n所有视频下载完成！")
    print(f"视频文件保存在: {os.path.abspath(video_folder_path)}")


async def single_video_download(url, output_dir):
    """
    下载单个视频（用于CLI调用）
    
    Args:
        url (str): 视频URL
        output_dir (str): 输出目录
    """
    print("Bili2Text - B站视频下载工具")
    print("=" * 50)
    print(f"下载视频: {url}")
    print(f"输出目录: {output_dir}")
    
    # 设置临时目录为storage/temp
    temp_folder_path = "./storage/temp"
    video_folder_path = output_dir
    
    # 创建必要的目录
    os.makedirs(video_folder_path, exist_ok=True)
    os.makedirs(temp_folder_path, exist_ok=True)
    
    try:
        start_time = datetime.now()
        
        # 下载视频
        await download_video(url, temp_folder_path)
        
        # 移动视频文件
        print("正在移动文件到输出目录...")
        move_video_files(temp_folder_path, video_folder_path)
        
        end_time = datetime.now()
        duration = (end_time - start_time).seconds
        print(f"视频下载完成，耗时 {duration} 秒")
        print(f"文件保存在: {os.path.abspath(video_folder_path)}")
        
    except Exception as e:
        print(f"下载视频时出现错误: {str(e)}")
        raise


def main(args):
    """
    CLI主入口函数（用于处理命令行参数）
    
    Args:
        args: 命令行参数对象
    """
    asyncio.run(single_video_download(args.url, args.output_dir))


if __name__ == "__main__":
    # 运行批量下载程序
    asyncio.run(batch_main()) 