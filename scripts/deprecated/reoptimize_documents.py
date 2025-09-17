#!/usr/bin/env python3
"""
重新优化现有文档，提升格式和结构
"""

import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from scripts.optimize.enhanced_gemini_optimizer import EnhancedGeminiOptimizer, EnhancedOptimizationConfig
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def reoptimize_poor_documents():
    """重新优化格式不佳的文档"""

    # 配置
    config = EnhancedOptimizationConfig(
        api_key="AIzaSyDAmHzFbKgZMJVp1nyOkVr89MjXM6ahWnE",
        temperature=0.2,  # 低温度保证稳定输出
        max_tokens_per_request=5000  # 减小块大小
    )

    optimizer = EnhancedGeminiOptimizer(config)

    # 需要重新优化的文档列表
    documents_to_reoptimize = [
        "顶级模型PK - 到底谁是编程之王？_gemini_optimized.md",
        "四大推理大模型数学与编程能力评测 - Grok3、Claude3.7、DeepSeep-R1、o3-mini-high 到底谁的推理能力最强？_gemini_optimized.md",
        "A2A协议_gemini_optimized.md"
    ]

    input_dir = Path("storage/results/gemini_optimized")
    output_dir = Path("storage/results/gemini_reoptimized")
    output_dir.mkdir(exist_ok=True)

    success_count = 0

    for doc_name in documents_to_reoptimize:
        input_file = input_dir / doc_name

        if not input_file.exists():
            logger.warning(f"文件不存在: {input_file}")
            continue

        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"正在重新优化: {doc_name}")
            logger.info(f"{'='*60}")

            # 生成输出文件名
            output_name = doc_name.replace("_gemini_optimized.md", "_reoptimized.md")
            output_file = output_dir / output_name

            # 优化文档
            result_path = optimizer.optimize_file(str(input_file), str(output_file))

            logger.info(f"✅ 成功优化: {output_name}")
            success_count += 1

        except Exception as e:
            logger.error(f"❌ 优化失败: {doc_name}")
            logger.error(f"   错误: {e}")

    logger.info(f"\n{'='*60}")
    logger.info(f"优化完成: {success_count}/{len(documents_to_reoptimize)} 个文档")
    logger.info(f"输出目录: {output_dir}")


def main():
    """主函数"""
    reoptimize_poor_documents()


if __name__ == "__main__":
    main()