#!/usr/bin/env python3
"""
批量优化技术文档脚本

对指定目录下的所有markdown文档进行智能优化
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict
import argparse
from datetime import datetime

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.optimize.document_optimizer import DocumentOptimizer
from scripts.optimize.structure_generator import TechnicalDocumentEnhancer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BatchOptimizer:
    """批量文档优化器"""

    def __init__(self):
        self.optimizer = DocumentOptimizer()
        self.enhancer = TechnicalDocumentEnhancer()
        self.stats = {
            'total': 0,
            'succeeded': 0,
            'failed': 0,
            'errors': []
        }

    def optimize_directory(self, input_dir: str, output_dir: str, enhance: bool = True) -> Dict:
        """优化目录下的所有文档"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)

        if not input_path.exists():
            raise ValueError(f"输入目录不存在: {input_dir}")

        # 创建输出目录
        output_path.mkdir(parents=True, exist_ok=True)

        # 查找所有markdown文件
        md_files = list(input_path.glob("*.md"))
        self.stats['total'] = len(md_files)

        logger.info(f"找到 {len(md_files)} 个markdown文件待优化")

        for md_file in md_files:
            self._process_file(md_file, output_path, enhance)

        return self._generate_report()

    def _process_file(self, input_file: Path, output_dir: Path, enhance: bool):
        """处理单个文件"""
        try:
            logger.info(f"开始处理: {input_file.name}")

            # 第一阶段：基础优化
            temp_file = output_dir / f"temp_{input_file.name}"
            success1 = self.optimizer.optimize_document(str(input_file), str(temp_file))

            if not success1:
                raise Exception("基础优化失败")

            # 第二阶段：结构增强 (可选)
            if enhance:
                final_file = output_dir / f"optimized_{input_file.name}"
                success2 = self.enhancer.enhance_document(str(temp_file), str(final_file))

                if success2:
                    temp_file.unlink()  # 删除临时文件
                else:
                    # 如果增强失败，至少保留基础优化结果
                    temp_file.rename(output_dir / f"basic_optimized_{input_file.name}")
                    logger.warning(f"结构增强失败，保留基础优化结果: {input_file.name}")
            else:
                # 仅基础优化
                final_file = output_dir / f"optimized_{input_file.name}"
                temp_file.rename(final_file)

            self.stats['succeeded'] += 1
            logger.info(f"处理成功: {input_file.name}")

        except Exception as e:
            self.stats['failed'] += 1
            error_msg = f"处理 {input_file.name} 失败: {e}"
            self.stats['errors'].append(error_msg)
            logger.error(error_msg)

    def _generate_report(self) -> Dict:
        """生成处理报告"""
        success_rate = (self.stats['succeeded'] / max(self.stats['total'], 1)) * 100

        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_files': self.stats['total'],
                'successful': self.stats['succeeded'],
                'failed': self.stats['failed'],
                'success_rate': f"{success_rate:.1f}%"
            },
            'errors': self.stats['errors']
        }

        return report

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量优化技术文档')
    parser.add_argument('--input', '-i',
                       default='/home/dministrator/project/Bili2Text/storage/results/mark_transcripts/markdown',
                       help='输入目录路径')
    parser.add_argument('--output', '-o',
                       default='/home/dministrator/project/Bili2Text/storage/results/optimized_transcripts',
                       help='输出目录路径')
    parser.add_argument('--basic-only', action='store_true',
                       help='仅执行基础优化，跳过结构增强')
    parser.add_argument('--files', nargs='+',
                       help='指定要处理的文件名（不包含路径）')

    args = parser.parse_args()

    try:
        logger.info("开始批量文档优化...")

        batch_optimizer = BatchOptimizer()

        # 如果指定了特定文件，只处理这些文件
        if args.files:
            input_dir = Path(args.input)
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)

            for filename in args.files:
                file_path = input_dir / filename
                if file_path.exists():
                    batch_optimizer._process_file(file_path, output_dir, not args.basic_only)
                    batch_optimizer.stats['total'] += 1
                else:
                    logger.warning(f"文件不存在: {filename}")
        else:
            # 处理整个目录
            report = batch_optimizer.optimize_directory(
                args.input,
                args.output,
                enhance=not args.basic_only
            )

        # 打印结果
        print("\n" + "="*50)
        print("📊 批量优化报告")
        print("="*50)
        print(f"总文件数: {batch_optimizer.stats['total']}")
        print(f"成功: {batch_optimizer.stats['succeeded']}")
        print(f"失败: {batch_optimizer.stats['failed']}")

        if batch_optimizer.stats['succeeded'] > 0:
            success_rate = (batch_optimizer.stats['succeeded'] / batch_optimizer.stats['total']) * 100
            print(f"成功率: {success_rate:.1f}%")

        if batch_optimizer.stats['errors']:
            print(f"\n❌ 错误列表:")
            for error in batch_optimizer.stats['errors']:
                print(f"  - {error}")

        print(f"\n📁 输出目录: {args.output}")

    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.error(f"批量优化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()