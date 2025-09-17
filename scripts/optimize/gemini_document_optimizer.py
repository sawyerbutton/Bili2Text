#!/usr/bin/env python3
"""
Gemini API 文档优化器
使用 Google Gemini API 进行智能文档纠错、结构化和优化
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import google.generativeai as genai
from dataclasses import dataclass, field
import re
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class OptimizationConfig:
    """优化配置"""
    api_key: str
    model_name: str = "models/gemini-2.5-flash"  # 支持: models/gemini-2.5-flash, gemini-2.0-flash-exp, gemini-1.5-flash, gemini-1.5-pro
    max_tokens_per_request: int = 30000
    temperature: float = 0.3
    top_p: float = 0.95
    top_k: int = 40
    cache_enabled: bool = True
    cache_dir: str = "storage/cache/gemini"

    # 专有名词映射表
    term_corrections: Dict[str, str] = field(default_factory=lambda: {
        # AI 模型名称纠正
        "Dipsyc R1": "DeepSeek R1",
        "Dipsyk R1": "DeepSeek R1",
        "Dipsick R1": "DeepSeek R1",
        "DipSix": "DeepSeek",
        "Gorax 3": "Grok 3",
        "Gerrx 3": "Grok 3",
        "Growx3": "Grok 3",
        "GroG3": "Grok 3",
        "Klaus 3.7": "Claude 3.7",
        "Claude3.7": "Claude 3.7",
        "O3 Mini Hide": "o3-mini-high",
        "O3 Mini-Hi": "o3-mini-high",
        "O3 mini害": "o3-mini-high",
        "O100本": "o1-preview",
        "Anstrapet": "Anthropic",

        # 技术术语纠正
        "LiCo": "LeetCode",
        "拼台": "平台",
        "四考": "思考",
        "自考": "思考",
        "Pi Game": "Pygame",
        "JowScript": "JavaScript",
        "DRTML": "HTML",
        "Rex組建": "React组件",
        "X-MINE": "XMind",

        # 其他常见错误
        "边缘": "编译",
        "副置": "复制",
        "站貼": "粘贴",
        "沾貼": "粘贴",
        "沾鐵": "粘贴",
        "負置": "复制",
        "预法错误": "语法错误",
        "韩式": "函数",
        "还是": "函数",
        "15": "食物",
        "肯清牛": "继续",
    })


class GeminiDocumentOptimizer:
    """使用 Gemini API 优化文档"""

    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.setup_api()
        self.setup_cache()

    def setup_api(self):
        """配置 Gemini API"""
        genai.configure(api_key=self.config.api_key)

        # 配置生成参数
        self.generation_config = genai.types.GenerationConfig(
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            top_k=self.config.top_k,
            max_output_tokens=8192,
        )

        # 初始化模型
        self.model = genai.GenerativeModel(
            self.config.model_name,
            generation_config=self.generation_config
        )

    def setup_cache(self):
        """设置缓存目录"""
        if self.config.cache_enabled:
            os.makedirs(self.config.cache_dir, exist_ok=True)

    def get_cache_key(self, text: str, task: str) -> str:
        """生成缓存键"""
        content = f"{task}:{text[:1000]}"  # 使用前1000字符
        return hashlib.md5(content.encode()).hexdigest()

    def get_from_cache(self, cache_key: str) -> Optional[str]:
        """从缓存获取"""
        if not self.config.cache_enabled:
            return None

        cache_file = Path(self.config.cache_dir) / f"{cache_key}.txt"
        if cache_file.exists():
            logger.info(f"从缓存加载: {cache_key}")
            return cache_file.read_text(encoding='utf-8')
        return None

    def save_to_cache(self, cache_key: str, content: str):
        """保存到缓存"""
        if not self.config.cache_enabled:
            return

        cache_file = Path(self.config.cache_dir) / f"{cache_key}.txt"
        cache_file.write_text(content, encoding='utf-8')

    def apply_term_corrections(self, text: str) -> str:
        """应用专有名词纠正"""
        result = text
        for wrong, correct in self.config.term_corrections.items():
            # 使用正则表达式进行不区分大小写的替换
            pattern = re.compile(re.escape(wrong), re.IGNORECASE)
            result = pattern.sub(correct, result)
        return result

    def split_text(self, text: str, max_length: int = 30000) -> List[str]:
        """智能分割文本"""
        if len(text) <= max_length:
            return [text]

        chunks = []
        sentences = re.split(r'[。！？\n]+', text)
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) > max_length:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
            else:
                current_chunk += sentence + "。"

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def correct_and_structure(self, text: str) -> str:
        """纠错并结构化文本"""
        cache_key = self.get_cache_key(text, "correct_structure")
        cached = self.get_from_cache(cache_key)
        if cached:
            return cached

        prompt = f"""
