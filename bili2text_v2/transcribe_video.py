#!/usr/bin/env python3
"""
视频文件转录脚本
支持直接转录视频文件（如MP4），自动提取音频并转录
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# 检查whisper是否安装
try:
    import whisper
    import torch
except ImportError:
    print("请安装依赖: pip install openai-whisper torch")
    sys.exit(1)


def transcribe_video(video_path: str, model_name: str = "medium", output_dir: str = "./result", language: str = None):
    """
    转录视频文件
    
    Args:
        video_path: 视频文件路径
        model_name: Whisper模型名称
        output_dir: 输出目录
        language: 指定语言代码（如'en'、'zh'等），None表示自动检测
    """
    # 检查视频文件是否存在
    if not os.path.exists(video_path):
        print(f"错误：视频文件不存在: {video_path}")
        return False
    
    video_path = Path(video_path)
    video_name = video_path.stem
    
    print(f"=== 视频转录工具 ===")
    print(f"视频文件: {video_path}")
    print(f"使用模型: {model_name}")
    print(f"使用设备: {'cuda' if torch.cuda.is_available() else 'cpu'}")
    print(f"语言设置: {'自动检测' if language is None else language}")
    
    try:
        # 加载Whisper模型
        print(f"\n正在加载Whisper模型: {model_name}")
        print("首次加载需要下载模型，请耐心等待...")
        start_time = datetime.now()
        
        model = whisper.load_model(
            name=model_name,
            device="cuda" if torch.cuda.is_available() else "cpu",
            download_root="./.cache/whisper"
        )
        
        load_time = (datetime.now() - start_time).seconds
        print(f"模型加载完成，耗时 {load_time} 秒")
        
        # 直接转录视频文件（Whisper支持直接处理视频）
        print(f"\n开始转录视频: {video_name}")
        print("这可能需要几分钟时间，请耐心等待...")
        
        # 准备转录参数
        transcribe_params = {
            "audio": str(video_path),
            "verbose": True
        }
        
        # 根据语言设置调整参数
        if language:
            transcribe_params["language"] = language
            # 针对不同语言设置不同的初始提示
            if language == 'zh':
                transcribe_params["initial_prompt"] = '简体中文,加上标点'
            elif language == 'en':
                transcribe_params["initial_prompt"] = 'English transcription with punctuation.'
        else:
            # 不指定语言，让Whisper自动检测
            print("将自动检测音频语言...")
        
        transcribe_start = datetime.now()
        result = model.transcribe(**transcribe_params)
        
        transcribe_time = (datetime.now() - transcribe_start).seconds
        print(f"\n转录完成，耗时 {transcribe_time} 秒")
        
        # 显示检测到的语言
        if 'language' in result:
            detected_lang = result.get('language', 'unknown')
            print(f"检测到的语言: {detected_lang}")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存纯文本结果
        text_output_path = os.path.join(output_dir, f"{video_name}_transcript.txt")
        with open(text_output_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        print(f"\n转录文本已保存到: {text_output_path}")
        
        # 生成Markdown格式结果
        markdown_content = f"""# {video_name}

## 视频信息
- 文件: {video_path}
- 转录时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 使用模型: {model_name}
- 转录耗时: {transcribe_time} 秒

## 转录内容

{result["text"]}
"""
        
        markdown_output_path = os.path.join(output_dir, f"{video_name}_transcript.md")
        with open(markdown_output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"Markdown格式已保存到: {markdown_output_path}")
        
        # 显示结果预览
        print("\n转录结果预览:")
        print("-" * 50)
        preview_text = result["text"][:300] + "..." if len(result["text"]) > 300 else result["text"]
        print(preview_text)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n转录失败: {e}")
        print("\n可能的解决方案:")
        print("1. 确保已安装ffmpeg（Whisper需要它来处理视频）")
        print("   macOS: brew install ffmpeg")
        print("   Ubuntu: sudo apt install ffmpeg")
        print("2. 确保已安装依赖: pip install openai-whisper torch")
        print("3. 检查视频文件是否损坏")
        print("4. 尝试使用更小的模型: --model tiny")
        return False


def main():
    parser = argparse.ArgumentParser(description="转录视频文件")
    parser.add_argument("video_path", help="视频文件路径")
    parser.add_argument("--model", default="medium", 
                       choices=["tiny", "base", "small", "medium", "large", "large-v3"],
                       help="Whisper模型名称 (默认: medium)")
    parser.add_argument("--output", default="./result", help="输出目录 (默认: ./result)")
    parser.add_argument("--language", default=None, 
                       help="指定语言代码，如: en, zh, ja, ko等 (默认: 自动检测)")
    
    args = parser.parse_args()
    
    success = transcribe_video(args.video_path, args.model, args.output, args.language)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n运行失败: {e}")
        sys.exit(1)