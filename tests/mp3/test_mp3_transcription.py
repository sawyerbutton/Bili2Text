#!/usr/bin/env python3
"""测试MP3文件转录"""
import os
import sys
import glob
import time

# 获取前3个MP3文件进行测试
mp3_files = sorted(glob.glob("./audio/mp3/*.mp3"))[:3]

print("="*60)
print("WhisperX MP3转录测试")
print("="*60)
print(f"找到 {len(mp3_files)} 个测试文件:")
for i, f in enumerate(mp3_files, 1):
    print(f"{i}. {os.path.basename(f)}")

print("\n开始转录测试...")

# 创建输出目录
output_dir = "./transcripts_whisperx_mp3_test"
os.makedirs(output_dir, exist_ok=True)

# 逐个文件转录
for i, mp3_file in enumerate(mp3_files, 1):
    print(f"\n[{i}/{len(mp3_files)}] 转录: {os.path.basename(mp3_file)}")
    
    cmd = [
        sys.executable,
        "legacy/transcribe_audio_whisperx_final.py",
        "--audio-dir", os.path.dirname(mp3_file),
        "--output-dir", output_dir,
        "--model", "tiny",
        "--batch-size", "4"
    ]
    
    # 只处理当前文件
    # 创建临时目录
    temp_dir = f"./temp_audio_{i}"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 复制文件到临时目录
    import shutil
    temp_file = os.path.join(temp_dir, os.path.basename(mp3_file))
    shutil.copy2(mp3_file, temp_file)
    
    # 更新命令
    cmd[4] = temp_dir  # 更新audio-dir参数
    
    # 执行转录
    import subprocess
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start_time
    
    if result.returncode == 0:
        print(f"✓ 成功！用时: {elapsed:.1f}秒")
        # 查找输出文件
        output_files = glob.glob(f"{output_dir}/*whisperx.txt")
        if output_files:
            latest_file = max(output_files, key=os.path.getctime)
            print(f"  输出文件: {os.path.basename(latest_file)}")
            
            # 显示部分结果
            with open(latest_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 找到纯文本版本
                for j, line in enumerate(lines):
                    if "纯文本版本" in line:
                        print("  内容预览:")
                        text_start = j + 3
                        if text_start < len(lines):
                            preview = lines[text_start].strip()[:100]
                            if len(lines[text_start].strip()) > 100:
                                preview += "..."
                            print(f"  {preview}")
                        break
    else:
        print(f"✗ 失败")
        if result.stderr:
            print(f"  错误: {result.stderr[:200]}")
    
    # 清理临时目录
    shutil.rmtree(temp_dir, ignore_errors=True)

print("\n" + "="*60)
print("测试完成！")
print(f"输出目录: {os.path.abspath(output_dir)}")

# 统计结果
output_files = glob.glob(f"{output_dir}/*whisperx.txt")
print(f"生成了 {len(output_files)} 个转录文件")