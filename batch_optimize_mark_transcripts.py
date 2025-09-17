#!/usr/bin/env python3
"""
批量优化 mark_transcripts/markdown 目录下的所有文档
使用专业版 Gemini 优化器进行处理
"""

import os
import sys
from pathlib import Path
import logging
import time
from datetime import datetime

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from scripts.optimize.professional_gemini_optimizer import ProfessionalGeminiOptimizer, ProfessionalOptConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def batch_optimize_mark_transcripts():
    """批量优化 mark_transcripts 目录下的所有 markdown 文件"""

    # 配置
    config = ProfessionalOptConfig(
        api_key=os.getenv("GEMINI_API_KEY", "AIzaSyDAmHzFbKgZMJVp1nyOkVr89MjXM6ahWnE"),
        temperature=0.0  # 确定性输出
    )

    optimizer = ProfessionalGeminiOptimizer(config)

    # 输入输出目录
    input_dir = Path("storage/results/mark_transcripts/markdown")
    output_dir = Path("storage/results/mark_transcripts_professional")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取所有 markdown 文件
    markdown_files = list(input_dir.glob("*.md"))
    total_files = len(markdown_files)

    logger.info(f"发现 {total_files} 个 Markdown 文件待优化")
    logger.info(f"输入目录: {input_dir}")
    logger.info(f"输出目录: {output_dir}")
    logger.info("=" * 60)

    # 统计
    results = {
        'success': [],
        'failed': [],
        'skipped': []
    }

    start_time = datetime.now()

    for i, input_file in enumerate(markdown_files, 1):
        try:
            logger.info(f"\n[{i}/{total_files}] 处理: {input_file.name}")

            # 检查文件大小
            file_size = input_file.stat().st_size
            char_count = len(input_file.read_text(encoding='utf-8'))

            logger.info(f"  文件大小: {file_size:,} 字节, {char_count:,} 字符")
            logger.info(f"  占100万token限制的: {char_count/1000000*100:.2f}%")

            # 如果文件过大，跳过
            if char_count > 100000:  # 10万字符限制
                logger.warning(f"  ⚠️ 文件过大 ({char_count:,} 字符)，跳过处理")
                results['skipped'].append(input_file.name)
                continue

            # 生成输出文件名
            output_file = output_dir / input_file.name

            # 如果输出文件已存在，可选择跳过
            if output_file.exists():
                logger.info(f"  ℹ️ 输出文件已存在，跳过: {output_file.name}")
                results['skipped'].append(input_file.name)
                continue

            # 优化文档
            file_start = datetime.now()
            optimizer.optimize_file(str(input_file), str(output_file))

            process_time = (datetime.now() - file_start).total_seconds()
            results['success'].append(input_file.name)
            logger.info(f"  ✅ 成功优化，用时 {process_time:.1f} 秒")

            # API 速率限制：每个文档间隔5秒
            if i < total_files:
                logger.info("  等待 5 秒避免API限制...")
                time.sleep(5)

        except Exception as e:
            logger.error(f"  ❌ 处理失败: {e}")
            results['failed'].append(input_file.name)

            # 错误后等待更长时间
            if "quota" in str(e).lower():
                logger.warning("  检测到配额限制，等待60秒...")
                time.sleep(60)
            else:
                time.sleep(10)

    # 生成处理报告
    total_time = (datetime.now() - start_time).total_seconds()

    logger.info("\n" + "=" * 60)
    logger.info("批处理完成！")
    logger.info(f"总用时: {total_time/60:.1f} 分钟")
    logger.info(f"成功: {len(results['success'])}/{total_files}")
    logger.info(f"失败: {len(results['failed'])}")
    logger.info(f"跳过: {len(results['skipped'])}")

    if results['success']:
        logger.info("\n成功优化的文档:")
        for doc in results['success']:
            logger.info(f"  ✅ {doc}")

    if results['failed']:
        logger.info("\n失败的文档:")
        for doc in results['failed']:
            logger.info(f"  ❌ {doc}")

    if results['skipped']:
        logger.info("\n跳过的文档:")
        for doc in results['skipped']:
            logger.info(f"  ⏭️ {doc}")

    # 保存处理报告
    report_file = output_dir / "OPTIMIZATION_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# Mark Transcripts 优化报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 统计数据\n\n")
        f.write(f"- 总文档数: {total_files}\n")
        f.write(f"- 成功优化: {len(results['success'])}\n")
        f.write(f"- 处理失败: {len(results['failed'])}\n")
        f.write(f"- 跳过处理: {len(results['skipped'])}\n")
        f.write(f"- 成功率: {len(results['success'])/total_files*100:.1f}%\n")
        f.write(f"- 总用时: {total_time/60:.1f} 分钟\n")
        f.write(f"- 平均处理时间: {total_time/len(results['success']):.1f} 秒/文档\n\n")

        f.write("## 优化配置\n\n")
        f.write("- **模型**: Gemini 2.5 Flash\n")
        f.write("- **温度**: 0.0 (确定性输出)\n")
        f.write("- **上下文窗口**: 100万 tokens\n")
        f.write("- **优化策略**: 专业视频逐字稿优化prompt\n\n")

        if results['success']:
            f.write("## 成功优化的文档\n\n")
            for doc in results['success']:
                f.write(f"- ✅ {doc}\n")
            f.write("\n")

        if results['failed']:
            f.write("## 处理失败的文档\n\n")
            for doc in results['failed']:
                f.write(f"- ❌ {doc}\n")
            f.write("\n")

        if results['skipped']:
            f.write("## 跳过的文档\n\n")
            for doc in results['skipped']:
                f.write(f"- ⏭️ {doc}\n")
            f.write("\n")

    logger.info(f"\n报告已保存到: {report_file}")
    logger.info(f"输出目录: {output_dir}")

    return results


if __name__ == "__main__":
    batch_optimize_mark_transcripts()