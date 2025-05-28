"""
Bili2Text - 哔哩哔哩视频音频转录工具
=================================

文件目的：
    自动获取指定B站UP主（小黛晨读）的最新动态，下载其"参考信息"系列视频的音频，
    并使用Whisper模型进行语音转录，最终生成包含视频信息和转录文本的Markdown文件。

主要功能：
    1. 获取B站用户最新动态信息
    2. 筛选"参考信息"系列视频
    3. 下载视频音频文件
    4. 使用Whisper进行语音转录
    5. 生成格式化的Markdown输出文件
    6. 避免重复处理已处理过的视频

依赖库：
    - asyncio: 异步编程支持
    - bilibili_api: B站API接口
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
from datetime import datetime, timezone

import torch
import whisper
from bilibili_api import settings, sync, user
from bilix.sites.bilibili import DownloaderBilibili

# 配置信息
uid = 1556651916  # 小黛晨读的B站UID
u = user.User(uid)

# 代理设置
use_proxy = True
if use_proxy:
    settings.proxy = "http://127.0.0.1:7890"


async def get_latest_video_info():
    """
    获取指定用户的最新动态信息
    
    功能：
        - 获取用户最新的动态列表
        - 提取第一个包含视频信息的动态
        - 返回视频的bvid、标题和描述
    
    Returns:
        tuple: (bvid, title, desc) - 视频ID、标题、描述
        
    异常处理：
        - 如果动态中没有视频信息，会跳过该动态
        - 返回第一个有效的视频信息
    """
    dynamics = []
    page = await u.get_dynamics(0)
    if "cards" in page:
        dynamics.extend(page["cards"])
    print(f"共获取 {len(dynamics)} 条动态")
    
    for dynamic in dynamics:
        try:
            bvid = dynamic["desc"]["bvid"]
        except:
            continue  # 跳过不包含视频的动态
        desc = dynamic["card"]["dynamic"]
        title = dynamic["card"]["title"]
        return bvid, title, desc


async def downloadaudio(url):
    """
    下载指定B站视频的音频文件
    
    Args:
        url (str): B站视频URL
        
    功能：
        - 使用bilix库下载视频的音频部分
        - 保存到./temp目录
        - 仅下载音频，不下载视频
    """
    async with DownloaderBilibili() as d:
        await d.get_video(url, path="./temp", only_audio=True)


# 获取最新视频信息
bvid, title_ori, desc = sync(get_latest_video_info())

# 检查是否为"参考信息"系列视频
if "参考信息" in title_ori:
    # 标准化标题格式：【参考信息第X期】-> 【参考信息X】
    title = re.sub(r"【参考信息第(.*?)期】(.*?)", r"【参考信息\1】\2", title_ori)
else:
    print("当前视频不是参考信息系列，程序退出")
    quit()

print(f"视频ID: {bvid}")
print(f"标题: {title}")
print(f"描述: {desc}")

# 检查是否已处理过该视频
with open("processed.txt", "r", encoding="utf-8") as f:
    processed_video = f.readlines()

if bvid in processed_video:
    print("----------")
    print(f"{bvid} {title} 已经处理过")
    quit()
else:
    # 记录已处理的视频ID
    with open("processed.txt", "a", encoding="utf-8") as f:
        f.write("\n" + bvid)

# 准备工作环境
print("准备工作环境......")
audio_folder_path = "./audio"      # 音频文件存储目录
temp_folder_path = "./temp"        # 临时文件目录
result_folder_path = "./result"    # 结果文件目录

# 创建必要的目录
for folder_path in [audio_folder_path, temp_folder_path, result_folder_path]:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# 下载音频文件
audio_url = "https://www.bilibili.com/video/" + bvid
print(f"正在从 {audio_url} 下载音频")
asyncio.run(downloadaudio(audio_url))
print("音频下载完成")

# 移动音频文件到指定目录
audio_name = os.listdir(temp_folder_path)[0]
temp_path = temp_folder_path + "/" + audio_name
audio_path = audio_folder_path + "/" + audio_name
shutil.move(temp_path, audio_path)

# 创建Markdown文件并写入基本信息
text_path = result_folder_path + "/" + audio_name + ".md"
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

# 加载Whisper模型
model_name = "large-v3"  # 可选：large-v3, large, medium, small, base, tiny
model_name = "medium"    # 当前使用medium模型（平衡速度和准确性）
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
text = re.sub(",", "，", text)
text = re.sub(r"\?", "？", text)

# 将转录文本追加到Markdown文件
with open(text_path, "a", encoding="utf-8") as f:
    f.write(text)
print(f"结果已保存到: {text_path}")
