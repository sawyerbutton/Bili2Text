#!/usr/bin/env python3
"""
批量转写storage/video目录下所有视频文件到逐字稿
使用GPU加速的Whisper模型
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
    video_files = []
    for ext in ['*.mp4', '*.mkv', '*.avi', '*.mov']:
        video_files.extend(video_dir.rglob(ext))
    
    total_files = len(video_files)
    print(f"🎬 发现 {total_files} 个视频文件待转写")
    print(f"📁 输出目录: {output_dir}")
    print("=" * 60)
    
    # 开始批量转写
    start_time = time.time()
    success_count = 0
    failed_files = []
    
    for idx, video_file in enumerate(video_files, 1):
        # 构建输出文件路径
        relative_path = video_file.relative_to(video_dir)
        output_file = output_dir / relative_path.with_suffix('.txt')
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 检查是否已经转写过
        if output_file.exists():
            print(f"[{idx}/{total_files}] ⏭️  跳过已存在: {relative_path}")
            success_count += 1
            continue
        
        print(f"[{idx}/{total_files}] 🔄 正在转写: {relative_path}")
        print(f"              输出到: {output_file}")
        
        # 使用conda环境运行GPU转写
        cmd = [
            "conda", "run", "-n", "bili2text-gpu",
            "python", "-m", "cli.main", "gpu-transcribe",
            "--input", str(video_file),
            "--output", str(output_file.parent),
            "--model", "medium",  # 使用medium模型，平衡速度和质量
            "--device", "cuda",
            "--compute-type", "float32"  # 使用float32避免精度问题
        ]
        
        try:
            # 执行转写
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                print(f"              ✅ 转写成功")
                success_count += 1
                
                # 显示部分转写结果
                if output_file.exists():
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()[:200]
                        if content:
                            print(f"              预览: {content[:100]}...")
            else:
                print(f"              ❌ 转写失败: {result.stderr}")
                failed_files.append(str(relative_path))
                
        except subprocess.TimeoutExpired:
            print(f"              ⚠️  转写超时")
            failed_files.append(str(relative_path))
        except Exception as e:
            print(f"              ❌ 发生错误: {e}")
            failed_files.append(str(relative_path))
        
        # 显示进度
        elapsed = time.time() - start_time
        avg_time = elapsed / idx
        remaining = (total_files - idx) * avg_time
        print(f"              进度: {idx}/{total_files} | 已用时: {elapsed/60:.1f}分钟 | 预计剩余: {remaining/60:.1f}分钟")
        print("-" * 60)
    
    # 总结
    total_time = time.time() - start_time
    print("=" * 60)
    print(f"📊 转写完成统计:")
    print(f"   总计: {total_files} 个视频")
    print(f"   成功: {success_count} 个")
    print(f"   失败: {len(failed_files)} 个")
    print(f"   总耗时: {total_time/60:.1f} 分钟")
    print(f"   平均: {total_time/total_files:.1f} 秒/视频")
    
    if failed_files:
        print(f"\n❌ 失败文件列表:")
        for f in failed_files:
            print(f"   - {f}")
    
    print(f"\n✅ 所有转写结果已保存到: {output_dir}")
    
    # 生成索引文件
    index_file = output_dir / "index.txt"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(f"批量转写完成报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"=" * 60 + "\n\n")
        f.write(f"统计信息:\n")
        f.write(f"  总文件数: {total_files}\n")
        f.write(f"  成功转写: {success_count}\n")
        f.write(f"  失败数量: {len(failed_files)}\n")
        f.write(f"  总耗时: {total_time/60:.1f} 分钟\n\n")
        
        f.write(f"成功转写文件列表:\n")
        for txt_file in sorted(output_dir.rglob("*.txt")):
            if txt_file.name != "index.txt":
                f.write(f"  - {txt_file.relative_to(output_dir)}\n")
    
    print(f"📄 索引文件已生成: {index_file}")

if __name__ == "__main__":
    main()