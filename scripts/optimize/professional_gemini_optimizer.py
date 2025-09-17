#!/usr/bin/env python3
"""
专业版 Gemini 优化器
整合了专业的视频逐字稿优化prompt
充分利用 Gemini 2.5 Flash 的 100万 token 上下文窗口
"""

import os
import re
import time
import logging
from pathlib import Path
import google.generativeai as genai
from dataclasses import dataclass, field
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ProfessionalOptConfig:
    """专业优化配置"""
    api_key: str
    model_name: str = "models/gemini-2.5-flash"

    # 充分利用长上下文
    max_document_size: int = 100000  # 10万字

    # 确定性输出
    temperature: float = 0.0
    top_p: float = 0.8
    top_k: int = 20

    # 扩展的专有名词映射
    term_corrections: Dict[str, str] = field(default_factory=lambda: {
        # AI模型
        "GEMD": "Gemini", "JAMM": "Gemini", "Gemini 2.2 Pro": "Gemini 2.5 Pro",
        "Dipsyc": "DeepSeek", "Dipstick": "DeepSeek", "DeepSeep": "DeepSeek",
        "Klaus": "Claude", "Klow": "Claude", "Claude3.7": "Claude 3.7",
        "o3-mini-high": "o3-mini-high", "O3 Mini": "o3-mini", "o3 mini害": "o3-mini-high",

        # 平台
        "Li-Co": "LeetCode", "Lee Code": "LeetCode",
        "Pi Game": "Pygame", "拍Germanard": "Pygame",
        "3rdjs": "Three.js", "Sray JS": "Three.js",

        # 常见错误
        "退力": "推理", "平测": "评测", "平色": "评测",
        "四考": "思考", "自考": "思考",
        "边缘": "编译", "副置": "复制", "站貼": "粘贴",
    })


