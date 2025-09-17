#!/usr/bin/env python3
"""
演示脚本：展示如何使用 TXT 转 Markdown 优化器
"""

from batch_optimize_txt_to_markdown import batch_optimize_txt_to_markdown

# 示例1：优化默认目录中的所有TXT文件
print("=" * 60)
print("示例1: 使用默认设置")
print("将自动查找 storage/results 目录下的 TXT 文件")
print("输出到 storage/results/professional_markdown")
print("=" * 60)

# batch_optimize_txt_to_markdown()

# 示例2：指定特定的输入输出目录
print("\n" + "=" * 60)
print("示例2: 指定输入输出目录")
print("=" * 60)

# 处理根目录下的几个测试文件
batch_optimize_txt_to_markdown(
    input_dir="storage/results",
    output_dir="storage/results/demo_optimized",
    file_pattern="*GPU转录结果.txt"  # 只处理GPU转录结果文件
)

# 示例3：处理特定用户目录的文件
print("\n" + "=" * 60)
print("示例3: 处理特定子目录")
print("=" * 60)

# batch_optimize_txt_to_markdown(
#     input_dir="storage/results/gpu_transcripts/519979716",
#     output_dir="storage/results/user_519979716_optimized",
#     file_pattern="*.txt"
# )