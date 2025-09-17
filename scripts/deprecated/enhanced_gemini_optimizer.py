#!/usr/bin/env python3
"""
增强版 Gemini 文档优化器
解决文档格式混乱、段落不清晰、结构化不足的问题
"""

import os
import re
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import google.generativeai as genai
from dataclasses import dataclass, field
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class EnhancedOptimizationConfig:
    """增强优化配置"""
    api_key: str
    model_name: str = "models/gemini-2.5-flash"
    temperature: float = 0.2  # 降低温度，提高输出稳定性
    max_tokens_per_request: int = 8000
    cache_enabled: bool = True
    cache_dir: str = "storage/cache/gemini"

    # 增强的专有名词映射
    term_corrections: Dict[str, str] = field(default_factory=lambda: {
        # AI模型名称
        "Dipsyc R1": "DeepSeek R1",
        "Dipsyk R1": "DeepSeek R1",
        "DeepSeep-R1": "DeepSeek R1",
        "DipSix": "DeepSeek",
        "Dipstick": "DeepSeek",
        "DipZick": "DeepSeek",
        "DPCV3": "DeepSeek V3",

        "Gorax 3": "Grok 3",
        "Gerrx 3": "Grok 3",
        "Guerk3": "Grok 3",
        "Grook": "Grok",

        "Klaus 3.7": "Claude 3.7",
        "Klow3.7": "Claude 3.7",
        "Gloss.7": "Claude 3.7",
        "课牢": "Claude",

        "O3 Mini-Hi": "o3-mini-high",
        "O3 Mini-Hide": "o3-mini-high",
        "Oh Samini Hi": "o3-mini-high",
        "MOS3 Mini-Hike": "o3-mini-high",

        "GEMD2.0 Pro": "Gemini 2.0 Pro",
        "GEMD2.2 Pro": "Gemini 2.0 Pro",
        "GEMD2.5 Pro": "Gemini 2.5 Pro",
        "GEM2.5 Pro": "Gemini 2.5 Pro",
        "JAMM 2.2.5 Pro": "Gemini 2.5 Pro",
        "JAMIN R.5 Pro": "Gemini 2.5 Pro",
        "Germanard Air 5 Pro": "Gemini 2.5 Pro",

        # 技术平台
        "Li-Co": "LeetCode",
        "Live CodeBand": "LeetCode",

        # 测试相关
        "ARME": "AMC",
        "MES500": "MATH500",

        # 其他技术术语
        "3rdjs": "Three.js",
        "7s": "Three.js",
        "Sray的JS": "Three.js",
        "artback": "HTML",
        "Pygame": "pygame",
        "拍Germanard": "pygame",
    })


