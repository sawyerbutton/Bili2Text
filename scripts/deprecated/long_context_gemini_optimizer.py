#!/usr/bin/env python3
"""
长上下文 Gemini 优化器
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
class LongContextConfig:
    """长上下文优化配置"""
    api_key: str
    model_name: str = "models/gemini-2.5-flash"

    # 充分利用长上下文
    max_document_size: int = 100000  # 10万字，远小于100万token限制

    # 确定性输出
    temperature: float = 0.0
    top_p: float = 0.8
    top_k: int = 20

    # 核心专有名词（最常见的）
    core_terms: Dict[str, str] = field(default_factory=lambda: {
        # AI模型 - 最关键的纠正
        "GEMD": "Gemini", "Gemini 2.5 Pro": "Gemini 2.5 Pro", "JAMM": "Gemini",
        "Dipsyc": "DeepSeek", "Dipstick": "DeepSeek", "DeepSeep": "DeepSeek",
        "Klaus": "Claude", "Klow": "Claude", "Claude3.7": "Claude 3.7",
        "o3-mini-high": "o3-mini-high", "O3 Mini": "o3-mini",

        # 平台
        "Li-Co": "LeetCode", "Lee Code": "LeetCode",

        # 常见错误
        "退力": "推理", "平测": "评测", "平色": "评测",
    })


class LongContextGeminiOptimizer:
    """利用长上下文的Gemini优化器"""

    def __init__(self, config: LongContextConfig):
        self.config = config
        self.setup_api()

    def setup_api(self):
        """配置API"""
        genai.configure(api_key=self.config.api_key)

        # 优化的生成配置
        self.generation_config = {
            'temperature': self.config.temperature,
            'top_p': self.config.top_p,
            'top_k': self.config.top_k,
            'max_output_tokens': 32000,  # 足够大的输出
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
        """优化整个文档 - 一次性处理"""

        # 检查文档大小
        if len(text) > self.config.max_document_size:
            logger.warning(f"文档超长（{len(text)}字），但仍将尝试一次性处理")

        logger.info("开始优化文档...")

        # Step 1: 快速预处理（不改变语义）
        text = self.quick_preprocess(text)

        # Step 2: 一次性深度优化（利用长上下文）
        optimized = self.single_pass_optimization(text)

        # Step 3: 轻量后处理
        final = self.light_postprocess(optimized)

        return final

    def quick_preprocess(self, text: str) -> str:
        """快速预处理 - 只处理明显问题"""
        # 基础清理
        text = re.sub(r'\s+', ' ', text)

        # 快速纠正最常见的错误
        for wrong, correct in self.config.core_terms.items():
            text = text.replace(wrong, correct)

        return text.strip()

    def single_pass_optimization(self, text: str) -> str:
        """单次优化 - 核心方法"""

        # 简洁有效的prompt
        prompt = self.create_effective_prompt(text)

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
                    # 安全过滤 - 使用更简单的prompt
                    logger.info("检测到安全过滤，使用简化prompt")
                    prompt = self.create_minimal_prompt(text)

                elif "quota" in error_msg.lower():
                    logger.warning("API配额问题，等待60秒")
                    time.sleep(60)

                else:
                    # 其他错误，等待后重试
                    time.sleep(5 * (attempt + 1))

        logger.error("所有尝试失败，返回预处理文本")
        return text

    def create_effective_prompt(self, text: str) -> str:
        """创建有效的prompt - 简洁明确"""
        return f"""你是专业的技术文档编辑。请将下面的ASR转录文本优化为格式规范的技术文档。

优化示例：

【原文】
今天我们来测评一下DeepSeek V3034和GEMD2.0 Pro的数据和编程能力这两个模型都是对近刚出的都有所耳闻DeepSeek V3034是第一个DeepSeek V30的升级版

【优化后】
今天我们来测评一下DeepSeek V3.034和Gemini 2.0 Pro的数据和编程能力。

这两个模型都是近期发布的热门模型。DeepSeek V3.034是DeepSeek V3.0的升级版。

主要规则：
1. 每个段落3-5句话，段落间加空行
2. 纠正技术术语（如上例）
3. 添加适当的标点符号
4. 保持原意不变

现在请优化下面的文档：

{text}

优化后的文档：
"""

    def create_minimal_prompt(self, text: str) -> str:
        """最简prompt - 用于规避安全过滤"""
        return f"""请改进下面技术文档的格式，每段3-5句话，段落间加空行：

{text[:10000]}  # 限制长度

改进后的文档：
"""

    def light_postprocess(self, text: str) -> str:
        """轻量后处理"""
        # 确保段落间距
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 清理首尾
        text = text.strip()

        # 如果缺少标题，尝试提取
        if not text.startswith('#'):
            lines = text.split('\n')
            if lines and len(lines[0]) < 100:
                text = f"# {lines[0]}\n\n{''.join(lines[1:])}"

        return text

    def optimize_file(self, input_path: str, output_path: str) -> str:
        """优化文件"""
        logger.info(f"处理文件: {input_path}")

        # 读取
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.info(f"文档大小: {len(content)} 字符")

        # 优化
        optimized = self.optimize_document(content)

        # 保存
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(optimized)

        logger.info(f"保存到: {output_path}")
        return output_path


def test_long_context_optimizer():
    """测试长上下文优化器"""

    config = LongContextConfig(
        api_key=os.getenv("GEMINI_API_KEY", "AIzaSyDAmHzFbKgZMJVp1nyOkVr89MjXM6ahWnE")
    )

    optimizer = LongContextGeminiOptimizer(config)

    # 测试最有问题的文档
    test_doc = "顶级模型PK - 到底谁是编程之王？_gemini_optimized.md"

    input_dir = Path("storage/results/gemini_optimized")
    output_dir = Path("storage/results/gemini_long_context")
    output_dir.mkdir(exist_ok=True)

    input_file = input_dir / test_doc

    if input_file.exists():
        output_file = output_dir / test_doc.replace("_gemini_optimized", "_long_context")

        try:
            # 显示文档大小
            with open(input_file, 'r', encoding='utf-8') as f:
                doc_size = len(f.read())
            logger.info(f"文档大小: {doc_size} 字符 (约 {doc_size//1000}K)")
            logger.info("这远小于Gemini的100万token限制，完全可以一次处理")

            # 优化
            optimizer.optimize_file(str(input_file), str(output_file))
            logger.info("✅ 优化完成")

            # 对比
            logger.info("\n" + "="*60)
            logger.info("建议对比以下文件查看效果：")
            logger.info(f"原始: {input_file}")
            logger.info(f"优化: {output_file}")

        except Exception as e:
            logger.error(f"❌ 优化失败: {e}")
    else:
        logger.error(f"文件不存在: {input_file}")


if __name__ == "__main__":
    test_long_context_optimizer()