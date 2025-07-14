#!/usr/bin/env python3
"""批量转录MP3文件"""
import os
import glob
import warnings
warnings.filterwarnings("ignore")

# 设置环境变量
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import whisperx
import torch
from datetime import datetime
import time

# 配置
MP3_DIR = "./audio/mp3"
OUTPUT_DIR = "./transcripts_whisperx_mp3"
MODEL_SIZE = "tiny"  # 使用tiny模型加快速度
BATCH_SIZE = 8

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 获取所有MP3文件
mp3_files = sorted(glob.glob(os.path.join(MP3_DIR, "*.mp3")))

print("="*70)
print("WhisperX批量MP3转录")
print("="*70)
print(f"找到 {len(mp3_files)} 个MP3文件")
print(f"输出目录: {OUTPUT_DIR}")
print(f"模型: {MODEL_SIZE}")
print("="*70)

# 设备配置
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"
print(f"设备: {device}, 计算类型: {compute_type}")

# 加载模型
print("\n加载WhisperX模型...")
model = whisperx.load_model(MODEL_SIZE, device, compute_type=compute_type, language="zh")
print("✓ 模型加载成功")

# 统计
success_count = 0
failed_files = []
start_time = time.time()

# 批量处理
for i, mp3_file in enumerate(mp3_files, 1):
    file_name = os.path.basename(mp3_file)
    print(f"\n[{i}/{len(mp3_files)}] 处理: {file_name}")
    
    try:
        # 加载音频
        audio = whisperx.load_audio(mp3_file)
        duration = len(audio) / 16000
        print(f"  音频长度: {duration:.1f}秒")
        
        # 转录
        print(f"  转录中...")
        file_start = time.time()
        result = model.transcribe(audio, batch_size=BATCH_SIZE, language="zh")
        transcribe_time = time.time() - file_start
        
        segments = result.get("segments", [])
        print(f"  ✓ 转录完成，{len(segments)}个片段，用时{transcribe_time:.1f}秒")
        
        # 保存结果
        output_name = os.path.splitext(file_name)[0]
        output_file = os.path.join(OUTPUT_DIR, f"{output_name}_whisperx.txt")
        
        with open(output_file, "w", encoding="utf-8") as f:
            # 元信息
            f.write("# WhisperX转录结果\n")
            f.write(f"# 音频文件: {file_name}\n")
            f.write(f"# 转录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 音频长度: {duration:.1f}秒\n")
            f.write(f"# 片段数: {len(segments)}\n")
            f.write(f"# 模型: {MODEL_SIZE}\n")
            f.write("\n" + "="*70 + "\n\n")
            
            # 带时间戳的转录
            if segments:
                f.write("## 带时间戳版本\n\n")
                for j, seg in enumerate(segments, 1):
                    start = seg.get('start', 0)
                    end = seg.get('end', 0)
                    text = seg.get('text', '').strip()
                    if text:
                        f.write(f"{j}. [{start:.2f}s - {end:.2f}s] {text}\n")
                
                # 纯文本版本
                f.write("\n" + "="*70 + "\n")
                f.write("## 纯文本版本\n")
                f.write("="*70 + "\n\n")
                full_text = " ".join([seg.get('text', '').strip() for seg in segments])
                f.write(full_text)
            else:
                f.write("[未检测到语音内容]")
        
        print(f"  ✓ 已保存: {output_file}")
        success_count += 1
        
        # 显示预览
        if segments:
            preview_text = segments[0].get('text', '').strip()[:50]
            if len(segments[0].get('text', '').strip()) > 50:
                preview_text += "..."
            print(f"  预览: {preview_text}")
        
    except KeyboardInterrupt:
        print("\n\n用户中断！")
        break
        
    except Exception as e:
        print(f"  ✗ 处理失败: {e}")
        failed_files.append(mp3_file)
        continue
    
    # 定期清理内存
    if i % 5 == 0:
        import gc
        gc.collect()

# 统计结果
total_time = time.time() - start_time
print("\n" + "="*70)
print("转录完成统计")
print("="*70)
print(f"总文件数: {len(mp3_files)}")
print(f"成功: {success_count}")
print(f"失败: {len(failed_files)}")
print(f"总用时: {total_time:.1f}秒 ({total_time/60:.1f}分钟)")
if success_count > 0:
    print(f"平均每个文件: {total_time/success_count:.1f}秒")

if failed_files:
    print("\n失败的文件:")
    for f in failed_files:
        print(f"  - {os.path.basename(f)}")

print(f"\n输出目录: {os.path.abspath(OUTPUT_DIR)}")
print("="*70)

# 清理
del model
import gc
gc.collect()
if device == "cuda":
    torch.cuda.empty_cache()