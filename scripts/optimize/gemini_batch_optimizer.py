#!/usr/bin/env python3
"""
批量优化文档 - 使用 Gemini API
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from gemini_document_optimizer import GeminiDocumentOptimizer, OptimizationConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchOptimizer:
    """批量文档优化器"""

    def __init__(self, config_path: str = "config/gemini_config.json"):
        self.load_config(config_path)
        self.optimizer = GeminiDocumentOptimizer(self.config)
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

    def load_config(self, config_path: str):
        """加载配置"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        else:
            # 使用默认配置
            config_data = {
                'api_key': os.getenv('GEMINI_API_KEY'),
                'model_name': 'models/gemini-2.5-flash',
                'temperature': 0.3,
                'cache_enabled': True
            }

        # 扩展专有名词纠正表
        term_corrections = {
            # AI 模型名称
            "Dipsyc R1": "DeepSeek R1",
            "Dipsyk R1": "DeepSeek R1",
            "Dipsick R1": "DeepSeek R1",
            "DipSix": "DeepSeek",
            "Deep Seek": "DeepSeek",
            "DeepSeep": "DeepSeek",

            "Gorax 3": "Grok 3",
            "Gerrx 3": "Grok 3",
            "Growx3": "Grok 3",
            "Growx 3": "Grok 3",
            "GroG3": "Grok 3",
            "GroG 3": "Grok 3",

            "Klaus 3.7": "Claude 3.7",
            "Claude3.7": "Claude 3.7",
            "Claude 37": "Claude 3.7",
            "Clause": "Claude",

            "O3 Mini Hide": "o3-mini-high",
            "O3 Mini-Hi": "o3-mini-high",
            "O3 mini害": "o3-mini-high",
            "o3-mini害": "o3-mini-high",
            "O3 Mini Height": "o3-mini-high",
            "O3面臨害": "o3-mini-high",

            "O100本": "o1-preview",
            "O1": "o1",

            "Anstrapet": "Anthropic",
            "Anstropic": "Anthropic",

            # 平台和工具
            "LiCo": "LeetCode",
            "Leet Code": "LeetCode",
            "力扣": "LeetCode",

            "X-MINE": "XMind",
            "X Mind": "XMind",

            "Pi Game": "Pygame",
            "PyGame": "Pygame",

            "JowScript": "JavaScript",
            "Java Script": "JavaScript",

            "DRTML": "HTML",
            "drtml": "HTML",

            "Rex組建": "React组件",
            "React組件": "React组件",

            # 技术术语
            "拼台": "平台",
            "四考": "思考",
            "自考": "思考",
            "边缘": "编译",
            "副置": "复制",
            "負置": "复制",
            "站貼": "粘贴",
            "沾貼": "粘贴",
            "沾鐵": "粘贴",
            "预法错误": "语法错误",
            "預法错误": "语法错误",
            "韩式": "函数",
            "還是": "函数",
            "15": "食物",
            "肯清牛": "继续",
            "界點": "节点",
            "接點": "节点",
            "捷點": "节点",
            "根捷點": "根节点",
            "根接點": "根节点",
            "米宮": "迷宫",
            "變程序準": "编程水平",
            "大魔型": "大模型",
            "大魔形": "大模型",
            "大波型": "大模型",
        }

        config_data['term_corrections'] = term_corrections

        self.config = OptimizationConfig(**config_data)

    def find_files(self, input_dir: str, pattern: str = "*.md") -> List[Path]:
        """查找待优化的文件"""
        input_path = Path(input_dir)
        files = []

        if input_path.is_file():
            files = [input_path]
        else:
            files = list(input_path.rglob(pattern))

        # 过滤已优化的文件
        files = [f for f in files if 'optimized' not in f.name and 'gemini' not in f.name]

        return files

    def optimize_single_file(self, file_path: Path, output_dir: Path) -> Dict:
        """优化单个文件"""
        result = {
            'file': str(file_path),
            'status': 'pending',
            'output': None,
            'error': None
        }

        try:
            # 确定输出路径
            relative_path = file_path.relative_to(file_path.parent.parent) if file_path.parent.parent.exists() else file_path.name
            output_path = output_dir / f"{file_path.stem}_gemini_optimized.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            logger.info(f"优化文件: {file_path}")

            # 执行优化
            self.optimizer.optimize_file(str(file_path), str(output_path))

            result['status'] = 'success'
            result['output'] = str(output_path)
            self.stats['success'] += 1

        except Exception as e:
            logger.error(f"优化失败 {file_path}: {e}")
            result['status'] = 'failed'
            result['error'] = str(e)
            self.stats['failed'] += 1

        return result

    def optimize_batch(self, input_dir: str, output_dir: str, max_workers: int = 1):
        """批量优化"""
        files = self.find_files(input_dir)
        self.stats['total'] = len(files)

        if not files:
            logger.warning("没有找到待优化的文件")
            return []

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"找到 {len(files)} 个文件待优化")

        results = []

        # 使用线程池处理（注意：Gemini API 有速率限制）
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.optimize_single_file, f, output_path): f
                for f in files
            }

            for future in as_completed(future_to_file):
                result = future.result()
                results.append(result)

                # 显示进度
                processed = self.stats['success'] + self.stats['failed']
                logger.info(f"进度: {processed}/{self.stats['total']}")

                # 避免API限流
                time.sleep(2)

        return results

    def print_summary(self):
        """打印处理摘要"""
        print("\n" + "="*50)
        print("处理完成")
        print("="*50)
        print(f"总文件数: {self.stats['total']}")
        print(f"成功: {self.stats['success']}")
        print(f"失败: {self.stats['failed']}")
        print(f"跳过: {self.stats['skipped']}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='批量优化文档')
    parser.add_argument('input_dir', help='输入目录或文件')
    parser.add_argument('-o', '--output-dir', default='storage/results/gemini_optimized',
                       help='输出目录')
    parser.add_argument('-c', '--config', default='config/gemini_config.json',
                       help='配置文件路径')
    parser.add_argument('-w', '--workers', type=int, default=1,
                       help='并发数（注意API限流）')

    args = parser.parse_args()

    # 检查API Key
    if not os.getenv('GEMINI_API_KEY'):
        print("错误：请设置环境变量 GEMINI_API_KEY")
        print("export GEMINI_API_KEY='your-api-key'")
        return 1

    # 创建优化器
    optimizer = BatchOptimizer(args.config)

    # 执行批量优化
    results = optimizer.optimize_batch(
        args.input_dir,
        args.output_dir,
        args.workers
    )

    # 保存处理结果
    result_file = Path(args.output_dir) / 'optimization_report.json'
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 打印摘要
    optimizer.print_summary()

    return 0


if __name__ == '__main__':
    exit(main())