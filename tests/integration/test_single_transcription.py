#!/usr/bin/env python3
"""测试单个文件转录"""
import os
import sys
import subprocess

# 选择一个测试文件
test_audio = "./audio/aac/你妹的，540也排队.aac"
output_dir = "./test_transcripts"

# 创建输出目录
os.makedirs(output_dir, exist_ok=True)

print("=== 测试单个音频文件转录 ===")
print(f"音频文件: {test_audio}")
print(f"输出目录: {output_dir}")
print("使用模型: tiny (最快)")
print("")

# 运行转录
cmd = [
    sys.executable,
    "legacy/transcribe_audio_whisper.py",
    "--model", "tiny",
    "--audio-dir", os.path.dirname(test_audio),
    "--output-dir", output_dir,
    "--language", "zh"
]

print("开始转录...")
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    print("\n✓ 转录成功!")
    # 查找输出文件
    audio_name = os.path.splitext(os.path.basename(test_audio))[0]
    output_file = os.path.join(output_dir, f"{audio_name}_whisper.txt")
    
    if os.path.exists(output_file):
        print(f"\n转录结果已保存到: {output_file}")
        print("\n转录内容预览:")
        print("-" * 50)
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:20]  # 显示前20行
            for line in lines:
                print(line.rstrip())
        print("-" * 50)
else:
    print("\n✗ 转录失败")
    print("错误信息:")
    print(result.stderr)