#!/usr/bin/env python3
"""简单测试WhisperX转录单个文件"""
import os
import warnings
warnings.filterwarnings("ignore")

# 设置环境变量
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE' 
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import whisperx

# 测试文件
audio_file = "./audio/aac/你妹的，540也排队.aac"

print("加载模型...")
# 使用最简单的参数
model = whisperx.load_model("tiny", "cpu")

print("加载音频...")
audio = whisperx.load_audio(audio_file)

print("开始转录...")
result = model.transcribe(audio, batch_size=16)

print("\n转录结果:")
for segment in result["segments"]:
    print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")

# 保存结果
output_file = "test_whisperx_output.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("WhisperX转录结果\n")
    f.write("="*50 + "\n\n")
    for segment in result["segments"]:
        f.write(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}\n")

print(f"\n结果已保存到: {output_file}")