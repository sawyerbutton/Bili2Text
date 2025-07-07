"""
Bili2Text - 音频下载工具 (InfinityAcademy专用版)
===============================================

文件目的：
    自动获取指定B站UP主（InfinityAcademy）的全部动态，批量下载其中所有视频的音频文件。

主要功能：
    1. 获取B站用户全部动态信息
    2. 筛选出所有包含视频的动态
    3. 批量下载视频音频文件
    4. 避免重复下载已下载过的视频

依赖库：
    - asyncio: 异步编程支持
    - bilibili_api: B站API接口
    - bilix: B站视频下载工具

作者：Auto Generated
创建时间：2024
"""

import asyncio
import os
import shutil
from datetime import datetime

from bilibili_api import sync, user, Credential, request_settings
from bilix.sites.bilibili import DownloaderBilibili

# 配置信息
uid = 10642220  # InfinityAcademy的B站UID

# 设置请求参数，避免412错误
request_settings.set_timeout(10.0)

# 代理设置（可选）
use_proxy = False  # 建议先不使用代理测试
if use_proxy:
    request_settings.set_proxy("http://127.0.0.1:7890")

# 创建用户对象
u = user.User(uid)


async def get_all_video_info():
    """
    获取指定用户的全部视频信息
    
    功能：
        - 首先尝试直接获取用户的视频列表
        - 如果失败，则尝试从动态中获取视频信息
        - 返回视频信息列表
    
    Returns:
        list: 包含(bvid, title, desc)元组的列表
        
    异常处理：
        - 如果视频获取失败，会尝试动态方式
        - 返回所有有效的视频信息
    """
    video_info_list = []
    
    # 方法1：直接获取用户视频列表
    try:
        print("正在获取用户视频列表...")
        page_num = 1
        
        while True:
            print(f"获取第 {page_num} 页视频...")
            
            # 获取视频页
            videos_page = await u.get_videos(pn=page_num)
            
            if not videos_page or "list" not in videos_page:
                print("没有更多视频数据")
                break
                
            videos = videos_page["list"]["vlist"]
            if not videos:
                print("当前页没有视频")
                break
                
            print(f"第 {page_num} 页获取到 {len(videos)} 个视频")
            
            # 处理视频信息
            for video in videos:
                try:
                    bvid = video.get("bvid", "")
                    title = video.get("title", "无标题")
                    desc = video.get("description", "无描述")
                    
                    if bvid:
                        video_info_list.append((bvid, title, desc))
                        print(f"找到视频: {bvid} - {title}")
                        
                except Exception as e:
                    print(f"处理视频信息时出错: {e}")
                    continue
            
            # 检查是否有下一页
            page_count = videos_page["page"]["count"]
            page_size = videos_page["page"]["ps"]
            total_pages = (page_count + page_size - 1) // page_size
            
            if page_num >= total_pages:
                print("已获取所有视频页面")
                break
                
            page_num += 1
            # 添加延迟避免请求过快
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"获取视频列表失败: {e}")
        print("尝试从动态中获取视频信息...")
        
        # 方法2：从动态中获取视频信息（备用方案）
        try:
            page_num = 1
            offset = ""
            
            while True:
                print(f"获取第 {page_num} 页动态...")
                
                if page_num == 1:
                    page = await u.get_dynamics(0)
                else:
                    page = await u.get_dynamics(offset)
                
                if not page or "cards" not in page:
                    print("没有更多动态数据")
                    break
                    
                cards = page["cards"]
                if not cards:
                    print("当前页没有动态卡片")
                    break
                    
                print(f"第 {page_num} 页获取到 {len(cards)} 条动态")
                
                # 提取动态中的视频信息
                for i, dynamic in enumerate(cards):
                    try:
                        if "desc" not in dynamic or "card" not in dynamic:
                            continue
                            
                        desc_info = dynamic["desc"]
                        card_info = dynamic["card"]
                        
                        if "bvid" not in desc_info:
                            continue
                            
                        bvid = desc_info["bvid"]
                        title = card_info.get("title", "无标题")
                        desc = card_info.get("dynamic", card_info.get("desc", "无描述"))
                        
                        video_info_list.append((bvid, title, desc))
                        print(f"找到视频: {bvid} - {title}")
                        
                    except Exception as e:
                        print(f"处理第 {i+1} 条动态时出错: {e}")
                        continue
                
                # 检查是否有下一页
                if "next_offset" in page and page["next_offset"]:
                    offset = page["next_offset"]
                    page_num += 1
                    await asyncio.sleep(1)
                else:
                    print("已获取所有动态页面")
                    break
                    
        except Exception as e2:
            print(f"从动态获取视频信息也失败: {e2}")
            print("可能原因：")
            print("1. 网络连接问题")
            print("2. B站反爬机制")
            print("3. 用户不存在或内容不公开")
            return []
    
    print(f"共找到 {len(video_info_list)} 个视频")
    return video_info_list


