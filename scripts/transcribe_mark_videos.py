#!/usr/bin/env python3
"""
专门转录马克的技术工作坊视频的脚本
"""

import os
import sys
import whisper
import torch
from pathlib import Path
import json
from datetime import datetime

def transcribe_videos():
    # 设置路径
    video_dir = Path("storage/video/1815948385")
    output_dir = Path("storage/results/mark_transcripts")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取所有视频文件
    video_files = list(video_dir.glob("*.mp4"))
    print(f"📹 找到 {len(video_files)} 个视频文件")

    # 检查GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🖥️  使用设备: {device}")

    # 加载模型
    print("🔄 加载Whisper模型 (base)...")
    model = whisper.load_model("base", device=device)

    # 转录结果汇总
    results = {}

    for idx, video_file in enumerate(video_files, 1):
        print(f"\n[{idx}/{len(video_files)}] 🎙️ 转录: {video_file.name}")

        # 生成输出文件名
        output_file = output_dir / f"{video_file.stem}.txt"

        # 如果已存在，跳过
        if output_file.exists():
            print(f"⏭️  已存在，跳过")
            with open(output_file, 'r', encoding='utf-8') as f:
                results[video_file.name] = f.read()
            continue

        try:
            # 转录
            print("   转录中...")
            result = model.transcribe(str(video_file), language='zh')

            # 保存结果
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"视频: {video_file.name}\n")
                f.write("="*60 + "\n\n")
                f.write(result['text'])

            results[video_file.name] = result['text']
            print(f"   ✅ 完成，保存到: {output_file}")

        except Exception as e:
            print(f"   ❌ 错误: {e}")
            results[video_file.name] = f"转录失败: {e}"

    # 保存汇总结果
    summary_file = output_dir / "summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n📊 转录完成！")
    print(f"   结果保存在: {output_dir}")
    print(f"   汇总文件: {summary_file}")

    return results

if __name__ == "__main__":
    transcribe_videos()