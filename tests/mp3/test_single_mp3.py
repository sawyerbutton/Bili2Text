#!/usr/bin/env python3
"""直接测试单个MP3文件"""
import os
import warnings
warnings.filterwarnings("ignore")

# 设置环境变量
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import whisperx
import torch

# 测试文件
mp3_file = "./audio/mp3/你妹的，540也排队.mp3"

print("="*60)
print("WhisperX MP3转录测试")
print("="*60)
print(f"测试文件: {mp3_file}")

# 设置
device = "cpu"
compute_type = "int8"
model_size = "tiny"

print(f"\n配置:")
print(f"- 设备: {device}")
print(f"- 计算类型: {compute_type}")
print(f"- 模型: {model_size}")

try:
    # 加载模型
    print("\n1. 加载模型...")
    model = whisperx.load_model(model_size, device, compute_type=compute_type, language="zh")
    print("✓ 模型加载成功")
    
    # 加载音频
    print("\n2. 加载音频...")
    audio = whisperx.load_audio(mp3_file)
    duration = len(audio) / 16000
    print(f"✓ 音频加载成功，长度: {duration:.2f}秒")
    
    # 转录
    print("\n3. 开始转录...")
    result = model.transcribe(audio, batch_size=8, language="zh")
    print(f"✓ 转录完成，包含 {len(result['segments'])} 个片段")
    
    # 显示结果
    print("\n4. 转录结果:")
    print("-"*60)
    for i, segment in enumerate(result["segments"][:5]):  # 显示前5个
        text = segment['text'].strip()
        start = segment['start']
        end = segment['end']
        print(f"{i+1}. [{start:.2f}s - {end:.2f}s] {text}")
    
    if len(result["segments"]) > 5:
        print(f"... 还有 {len(result['segments']) - 5} 个片段")
    
    # 保存完整结果
    output_file = "mp3_test_result.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("WhisperX MP3转录测试结果\n")
        f.write(f"文件: {mp3_file}\n")
        f.write("="*60 + "\n\n")
        
        # 带时间戳版本
        for segment in result["segments"]:
            f.write(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text'].strip()}\n")
        
        # 纯文本版本
        f.write("\n" + "="*60 + "\n")
        f.write("纯文本版本:\n")
        f.write("="*60 + "\n\n")
        full_text = " ".join([seg['text'].strip() for seg in result["segments"]])
        f.write(full_text)
    
    print(f"\n✓ 完整结果已保存到: {output_file}")
    print("\n✅ MP3文件转录成功！")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()