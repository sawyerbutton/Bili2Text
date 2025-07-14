#!/usr/bin/env python3
"""简单MP3转录测试 - 只处理前2个文件"""
import os
import warnings
warnings.filterwarnings("ignore")
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import whisperx
import time

# 选择2个MP3文件测试
test_files = [
    "./audio/mp3/你妹的，540也排队.mp3",
    "./audio/mp3/梦幻西游：2025.7.8维护公告.mp3"
]

# 输出目录
output_dir = "./test_mp3_results"
os.makedirs(output_dir, exist_ok=True)

print("WhisperX MP3转录测试")
print("="*60)

# 加载模型
print("加载模型...")
model = whisperx.load_model("tiny", "cpu", compute_type="int8", language="zh")
print("✓ 模型加载成功\n")

# 处理每个文件
for i, mp3_file in enumerate(test_files, 1):
    print(f"[{i}/2] 处理: {os.path.basename(mp3_file)}")
    
    try:
        # 加载音频
        start = time.time()
        audio = whisperx.load_audio(mp3_file)
        duration = len(audio) / 16000
        print(f"  音频长度: {duration:.1f}秒")
        
        # 转录
        print("  转录中...")
        result = model.transcribe(audio, batch_size=8, language="zh")
        elapsed = time.time() - start
        
        segments = result.get("segments", [])
        print(f"  ✓ 完成！{len(segments)}个片段，用时{elapsed:.1f}秒")
        
        # 保存
        output_file = os.path.join(output_dir, f"test_{i}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"文件: {os.path.basename(mp3_file)}\n")
            f.write(f"长度: {duration:.1f}秒\n")
            f.write(f"片段: {len(segments)}\n")
            f.write("="*60 + "\n\n")
            
            # 纯文本
            text = " ".join([s.get("text", "").strip() for s in segments])
            f.write(text if text else "[无内容]")
        
        print(f"  保存到: {output_file}")
        
        # 显示部分内容
        if segments:
            preview = segments[0].get("text", "").strip()[:80]
            print(f"  内容: {preview}...")
        
    except Exception as e:
        print(f"  ✗ 错误: {e}")
    
    print()

print(f"\n完成！结果保存在: {output_dir}/")

# 显示结果文件
import glob
results = glob.glob(f"{output_dir}/*.txt")
print(f"生成了 {len(results)} 个文件:")
for r in results:
    print(f"  - {os.path.basename(r)}")