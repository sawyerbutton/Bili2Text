"""
Bili2Text - 音频下载与转录工具
============================

功能：下载B站视频音频并使用Whisper进行转录
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main(args):
    """音频下载和转录的主函数"""
    video_url = args.url
    model_name = args.model
    output_dir = Path(args.output_dir)
    
    print("=" * 50)
    print("Bili2Text - 音频下载与转录工具")
    print("=" * 50)
    print(f"视频URL: {video_url}")
    print(f"Whisper模型: {model_name}")
    print(f"输出目录: {output_dir}")
    print("=" * 50)
    
    # 创建必要的目录
    temp_dir = Path("./storage/temp")
    audio_dir = Path("./storage/audio")
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. 下载音频
        print("\n[1/3] 正在下载音频...")
        start_time = time.time()
        
        # 异步下载音频
        audio_path = asyncio.run(download_audio(video_url, temp_dir, audio_dir))
        
        download_time = time.time() - start_time
        print(f"音频下载完成，耗时 {download_time:.1f} 秒")
        print(f"音频文件: {audio_path}")
        
        # 2. 加载Whisper模型
        print(f"\n[2/3] 正在加载Whisper模型 ({model_name})...")
        model_start = time.time()
        
        import torch
        import whisper
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"使用设备: {device}")
        
        # 设置模型缓存目录
        cache_dir = Path.home() / ".cache" / "whisper"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 尝试加载模型，如果失败则使用更小的模型
        try:
            model = whisper.load_model(
                name=model_name,
                device=device,
                download_root=str(cache_dir)
            )
        except Exception as e:
            if "SHA256 checksum does not match" in str(e):
                print(f"\n⚠️ {model_name}模型文件损坏，尝试使用tiny模型...")
                # 清理损坏的模型文件
                model_file = cache_dir / f"{model_name}.pt"
                if model_file.exists():
                    model_file.unlink()
                # 使用tiny模型
                model_name = "tiny"
                model = whisper.load_model(
                    name=model_name,
                    device=device,
                    download_root=str(cache_dir)
                )
                print(f"已切换到{model_name}模型")
            else:
                raise
        
        model_time = time.time() - model_start
        print(f"模型加载完成，耗时 {model_time:.1f} 秒")
        
        # 3. 执行转录
        print(f"\n[3/3] 正在转录音频...")
        transcribe_start = time.time()
        
        result = model.transcribe(
            str(audio_path),
            verbose=True,
            language="zh",
            initial_prompt="以下是普通话的句子。"
        )
        
        transcribe_time = time.time() - transcribe_start
        print(f"\n转录完成，耗时 {transcribe_time:.1f} 秒")
        
        # 4. 保存结果
        text = result["text"]
        
        # 标点符号标准化
        text = text.replace(",", "，")
        text = text.replace("?", "？")
        text = text.replace("!", "！")
        text = text.replace(";", "；")
        text = text.replace(":", "：")
        
        # 生成输出文件名
        audio_name = Path(audio_path).stem
        output_file = output_dir / f"{audio_name}_转录结果.txt"
        
        # 保存转录结果
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"视频URL: {video_url}\n")
            f.write(f"转录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"使用模型: {model_name}\n")
            f.write(f"转录耗时: {transcribe_time:.1f} 秒\n")
            f.write("=" * 50 + "\n\n")
            f.write(text)
        
        print(f"\n转录结果已保存到: {output_file}")
        
        # 输出摘要
        total_time = time.time() - start_time
        print("\n" + "=" * 50)
        print("任务完成！")
        print(f"总耗时: {total_time:.1f} 秒")
        print(f"  - 下载: {download_time:.1f} 秒")
        print(f"  - 加载模型: {model_time:.1f} 秒")
        print(f"  - 转录: {transcribe_time:.1f} 秒")
        print("=" * 50)
        
        return 0
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


async def download_audio(url, temp_dir, audio_dir):
    """下载视频音频"""
    from bilix.sites.bilibili import DownloaderBilibili
    
    # 使用bilix下载音频
    async with DownloaderBilibili() as d:
        await d.get_video(url, path=str(temp_dir), only_audio=True)
    
    # 移动音频文件到指定目录
    audio_files = list(temp_dir.glob("*.mp4"))
    if not audio_files:
        audio_files = list(temp_dir.glob("*.m4a"))
    if not audio_files:
        audio_files = list(temp_dir.glob("*.aac"))
    if not audio_files:
        audio_files = list(temp_dir.glob("*.mp3"))
    
    if not audio_files:
        # 列出所有文件
        all_files = list(temp_dir.glob("*"))
        print(f"临时目录中的文件: {[f.name for f in all_files]}")
        raise Exception("未找到下载的音频文件")
    
    audio_file = audio_files[0]
    target_path = audio_dir / audio_file.name
    
    # 移动文件
    import shutil
    shutil.move(str(audio_file), str(target_path))
    
    return target_path


if __name__ == '__main__':
    # 用于测试
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--model', default='tiny')
    parser.add_argument('--output-dir', default='./storage/results')
    args = parser.parse_args()
    main(args)