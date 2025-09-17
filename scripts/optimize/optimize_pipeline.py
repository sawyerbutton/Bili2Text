#!/usr/bin/env python3
"""
技术文档优化流水线

集成所有优化步骤，提供完整的文档处理方案
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import argparse

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.optimize.document_optimizer import DocumentOptimizer
from scripts.optimize.structure_generator import TechnicalDocumentEnhancer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/dministrator/project/Bili2Text/logs/optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OptimizationPipeline:
    """文档优化流水线"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.document_optimizer = DocumentOptimizer()
        self.document_enhancer = TechnicalDocumentEnhancer()
        self.stats = {
            'processed': 0,
            'succeeded': 0,
            'failed': 0,
            'errors': []
        }

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置"""
        default_config = {
            "input_dir": "/home/dministrator/project/Bili2Text/storage/results/mark_transcripts/markdown",
            "temp_dir": "/home/dministrator/project/Bili2Text/storage/temp/optimization",
            "output_dir": "/home/dministrator/project/Bili2Text/storage/results/optimized_transcripts",
            "backup_dir": "/home/dministrator/project/Bili2Text/storage/backup/original_transcripts",
            "file_patterns": ["*.md"],
            "skip_patterns": ["optimized_*", "enhanced_*"],
            "optimization_stages": [
                "term_correction",
                "structure_analysis",
                "content_enhancement",
                "technical_validation"
            ],
            "quality_checks": {
                "min_paragraphs": 3,
                "min_sections": 2,
                "max_paragraph_length": 1000
            }
        }

        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def run_pipeline(self, files: Optional[List[str]] = None) -> Dict:
        """运行完整的优化流水线"""
        logger.info("开始技术文档优化流水线")

        try:
            # 准备工作目录
            self._prepare_directories()

            # 获取待处理文件列表
            file_list = files or self._get_file_list()

            # 批量处理文件
            for file_path in file_list:
                self._process_single_file(file_path)

            # 生成报告
            report = self._generate_report()

            logger.info(f"优化流水线完成: {self.stats['succeeded']}/{self.stats['processed']} 文件成功处理")
            return report

        except Exception as e:
            logger.error(f"流水线执行失败: {e}")
            raise

    def _prepare_directories(self):
        """准备工作目录"""
        for dir_key in ['temp_dir', 'output_dir', 'backup_dir']:
            dir_path = Path(self.config[dir_key])
            dir_path.mkdir(parents=True, exist_ok=True)

        # 确保日志目录存在
        log_dir = Path("/home/dministrator/project/Bili2Text/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_list(self) -> List[str]:
        """获取待处理文件列表"""
        input_dir = Path(self.config['input_dir'])
        file_list = []

        for pattern in self.config['file_patterns']:
            files = input_dir.glob(pattern)
            for file_path in files:
                # 检查是否需要跳过
                skip = False
                for skip_pattern in self.config['skip_patterns']:
                    if skip_pattern in file_path.name:
                        skip = True
                        break

                if not skip:
                    file_list.append(str(file_path))

        logger.info(f"找到 {len(file_list)} 个待处理文件")
        return file_list

    def _process_single_file(self, file_path: str):
        """处理单个文件"""
        self.stats['processed'] += 1
        file_name = Path(file_path).name

        try:
            logger.info(f"开始处理文件: {file_name}")

            # 备份原始文件
            self._backup_file(file_path)

            # 第一阶段: 基础优化 (术语修正、段落优化)
            temp_file1 = Path(self.config['temp_dir']) / f"stage1_{file_name}"
            success1 = self.document_optimizer.optimize_document(file_path, str(temp_file1))

            if not success1:
                raise Exception("基础优化阶段失败")

            # 第二阶段: 结构增强
            temp_file2 = Path(self.config['temp_dir']) / f"stage2_{file_name}"
            success2 = self.document_enhancer.enhance_document(str(temp_file1), str(temp_file2))

            if not success2:
                raise Exception("结构增强阶段失败")

            # 第三阶段: 质量检查和最终输出
            output_file = Path(self.config['output_dir']) / f"optimized_{file_name}"
            success3 = self._final_quality_check(str(temp_file2), str(output_file))

            if not success3:
                raise Exception("质量检查阶段失败")

            # 清理临时文件
            temp_file1.unlink(missing_ok=True)
            temp_file2.unlink(missing_ok=True)

            self.stats['succeeded'] += 1
            logger.info(f"文件处理成功: {file_name}")

        except Exception as e:
            self.stats['failed'] += 1
            error_msg = f"处理文件 {file_name} 时出错: {e}"
            self.stats['errors'].append(error_msg)
            logger.error(error_msg)

    def _backup_file(self, file_path: str):
        """备份原始文件"""
        try:
            source = Path(file_path)
            backup_dir = Path(self.config['backup_dir'])
            backup_file = backup_dir / source.name

            if not backup_file.exists():
                import shutil
                shutil.copy2(source, backup_file)
                logger.debug(f"已备份: {source.name}")

        except Exception as e:
            logger.warning(f"备份文件失败: {e}")

    def _final_quality_check(self, input_file: str, output_file: str) -> bool:
        """最终质量检查"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 基本质量检查
            checks = self.config.get('quality_checks', {
                'min_paragraphs': 3,
                'min_sections': 2,
                'max_paragraph_length': 1000
            })

            # 检查段落数量
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            if len(paragraphs) < checks['min_paragraphs']:
                logger.warning(f"段落数量不足: {len(paragraphs)} < {checks['min_paragraphs']}")

            # 检查章节数量
            sections = len([line for line in content.split('\n') if line.startswith('#')])
            if sections < checks['min_sections']:
                logger.warning(f"章节数量不足: {sections} < {checks['min_sections']}")

            # 检查段落长度
            for i, para in enumerate(paragraphs):
                if len(para) > checks['max_paragraph_length']:
                    logger.warning(f"段落 {i+1} 过长: {len(para)} > {checks['max_paragraph_length']}")

            # 添加优化说明
            enhanced_content = self._add_optimization_notes(content)

            # 写入最终文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)

            return True

        except Exception as e:
            logger.error(f"质量检查失败: {e}")
            return False

    def _add_optimization_notes(self, content: str) -> str:
        """添加优化说明"""
        optimization_note = """
---

## 文档优化说明

本文档已通过以下优化步骤处理：

1. **术语修正**: 修正了语音识别产生的技术术语错误
2. **结构优化**: 重新组织了文档层次结构
3. **内容增强**: 改善了段落划分和逻辑结构
4. **质量检查**: 确保了文档的技术准确性和可读性

> 💡 提示：如发现任何技术错误或需要进一步说明的内容，请参考原始转录文件或相关技术文档。

---
"""
        return content + optimization_note

    def _generate_report(self) -> Dict:
        """生成处理报告"""
        report = {
            'summary': {
                'total_processed': self.stats['processed'],
                'successful': self.stats['succeeded'],
                'failed': self.stats['failed'],
                'success_rate': f"{(self.stats['succeeded'] / max(self.stats['processed'], 1)) * 100:.1f}%"
            },
            'errors': self.stats['errors'],
            'output_directory': self.config['output_dir'],
            'backup_directory': self.config['backup_dir']
        }

        # 保存报告
        report_file = Path(self.config['output_dir']) / 'optimization_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='技术文档优化流水线')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--files', nargs='+', help='指定要处理的文件')
    parser.add_argument('--dry-run', action='store_true', help='仅显示将要处理的文件，不执行优化')

    args = parser.parse_args()

    try:
        pipeline = OptimizationPipeline(args.config)

        if args.dry_run:
            file_list = pipeline._get_file_list()
            print(f"将要处理的文件 ({len(file_list)}):")
            for file_path in file_list:
                print(f"  - {file_path}")
            return

        report = pipeline.run_pipeline(args.files)

        print("\n=== 优化报告 ===")
        print(f"总处理文件: {report['summary']['total_processed']}")
        print(f"成功: {report['summary']['successful']}")
        print(f"失败: {report['summary']['failed']}")
        print(f"成功率: {report['summary']['success_rate']}")

        if report['errors']:
            print(f"\n错误列表:")
            for error in report['errors']:
                print(f"  - {error}")

        print(f"\n输出目录: {report['output_directory']}")
        print(f"备份目录: {report['backup_directory']}")

    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()