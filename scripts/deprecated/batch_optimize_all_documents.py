#!/usr/bin/env python3
"""
批量优化所有文档 - 使用 Gemini 2.5 Flash
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import List, Dict
import logging

# 添加项目根目录
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.optimize.gemini_document_optimizer import GeminiDocumentOptimizer, OptimizationConfig
import google.generativeai as genai

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API配置
API_KEY = "AIzaSyDAmHzFbKgZMJVp1nyOkVr89MjXM6ahWnE"


class BatchDocumentOptimizer:
    """批量文档优化器"""

    def __init__(self):
        self.config = OptimizationConfig(
            api_key=API_KEY,
            model_name='models/gemini-2.5-flash',
            temperature=0.3,
            cache_enabled=True,
            max_tokens_per_request=8000  # 适中的请求大小
        )
        self.optimizer = GeminiDocumentOptimizer(self.config)
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')

        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

        # 进度文件
        self.progress_file = Path("batch_progress.json")
        self.load_progress()

    def load_progress(self):
        """加载进度"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.progress = json.load(f)
        else:
            self.progress = {'completed': [], 'failed': []}

    def save_progress(self):
        """保存进度"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)

    def find_documents(self, input_dir: str) -> List[Path]:
        """查找所有待优化文档"""
        input_path = Path(input_dir)
        files = list(input_path.glob("*.md"))

        # 过滤已完成的文件
        files = [f for f in files if str(f) not in self.progress['completed']]

        return sorted(files)

    def optimize_single_document(self, input_file: Path, output_dir: Path) -> bool:
        """优化单个文档"""
        try:
            # 生成输出文件名
            output_name = input_file.stem.replace('_深度优化版', '').replace('_专家优化版', '')
            output_name = f"{output_name}_gemini25_optimized.md"
            output_file = output_dir / output_name

            logger.info(f"开始优化: {input_file.name}")

            # 读取文件
            content = input_file.read_text(encoding='utf-8')
            file_size = len(content)

            # 1. 基础纠错
            logger.info("  第1步：基础纠错...")
            corrected = self.optimizer.apply_term_corrections(content)

            # 2. 智能优化（分段处理大文件）
            logger.info("  第2步：AI深度优化...")

            if file_size > 10000:
                # 大文件：只处理前8000字符
                sample_size = 8000
                sample_text = corrected[:sample_size]
                logger.info(f"  文件较大({file_size}字符)，优化前{sample_size}字符")
            else:
                # 小文件：全部处理
                sample_text = corrected
                sample_size = file_size

            # 分段处理
            chunks = self.optimizer.split_text(sample_text, max_length=3000)
            optimized_parts = []

            for i, chunk in enumerate(chunks):
                logger.info(f"    处理段落 {i+1}/{len(chunks)}...")

                prompt = f"""
请将以下语音转录文本优化为专业的技术文档：

要求：
1. 纠正所有专有名词错误（如AI模型名称、技术术语）
2. 改善段落结构，添加合适的标题层级
3. 去除口语化表达和重复内容
4. 保持原意不变，但使表达更专业
5. 使用Markdown格式

原文：
{chunk}

请直接输出优化后的内容，不要包含任何说明：
"""

                try:
                    response = self.model.generate_content(prompt)
                    optimized_parts.append(response.text)

                    # 避免API限流
                    if i < len(chunks) - 1:
                        time.sleep(2)

                except Exception as e:
                    logger.warning(f"    段落{i+1}优化失败: {e}")
                    # 降级：使用纠错版本
                    optimized_parts.append(chunk)

            # 合并结果
            optimized_content = "\n\n".join(optimized_parts)

            # 如果文档很长，添加剩余的纠错内容
            if file_size > sample_size:
                optimized_content += f"\n\n---\n\n_[注：以下为基础纠错内容，未经AI深度优化]_\n\n"
                optimized_content += corrected[sample_size:]

            # 保存结果
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(optimized_content, encoding='utf-8')

            logger.info(f"  ✅ 成功！输出: {output_file.name}")

            # 记录进度
            self.progress['completed'].append(str(input_file))
            self.save_progress()

            self.stats['success'] += 1
            return True

        except Exception as e:
            logger.error(f"  ❌ 失败: {e}")
            self.progress['failed'].append(str(input_file))
            self.save_progress()
            self.stats['failed'] += 1
            return False

    def optimize_all(self, input_dir: str, output_dir: str):
        """批量优化所有文档"""
        # 查找文档
        files = self.find_documents(input_dir)
        self.stats['total'] = len(files)

        if not files:
            logger.info("没有待优化的文档（可能都已完成）")
            return

        logger.info(f"找到 {len(files)} 个待优化文档")

        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 处理每个文档
        for idx, file in enumerate(files, 1):
            logger.info(f"\n[{idx}/{len(files)}] 处理文档...")

            # 优化文档
            success = self.optimize_single_document(file, output_path)

            # 显示进度
            progress_pct = (self.stats['success'] + self.stats['failed']) / self.stats['total'] * 100
            logger.info(f"总进度: {progress_pct:.1f}% "
                       f"(成功: {self.stats['success']}, 失败: {self.stats['failed']})")

            # 休息一下，避免API限流
            if idx < len(files):
                wait_time = 3
                logger.info(f"等待{wait_time}秒...")
                time.sleep(wait_time)

    def print_summary(self):
        """打印处理摘要"""
        logger.info("\n" + "="*60)
        logger.info("批量优化完成")
        logger.info("="*60)
        logger.info(f"总文档数: {self.stats['total']}")
        logger.info(f"成功: {self.stats['success']}")
        logger.info(f"失败: {self.stats['failed']}")
        logger.info(f"跳过: {self.stats['skipped']}")

        if self.stats['failed'] > 0:
            logger.info("\n失败的文档:")
            for doc in self.progress['failed']:
                logger.info(f"  - {Path(doc).name}")

        # 清理进度文件（如果全部成功）
        if self.stats['failed'] == 0 and self.stats['success'] == self.stats['total']:
            self.progress_file.unlink(missing_ok=True)
            logger.info("\n✅ 所有文档优化成功，已清理进度文件")


def main():
    """主函数"""
    # 配置
    input_dir = "storage/results/expert_optimized"
    output_dir = "storage/results/gemini_optimized"

    logger.info("="*60)
    logger.info("Gemini 2.5 Flash 批量文档优化")
    logger.info("="*60)
    logger.info(f"输入目录: {input_dir}")
    logger.info(f"输出目录: {output_dir}")
    logger.info(f"API模型: models/gemini-2.5-flash")

    # 创建优化器
    optimizer = BatchDocumentOptimizer()

    try:
        # 执行批量优化
        optimizer.optimize_all(input_dir, output_dir)

        # 打印摘要
        optimizer.print_summary()

        # 生成报告
        report_file = Path(output_dir) / "optimization_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"Gemini 2.5 Flash 批量优化报告\n")
            f.write(f"{'='*50}\n")
            f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总文档数: {optimizer.stats['total']}\n")
            f.write(f"成功: {optimizer.stats['success']}\n")
            f.write(f"失败: {optimizer.stats['failed']}\n")

        logger.info(f"\n📊 报告已生成: {report_file}")

    except KeyboardInterrupt:
        logger.info("\n\n⚠️ 用户中断，保存进度...")
        optimizer.save_progress()
        logger.info("进度已保存，下次运行将继续")
        return 1

    except Exception as e:
        logger.error(f"\n批量优化失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())