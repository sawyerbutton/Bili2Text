#!/usr/bin/env python3
"""
批量修复所有格式有问题的文档
"""

import os
import sys
from pathlib import Path
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from scripts.optimize.simple_formatter import SimpleDocumentFormatter


def batch_format_all_documents():
    """批量格式化所有需要修复的文档"""

    # 初始化格式化器
    formatter = SimpleDocumentFormatter()

    # 输入输出目录
    input_dir = Path("storage/results/gemini_optimized")
    output_dir = Path("storage/results/gemini_formatted")
    output_dir.mkdir(exist_ok=True)

    # 获取所有需要处理的文档
    documents = list(input_dir.glob("*_gemini_optimized.md"))

    logger.info(f"找到 {len(documents)} 个文档需要处理")
    logger.info("=" * 60)

    success_count = 0
    failed_docs = []

    for doc_path in documents:
        try:
            logger.info(f"处理: {doc_path.name}")

            # 生成输出文件名
            output_name = doc_path.name.replace("_gemini_optimized.md", "_formatted.md")
            output_file = output_dir / output_name

            # 格式化文档
            formatter.format_file(str(doc_path), str(output_file))

            success_count += 1
            logger.info(f"  ✅ 成功: {output_name}")

        except Exception as e:
            logger.error(f"  ❌ 失败: {doc_path.name}")
            logger.error(f"     错误: {e}")
            failed_docs.append(doc_path.name)

        # 短暂延迟避免系统压力
        time.sleep(0.1)

    # 汇总报告
    logger.info("=" * 60)
    logger.info("处理完成！")
    logger.info(f"成功: {success_count}/{len(documents)}")

    if failed_docs:
        logger.warning("失败的文档:")
        for doc in failed_docs:
            logger.warning(f"  - {doc}")

    logger.info(f"输出目录: {output_dir}")

    # 创建汇总报告
    report_file = output_dir / "FORMAT_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 文档格式化报告\n\n")
        f.write(f"## 统计\n\n")
        f.write(f"- 总文档数: {len(documents)}\n")
        f.write(f"- 成功处理: {success_count}\n")
        f.write(f"- 失败: {len(failed_docs)}\n")
        f.write(f"- 成功率: {success_count/len(documents)*100:.1f}%\n\n")

        if failed_docs:
            f.write("## 失败的文档\n\n")
            for doc in failed_docs:
                f.write(f"- {doc}\n")

    logger.info(f"报告已保存到: {report_file}")


if __name__ == "__main__":
    batch_format_all_documents()