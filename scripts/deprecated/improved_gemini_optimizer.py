#!/usr/bin/env python3
"""
改进版 Gemini 文档优化器
基于问题分析实施的优化方案
"""

import os
import re
import time
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import google.generativeai as genai
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ImprovedOptimizationConfig:
    """改进的优化配置"""
    api_key: str
    model_name: str = "models/gemini-2.5-flash"

    # 关键参数调整 - 追求稳定性
    temperature: float = 0.0  # 完全确定性输出
    top_p: float = 0.8       # 降低随机性
    top_k: int = 20          # 限制词汇选择

    # 分块策略优化
    max_tokens_per_request: int = 5000  # 更小的块
    chunk_overlap: int = 500             # 块间重叠

    # 重试机制
    max_retries: int = 3
    retry_delay: int = 5

    # 扩展的专有名词映射表
    term_corrections: Dict[str, str] = field(default_factory=lambda: {
        # AI模型名称
        "GEMD": "Gemini", "JAMM": "Gemini", "Germanard": "Gemini",
        "Dipsyc": "DeepSeek", "Dipstick": "DeepSeek", "Dipsyk": "DeepSeek",
        "Klaus": "Claude", "Klow": "Claude", "Gloss": "Claude",
        "o3-mini-high": "o3-mini-high", "O3 Mini": "o3-mini",

        # 平台和工具
        "Li-Co": "LeetCode", "Lee Code": "LeetCode",
        "Pi Game": "Pygame", "拍Germanard": "Pygame",
        "3rdjs": "Three.js", "7s": "Three.js",

        # 技术术语
        "退力": "推理", "平仇": "评测", "平色": "评测",
        "自考": "思考", "四考": "思考",
        "边缘": "编译", "副置": "复制", "站貼": "粘贴",
        "预法错误": "语法错误", "韩式": "函数",
    })


class ImprovedGeminiOptimizer:
    """改进版Gemini文档优化器"""

    def __init__(self, config: ImprovedOptimizationConfig):
        self.config = config
        self.setup_api()

    def setup_api(self):
        """配置API"""
        genai.configure(api_key=self.config.api_key)

        # 严格的生成配置
        self.generation_config = genai.types.GenerationConfig(
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            top_k=self.config.top_k,
            max_output_tokens=8192,
        )

        # 安全设置 - 避免过滤
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]

        self.model = genai.GenerativeModel(
            model_name=self.config.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )

    def process_document(self, text: str) -> str:
        """分阶段处理文档"""
        logger.info("开始文档优化处理...")

        # 阶段1: 基础清理
        logger.info("阶段1: 基础清理")
        text = self.stage1_basic_cleaning(text)

        # 阶段2: 专有名词纠正
        logger.info("阶段2: 专有名词纠正")
        text = self.stage2_term_correction(text)

        # 阶段3: 句子分割和段落组织
        logger.info("阶段3: 段落组织")
        text = self.stage3_paragraph_organization(text)

        # 阶段4: AI深度优化（小块处理）
        logger.info("阶段4: AI深度优化")
        text = self.stage4_ai_enhancement(text)

        # 阶段5: 最终格式验证
        logger.info("阶段5: 格式验证")
        text = self.stage5_format_validation(text)

        return text

    def stage1_basic_cleaning(self, text: str) -> str:
        """基础清理"""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 确保标点后有空格
        text = re.sub(r'([。！？])(?=[^\s])', r'\1 ', text)
        # 移除重复标点
        text = re.sub(r'([。！？])\1+', r'\1', text)
        return text.strip()

    def stage2_term_correction(self, text: str) -> str:
        """专有名词纠正"""
        for wrong, correct in self.config.term_corrections.items():
            # 使用正则进行更智能的替换
            pattern = re.compile(re.escape(wrong), re.IGNORECASE)
            text = pattern.sub(correct, text)
        return text

    def stage3_paragraph_organization(self, text: str) -> str:
        """段落组织"""
        # 分句
        sentences = re.split(r'([。！？])', text)

        # 重组句子
        full_sentences = []
        for i in range(0, len(sentences)-1, 2):
            if i+1 < len(sentences):
                full_sentences.append(sentences[i] + sentences[i+1])

        # 组织成段落（每3-5句一段）
        paragraphs = []
        current_para = []

        for sentence in full_sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            current_para.append(sentence)

            # 检查是否应该结束段落
            if len(current_para) >= 3:
                # 简单的语义边界检测
                if self.is_paragraph_boundary(sentence):
                    paragraphs.append(' '.join(current_para))
                    current_para = []
                elif len(current_para) >= 5:
                    paragraphs.append(' '.join(current_para))
                    current_para = []

        if current_para:
            paragraphs.append(' '.join(current_para))

        return '\n\n'.join(paragraphs)

    def is_paragraph_boundary(self, sentence: str) -> bool:
        """检测段落边界"""
        # 段落结束的标志
        boundary_markers = [
            '综上所述', '总之', '因此', '所以', '最后',
            '接下来', '然后', '首先', '其次', '另外',
            '下面', '现在', '那么'
        ]
        return any(marker in sentence for marker in boundary_markers)

    def stage4_ai_enhancement(self, text: str) -> str:
        """AI深度优化 - 小块处理"""
        # 智能分块
        chunks = self.smart_split(text)
        enhanced_chunks = []

        for i, chunk in enumerate(chunks):
            logger.info(f"处理第 {i+1}/{len(chunks)} 块...")

            # 准备上下文
            context_hint = ""
            if i > 0:
                context_hint = f"（续前文）"

            enhanced = self.enhance_chunk_with_ai(chunk, context_hint)
            enhanced_chunks.append(enhanced)

            # 避免API限制
            if i < len(chunks) - 1:
                time.sleep(2)

        return '\n\n'.join(enhanced_chunks)

    def smart_split(self, text: str) -> List[str]:
        """智能分块 - 保持段落完整性"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para)

            if current_size + para_size > self.config.max_tokens_per_request:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size

        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        return chunks

    def enhance_chunk_with_ai(self, chunk: str, context_hint: str = "") -> str:
        """使用AI增强单个块"""
        prompt = f"""