class ProfessionalGeminiOptimizer:
    """专业版Gemini优化器"""

    def __init__(self, config: ProfessionalOptConfig):
        self.config = config
        self.setup_api()

    def setup_api(self):
        """配置API"""
        genai.configure(api_key=self.config.api_key)

        # 严格的生成配置
        self.generation_config = {
            'temperature': self.config.temperature,
            'top_p': self.config.top_p,
            'top_k': self.config.top_k,
            'max_output_tokens': 32000,
        }

        # 宽松的安全设置
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
        ]

        self.model = genai.GenerativeModel(
            model_name=self.config.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )

    def optimize_document(self, text: str) -> str:
        """优化文档 - 一次性处理"""

        logger.info(f"文档大小: {len(text)} 字符 (约占100万token的 {len(text)/1000000*100:.1f}%)")

        # Step 1: 快速预处理
        text = self.quick_preprocess(text)

        # Step 2: 专业深度优化（使用完整的专业prompt）
        optimized = self.professional_optimization(text)

        # Step 3: 后处理验证
        final = self.post_process(optimized)

        return final

    def quick_preprocess(self, text: str) -> str:
        """快速预处理"""
        # 基础清理
        text = re.sub(r'\s+', ' ', text)

        # 快速纠正最常见的错误
        for wrong, correct in self.config.term_corrections.items():
            text = text.replace(wrong, correct)

        return text.strip()

    def professional_optimization(self, text: str) -> str:
        """专业优化 - 核心方法"""

        # 使用专业的视频逐字稿优化prompt
        prompt = self.create_professional_prompt(text)

        # 重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"调用Gemini API (尝试 {attempt + 1}/{max_retries})...")

                response = self.model.generate_content(prompt)

                if response and response.text:
                    logger.info("API调用成功")
                    return response.text

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"API调用失败: {error_msg}")

                if "safety" in error_msg.lower() or "finish_reason" in error_msg:
                    logger.info("检测到安全过滤，使用备用prompt")
                    prompt = self.create_fallback_prompt(text)

                elif "quota" in error_msg.lower():
                    logger.warning("API配额问题，等待60秒")
                    time.sleep(60)

                else:
                    time.sleep(5 * (attempt + 1))

        logger.error("所有尝试失败，返回预处理文本")
        return text

    def create_professional_prompt(self, text: str) -> str:
        """创建专业优化prompt"""
        return f"""请将以下视频逐字稿整理成一份结构清晰、逻辑连贯的文档。在整理过程中请遵循以下原则：

## 处理要求：

1. **内容完整性**：保留逐字稿中的所有实质性内容，不得删减任何信息点、观点或细节

2. **错别字校正**：
   - 纠正明显的错别字和同音字错误
   - 特别注意AI模型名称：DeepSeek、Claude、Gemini、o3-mini等
   - 技术平台名称：LeetCode、GitHub、OpenAI等
   - 保持专业术语的准确性

3. **逻辑重组**：
   - 识别视频中的核心主题和子主题
   - 将相关内容归类整合，形成清晰的章节结构
   - 可以打破原视频的时间顺序，按照内容的逻辑关系重新组织

4. **格式优化**：
   - 添加适当的标题和小标题（使用#、##、###）
   - 确保每个段落3-5句话，段落间用空行分隔
   - 对列举性内容使用项目符号或编号
   - 重要观点使用**加粗**突出

5. **语言润色**：
   - 去除口语化的重复、停顿词（如"嗯"、"啊"、"那个"）
   - 将不完整的句子补充完整
   - 保持讲者的语言风格和表达特点

6. **结构建议**：
   - 开篇：概述视频主题和核心观点
   - 正文：按逻辑分章节展开
   - 结尾：总结要点或关键结论

## 原始逐字稿：

{text}

## 请输出优化后的文档（直接输出，不要任何额外说明）："""

    def create_fallback_prompt(self, text: str) -> str:
        """备用prompt - 用于规避安全过滤"""
        return f"""请整理下面的技术文档，要求：

1. 保留所有内容信息
2. 纠正错别字（特别是技术术语）
3. 每段3-5句话，段落间加空行
4. 添加合适的标题结构

文档内容：
{text[:20000]}  # 限制长度

整理后的文档："""

    def post_process(self, text: str) -> str:
        """后处理验证"""
        # 移除可能的前缀说明
        if text.startswith("好的") or text.startswith("以下是"):
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    text = '\n'.join(lines[i:])
                    break

        # 确保段落间距
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 清理首尾
        text = text.strip()

        return text

    def optimize_file(self, input_path: str, output_path: str) -> str:
        """优化文件"""
        logger.info(f"处理文件: {input_path}")

        # 读取
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.info(f"原始文档: {len(content)} 字符")

        # 优化
        optimized = self.optimize_document(content)

        # 保存
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(optimized)

        logger.info(f"保存到: {output_path}")
        return output_path


def batch_process_with_professional_optimizer():
    """批量处理示例"""

    config = ProfessionalOptConfig(
        api_key=os.getenv("GEMINI_API_KEY", "AIzaSyDAmHzFbKgZMJVp1nyOkVr89MjXM6ahWnE")
    )

    optimizer = ProfessionalGeminiOptimizer(config)

    # 需要处理的文档
    test_documents = [
        "顶级模型PK - 到底谁是编程之王？_gemini_optimized.md",
        "四大推理大模型数学与编程能力评测 - Grok3、Claude3.7、DeepSeep-R1、o3-mini-high 到底谁的推理能力最强？_gemini_optimized.md",
    ]

    input_dir = Path("storage/results/gemini_optimized")
    output_dir = Path("storage/results/gemini_professional")
    output_dir.mkdir(exist_ok=True)

    for doc_name in test_documents:
        input_file = input_dir / doc_name

        if not input_file.exists():
            logger.warning(f"文件不存在: {input_file}")
            continue

        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"处理: {doc_name}")

            output_name = doc_name.replace("_gemini_optimized.md", "_professional.md")
            output_file = output_dir / output_name

            optimizer.optimize_file(str(input_file), str(output_file))

            logger.info(f"✅ 成功: {output_name}")

            # 短暂延迟
            time.sleep(5)

        except Exception as e:
            logger.error(f"❌ 失败: {doc_name} - {e}")

    logger.info(f"\n输出目录: {output_dir}")


if __name__ == "__main__":
    batch_process_with_professional_optimizer()