请对以下语音转录文本进行智能优化：

1. **纠正识别错误**：
   - 修正AI模型名称（DeepSeek R1, Grok 3, Claude 3.7, o3-mini-high等）
   - 修正技术术语（LeetCode, JavaScript, HTML, React等）
   - 修正中文识别错误

2. **结构化组织**：
   - 添加合适的段落划分
   - 使用清晰的标题层级
   - 保持逻辑连贯性

3. **内容优化**：
   - 去除口语化表达和重复内容
   - 保留关键信息和核心观点
   - 使用专业技术写作风格

4. **格式要求**：
   - 使用Markdown格式
   - 标题使用##、###等
   - 重点内容用**粗体**标记

原始文本：
{text}

请直接输出优化后的文档内容，不要包含任何解释或说明。
"""

        try:
            response = self.model.generate_content(prompt)
            result = response.text
            self.save_to_cache(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Gemini API 错误: {e}")
            # 降级处理：仅应用基础纠错
            return self.apply_term_corrections(text)

    def extract_key_information(self, text: str) -> Dict:
        """提取关键信息"""
        cache_key = self.get_cache_key(text, "extract_info")
        cached = self.get_from_cache(cache_key)
        if cached:
            return json.loads(cached)

        prompt = f"""
从以下文本中提取关键信息，以JSON格式返回：

{{
    "title": "文档标题",
    "summary": "简短摘要（50字以内）",
    "key_points": ["关键点1", "关键点2", ...],
    "models_mentioned": ["提到的AI模型"],
    "test_results": {{
        "model_name": {{
            "algorithm_score": "算法测试结果",
            "engineering_score": "工程测试结果"
        }}
    }},
    "conclusions": ["主要结论"],
    "recommendations": ["使用建议"]
}}

文本：
{text[:5000]}  # 只使用前5000字符提取关键信息

