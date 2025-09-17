#!/usr/bin/env python3
"""
串行批量优化文档 - 避免API限流
"""

import os
import sys
import time
import json
from pathlib import Path
import logging
import google.generativeai as genai

# 添加项目根目录
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.optimize.gemini_document_optimizer import GeminiDocumentOptimizer, OptimizationConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('serial_optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API配置
API_KEY = "AIzaSyDAmHzFbKgZMJVp1nyOkVr89MjXM6ahWnE"


class SerialOptimizer:
    """串行文档优化器"""

    def __init__(self):
        self.config = OptimizationConfig(
            api_key=API_KEY,
            model_name='models/gemini-2.5-flash',
            temperature=0.3,
            cache_enabled=True,
            max_tokens_per_request=5000
        )

        self.optimizer = GeminiDocumentOptimizer(self.config)

        # 初始化Gemini
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')

        # 进度跟踪
        self.progress_file = Path("serial_progress.json")
        self.load_progress()

    def load_progress(self):
        """加载进度"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.progress = json.load(f)
        else:
            self.progress = {'completed': [], 'failed': [], 'current': None}

    def save_progress(self):
        """保存进度"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)

    def optimize_document(self, input_file: Path, output_file: Path) -> bool:
        """优化单个文档 - 完全串行处理"""
        try:
            logger.info(f"处理: {input_file.name}")

            # 标记当前处理文件
            self.progress['current'] = str(input_file)
            self.save_progress()

            # 读取内容
            content = input_file.read_text(encoding='utf-8')
            file_size = len(content)
            logger.info(f"  文件大小: {file_size} 字符")

            # Step 1: 基础纠错
            logger.info("  [1/3] 基础纠错...")
            corrected = self.optimizer.apply_term_corrections(content)

            # Step 2: 决定优化策略
            if file_size < 4000:
                # 小文件：完整AI优化
                logger.info("  [2/3] AI深度优化（小文件）...")

                prompt = f"""
请将以下文本优化为专业的技术文档：

要求：
1. 修正所有技术术语和专有名词
2. 改善段落结构，使用Markdown格式
3. 去除口语化表达
4. 保持原意完整

文本：
{corrected}

直接输出优化后的内容：
"""

                # API调用 - 等待完成
                response = self.model.generate_content(prompt)
                optimized = response.text

                logger.info("  [3/3] AI优化完成")

            elif file_size < 10000:
                # 中等文件：部分AI优化
                logger.info("  [2/3] AI部分优化（中等文件）...")

                # 只优化前3000字
                sample = corrected[:3000]

                prompt = f"""
请优化以下文本的结构和格式：

1. 添加合适的Markdown标题
2. 改善段落划分
3. 去除明显的口语化内容

文本：
{sample}

直接输出优化后的内容：
"""

                # API调用 - 等待完成
                response = self.model.generate_content(prompt)
                optimized = response.text + "\n\n" + corrected[3000:]

                logger.info("  [3/3] 部分优化完成")

            else:
                # 大文件：仅纠错
                logger.info("  [2/3] 跳过AI优化（大文件）")
                optimized = corrected
                logger.info("  [3/3] 仅应用纠错")

            # Step 3: 保存结果
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(optimized, encoding='utf-8')

            # 更新进度
            self.progress['completed'].append(str(input_file))
            self.progress['current'] = None
            self.save_progress()

            logger.info(f"  ✅ 成功保存到: {output_file.name}")
            return True

        except Exception as e:
            logger.error(f"  ❌ 失败: {e}")
            self.progress['failed'].append(str(input_file))
            self.progress['current'] = None
            self.save_progress()
            return False

    def run_batch(self, input_dir: str, output_dir: str):
        """运行批量优化 - 严格串行"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 获取所有文件
        all_files = sorted(input_path.glob("*.md"))

        # 过滤已完成的
        pending_files = [
            f for f in all_files
            if str(f) not in self.progress['completed']
        ]

        logger.info("="*60)
        logger.info("串行批量优化")
        logger.info("="*60)
        logger.info(f"总文件数: {len(all_files)}")
        logger.info(f"已完成: {len(self.progress['completed'])}")
        logger.info(f"待处理: {len(pending_files)}")
        logger.info(f"失败: {len(self.progress['failed'])}")

        if not pending_files:
            logger.info("所有文档已处理完成！")
            return

        # 串行处理每个文档
        success_count = 0
        fail_count = 0

        for idx, file in enumerate(pending_files, 1):
            logger.info(f"\n[{idx}/{len(pending_files)}] 开始处理...")

            # 生成输出文件名
            output_name = file.stem.replace('_深度优化版', '').replace('_专家优化版', '')
            output_name = f"{output_name}_gemini_optimized.md"
            output_file = output_path / output_name

            # 处理文档
            if self.optimize_document(file, output_file):
                success_count += 1
            else:
                fail_count += 1

            # 显示累计进度
            total_completed = len(self.progress['completed'])
            total_files = len(all_files)
            progress_pct = (total_completed / total_files) * 100

            logger.info(f"总进度: {total_completed}/{total_files} ({progress_pct:.1f}%)")

            # API速率限制 - 每个请求后等待
            if idx < len(pending_files):
                wait_time = 5  # 5秒间隔，确保不超限
                logger.info(f"等待 {wait_time} 秒（API速率限制）...")
                time.sleep(wait_time)

        # 最终报告
        logger.info("\n" + "="*60)
        logger.info("批量优化完成")
        logger.info("="*60)
        logger.info(f"本次成功: {success_count}")
        logger.info(f"本次失败: {fail_count}")
        logger.info(f"累计完成: {len(self.progress['completed'])}/{len(all_files)}")

        # 生成报告
        report = f"""
Gemini 2.5 Flash 串行批量优化报告
================================
生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

总文件数: {len(all_files)}
已完成: {len(self.progress['completed'])}
失败: {len(self.progress['failed'])}

本次运行:
- 处理: {len(pending_files)}
- 成功: {success_count}
- 失败: {fail_count}

已完成文档:
{chr(10).join(f"- {Path(f).name}" for f in self.progress['completed'][-10:])}

{'失败文档:' if self.progress['failed'] else ''}
{chr(10).join(f"- {Path(f).name}" for f in self.progress['failed'])}
"""

        report_file = output_path / "serial_optimization_report.txt"
        report_file.write_text(report, encoding='utf-8')
        logger.info(f"报告已保存: {report_file}")


def main():
    """主函数"""
    input_dir = "storage/results/expert_optimized"
    output_dir = "storage/results/gemini_optimized"

    optimizer = SerialOptimizer()

    try:
        optimizer.run_batch(input_dir, output_dir)
    except KeyboardInterrupt:
        logger.info("\n用户中断，进度已保存")
        return 1
    except Exception as e:
        logger.error(f"批量优化失败: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())