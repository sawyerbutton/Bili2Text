"""
Bili2Text - 哔哩哔哩视频音频转录工具 (InfinityAcademy专用版)
=======================================================

文件目的：
    自动获取指定B站UP主（InfinityAcademy）的全部动态，下载其中所有视频的音频，
    并使用Whisper模型进行语音转录，最终生成包含视频信息和转录文本的Markdown文件。

主要功能：
    1. 获取B站用户全部动态信息
    2. 筛选出所有包含视频的动态
    3. 批量下载视频音频文件
    4. 使用Whisper进行语音转录
    5. 生成格式化的Markdown输出文件
    6. 避免重复处理已处理过的视频

依赖库：
    - asyncio: 异步编程支持
    - bilibili_api: B站API接口
    - bilix: B站视频下载工具
    - whisper: OpenAI语音转录模型
    - torch: PyTorch深度学习框架

作者：Auto Generated
创建时间：2024
"""

import asyncio
import os
import re
import shutil
from datetime import datetime, timezone

import torch
import whisper
from bilibili_api import settings, sync, user
from bilix.sites.bilibili import DownloaderBilibili

# 配置信息
uid = 10642220  # InfinityAcademy的B站UID
u = user.User(uid)

# 代理设置
use_proxy = True
if use_proxy:
    settings.proxy = "http://127.0.0.1:7890"


async def get_all_video_info():
    """
    获取指定用户的全部动态信息
    
    功能：
        - 获取用户全部的动态列表
        - 提取所有包含视频信息的动态
        - 返回视频信息列表
    
    Returns:
        list: 包含(bvid, title, desc)元组的列表
        
    异常处理：
        - 如果动态中没有视频信息，会跳过该动态
        - 返回所有有效的视频信息
    """
    dynamics = []
    video_info_list = []
    
    # 获取第一页动态
    page = await u.get_dynamics(0)
    if "cards" in page:
        dynamics.extend(page["cards"])
    
    # 获取后续页面的动态
    offset = page.get("next_offset", 0)
    while offset > 0:
        try:
            page = await u.get_dynamics(offset)
            if "cards" in page:
                dynamics.extend(page["cards"])
            offset = page.get("next_offset", 0)
        except:
            break
    
    print(f"共获取 {len(dynamics)} 条动态")
    
    # 提取所有视频信息
    for dynamic in dynamics:
        try:
            bvid = dynamic["desc"]["bvid"]
            desc = dynamic["card"]["dynamic"]
            title = dynamic["card"]["title"]
            video_info_list.append((bvid, title, desc))
        except:
            continue  # 跳过不包含视频的动态
    
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


def load_processed_videos(file_path="processed_infinityacademy.txt"):
    """
    加载已处理的视频列表
    
    Args:
        file_path (str): 已处理视频列表文件路径
        
    Returns:
        set: 已处理的视频ID集合
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f.readlines())
    except FileNotFoundError:
        return set()


def save_processed_video(bvid, file_path="processed_infinityacademy.txt"):
    """
    保存已处理的视频ID
    
    Args:
        bvid (str): 视频ID
        file_path (str): 保存文件路径
    """
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(bvid + "\n")


def create_markdown_file(bvid, title, desc, audio_name, result_folder_path):
    """
    创建Markdown文件并写入基本信息
    
    Args:
        bvid (str): 视频ID
        title (str): 视频标题
        desc (str): 视频描述
        audio_name (str): 音频文件名
        result_folder_path (str): 结果文件夹路径
        
    Returns:
        str: Markdown文件路径
    """
    text_path = os.path.join(result_folder_path, audio_name + ".md")
    
    with open(text_path, "w", encoding="utf-8") as f:
        # 写入YAML前置信息
        f.write("---\ntitle: ")
        f.write(title + "\n")
        f.write("description: " + desc + "\n")
        f.write("published: true\n")
        
        # 生成时间戳
        timestr = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + ".000Z"
        f.write("date: " + timestr + "\n")
        f.write("tags: \neditor: markdown\n")
        f.write("dateCreated: " + timestr + "\n---\n")
        
        # 写入视频嵌入模板
        text = """
