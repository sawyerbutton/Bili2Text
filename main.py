"""
Bili2Text - 哔哩哔哩视频音频转文字工具
功能：从B站视频链接下载音频，并使用OpenAI的Whisper模型将语音转换为文本
作者：原作者
日期：创建日期
"""

import asyncio  # 导入异步IO库，用于异步下载
import os  # 导入操作系统模块，用于文件和目录操作
import re  # 导入正则表达式模块，用于文本替换
import shutil  # 导入文件操作模块，用于移动文件
from datetime import datetime  # 导入日期时间模块，用于计时

import torch  # 导入PyTorch库，用于深度学习
import whisper  # 导入Whisper模型，用于语音识别
from bilix.sites.bilibili import DownloaderBilibili  # 导入B站下载器

# B站视频URL列表
audio_urls = [
    "https://www.bilibili.com/video/BV1D1MTz5EzP/?spm_id_from=333.337.search-card.all.click&vd_source=41395574d05172f2bcc7dfec3acf5363"
    ]


async def downloadaudio(url):
    """异步下载B站视频音频
    
    Args:
        url: B站视频URL
    """
    async with DownloaderBilibili() as d:
        await d.get_video(url, path="./temp", only_audio=True)


## 准备环境
print("Preparing......")
audio_folder_path = "./audio"  # 音频存储目录
temp_folder_path = "./temp"    # 临时文件目录
result_folder_path = "./result"  # 结果存储目录
# 确保必要的目录存在
if not os.path.exists(audio_folder_path):
    os.makedirs(audio_folder_path)
if not os.path.exists(temp_folder_path):
    os.makedirs(temp_folder_path)
if not os.path.exists(result_folder_path):
    os.makedirs(result_folder_path)

## 加载Whisper模型
# model_name = "large-v3"
model_name = "medium"  # 选择使用中等大小的模型
print("Using whisper model", model_name)
print("Loading Model......")
time1 = datetime.now()  # 记录模型加载开始时间
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # 检测并选择设备(GPU或CPU)
model = whisper.load_model(
    name=model_name,
    device=device,
    download_root="./.cache/whisper",  # 设置模型下载和缓存目录
)
time2 = datetime.now()  # 记录模型加载结束时间
print("Model Loaded in", (time2 - time1).seconds, "seconds")  # 输出模型加载耗时


## 下载并转录
for audio_url in audio_urls:
    ## 下载音频到临时目录
    print("Downloading audio from", audio_url)
    asyncio.run(downloadaudio(audio_url))  # 执行异步下载任务
    print("Audio Downloaded.")
    audio_name = os.listdir(temp_folder_path)[0]  # 获取下载的音频文件名
    temp_path = temp_folder_path + "/" + audio_name  # 临时文件路径
    audio_path = audio_folder_path + "/" + audio_name  # 目标音频文件路径
    shutil.move(temp_path, audio_path)  # 将音频从临时目录移动到音频目录

    print("Start Transcribe......")
    time3 = datetime.now()  # 记录转录开始时间
    result = model.transcribe(
        audio_path,
        verbose=True,  # 启用详细输出
        initial_prompt='"生于忧患，死于安乐。岂不快哉？"简体中文，加上标点。',  # 设置初始提示，优化中文识别
    )
    time4 = datetime.now()  # 记录转录结束时间
    print("Transcribe Finish in", (time4 - time3).seconds, "seconds")  # 输出转录耗时

    print("Saving result......")
    text = result["text"]  # 获取转录文本
    text = re.sub(",", "，", text)  # 将英文逗号替换为中文逗号
    text = re.sub(r"\?", "？", text)  # 将英文问号替换为中文问号
    with open(
        result_folder_path + "/" + audio_name + ".txt", "w", encoding="utf-8"
    ) as f:
        f.write(text)  # 将转录结果写入文件
    print("Result Saved to", result_folder_path + "/" + audio_name + ".txt")  # 输出结果保存路径