class EnhancedGeminiOptimizer:
    """增强的Gemini文档优化器"""

    def __init__(self, config: EnhancedOptimizationConfig):
        self.config = config
        self.setup_api()
        self.setup_cache()

    def setup_api(self):
        """配置API"""
        genai.configure(api_key=self.config.api_key)
        self.model = genai.GenerativeModel(
            self.config.model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=self.config.temperature,
                top_p=0.95,
                max_output_tokens=8192,
            )
        )

    def setup_cache(self):
        """设置缓存"""
        if self.config.cache_enabled:
            Path(self.config.cache_dir).mkdir(parents=True, exist_ok=True)

    def preprocess_text(self, text: str) -> str:
        """预处理文本：添加基础段落分割"""
        # 1. 应用专有名词纠正
        for wrong, correct in self.config.term_corrections.items():
            text = text.replace(wrong, correct)

        # 2. 识别潜在的段落边界（基于句号和内容长度）
        sentences = re.split(r'([。！？])', text)

        # 3. 重组句子为段落
        paragraphs = []
        current_para = []
        current_length = 0

        for i in range(0, len(sentences)-1, 2):
            sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '')
            current_para.append(sentence)
            current_length += len(sentence)

            # 当段落达到一定长度时，开始新段落
            if current_length > 200 and sentence.endswith(('。', '！', '？')):
                paragraphs.append(''.join(current_para))
                current_para = []
                current_length = 0

        # 添加最后的段落
        if current_para:
            paragraphs.append(''.join(current_para))

        return '\n\n'.join(paragraphs)

    def identify_document_type(self, text: str) -> str:
        """识别文档类型"""
        if "测评" in text or "评测" in text or "对比" in text:
            return "evaluation"
        elif "教程" in text or "如何" in text or "步骤" in text:
            return "tutorial"
        elif "解析" in text or "分析" in text or "原理" in text:
            return "analysis"
        else:
            return "general"

    def create_optimized_prompt(self, text: str, doc_type: str) -> str:
        """创建优化的prompt"""
        type_specific_instructions = {
            "evaluation": """
- 创建清晰的对比表格
- 分别列出每个产品/模型的优缺点
- 提供评分或排名总结
- 使用子标题分隔不同测试项目
""",
            "tutorial": """
- 使用编号步骤
- 为每个步骤提供清晰的说明
- 添加代码块或命令示例
- 包含常见问题解决方案
""",
            "analysis": """
- 使用层级化的标题结构
- 提供概念定义和解释
- 使用示例说明复杂概念
- 添加总结和要点回顾
""",
            "general": """
- 识别主要话题并创建相应章节
- 保持逻辑流畅性
- 使用适当的过渡语句
"""
        }

        return f"""
请将以下ASR转录文本优化为专业、易读的技术文档。

【重要要求】：
1. **段落分割**：
   - 每个段落控制在3-5句话
   - 段落之间必须有空行分隔
   - 相关内容归入同一段落

2. **结构层次**：
   - 使用 # 作为主标题（仅一个）
   - 使用 ## 作为章节标题
   - 使用 ### 作为子章节标题
   - 每个标题后必须有空行

3. **专有名词纠正**（已预处理，但请检查遗漏）：
   - AI模型：DeepSeek, Claude, Grok, Gemini, o3-mini-high
   - 平台：LeetCode, GitHub, Three.js, pygame
   - 确保一致性

4. **内容优化**：
   - 去除"啊"、"呢"、"吧"等语气词
   - 将口语化表达改为书面语
   - 删除重复内容
   - 保留所有技术细节和数据

5. **格式规范**：
   - 代码用 `反引号` 标记
   - 重要概念用 **粗体**
   - 列表项使用 - 或数字
   - 测试结果使用表格展示

{type_specific_instructions.get(doc_type, type_specific_instructions['general'])}

【输出要求】：
- 必须是完整的Markdown文档
- 段落之间必须有明显的视觉分隔（空行）
- 保持内容的完整性，不要删减重要信息
- 确保输出的可读性和专业性

原始文本：
{text}

请输出优化后的完整文档："""

    def optimize_document(self, text: str, title: str = None) -> str:
        """优化文档的主方法"""
        try:
            # 1. 预处理
            logger.info("步骤1：预处理文本...")
            preprocessed = self.preprocess_text(text)

            # 2. 识别文档类型
            logger.info("步骤2：识别文档类型...")
            doc_type = self.identify_document_type(preprocessed)
            logger.info(f"  文档类型：{doc_type}")

            # 3. 分块处理
            chunks = self.split_text(preprocessed, 6000)  # 减小块大小以获得更好的处理
            optimized_chunks = []

            for i, chunk in enumerate(chunks):
                logger.info(f"步骤3：处理第 {i+1}/{len(chunks)} 块...")

                # 创建优化prompt
                prompt = self.create_optimized_prompt(chunk, doc_type)

                # 调用Gemini API
                try:
                    response = self.model.generate_content(prompt)
                    optimized_chunks.append(response.text)

                    # 避免API限流
                    if i < len(chunks) - 1:
                        time.sleep(3)

                except Exception as e:
                    logger.error(f"  处理块 {i+1} 失败：{e}")
                    optimized_chunks.append(chunk)  # 失败时使用原文

            # 4. 合并结果
            logger.info("步骤4：合并优化结果...")
            if len(optimized_chunks) == 1:
                final_document = optimized_chunks[0]
            else:
                # 对于多块文档，需要智能合并
                final_document = self.merge_chunks(optimized_chunks, title)

            # 5. 最终格式化
            logger.info("步骤5：最终格式化...")
            final_document = self.final_formatting(final_document, title)

            return final_document

        except Exception as e:
            logger.error(f"优化失败：{e}")
            return text

    def split_text(self, text: str, max_chars: int) -> List[str]:
        """智能分割文本"""
        if len(text) <= max_chars:
            return [text]

        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para)

            if current_size + para_size > max_chars and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size

        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        return chunks

    def merge_chunks(self, chunks: List[str], title: str = None) -> str:
        """智能合并多个优化块"""
        # 如果只有一个块，直接返回
        if len(chunks) == 1:
            return chunks[0]

        # 提取第一个块的标题（如果有）
        first_chunk = chunks[0]
        main_title = title

        if not main_title and first_chunk.startswith('#'):
            lines = first_chunk.split('\n')
            if lines[0].startswith('# '):
                main_title = lines[0]
                chunks[0] = '\n'.join(lines[1:])

        # 合并所有块
        merged = []
        if main_title:
            merged.append(main_title if main_title.startswith('#') else f"# {main_title}")
            merged.append('')

        for chunk in chunks:
            # 去除每个块可能重复的主标题
            if chunk.startswith('# '):
                lines = chunk.split('\n')
                chunk = '\n'.join(lines[1:])
            merged.append(chunk.strip())

        return '\n\n'.join(merged)

    def final_formatting(self, text: str, title: str = None) -> str:
        """最终格式化确保可读性"""
        lines = text.split('\n')
        formatted_lines = []
        last_was_empty = False

        for line in lines:
            line = line.strip()

            if not line:
                # 避免多个连续空行
                if not last_was_empty:
                    formatted_lines.append('')
                    last_was_empty = True
            else:
                # 确保标题后有空行
                if line.startswith('#'):
                    if formatted_lines and formatted_lines[-1]:
                        formatted_lines.append('')
                    formatted_lines.append(line)
                    formatted_lines.append('')
                    last_was_empty = True
                else:
                    formatted_lines.append(line)
                    last_was_empty = False

        # 确保文档以标题开始
        result = '\n'.join(formatted_lines)
        if title and not result.startswith('#'):
            result = f"# {title}\n\n{result}"

        return result

    def get_cache_key(self, text: str, operation: str) -> str:
        """生成缓存键"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"{operation}_{text_hash}"

    def optimize_file(self, input_path: str, output_path: str = None) -> str:
        """优化文件"""
        input_file = Path(input_path)

        if not input_file.exists():
            raise FileNotFoundError(f"文件不存在: {input_path}")

        # 读取文件
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 从文件名提取标题
        title = input_file.stem.replace('_', ' ').replace('-', ' ')

        # 优化文档
        logger.info(f"开始优化文件: {input_file.name}")
        optimized = self.optimize_document(content, title)

        # 保存结果
        if output_path:
            output_file = Path(output_path)
        else:
            output_file = input_file.parent / f"{input_file.stem}_enhanced.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(optimized)

        logger.info(f"优化完成，已保存到: {output_file}")
        return str(output_file)


def main():
    """测试函数"""
    config = EnhancedOptimizationConfig(
        api_key="AIzaSyDAmHzFbKgZMJVp1nyOkVr89MjXM6ahWnE",
        temperature=0.2
    )

    optimizer = EnhancedGeminiOptimizer(config)

    # 测试优化一个文档
    test_file = "storage/results/gemini_optimized/顶级模型PK - 到底谁是编程之王？_gemini_optimized.md"

    if Path(test_file).exists():
        output = test_file.replace("_gemini_optimized.md", "_enhanced.md")
        optimizer.optimize_file(test_file, output)
    else:
        print(f"测试文件不存在: {test_file}")


if __name__ == "__main__":
    main()