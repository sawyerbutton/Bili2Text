#!/usr/bin/env python3
"""
批量使用长上下文优化器处理文档
"""

import os
import sys
from pathlib import Path
import logging
import time

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from scripts.optimize.long_context_gemini_optimizer import LongContextGeminiOptimizer, LongContextConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def batch_optimize_with_long_context():
    """使用长上下文优化器批量处理文档"""

    # 配置
    config = LongContextConfig(
        api_key=os.getenv("GEMINI_API_KEY", "AIzaSyDAmHzFbKgZMJVp1nyOkVr89MjXM6ahWnE"),
        temperature=0.0  # 确定性输出
    )

    optimizer = LongContextGeminiOptimizer(config)

    # 需要重新优化的文档（选择格式最差的几个）
    priority_documents = [
        "顶级模型PK - 到底谁是编程之王？_gemini_optimized.md",
        "四大推理大模型数学与编程能力评测 - Grok3、Claude3.7、DeepSeep-R1、o3-mini-high 到底谁的推理能力最强？_gemini_optimized.md",
        "A2A协议_gemini_optimized.md",
        "如何5分钟快速搞定视频创意脚本？AI批量生成短视频口播文案(2025最新)_gemini_optimized.md",
        "免费10分钟克隆你的AI声音，支持32种语言！Ai配音工具Coqou-TTS和VoiceCraft，免费开源离线运行_gemini_optimized.md"
    ]

    input_dir = Path("storage/results/gemini_optimized")
    output_dir = Path("storage/results/gemini_long_context")
    output_dir.mkdir(exist_ok=True)

    logger.info(f"准备优化 {len(priority_documents)} 个文档")
    logger.info("=" * 60)

    results = {
        'success': [],
        'failed': [],
        'skipped': []
    }

    for i, doc_name in enumerate(priority_documents, 1):
        input_file = input_dir / doc_name

        if not input_file.exists():
            logger.warning(f"[{i}/{len(priority_documents)}] 文件不存在: {doc_name}")
            results['skipped'].append(doc_name)
            continue

        try:
            logger.info(f"\n[{i}/{len(priority_documents)}] 处理: {doc_name}")

            # 检查文档大小
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                doc_size = len(content)

            logger.info(f"  文档大小: {doc_size:,} 字符 (仅占100万token限制的 {doc_size/1000000*100:.1f}%)")

            # 生成输出文件名
            output_name = doc_name.replace("_gemini_optimized.md", "_long_context.md")
            output_file = output_dir / output_name

            # 优化文档
            optimizer.optimize_file(str(input_file), str(output_file))

            results['success'].append(doc_name)
            logger.info(f"  ✅ 成功: {output_name}")

            # 短暂延迟，避免API限制
            if i < len(priority_documents):
                logger.info("  等待5秒...")
                time.sleep(5)

        except Exception as e:
            logger.error(f"  ❌ 失败: {doc_name}")
            logger.error(f"     错误: {e}")
            results['failed'].append(doc_name)

            # 错误后等待更长时间
            time.sleep(10)

    # 汇总报告
    logger.info("\n" + "=" * 60)
    logger.info("批处理完成！")
    logger.info(f"成功: {len(results['success'])}/{len(priority_documents)}")
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

    # 创建对比报告
    if results['success']:
        report_file = output_dir / "OPTIMIZATION_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 长上下文优化报告\n\n")
            f.write(f"## 统计\n\n")
            f.write(f"- 处理文档数: {len(priority_documents)}\n")
            f.write(f"- 成功: {len(results['success'])}\n")
            f.write(f"- 失败: {len(results['failed'])}\n")
            f.write(f"- 成功率: {len(results['success'])/len(priority_documents)*100:.1f}%\n\n")

            f.write("## 核心改进\n\n")
            f.write("- **策略**: 一次性处理整个文档，充分利用100万token上下文\n")
            f.write("- **温度**: 0.0 (完全确定性输出)\n")
            f.write("- **Prompt**: 简化并提供清晰示例\n\n")

            f.write("## 文档列表\n\n")
            for doc in results['success']:
                original = f"gemini_optimized/{doc}"
                optimized = f"gemini_long_context/{doc.replace('_gemini_optimized', '_long_context')}"
                f.write(f"- ✅ {doc}\n")
                f.write(f"  - 原始: `{original}`\n")
                f.write(f"  - 优化: `{optimized}`\n\n")

        logger.info(f"\n报告已保存到: {report_file}")

    logger.info(f"\n输出目录: {output_dir}")
    logger.info("\n建议对比查看优化前后的文档效果")


if __name__ == "__main__":
    batch_optimize_with_long_context()