请只返回JSON，不要包含其他内容。
"""

        try:
            response = self.model.generate_content(prompt)
            # 提取JSON内容
            json_text = response.text
            json_match = re.search(r'\{.*\}', json_text, re.DOTALL)
            if json_match:
                json_text = json_match.group()

            result = json.loads(json_text)
            self.save_to_cache(cache_key, json.dumps(result, ensure_ascii=False))
            return result
        except Exception as e:
            logger.error(f"信息提取错误: {e}")
            return {}

    def generate_structured_document(self, text: str, metadata: Dict = None) -> str:
        """生成结构化文档"""
        # 1. 先应用基础纠错
        text = self.apply_term_corrections(text)

        # 2. 提取关键信息
        key_info = self.extract_key_information(text)

        # 3. 分段处理长文本
        chunks = self.split_text(text, self.config.max_tokens_per_request)
        optimized_chunks = []

        for i, chunk in enumerate(chunks):
            logger.info(f"处理第 {i+1}/{len(chunks)} 段...")
            optimized = self.correct_and_structure(chunk)
            optimized_chunks.append(optimized)

            # 避免API限流
            if i < len(chunks) - 1:
                time.sleep(1)

        # 4. 合并优化后的文本
        full_text = "\n\n".join(optimized_chunks)

        # 5. 生成最终文档
        document = self.format_final_document(full_text, key_info, metadata)

        return document

    def format_final_document(self, content: str, key_info: Dict, metadata: Dict = None) -> str:
        """格式化最终文档"""
        doc_parts = []

        # 添加元数据头部
        if metadata:
            doc_parts.append(f"---")
            doc_parts.append(f"title: {metadata.get('title', '未命名文档')}")
            doc_parts.append(f"date: {metadata.get('date', '')}")
            doc_parts.append(f"source: {metadata.get('source', '')}")
            doc_parts.append(f"---\n")

        # 添加标题和摘要
        title = key_info.get('title', '文档标题')
        doc_parts.append(f"# {title}\n")

        if key_info.get('summary'):
            doc_parts.append(f"> **摘要**: {key_info['summary']}\n")

        # 添加关键点
        if key_info.get('key_points'):
            doc_parts.append("## 关键要点\n")
            for point in key_info['key_points']:
                doc_parts.append(f"- {point}")
            doc_parts.append("")

        # 添加主体内容
        doc_parts.append("## 详细内容\n")
        doc_parts.append(content)

        # 添加测试结果表格（如果有）
        if key_info.get('test_results'):
            doc_parts.append("\n## 测试结果汇总\n")
            doc_parts.append("| 模型 | 算法测试 | 工程测试 |")
            doc_parts.append("|------|----------|----------|")
            for model, scores in key_info['test_results'].items():
                algo = scores.get('algorithm_score', 'N/A')
                eng = scores.get('engineering_score', 'N/A')
                doc_parts.append(f"| {model} | {algo} | {eng} |")
            doc_parts.append("")

        # 添加结论
        if key_info.get('conclusions'):
            doc_parts.append("## 结论\n")
            for conclusion in key_info['conclusions']:
                doc_parts.append(f"- {conclusion}")
            doc_parts.append("")

        # 添加建议
        if key_info.get('recommendations'):
            doc_parts.append("## 使用建议\n")
            for rec in key_info['recommendations']:
                doc_parts.append(f"- {rec}")

        return "\n".join(doc_parts)

    def optimize_file(self, input_path: str, output_path: str = None) -> str:
        """优化文件"""
        logger.info(f"开始优化文件: {input_path}")

        # 读取输入文件
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取元数据
        metadata = {
            'title': Path(input_path).stem,
            'source': input_path,
            'date': time.strftime('%Y-%m-%d')
        }

        # 生成优化后的文档
        optimized = self.generate_structured_document(content, metadata)

        # 保存结果
        if output_path is None:
            output_path = input_path.replace('.md', '_gemini_optimized.md')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(optimized)

        logger.info(f"优化完成，已保存到: {output_path}")
        return output_path


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='使用 Gemini API 优化文档')
    parser.add_argument('input', help='输入文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('--api-key', help='Gemini API Key',
                       default=os.getenv('GEMINI_API_KEY'))
    parser.add_argument('--model', default='models/gemini-2.5-flash',
                       choices=['models/gemini-2.5-flash', 'gemini-2.0-flash-exp', 'gemini-1.5-flash', 'gemini-1.5-pro'],
                       help='使用的模型')
    parser.add_argument('--no-cache', action='store_true', help='禁用缓存')

    args = parser.parse_args()

    if not args.api_key:
        print("错误：请提供 Gemini API Key")
        print("可以通过 --api-key 参数或设置 GEMINI_API_KEY 环境变量")
        return 1

    # 创建配置
    config = OptimizationConfig(
        api_key=args.api_key,
        model_name=args.model,
        cache_enabled=not args.no_cache
    )

    # 创建优化器并处理文件
    optimizer = GeminiDocumentOptimizer(config)
    optimizer.optimize_file(args.input, args.output)

    return 0


if __name__ == '__main__':
    exit(main())