#!/usr/bin/env python3
"""
快速修复优化器 - 专注解决格式问题
"""

import os
from pathlib import Path
from scripts.optimize.gemini_document_optimizer import GeminiDocumentOptimizer, OptimizationConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def quick_fix_documents():
    """快速修复格式问题严重的文档"""

    # 使用更低的温度和更严格的prompt
    config = OptimizationConfig(
        api_key="AIzaSyDAmHzFbKgZMJVp1nyOkVr89MjXM6ahWnE",
        model_name="models/gemini-2.5-flash",
        temperature=0.1,  # 极低温度保证稳定
        top_p=0.9,
        max_tokens_per_request=4000  # 更小的块
    )

    # 修改优化器的correct_and_structure方法
    original_method = GeminiDocumentOptimizer.correct_and_structure

    def enhanced_correct_and_structure(self, text: str) -> str:
        """增强的纠错和结构化方法"""
        prompt = f"""
将以下转录文本优化为专业技术文档。

【极其重要的格式要求】：
1. 每3-4句话必须分为一个段落
2. 段落之间必须有空行（两个换行符）
3. 使用Markdown格式，标题用##，子标题用###
4. 纠正所有AI模型名称：DeepSeek, Claude, Gemini, o3-mini-high等

【输出格式示例】：
## 标题

第一段内容，包含3-4句话。段落结束后有空行。

第二段内容，与第一段用空行分隔。内容连贯清晰。

### 子标题

子标题下的内容...

【原文】：
{text[:4000]}  # 限制长度避免超时

请严格按照格式要求输出优化后的文档："""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"优化失败: {e}")
            # 失败时至少做基础格式化
            sentences = text.split('。')
            paragraphs = []
            for i in range(0, len(sentences), 3):
                para = '。'.join(sentences[i:i+3]) + '。'
                paragraphs.append(para)
            return '\n\n'.join(paragraphs)

    # 替换方法
    GeminiDocumentOptimizer.correct_and_structure = enhanced_correct_and_structure

    optimizer = GeminiDocumentOptimizer(config)

    # 需要修复的文档
    documents = [
        "顶级模型PK - 到底谁是编程之王？_gemini_optimized.md",
        "四大推理大模型数学与编程能力评测 - Grok3、Claude3.7、DeepSeep-R1、o3-mini-high 到底谁的推理能力最强？_gemini_optimized.md"
    ]

    input_dir = Path("storage/results/gemini_optimized")
    output_dir = Path("storage/results/gemini_fixed")
    output_dir.mkdir(exist_ok=True)

    for doc_name in documents:
        input_file = input_dir / doc_name

        if not input_file.exists():
            logger.warning(f"文件不存在: {input_file}")
            continue

        logger.info(f"修复: {doc_name}")

        output_name = doc_name.replace("_gemini_optimized.md", "_fixed.md")
        output_file = output_dir / output_name

        try:
            optimizer.optimize_file(str(input_file), str(output_file))
            logger.info(f"✅ 成功修复: {output_name}")
        except Exception as e:
            logger.error(f"❌ 修复失败: {e}")


if __name__ == "__main__":
    quick_fix_documents()