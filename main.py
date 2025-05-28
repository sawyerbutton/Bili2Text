"""
Bili2Text - 哔哩哔哩视频音频转录工具（批量处理版本）
=====================================================

文件目的：
    批量下载指定B站视频的音频文件，并使用Whisper模型进行语音转录，
    将转录结果保存为文本文件。这是一个简化版本的音频转录工具。

主要功能：
    1. 批量下载B站视频的音频文件
    2. 使用Whisper模型进行语音转录
    3. 标点符号标准化处理
    4. 保存转录结果为文本文件
    5. 自动管理文件目录结构

与get_ref_from_dynamics.py的区别：
    - 本文件用于批量处理指定的视频URL列表
    - 不包含动态获取和视频筛选功能
    - 输出格式为简单的文本文件，而非Markdown
    - 适用于已知视频URL的批量转录场景

依赖库：
    - asyncio: 异步编程支持
    - bilix: B站视频下载工具
    - whisper: OpenAI语音转录模型
    - torch: PyTorch深度学习框架

作者：[Your Name]
创建时间：[Date]
"""

import asyncio
import os
import re
import shutil
from datetime import datetime

import torch
import whisper
from bilix.sites.bilibili import DownloaderBilibili

# 配置要处理的视频URL列表
audio_urls = ["https://www.bilibili.com/video/BV15N4y1J7CA"]


async def downloadaudio(url):
    """
    下载指定B站视频的音频文件
    
    Args:
        url (str): B站视频URL
        
    功能：
        - 使用bilix库异步下载视频的音频部分
        - 保存到./temp目录
        - 仅下载音频，不下载视频文件
        
    注意：
        - 需要在异步环境中调用
        - 下载的文件会保存在temp目录中
    """
    async with DownloaderBilibili() as d:
        await d.get_video(url, path="./temp", only_audio=True)


# 准备工作环境
print("准备工作环境......")
audio_folder_path = "./audio"      # 音频文件存储目录
temp_folder_path = "./temp"        # 临时下载目录
result_folder_path = "./result"    # 转录结果存储目录

# 创建必要的目录结构
if not os.path.exists(audio_folder_path):
    os.makedirs(audio_folder_path)
if not os.path.exists(temp_folder_path):
    os.makedirs(temp_folder_path)
if not os.path.exists(result_folder_path):
    os.makedirs(result_folder_path)

# 加载Whisper语音转录模型
# model_name = "large-v3"  # 可选：large-v3（最高精度，速度较慢）
model_name = "medium"      # 当前使用：medium（平衡精度和速度）
print(f"使用Whisper模型: {model_name}")
print("正在加载模型......")

time1 = datetime.now()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # 自动选择GPU或CPU
model = whisper.load_model(
    name=model_name,
    device=device,
    download_root="./.cache/whisper",  # 模型缓存目录
)
time2 = datetime.now()
print(f"模型加载完成，耗时 {(time2 - time1).seconds} 秒")

# 批量下载和转录处理
for audio_url in audio_urls:
    print(f"\n处理视频: {audio_url}")
    
    # 下载音频文件到临时目录
    print(f"正在从 {audio_url} 下载音频")
    asyncio.run(downloadaudio(audio_url))
    print("音频下载完成")
    
    # 移动音频文件到指定目录
    audio_name = os.listdir(temp_folder_path)[0]  # 获取下载的音频文件名
    temp_path = temp_folder_path + "/" + audio_name
    audio_path = audio_folder_path + "/" + audio_name
    shutil.move(temp_path, audio_path)

    # 执行语音转录
    print("开始转录......")
    time3 = datetime.now()
    result = model.transcribe(
        audio_path,
        verbose=True,  # 显示转录进度
        initial_prompt='"生于忧患，死于安乐。岂不快哉？"简体中文,加上标点。',  # 提示模型使用中文和标点
    )
    time4 = datetime.now()
    print(f"转录完成，耗时 {(time4 - time3).seconds} 秒")

    # 保存转录结果
    print("正在保存结果......")
    text = result["text"]
    
    # 标点符号标准化（英文标点转中文标点）
    text = re.sub(",", "，", text)      # 逗号标准化
    text = re.sub(r"\?", "？", text)    # 问号标准化
    
    # 保存为文本文件
    result_file_path = result_folder_path + "/" + audio_name + ".txt"
    with open(result_file_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"结果已保存到: {result_file_path}")
