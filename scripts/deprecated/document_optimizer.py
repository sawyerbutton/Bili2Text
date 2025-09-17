#!/usr/bin/env python3
"""
技术视频转录文档智能优化器

主要功能：
1. 技术术语识别和修正
2. 智能段落划分
3. 文档结构重组
4. 内容逻辑优化
"""

import re
import json
import os
from typing import Dict, List, Tuple
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TechnicalTermCorrector:
    """技术术语修正器"""

    def __init__(self):
        self.term_corrections = {
            # AI/ML相关术语
            "方克森靠0": "Function Calling",
            "方克森Calling": "Function Calling",
            "方聲考慮": "Function Calling",
            "方式靠領": "Function Calling",
            "方式靠零": "Function Calling",
            "方向靠近": "Function Calling",
            "材質BT": "ChatGPT",
            "ChadGBT": "ChatGPT",
            "ChaBT": "ChatGPT",
            "安斯羅培克": "Anthropic",
            "大摩星": "大模型",
            "大语言模星": "大语言模型",
            "模星": "模型",
            "電腦函数": "调用函数",
            "GiveBarkest": "GetWeather",
            "Closed AI": "OpenAI",
            "GPD4O": "GPT-4O",
            "GBT4O": "GPT-4O",
            "Gemnet": "Gemini",
            "ClawD": "Claude",
            "電視機": "消息列表",
            "Sell電視機": "消息列表",
            "历史消息列表": "历史对话",
            "韓樹": "函数",
            "半到": "看到",
            "殘數": "参数",
            "进阶篇": "进阶篇",
            "中級指南": "中级指南",
            "中計指南": "中级指南",
            "中計時難": "中级指南",

            # MCP相关
            "MCP中計指南": "MCP中级指南",
            "MCP中計時難": "MCP中级指南",
            "mCP": "MCP",
            "mCP client": "MCP Client",
            "mCP server": "MCP Server",

            # 技术概念
            "API": "API",
            "HTTP": "HTTP",
            "HDDP": "HTTP",
            "HTDP": "HTTP",
            "JSAN": "JSON",
            "JSON Schema": "JSON Schema",
            "Token": "Token",
            "Context Window": "Context Window",
            "Context Engineering": "Context Engineering",
            "RAG": "RAG",
            "Agent": "Agent",
            "Multi-Agent": "Multi-Agent",
            "SubAgent": "SubAgent",

            # 常见错字
            "访问": "访问",
            "协议": "协议",
            "函数": "函数",
            "参数": "参数",
            "返回": "返回",
            "调用": "调用",
            "接口": "接口",
            "模型": "模型",
            "工具": "工具",
            "列錄": "流程",
            "鏈錄": "流程",
            "中間人": "中介",
            "外部工具": "外部工具",
            "交互": "交互",
            "能力": "能力",
            "应用": "应用",
            "产品": "产品",
            "视频": "视频",
            "问题": "问题",
            "答案": "答案",
            "结果": "结果",
            "数据": "数据",
            "信息": "信息",
            "内容": "内容",
            "系统": "系统",
            "服务": "服务",
            "服氣": "服务器",
            "服务器": "服务器",
            "网络": "网络",
            "網路": "网络",
            "网路": "网络",
            "搜索": "搜索",
            "索索": "搜索",
            "速速": "搜索",
            "查询": "查询",
            "查詢": "查询",
            "请求": "请求",
            "响应": "响应",
            "執行": "执行",
            "执行": "执行",
            "處理": "处理",
            "处理": "处理",
            "実現": "实现",
            "实现": "实现",
            "項目": "项目",
            "項目": "项目",
            "项目": "项目",
            "開發": "开发",
            "开发": "开发",
            "設計": "设计",
            "设计": "设计",
            "構建": "构建",
            "构建": "构建"
        }

    def correct_terms(self, text: str) -> str:
        """修正技术术语"""
        corrected_text = text
        for wrong_term, correct_term in self.term_corrections.items():
            corrected_text = corrected_text.replace(wrong_term, correct_term)
        return corrected_text

class DocumentStructureAnalyzer:
    """文档结构分析器"""

    def __init__(self):
        self.section_patterns = [
            # 常见的章节模式
            r'第\d+[部分|章|节]',
            r'\d+[、.]',
            r'[一二三四五六七八九十]+[、.]',
            r'首先|其次|然后|接下来|最后|总结',
            r'什么是|为什么|如何|怎么',
            r'定义|概念|原理|实现|应用|示例|例子'
        ]

    def identify_sections(self, text: str) -> List[Tuple[int, str, str]]:
        """识别文档中的潜在章节"""
        sections = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # 检查是否匹配章节模式
            for pattern in self.section_patterns:
                if re.search(pattern, line_stripped):
                    sections.append((i, pattern, line_stripped))
                    break

        return sections