你是专业的技术文档编辑。请优化以下文本，严格遵守格式要求。

【格式要求】
1. 保持段落结构（3-5句为一段）
2. 段落间必须有空行
3. 使用Markdown格式
4. 纠正所有技术术语

【示例格式】
这是第一段，包含3-5个句子。每个句子清晰明了。段落结束后有空行。

这是第二段，与上段用空行分隔。专有名词如DeepSeek、Claude都正确。

【待优化文本】{context_hint}
{chunk}

【输出】
直接输出优化后的文本，不要任何说明：
"""

        # 重试机制
        for attempt in range(self.config.max_retries):
            try:
                response = self.model.generate_content(prompt)

                if response and response.text:
                    return response.text.strip()

            except Exception as e:
                logger.warning(f"API调用失败 (尝试 {attempt+1}/{self.config.max_retries}): {e}")

                if "finish_reason" in str(e) and "2" in str(e):
                    # 安全过滤器 - 简化prompt
                    prompt = self.simplify_prompt(prompt, chunk)

                time.sleep(self.config.retry_delay * (attempt + 1))

        # 所有尝试失败，返回原文
        logger.error("API调用完全失败，返回原文")
        return chunk

    def simplify_prompt(self, original_prompt: str, chunk: str) -> str:
        """简化prompt以避免安全过滤"""
        return f"""
请改进以下技术文档的格式：

要求：
- 每段3-5句话
- 段落间加空行
- 纠正技术术语

文本：
{chunk[:2000]}  # 限制长度

输出改进后的文本：
"""

    def stage5_format_validation(self, text: str) -> str:
        """最终格式验证和修正"""
        # 确保段落间距
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 添加标题（如果缺失）
        if not text.startswith('#'):
            lines = text.split('\n')
            if lines:
                # 尝试提取标题
                first_line = lines[0].strip()
                if len(first_line) < 100:  # 可能是标题
                    text = f"# {first_line}\n\n" + '\n'.join(lines[1:])

        # 确保末尾干净
        text = text.strip()

        return text

    def optimize_file(self, input_path: str, output_path: str):
        """优化文件"""
        logger.info(f"开始优化: {input_path}")

        # 读取文件
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 处理文档
        optimized = self.process_document(content)

        # 保存结果
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(optimized)

        logger.info(f"优化完成: {output_path}")
        return output_path


def main():
    """测试改进版优化器"""
    config = ImprovedOptimizationConfig(
        api_key=os.getenv("GEMINI_API_KEY", "AIzaSyDAmHzFbKgZMJVp1nyOkVr89MjXM6ahWnE"),
        temperature=0.0,  # 完全确定性
        max_tokens_per_request=5000  # 小块处理
    )

    optimizer = ImprovedGeminiOptimizer(config)

    # 测试文档
    test_docs = [
        "顶级模型PK - 到底谁是编程之王？_gemini_optimized.md"
    ]

    input_dir = Path("storage/results/gemini_optimized")
    output_dir = Path("storage/results/gemini_improved")
    output_dir.mkdir(exist_ok=True)

    for doc_name in test_docs:
        input_file = input_dir / doc_name
        if input_file.exists():
            output_name = doc_name.replace("_gemini_optimized.md", "_improved.md")
            output_file = output_dir / output_name

            try:
                optimizer.optimize_file(str(input_file), str(output_file))
                logger.info(f"✅ 成功: {output_name}")
            except Exception as e:
                logger.error(f"❌ 失败: {doc_name} - {e}")


if __name__ == "__main__":
    main()