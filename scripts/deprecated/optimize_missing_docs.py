#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化缺失的两个文档
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.optimize.gemini_document_optimizer import GeminiDocumentOptimizer, OptimizationConfig
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # 设置API密钥
    api_key = "AIzaSyDAmHzFbKgZMJVp1nyOkVr89MjXM6ahWnE"

    # 初始化优化器
    config = OptimizationConfig(
        api_key=api_key,
        model_name="models/gemini-2.5-flash",
        temperature=0.3
    )

    optimizer = GeminiDocumentOptimizer(config)

    # 定义输入输出路径
    input_dir = Path("storage/results/mark_transcripts")
    output_dir = Path("storage/results/gemini_optimized")

    # 需要优化的文档
    files_to_optimize = [
        "5种使用Deepseek打造可视化内容的方法，构建创意视觉图和专业数据分析报表，增强画面冲击力，可直接用在PPT，总结报告和视频解说中，总有一款适合你！.txt",
        "使用 Cursor 和 Claude3.7 10分钟构建产品原型图和iOS应用，无需写一行代码.txt"
    ]

    # 输出文件名映射
    output_names = {
        files_to_optimize[0]: "5种使用Deepseek打造可视化内容的方法_gemini_optimized.md",
        files_to_optimize[1]: "使用Cursor和Claude3.7构建产品原型图和iOS应用_gemini_optimized.md"
    }

    # 优化文档
    for file_name in files_to_optimize:
        input_file = input_dir / file_name

        if not input_file.exists():
            logger.error(f"文件不存在: {input_file}")
            continue

        logger.info(f"正在优化: {file_name}")

        try:
            # 读取原始内容
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 优化文档 - 使用optimize_file方法
            # 先保存到临时文件
            temp_input = Path(f"/tmp/{file_name}")
            temp_input.write_text(content, encoding='utf-8')

            # 调用optimize_file方法
            temp_output = Path(f"/tmp/optimized_{file_name}.md")
            optimizer.optimize_file(str(temp_input), str(temp_output))

            # 读取优化后的内容
            optimized_content = temp_output.read_text(encoding='utf-8')

            # 写入优化后的内容
            output_file = output_dir / output_names[file_name]
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(optimized_content)

            logger.info(f"✅ 成功优化并保存到: {output_file}")

        except Exception as e:
            logger.error(f"❌ 优化失败: {e}")
            continue

    logger.info("所有文档优化完成！")

if __name__ == "__main__":
    main()