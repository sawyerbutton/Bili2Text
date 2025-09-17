#!/usr/bin/env python3
"""
快速批量优化文档 - 主要做纠错和基础优化
"""

import os
import sys
import time
from pathlib import Path
import logging
import google.generativeai as genai

# 添加项目根目录
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.optimize.gemini_document_optimizer import OptimizationConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API配置
API_KEY = "AIzaSyDAmHzFbKgZMJVp1nyOkVr89MjXM6ahWnE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# 专有名词纠错表
CORRECTIONS = {
    # AI模型
    "Dipsyc R1": "DeepSeek R1",
    "Dipsyk R1": "DeepSeek R1",
    "Dipsick R1": "DeepSeek R1",
    "DipSix": "DeepSeek",
    "Gorax 3": "Grok 3",
    "Gerrx 3": "Grok 3",
    "Growx3": "Grok 3",
    "Klaus 3.7": "Claude 3.7",
    "Claude3.7": "Claude 3.7",
    "O3 Mini Hide": "o3-mini-high",
    "O3 Mini High": "o3-mini-high",
    "O100本": "o1-preview",
    "Anstrapet": "Anthropic",

    # 技术平台
    "LiCo": "LeetCode",
    "X-MINE": "XMind",
    "Pi Game": "Pygame",
    "JowScript": "JavaScript",
    "DRTML": "HTML",
    "Rex組建": "React组件",

    # 常见错误
    "拼台": "平台",
    "四考": "思考",
    "边缘": "编译",
    "副置": "复制",
    "負置": "复制",
    "站貼": "粘贴",
    "沾貼": "粘贴",
    "预法错误": "语法错误",
    "韩式": "函数",
    "大魔型": "大模型",
    "大魔形": "大模型",
}


def apply_corrections(text):
    """应用纠错"""
    import re
    result = text
    for wrong, correct in CORRECTIONS.items():
        pattern = re.compile(re.escape(wrong), re.IGNORECASE)
        result = pattern.sub(correct, result)
    return result


def optimize_document(input_file, output_file):
    """快速优化单个文档"""
    try:
        # 读取文件
        content = Path(input_file).read_text(encoding='utf-8')

        # 1. 基础纠错
        corrected = apply_corrections(content)

        # 2. 如果文件不太大，做简单AI优化
        if len(content) < 5000:
            try:
                prompt = f"""
请优化以下文本的格式和结构，使其更专业：
1. 改善段落划分
2. 添加合适的Markdown标题
3. 去除明显的口语化表达

原文（前2000字）：
{corrected[:2000]}

直接输出优化后的内容：
"""
                response = model.generate_content(prompt)
                optimized = response.text + "\n\n" + corrected[2000:]
            except:
                optimized = corrected
        else:
            # 大文件只做纠错
            optimized = corrected

        # 保存结果
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(output_file).write_text(optimized, encoding='utf-8')

        return True
    except Exception as e:
        logger.error(f"处理失败: {e}")
        return False


def main():
    """主函数"""
    input_dir = Path("storage/results/expert_optimized")
    output_dir = Path("storage/results/gemini_optimized")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取所有待处理文件
    files = sorted(input_dir.glob("*.md"))

    # 跳过已处理的
    existing = {f.name for f in output_dir.glob("*.md")}

    logger.info(f"找到 {len(files)} 个文档，已处理 {len(existing)} 个")

    success_count = 0
    failed_count = 0

    for idx, file in enumerate(files, 1):
        # 生成输出文件名
        output_name = file.stem.replace('_深度优化版', '').replace('_专家优化版', '')
        output_name = f"{output_name}_gemini_optimized.md"
        output_file = output_dir / output_name

        # 跳过已存在的
        if output_file.exists():
            logger.info(f"[{idx}/{len(files)}] 跳过已存在: {file.name}")
            continue

        logger.info(f"[{idx}/{len(files)}] 优化: {file.name}")

        if optimize_document(file, output_file):
            success_count += 1
            logger.info(f"  ✅ 成功")
        else:
            failed_count += 1
            logger.info(f"  ❌ 失败")

        # 避免API限流
        if idx < len(files) and len(Path(file).read_text()) < 5000:
            time.sleep(2)

    logger.info(f"\n完成！成功: {success_count}, 失败: {failed_count}")

    # 生成报告
    report = f"""
Gemini 2.5 Flash 批量优化报告
===============================
时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
总文档: {len(files)}
成功: {success_count}
失败: {failed_count}
跳过: {len(existing)}
"""

    report_file = output_dir / "optimization_report.txt"
    report_file.write_text(report, encoding='utf-8')
    logger.info(f"报告已保存: {report_file}")


if __name__ == '__main__':
    main()