#!/usr/bin/env python3
"""最终测试WhisperX转录"""
import os
import warnings
warnings.filterwarnings("ignore")

# 设置环境变量
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE' 
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import whisperx
import torch

# 测试文件
audio_file = "./audio/aac/你妹的，540也排队.aac"

print("WhisperX最终测试")
print("="*50)

# 检测设备
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"
print(f"设备: {device}")
print(f"计算类型: {compute_type}")

print("\n加载模型...")
# 明确指定计算类型
model = whisperx.load_model("tiny", device, compute_type=compute_type)
print("✓ 模型加载成功")

print("\n加载音频...")
audio = whisperx.load_audio(audio_file)
duration = len(audio) / 16000
print(f"✓ 音频加载成功，长度: {duration:.2f}秒")

print("\n开始转录...")
result = model.transcribe(audio, batch_size=16, language="zh")
print("✓ 转录完成")

print("\n转录结果:")
print("-"*50)
for i, segment in enumerate(result["segments"]):
    print(f"{i+1}. [{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text'].strip()}")

# 保存结果
output_file = "whisperx_result.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("WhisperX转录结果\n")
    f.write(f"音频文件: {audio_file}\n")
    f.write(f"模型: tiny\n")
    f.write(f"设备: {device}\n")
    f.write("="*50 + "\n\n")
    
    for segment in result["segments"]:
        f.write(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text'].strip()}\n")
    
    # 添加纯文本版本
    f.write("\n" + "="*50 + "\n")
    f.write("纯文本版本:\n")
    f.write("="*50 + "\n\n")
    full_text = " ".join([seg["text"].strip() for seg in result["segments"]])
    f.write(full_text)

print(f"\n✓ 结果已保存到: {output_file}")
print("\n✅ WhisperX成功运行！")