async def downloadaudio(url, output_path="./temp"):
    """
    下载指定B站视频的音频文件
    
    Args:
        url (str): B站视频URL
        output_path (str): 输出路径
        
    功能：
        - 使用bilix库下载视频的音频部分
        - 保存到指定目录
        - 仅下载音频，不下载视频
    """
    async with DownloaderBilibili() as d:
        await d.get_video(url, path=output_path, only_audio=True)


def load_downloaded_videos(file_path="downloaded_infinityacademy.txt"):
    """
    加载已下载的视频列表
    
    Args:
        file_path (str): 已下载视频列表文件路径
        
    Returns:
        set: 已下载的视频ID集合
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f.readlines())
    except FileNotFoundError:
        return set()


def save_downloaded_video(bvid, file_path="downloaded_infinityacademy.txt"):
    """
    保存已下载的视频ID
    
    Args:
        bvid (str): 视频ID
        file_path (str): 保存文件路径
    """
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(bvid + "\n")


def save_video_info(bvid, title, desc, audio_filename, info_file="video_info_infinityacademy.txt"):
    """
    保存视频信息到文件，供转录脚本使用
    
    Args:
        bvid (str): 视频ID
        title (str): 视频标题
        desc (str): 视频描述
        audio_filename (str): 音频文件名
        info_file (str): 信息文件路径
    """
    with open(info_file, "a", encoding="utf-8") as f:
        # 格式：bvid|title|desc|audio_filename
        f.write(f"{bvid}|{title}|{desc}|{audio_filename}\n")


def main():
    """
    主函数：下载全部动态中的视频音频
    """
    print("=== InfinityAcademy 音频下载工具 ===")
    print(f"目标用户UID: {uid}")
    print(f"代理设置: {'启用' if use_proxy else '禁用'}")
    print("开始获取视频信息...")
    
    try:
        # 获取全部视频信息
        video_info_list = sync(get_all_video_info())
        
        if not video_info_list:
            print("没有找到任何视频，程序退出")
            print("可能的解决方案：")
            print("1. 检查用户UID是否正确")
            print("2. 检查网络连接")
            print("3. 用户可能没有公开的视频动态")
            return
            
    except Exception as e:
        print(f"获取视频信息失败: {e}")
        print("请检查网络连接和用户ID是否正确")
        return
    
    # 加载已下载的视频列表
    downloaded_videos = load_downloaded_videos()
    
    # 准备工作环境
    print("准备工作环境......")
    audio_folder_path = "./audio"      # 音频文件存储目录
    temp_folder_path = "./temp"        # 临时文件目录
    
    # 创建必要的目录
    for folder_path in [audio_folder_path, temp_folder_path]:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    
    # 处理每个视频
    total_videos = len(video_info_list)
    downloaded_count = 0
    
    for i, (bvid, title, desc) in enumerate(video_info_list, 1):
        print(f"\n下载进度: {i}/{total_videos}")
        print(f"视频ID: {bvid}")
        print(f"标题: {title}")
        print(f"描述: {desc}")
        
        # 检查是否已下载过该视频
        if bvid in downloaded_videos:
            print(f"视频 {bvid} 已经下载过，跳过")
            continue
        
        try:
            # 下载音频文件
            audio_url = "https://www.bilibili.com/video/" + bvid
            print(f"正在从 {audio_url} 下载音频")
            
            # 清理临时目录
            for file in os.listdir(temp_folder_path):
                os.remove(os.path.join(temp_folder_path, file))
            
            # 下载音频
            asyncio.run(downloadaudio(audio_url, temp_folder_path))
            print("音频下载完成")
            
            # 移动音频文件到指定目录
            audio_files = os.listdir(temp_folder_path)
            if not audio_files:
                print("音频下载失败，跳过此视频")
                continue
                
            audio_name = audio_files[0]
            temp_path = os.path.join(temp_folder_path, audio_name)
            
            # 使用视频ID作为前缀避免文件名冲突
            audio_name_with_id = f"{bvid}_{audio_name}"
            audio_path = os.path.join(audio_folder_path, audio_name_with_id)
            
            # 移动文件
            shutil.move(temp_path, audio_path)
            print(f"音频文件已保存到: {audio_path}")
            
            # 保存视频信息供转录脚本使用
            save_video_info(bvid, title, desc, audio_name_with_id)
            
            # 记录已下载的视频
            save_downloaded_video(bvid)
            downloaded_videos.add(bvid)
            downloaded_count += 1
            
        except Exception as e:
            print(f"下载视频 {bvid} 时出错: {e}")
            continue
    
    print(f"\n下载完成！共下载 {downloaded_count} 个新视频的音频文件")


if __name__ == "__main__":
    main() 