## Tabs {.tabset}
### B站
<div style="position: relative; padding: 30% 45%;">
<iframe style="position: absolute; width: 100%; height: 100%; left: 0; top: 0;" src="//player.bilibili.com/player.html?&bvid="""

        text2 = """&page=1&as_wide=1&high_quality=1&danmaku=1&autoplay=0" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe>
</div>

### YouTube
<div style="position: relative; padding: 30% 45%;">
<iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" src="https://www.youtube-nocookie.com/embed/YouTubeVID" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

##

> 以下文本为音频转录结果，存在一定错误，校对正在进行中。
{.is-warning}

"""
        f.write(text)
        f.write(bvid)
        f.write(text2)
    
    return text_path


def transcribe_audio(audio_path, model):
    """
    对音频文件进行语音转录
    
    Args:
        audio_path (str): 音频文件路径
        model: Whisper模型
        
    Returns:
        str: 转录结果文本
    """
    print(f"开始转录: {audio_path}")
    time3 = datetime.now()
    
    result = model.transcribe(
        audio_path,
        verbose=True,  # 显示转录进度
        initial_prompt='简体中文,加上标点',  # 提示模型使用中文和标点
    )
    
    time4 = datetime.now()
    print(f"转录完成，耗时 {(time4 - time3).seconds} 秒")
    
    # 获取转录文本
    text = result["text"]
    
    # 标点符号标准化（英文标点转中文标点）
    text = re.sub(",", "，", text)
    text = re.sub(r"\?", "？", text)
    
    return text


def main():
    """
    主函数：处理全部动态中的视频
    """
    # 获取全部视频信息
    video_info_list = sync(get_all_video_info())
    
    if not video_info_list:
        print("没有找到任何视频，程序退出")
        return
    
    # 加载已处理的视频列表
    processed_videos = load_processed_videos()
    
    # 准备工作环境
    print("准备工作环境......")
    audio_folder_path = "./audio"      # 音频文件存储目录
    temp_folder_path = "./temp"        # 临时文件目录
    result_folder_path = "./result"    # 结果文件目录
    
    # 创建必要的目录
    for folder_path in [audio_folder_path, temp_folder_path, result_folder_path]:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    
    # 加载Whisper模型
    model_name = "medium"    # 使用medium模型（平衡速度和准确性）
    print(f"使用Whisper模型: {model_name}")
    print("正在加载模型......")
    
    time1 = datetime.now()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = whisper.load_model(
        name=model_name,
        device=device,
        download_root="./.cache/whisper",  # 模型缓存目录
    )
    time2 = datetime.now()
    print(f"模型加载完成，耗时 {(time2 - time1).seconds} 秒")
    
    # 处理每个视频
    total_videos = len(video_info_list)
    processed_count = 0
    
    for i, (bvid, title, desc) in enumerate(video_info_list, 1):
        print(f"\n处理进度: {i}/{total_videos}")
        print(f"视频ID: {bvid}")
        print(f"标题: {title}")
        print(f"描述: {desc}")
        
        # 检查是否已处理过该视频
        if bvid in processed_videos:
            print(f"视频 {bvid} 已经处理过，跳过")
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
            audio_path = os.path.join(audio_folder_path, audio_name)
            
            if os.path.exists(audio_path):
                # 如果音频文件已存在，添加视频ID前缀
                audio_name_with_id = f"{bvid}_{audio_name}"
                audio_path = os.path.join(audio_folder_path, audio_name_with_id)
                audio_name = audio_name_with_id
            
            shutil.move(temp_path, audio_path)
            
            # 创建Markdown文件
            text_path = create_markdown_file(bvid, title, desc, audio_name, result_folder_path)
            
            # 执行语音转录
            transcribed_text = transcribe_audio(audio_path, model)
            
            # 将转录文本追加到Markdown文件
            with open(text_path, "a", encoding="utf-8") as f:
                f.write(transcribed_text)
            
            print(f"结果已保存到: {text_path}")
            
            # 记录已处理的视频
            save_processed_video(bvid)
            processed_videos.add(bvid)
            processed_count += 1
            
        except Exception as e:
            print(f"处理视频 {bvid} 时出错: {e}")
            continue
    
    print(f"\n处理完成！共处理 {processed_count} 个新视频")


if __name__ == "__main__":
    main() 