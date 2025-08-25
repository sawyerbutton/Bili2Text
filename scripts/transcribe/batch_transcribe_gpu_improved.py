#!/usr/bin/env python3
"""
改进版批量转写脚本
处理文件名特殊字符问题，使用GPU加速转写所有视频
"""

import os
import sys
import subprocess
from pathlib import Path
import time
from datetime import datetime
import shutil
import hashlib

def safe_filename(filename):
    """生成安全的文件名"""
    # 移除或替换特殊字符
    safe = filename.replace('"', '').replace("'", '').replace('【', '[').replace('】', ']')
    safe = safe.replace('（', '(').replace('）', ')').replace('：', '-')
    return safe

def get_temp_filename(filepath):
    """生成临时文件名"""
    # 使用MD5哈希生成唯一的临时文件名
    hash_obj = hashlib.md5(str(filepath).encode())
    temp_name = f"temp_{hash_obj.hexdigest()[:8]}.mp4"
    return temp_name

def main():
    # 设置路径
    video_dir = Path("storage/video")
    output_dir = Path("storage/results/gpu_transcripts")
    temp_dir = Path("storage/temp/transcribe")
    
    # 创建必要的目录
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # 收集所有视频文件
    video_files = []
    for ext in ['*.mp4', '*.mkv', '*.avi', '*.mov']:
        video_files.extend(video_dir.rglob(ext))
    
    total_files = len(video_files)
    print(f"🎬 发现 {total_files} 个视频文件待转写")
    print(f"📁 输出目录: {output_dir}")
    print(f"🔧 使用GPU加速转写")
    print("=" * 60)
    
    # 开始批量转写
    start_time = time.time()
    success_count = 0
    failed_files = []
    
    for idx, video_file in enumerate(video_files, 1):
        # 构建输出文件路径
        relative_path = video_file.relative_to(video_dir)
        
        # 处理文件名，生成安全的输出文件名
        safe_name = safe_filename(relative_path.stem)
        output_file = output_dir / relative_path.parent / f"{safe_name}.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 检查是否已经转写过
        if output_file.exists():
            print(f"[{idx}/{total_files}] ⏭️  跳过已存在: {relative_path}")
            success_count += 1
            continue
        
        print(f"[{idx}/{total_files}] 🔄 正在转写: {relative_path}")
        
        # 创建临时文件（避免特殊字符问题）
        temp_filename = get_temp_filename(video_file)
        temp_file = temp_dir / temp_filename
        
        try:
            # 复制到临时文件
            print(f"              准备临时文件...")
            shutil.copy2(video_file, temp_file)
            
            # 使用conda环境运行GPU转写
            cmd = [
                "conda", "run", "-n", "bili2text-gpu",
                "python", "-m", "cli.main", "gpu-transcribe",
                "--input", str(temp_file),
                "--output", str(output_file.parent),
                "--model", "base",  # 使用base模型，速度更快
                "--device", "cuda",
                "--compute-type", "float32"
            ]
            
            # 执行转写
            print(f"              开始GPU转写...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                # 查找生成的文件并重命名
                generated_files = list(output_file.parent.glob(f"{temp_filename.replace('.mp4', '')}*.txt"))
                if generated_files:
                    # 移动生成的文件到目标位置
                    shutil.move(str(generated_files[0]), str(output_file))
                    print(f"              ✅ 转写成功")
                    success_count += 1
                    
                    # 显示部分转写结果
                    with open(output_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        # 查找实际内容开始的位置（跳过头部信息）
                        content_start = 0
                        for i, line in enumerate(lines):
                            if '=' * 10 in line:
                                content_start = i + 1
                                break
                        if content_start < len(lines):
                            preview = ''.join(lines[content_start:content_start+2]).strip()
                            if preview:
                                print(f"              预览: {preview[:100]}...")
                else:
                    print(f"              ⚠️  未找到输出文件")
                    failed_files.append(str(relative_path))
            else:
                error_msg = result.stderr.split('\n')[-2] if result.stderr else "Unknown error"
                print(f"              ❌ 转写失败: {error_msg}")
                failed_files.append(str(relative_path))
                
        except subprocess.TimeoutExpired:
            print(f"              ⚠️  转写超时")
            failed_files.append(str(relative_path))
        except Exception as e:
            print(f"              ❌ 发生错误: {e}")
            failed_files.append(str(relative_path))
        finally:
            # 清理临时文件
            if temp_file.exists():
                temp_file.unlink()
        
        # 显示进度
        elapsed = time.time() - start_time
        avg_time = elapsed / idx
        remaining = (total_files - idx) * avg_time
        print(f"              进度: {idx}/{total_files} | 已用时: {elapsed/60:.1f}分钟 | 预计剩余: {remaining/60:.1f}分钟")
        print("-" * 60)
        
        # 每处理10个文件暂停一下，避免GPU过热
        if idx % 10 == 0:
            print("💤 暂停10秒，让GPU休息一下...")
            time.sleep(10)
    
    # 清理临时目录
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    # 总结
    total_time = time.time() - start_time
    print("=" * 60)
    print(f"📊 转写完成统计:")
    print(f"   总计: {total_files} 个视频")
    print(f"   成功: {success_count} 个")
    print(f"   失败: {len(failed_files)} 个")
    print(f"   总耗时: {total_time/60:.1f} 分钟")
    if total_files > 0:
        print(f"   平均: {total_time/total_files:.1f} 秒/视频")
    
    if failed_files:
        print(f"\n❌ 失败文件列表:")
        for f in failed_files[:10]:  # 只显示前10个
            print(f"   - {f}")
        if len(failed_files) > 10:
            print(f"   ... 还有 {len(failed_files)-10} 个文件")
    
    print(f"\n✅ 所有转写结果已保存到: {output_dir}")
    
    # 生成索引文件
    index_file = output_dir / "index.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(f"# 批量转写完成报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 统计信息\n\n")
        f.write(f"- 总文件数: {total_files}\n")
        f.write(f"- 成功转写: {success_count}\n")
        f.write(f"- 失败数量: {len(failed_files)}\n")
        f.write(f"- 总耗时: {total_time/60:.1f} 分钟\n\n")
        
        f.write(f"## 成功转写文件列表\n\n")
        for txt_file in sorted(output_dir.rglob("*.txt")):
            if txt_file.name not in ["index.txt", "index.md"]:
                rel_path = txt_file.relative_to(output_dir)
                f.write(f"- [{rel_path}]({rel_path})\n")
        
        if failed_files:
            f.write(f"\n## 失败文件列表\n\n")
            for f_path in failed_files:
                f.write(f"- {f_path}\n")
    
    print(f"📄 索引文件已生成: {index_file}")

if __name__ == "__main__":
    main()