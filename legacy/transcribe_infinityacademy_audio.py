"""
Bili2Text - 音频转录工具 (InfinityAcademy专用版)
===============================================

文件目的：
    扫描音频文件夹，使用Whisper模型对音频文件进行语音转录，
    生成包含视频信息和转录文本的格式化Markdown文件。

主要功能：
    1. 扫描音频文件夹，找到所有音频文件
    2. 读取视频信息文件，获取对应的视频信息
    3. 使用Whisper进行语音转录
    4. 生成格式化的Markdown输出文件
    5. 避免重复处理已处理过的音频文件

依赖库：
    - whisper: OpenAI语音转录模型
    - torch: PyTorch深度学习框架

作者：Auto Generated
创建时间：2024
更新时间：2024 (兼容bilibili-api-python 17.3.0)
"""

import os
import re
from datetime import datetime, timezone

import torch
import whisper


def load_video_info(info_file="video_info_infinityacademy.txt"):
    """
    加载视频信息文件
    
    Args:
        info_file (str): 视频信息文件路径
        
    Returns:
        dict: 音频文件名到视频信息的映射字典
    """
    video_info_dict = {}
    
    try:
        with open(info_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        bvid, title, desc, audio_filename = parts[0], parts[1], parts[2], parts[3]
                        video_info_dict[audio_filename] = {
                            "bvid": bvid,
                            "title": title,
                            "desc": desc
                        }
    except FileNotFoundError:
        print(f"视频信息文件 {info_file} 不存在")
        return {}
    
    return video_info_dict


def load_transcribed_files(file_path="transcribed_infinityacademy.txt"):
    """
    加载已转录的音频文件列表
    
    Args:
        file_path (str): 已转录文件列表文件路径
        
    Returns:
        set: 已转录的音频文件名集合
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f.readlines())
    except FileNotFoundError:
        return set()


def save_transcribed_file(audio_filename, file_path="transcribed_infinityacademy.txt"):
    """
    保存已转录的音频文件名
    
    Args:
        audio_filename (str): 音频文件名
        file_path (str): 保存文件路径
    """
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(audio_filename + "\n")


def create_markdown_file(bvid, title, desc, audio_filename, result_folder_path):
    """
    创建Markdown文件并写入基本信息
    
    Args:
        bvid (str): 视频ID
        title (str): 视频标题
        desc (str): 视频描述
        audio_filename (str): 音频文件名
        result_folder_path (str): 结果文件夹路径
        
    Returns:
        str: Markdown文件路径
    """
    # 使用音频文件名作为Markdown文件名
    md_filename = os.path.splitext(audio_filename)[0] + ".md"
    text_path = os.path.join(result_folder_path, md_filename)
    
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


def get_audio_files(audio_folder_path):
    """
    获取音频文件夹中的所有音频文件
    
    Args:
        audio_folder_path (str): 音频文件夹路径
        
    Returns:
        list: 音频文件列表
    """
    audio_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.wma']
    audio_files = []
    
    if not os.path.exists(audio_folder_path):
        print(f"音频文件夹 {audio_folder_path} 不存在")
        return audio_files
    
    for file in os.listdir(audio_folder_path):
        if any(file.lower().endswith(ext) for ext in audio_extensions):
            audio_files.append(file)
    
    return audio_files


def main():
    """
    主函数：转录音频文件并生成Markdown
    """
    # 准备工作环境
    print("准备工作环境......")
    audio_folder_path = "./audio"      # 音频文件存储目录
    result_folder_path = "./result"    # 结果文件目录
    
    # 创建必要的目录
    if not os.path.exists(result_folder_path):
        os.makedirs(result_folder_path)
    
    # 获取音频文件列表
    audio_files = get_audio_files(audio_folder_path)
    
    if not audio_files:
        print("没有找到任何音频文件，程序退出")
        return
    
    print(f"找到 {len(audio_files)} 个音频文件")
    
    # 加载视频信息
    video_info_dict = load_video_info()
    
    if not video_info_dict:
        print("没有找到视频信息文件，程序退出")
        return
    
    # 加载已转录的文件列表
    transcribed_files = load_transcribed_files()
    
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
    
    # 处理每个音频文件
    total_files = len(audio_files)
    transcribed_count = 0
    
    for i, audio_filename in enumerate(audio_files, 1):
        print(f"\n转录进度: {i}/{total_files}")
        print(f"音频文件: {audio_filename}")
        
        # 检查是否已转录过该文件
        if audio_filename in transcribed_files:
            print(f"音频文件 {audio_filename} 已经转录过，跳过")
            continue
        
        # 检查是否有对应的视频信息
        if audio_filename not in video_info_dict:
            print(f"音频文件 {audio_filename} 没有对应的视频信息，跳过")
            continue
        
        video_info = video_info_dict[audio_filename]
        bvid = video_info["bvid"]
        title = video_info["title"]
        desc = video_info["desc"]
        
        print(f"视频ID: {bvid}")
        print(f"标题: {title}")
        print(f"描述: {desc}")
        
        try:
            # 音频文件路径
            audio_path = os.path.join(audio_folder_path, audio_filename)
            
            # 创建Markdown文件
            text_path = create_markdown_file(bvid, title, desc, audio_filename, result_folder_path)
            
            # 执行语音转录
            transcribed_text = transcribe_audio(audio_path, model)
            
            # 将转录文本追加到Markdown文件
            with open(text_path, "a", encoding="utf-8") as f:
                f.write(transcribed_text)
            
            print(f"结果已保存到: {text_path}")
            
            # 记录已转录的文件
            save_transcribed_file(audio_filename)
            transcribed_files.add(audio_filename)
            transcribed_count += 1
            
        except Exception as e:
            print(f"转录音频文件 {audio_filename} 时出错: {e}")
            continue
    
    print(f"\n转录完成！共转录 {transcribed_count} 个新音频文件")


if __name__ == "__main__":
    main() 