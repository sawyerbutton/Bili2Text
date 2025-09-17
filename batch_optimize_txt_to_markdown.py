#!/usr/bin/env python3
"""
批量优化 TXT 转录文件到专业 Markdown 文档
适用于 ASR 转录后的 txt 文件优化场景
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


def batch_optimize_txt_to_markdown(input_dir=None, output_dir=None, file_pattern="*.txt"):
    """
    批量优化 TXT 转录文件到专业 Markdown 文档

    Args:
        input_dir: 输入目录路径，默认为 storage/results/gpu_transcripts
        output_dir: 输出目录路径，默认为 storage/results/professional_markdown
        file_pattern: 文件匹配模式，默认为 *.txt
    """

    # 配置
    config = ProfessionalOptConfig(
        api_key=os.getenv("GEMINI_API_KEY", "AIzaSyDAmHzFbKgZMJVp1nyOkVr89MjXM6ahWnE"),
        temperature=0.0  # 确定性输出
    )

    optimizer = ProfessionalGeminiOptimizer(config)

    # 默认输入输出目录
    if input_dir is None:
        # 尝试多个可能的输入目录
        possible_dirs = [
            Path("storage/results/gpu_transcripts"),
            Path("storage/results/result"),
            Path("storage/results/mark_transcripts/txt"),
            Path("storage/results/transcripts"),
        ]

        for dir_path in possible_dirs:
            if dir_path.exists():
                input_dir = dir_path
                logger.info(f"自动检测到输入目录: {input_dir}")
                break

        if input_dir is None:
            input_dir = Path("storage/results/gpu_transcripts")
            logger.warning(f"未找到现有目录，使用默认: {input_dir}")
    else:
        input_dir = Path(input_dir)

    if output_dir is None:
        output_dir = Path("storage/results/professional_markdown")
    else:
        output_dir = Path(output_dir)

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取所有 txt 文件
    txt_files = list(input_dir.glob(file_pattern))
    total_files = len(txt_files)

    if total_files == 0:
        logger.warning(f"在 {input_dir} 中未找到任何 {file_pattern} 文件")
        return

    logger.info(f"发现 {total_files} 个 TXT 文件待优化")
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

    for i, input_file in enumerate(txt_files, 1):
        try:
            logger.info(f"\n[{i}/{total_files}] 处理: {input_file.name}")

            # 检查文件大小
            file_size = input_file.stat().st_size

            # 读取文件内容
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 尝试其他编码
                with open(input_file, 'r', encoding='gbk') as f:
                    content = f.read()

            char_count = len(content)

            logger.info(f"  文件大小: {file_size:,} 字节, {char_count:,} 字符")
            logger.info(f"  占100万token限制的: {char_count/1000000*100:.2f}%")

            # 如果文件过大，跳过
            if char_count > 100000:  # 10万字符限制
                logger.warning(f"  ⚠️ 文件过大 ({char_count:,} 字符)，跳过处理")
                results['skipped'].append(input_file.name)
                continue

            # 如果文件太小，可能是空文件或错误
            if char_count < 10:
                logger.warning(f"  ⚠️ 文件过小 ({char_count} 字符)，跳过处理")
                results['skipped'].append(input_file.name)
                continue

            # 生成输出文件名（.txt 改为 .md）
            output_filename = input_file.stem + "_optimized.md"
            output_file = output_dir / output_filename

            # 如果输出文件已存在，可选择跳过
            if output_file.exists():
                logger.info(f"  ℹ️ 输出文件已存在，覆盖: {output_file.name}")

            # 预处理 TXT 内容
            content = preprocess_txt_content(content)

            # 创建临时文件用于优化（因为optimizer需要文件路径）
            temp_input = output_dir / f"temp_{input_file.name}"
            with open(temp_input, 'w', encoding='utf-8') as f:
                f.write(content)

            # 优化文档
            file_start = datetime.now()

            try:
                optimizer.optimize_file(str(temp_input), str(output_file))
                process_time = (datetime.now() - file_start).total_seconds()
                results['success'].append({
                    'name': input_file.name,
                    'output': output_filename,
                    'time': process_time,
                    'size': char_count
                })
                logger.info(f"  ✅ 成功优化，用时 {process_time:.1f} 秒")
            finally:
                # 删除临时文件
                if temp_input.exists():
                    temp_input.unlink()

            # API 速率限制：每个文档间隔5秒
            if i < total_files:
                logger.info("  等待 5 秒避免API限制...")
                time.sleep(5)

        except Exception as e:
            logger.error(f"  ❌ 处理失败: {e}")
            results['failed'].append({
                'name': input_file.name,
                'error': str(e)
            })

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
            logger.info(f"  ✅ {doc['name']} -> {doc['output']} ({doc['time']:.1f}秒)")

    if results['failed']:
        logger.info("\n失败的文档:")
        for doc in results['failed']:
            logger.info(f"  ❌ {doc['name']}: {doc['error']}")

    if results['skipped']:
        logger.info("\n跳过的文档:")
        for doc in results['skipped']:
            logger.info(f"  ⏭️ {doc}")

    # 保存处理报告
    report_file = output_dir / "OPTIMIZATION_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# TXT 转 Markdown 优化报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 统计数据\n\n")
        f.write(f"- 输入格式: TXT (ASR转录文件)\n")
        f.write(f"- 输出格式: Markdown (专业文档)\n")
        f.write(f"- 总文档数: {total_files}\n")
        f.write(f"- 成功优化: {len(results['success'])}\n")
        f.write(f"- 处理失败: {len(results['failed'])}\n")
        f.write(f"- 跳过处理: {len(results['skipped'])}\n")
        f.write(f"- 成功率: {len(results['success'])/total_files*100:.1f}%\n")
        f.write(f"- 总用时: {total_time/60:.1f} 分钟\n")

        if results['success']:
            avg_time = sum(d['time'] for d in results['success']) / len(results['success'])
            avg_size = sum(d['size'] for d in results['success']) / len(results['success'])
            f.write(f"- 平均处理时间: {avg_time:.1f} 秒/文档\n")
            f.write(f"- 平均文档大小: {avg_size:.0f} 字符\n")

        f.write(f"\n## 优化配置\n\n")
        f.write("- **模型**: Gemini 2.5 Flash\n")
        f.write("- **温度**: 0.0 (确定性输出)\n")
        f.write("- **上下文窗口**: 100万 tokens\n")
        f.write("- **优化策略**: 专业视频逐字稿优化prompt\n")
        f.write("- **输入目录**: `{}`\n".format(input_dir))
        f.write("- **输出目录**: `{}`\n\n".format(output_dir))

        if results['success']:
            f.write("## 成功优化的文档\n\n")
            f.write("| 原始文件 | 优化后文件 | 大小 | 用时 |\n")
            f.write("|---------|-----------|------|------|\n")
            for doc in results['success']:
                f.write(f"| {doc['name']} | {doc['output']} | {doc['size']:,}字符 | {doc['time']:.1f}秒 |\n")
            f.write("\n")

        if results['failed']:
            f.write("## 处理失败的文档\n\n")
            for doc in results['failed']:
                f.write(f"- ❌ **{doc['name']}**: {doc['error']}\n")
            f.write("\n")

        if results['skipped']:
            f.write("## 跳过的文档\n\n")
            for doc in results['skipped']:
                f.write(f"- ⏭️ {doc}\n")
            f.write("\n")

    logger.info(f"\n报告已保存到: {report_file}")
    logger.info(f"输出目录: {output_dir}")

    return results


def preprocess_txt_content(content):
    """
    预处理TXT内容，为优化做准备

    Args:
        content: 原始TXT内容

    Returns:
        预处理后的内容
    """

    # 移除多余的空白行
    lines = content.split('\n')
    processed_lines = []

    for line in lines:
        line = line.strip()
        if line:  # 保留非空行
            processed_lines.append(line)

    # 重新组合，确保段落间有适当的空行
    content = '\n\n'.join(processed_lines)

    # 添加基础标题（如果内容没有明显的标题结构）
    if not content.startswith('#'):
        # 尝试从文件内容中提取可能的标题
        first_line = processed_lines[0] if processed_lines else "视频转录文档"
        if len(first_line) < 100:  # 如果第一行不太长，可能是标题
            content = f"# {first_line}\n\n" + '\n\n'.join(processed_lines[1:])
        else:
            content = f"# 视频转录文档\n\n{content}"

    return content


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='批量优化TXT转录文件到Markdown格式')
    parser.add_argument('--input', '-i', type=str, help='输入目录路径')
    parser.add_argument('--output', '-o', type=str, help='输出目录路径')
    parser.add_argument('--pattern', '-p', type=str, default='*.txt', help='文件匹配模式')

    args = parser.parse_args()

    batch_optimize_txt_to_markdown(
        input_dir=args.input,
        output_dir=args.output,
        file_pattern=args.pattern
    )