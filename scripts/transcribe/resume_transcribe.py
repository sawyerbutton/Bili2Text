#!/usr/bin/env python3
"""
断点续传转写脚本 - 从上次中断的地方继续转写
"""

import os
import sys
import subprocess
from pathlib import Path
import time
from datetime import datetime

def main():
    # 设置路径
    video_dir = Path("storage/video")
    output_dir = Path("storage/results/gpu_transcripts")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 收集所有视频文件
    print("📋 正在扫描视频文件...")
    video_files = []
    for ext in ['*.mp4', '*.mkv', '*.avi', '*.mov']:
        video_files.extend(video_dir.rglob(ext))
    
    total_files = len(video_files)
    print(f"📁 总共找到 {total_files} 个视频文件")
    
    # 检查已完成的文件
    print("🔍 检查已完成的转写...")
    completed_count = 0
    pending_files = []
    
    for video_file in video_files:
        # 构建对应的输出文件路径
        relative_path = video_file.relative_to(video_dir)
        # 简化文件名，移除特殊字符
        safe_name = str(relative_path.stem).replace('"', '').replace("'", '')
        safe_name = safe_name.replace('【', '[').replace('】', ']')
        output_file = output_dir / relative_path.parent / f"{safe_name}.txt"
        
        if output_file.exists():
            completed_count += 1
        else:
            pending_files.append(video_file)
    
    print(f"✅ 已完成: {completed_count} 个")
    print(f"⏳ 待处理: {len(pending_files)} 个")
    
    if len(pending_files) == 0:
        print("🎉 所有文件都已转写完成！")
        return
    
    print("=" * 60)
    print(f"🚀 开始转写剩余的 {len(pending_files)} 个文件...")
    print("=" * 60)
    
    # 开始转写剩余文件
    start_time = time.time()
    success_count = 0
    failed_files = []
    
    for idx, video_file in enumerate(pending_files, 1):
        relative_path = video_file.relative_to(video_dir)
        print(f"\n[{idx}/{len(pending_files)}] 处理: {relative_path}")
        
        # 使用原始文件直接转写（避免复制）
        # 构建输出路径
        safe_name = str(relative_path.stem).replace('"', '').replace("'", '')
        safe_name = safe_name.replace('【', '[').replace('】', ']')
        output_file = output_dir / relative_path.parent / f"{safe_name}.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 直接调用GPU转写
        cmd = [
            "conda", "run", "-n", "bili2text-gpu",
            "python", "-c",
            f"""
import whisper
import torch
import sys
from pathlib import Path
from datetime import datetime

# 设置文件路径
video_path = r'{video_file}'
output_path = r'{output_file}'

print(f"Loading model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base", device=device)

print(f"Transcribing...")
result = model.transcribe(video_path, language="zh")

print(f"Saving result...")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(f"源文件: {{Path(video_path).name}}\\n")
    f.write(f"转录时间: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}\\n")
    f.write("=" * 50 + "\\n\\n")
    f.write(result["text"])

print(f"✅ Success!")
"""
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0 and output_file.exists():
                print(f"✅ 转写成功")
                success_count += 1
            else:
                print(f"❌ 转写失败")
                if result.stderr:
                    print(f"错误: {result.stderr[:200]}")
                failed_files.append(str(relative_path))
                
        except subprocess.TimeoutExpired:
            print(f"⚠️ 超时")
            failed_files.append(str(relative_path))
        except Exception as e:
            print(f"❌ 错误: {e}")
            failed_files.append(str(relative_path))
        
        # 显示进度
        elapsed = time.time() - start_time
        avg_time = elapsed / idx if idx > 0 else 0
        remaining = (len(pending_files) - idx) * avg_time
        total_progress = ((completed_count + idx) / total_files) * 100
        
        print(f"进度: {idx}/{len(pending_files)} | 总进度: {total_progress:.1f}%")
        print(f"已用时: {elapsed/60:.1f}分钟 | 预计剩余: {remaining/60:.1f}分钟")
        
        # 每5个文件休息一下
        if idx % 5 == 0:
            print("💤 休息5秒...")
            time.sleep(5)
    
    # 总结
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"📊 本次转写完成统计:")
    print(f"   成功: {success_count} 个")
    print(f"   失败: {len(failed_files)} 个")
    print(f"   耗时: {total_time/60:.1f} 分钟")
    
    final_completed = completed_count + success_count
    print(f"\n📈 总体进度: {final_completed}/{total_files} ({final_completed*100/total_files:.1f}%)")
    
    if failed_files:
        print(f"\n❌ 失败文件:")
        for f in failed_files[:5]:
            print(f"   - {f}")
        if len(failed_files) > 5:
            print(f"   ... 还有 {len(failed_files)-5} 个")

if __name__ == "__main__":
    main()