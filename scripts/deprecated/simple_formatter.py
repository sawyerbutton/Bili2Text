#!/usr/bin/env python3
"""
简单但有效的文档格式化工具
专注于解决段落、换行和基础结构问题
"""

import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleDocumentFormatter:
    """简单文档格式化器"""

    def __init__(self):
        # 专有名词映射（关键的）
        self.term_map = {
            # AI模型
            "GEMD2.5 Pro": "Gemini 2.5 Pro",
            "GEM2.5 Pro": "Gemini 2.5 Pro",
            "JAMM 2.2.5 Pro": "Gemini 2.5 Pro",
            "JAMIN R.5 Pro": "Gemini 2.5 Pro",

            "O3 Mini-Hi": "o3-mini-high",
            "O3 Mini-Hide": "o3-mini-high",

            "Dipsyg": "DeepSeek",
            "Dipstick": "DeepSeek",
            "DPCV3": "DeepSeek V3",

            "Klaus 3.7": "Claude 3.7",
            "Klow3.7": "Claude 3.7",
            "课牢": "Claude",

            # 平台
            "Li-Co": "LeetCode",
            "3rdjs": "Three.js",
        }

        # 句子结束标记
        self.sentence_endings = ['。', '！', '？', '.', '!', '?']

    def fix_terms(self, text: str) -> str:
        """修正专有名词"""
        for wrong, correct in self.term_map.items():
            text = text.replace(wrong, correct)
        return text

    def split_into_sentences(self, text: str) -> list:
        """将文本分割成句子"""
        # 使用正则表达式分割句子
        pattern = r'([。！？.!?])'
        parts = re.split(pattern, text)

        sentences = []
        for i in range(0, len(parts)-1, 2):
            sentence = parts[i] + (parts[i+1] if i+1 < len(parts) else '')
            sentence = sentence.strip()
            if sentence:
                sentences.append(sentence)

        return sentences

    def group_into_paragraphs(self, sentences: list, target_size: int = 3) -> list:
        """将句子组合成段落"""
        paragraphs = []
        current_para = []

        for sentence in sentences:
            current_para.append(sentence)

            # 检查是否应该开始新段落
            should_break = False

            # 1. 达到目标句子数
            if len(current_para) >= target_size:
                should_break = True

            # 2. 遇到明显的主题转换词
            topic_markers = ['首先', '其次', '然后', '接下来', '另外', '此外', '总之', '综上所述', '最后']
            for marker in topic_markers:
                if sentence.startswith(marker):
                    should_break = True
                    break

            # 3. 代码或特殊标记后
            if '```' in sentence or sentence.startswith(('##', '###')):
                should_break = True

            if should_break and current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []

        # 添加剩余句子
        if current_para:
            paragraphs.append(' '.join(current_para))

        return paragraphs

    def identify_sections(self, text: str) -> dict:
        """识别文档的主要部分"""
        sections = {
            'title': None,
            'overview': [],
            'main_content': [],
            'conclusion': []
        }

        lines = text.split('\n')

        # 尝试提取标题
        for line in lines[:5]:  # 只看前5行
            if '评测' in line or 'PK' in line or '对比' in line:
                sections['title'] = line.strip()
                break

        return sections

    def format_as_markdown(self, paragraphs: list, title: str = None) -> str:
        """将段落格式化为Markdown"""
        output = []

        # 添加标题
        if title:
            output.append(f"# {title}")
            output.append("")

        # 识别内容类型并添加适当的节标题
        current_section = None

        for i, para in enumerate(paragraphs):
            # 检测节的开始
            if i == 0 or '介绍' in para[:20] or '概述' in para[:20]:
                if current_section != 'intro':
                    output.append("## 概述")
                    output.append("")
                    current_section = 'intro'

            elif '测试' in para or '评测' in para or '算法' in para:
                if current_section != 'test':
                    output.append("## 测试与评测")
                    output.append("")
                    current_section = 'test'

            elif '结果' in para or '总结' in para or '结论' in para:
                if current_section != 'conclusion':
                    output.append("## 结果与总结")
                    output.append("")
                    current_section = 'conclusion'

            # 添加段落
            output.append(para)
            output.append("")  # 段落间空行

        return '\n'.join(output)

    def format_document(self, text: str, title: str = None) -> str:
        """格式化整个文档"""
        try:
            # 1. 修正专有名词
            logger.info("步骤1：修正专有名词...")
            text = self.fix_terms(text)

            # 2. 分割成句子
            logger.info("步骤2：分割句子...")
            sentences = self.split_into_sentences(text)
            logger.info(f"  共 {len(sentences)} 个句子")

            # 3. 组合成段落
            logger.info("步骤3：组合段落...")
            paragraphs = self.group_into_paragraphs(sentences, target_size=4)
            logger.info(f"  共 {len(paragraphs)} 个段落")

            # 4. 格式化为Markdown
            logger.info("步骤4：生成Markdown...")
            formatted = self.format_as_markdown(paragraphs, title)

            return formatted

        except Exception as e:
            logger.error(f"格式化失败: {e}")
            return text

    def format_file(self, input_path: str, output_path: str = None):
        """格式化文件"""
        input_file = Path(input_path)

        if not input_file.exists():
            raise FileNotFoundError(f"文件不存在: {input_path}")

        # 读取文件
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 从文件名提取标题
        title = input_file.stem.replace('_gemini_optimized', '').replace('_', ' ')

        # 格式化文档
        logger.info(f"开始格式化: {input_file.name}")
        formatted = self.format_document(content, title)

        # 保存结果
        if output_path:
            output_file = Path(output_path)
        else:
            output_file = input_file.parent / f"{input_file.stem}_formatted.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted)

        logger.info(f"格式化完成: {output_file}")
        return str(output_file)


def main():
    """测试函数"""
    formatter = SimpleDocumentFormatter()

    # 测试文件
    test_file = "storage/results/gemini_optimized/顶级模型PK - 到底谁是编程之王？_gemini_optimized.md"

    if Path(test_file).exists():
        output = test_file.replace("_gemini_optimized.md", "_simple_formatted.md")
        formatter.format_file(test_file, output)
    else:
        print(f"测试文件不存在: {test_file}")


if __name__ == "__main__":
    main()