class ContentLogicOptimizer:
    """内容逻辑优化器"""

    def __init__(self):
        self.technical_keywords = [
            'API', 'HTTP', 'JSON', 'Token', 'Context', 'Agent', 'Model',
            'Function Calling', 'MCP', 'RAG', 'GPT', 'Claude', 'OpenAI',
            '模型', '函数', '接口', '协议', '工具', '算法', '架构', '系统'
        ]

    def add_punctuation(self, text: str) -> str:
        """为长段落添加标点符号"""
        # 基于语义停顿添加标点
        text = re.sub(r'([。！？；])(\w)', r'\1\n\2', text)
        text = re.sub(r'(但是|然而|不过|另外|此外|因此|所以|总之)([^，。！？；])', r'，\2', text)
        text = re.sub(r'(\w{10,}?)([，。])', r'\1\2\n', text)
        return text

    def split_long_paragraphs(self, text: str) -> str:
        """拆分过长的段落"""
        paragraphs = text.split('\n\n')
        optimized_paragraphs = []

        for para in paragraphs:
            if len(para) > 500:  # 超过500字符的段落需要拆分
                # 寻找合适的拆分点
                sentences = re.split(r'[。！？；]\s*', para)
                current_chunk = ""

                for sentence in sentences:
                    if len(current_chunk + sentence) > 200:
                        if current_chunk:
                            optimized_paragraphs.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        current_chunk += sentence + "。"

                if current_chunk:
                    optimized_paragraphs.append(current_chunk.strip())
            else:
                optimized_paragraphs.append(para)

        return '\n\n'.join(optimized_paragraphs)

class DocumentOptimizer:
    """主文档优化器"""

    def __init__(self):
        self.term_corrector = TechnicalTermCorrector()
        self.structure_analyzer = DocumentStructureAnalyzer()
        self.logic_optimizer = ContentLogicOptimizer()

    def optimize_document(self, input_file: str, output_file: str) -> bool:
        """优化单个文档"""
        try:
            logger.info(f"开始优化文档: {input_file}")

            # 读取原始文档
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 第一阶段：修正技术术语
            logger.info("阶段1: 修正技术术语")
            content = self.term_corrector.correct_terms(content)

            # 第二阶段：添加标点符号和段落优化
            logger.info("阶段2: 优化段落结构")
            content = self.logic_optimizer.add_punctuation(content)
            content = self.logic_optimizer.split_long_paragraphs(content)

            # 第三阶段：分析和优化文档结构
            logger.info("阶段3: 分析文档结构")
            sections = self.structure_analyzer.identify_sections(content)

            # 第四阶段：生成结构化markdown
            logger.info("阶段4: 生成优化后的文档")
            optimized_content = self._generate_structured_markdown(content, sections)

            # 写入优化后的文档
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(optimized_content)

            logger.info(f"文档优化完成: {output_file}")
            return True

        except Exception as e:
            logger.error(f"优化文档时出错: {e}")
            return False

    def _generate_structured_markdown(self, content: str, sections: List[Tuple[int, str, str]]) -> str:
        """生成结构化的markdown"""
        lines = content.split('\n')
        result = []

        # 添加文档头部
        if lines and lines[0].strip():
            title = lines[0].strip().replace('#', '').strip()
            result.append(f"# {title}")
            result.append("")
            result.append("## 文档概述")
            result.append("")
            result.append("本文档是基于技术视频转录内容优化生成的技术文档。")
            result.append("")

        current_section = ""
        section_level = 2

        for i, line in enumerate(lines[1:], 1):  # 跳过标题行
            line_stripped = line.strip()

            if not line_stripped:
                result.append("")
                continue

            # 检查是否是章节标题
            is_section = False
            for line_num, pattern, section_text in sections:
                if line_num == i:
                    # 确定章节级别
                    if re.search(r'第\d+[部分|章]', line_stripped):
                        section_level = 2
                    elif re.search(r'\d+[、.]', line_stripped):
                        section_level = 3
                    else:
                        section_level = 4

                    result.append(f"{'#' * section_level} {line_stripped}")
                    result.append("")
                    is_section = True
                    break

            if not is_section:
                result.append(line)

        return '\n'.join(result)

    def batch_optimize(self, input_dir: str, output_dir: str) -> Dict[str, bool]:
        """批量优化文档"""
        results = {}
        input_path = Path(input_dir)

        if not input_path.exists():
            logger.error(f"输入目录不存在: {input_dir}")
            return results

        # 处理所有markdown文件
        for md_file in input_path.glob("*.md"):
            output_file = Path(output_dir) / f"optimized_{md_file.name}"
            success = self.optimize_document(str(md_file), str(output_file))
            results[str(md_file)] = success

        return results

def main():
    """主函数"""
    # 配置路径
    input_dir = "/home/dministrator/project/Bili2Text/storage/results/mark_transcripts/markdown"
    output_dir = "/home/dministrator/project/Bili2Text/storage/results/optimized_transcripts"

    # 创建优化器
    optimizer = DocumentOptimizer()

    # 批量优化文档
    logger.info("开始批量优化技术文档...")
    results = optimizer.batch_optimize(input_dir, output_dir)

    # 输出结果统计
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)

    logger.info(f"优化完成: {success_count}/{total_count} 个文档优化成功")

    # 输出详细结果
    for file_path, success in results.items():
        status = "成功" if success else "失败"
        logger.info(f"{file_path}: {status}")

if __name__ == "__main__":
    main()