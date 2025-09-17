#!/usr/bin/env python3
"""
智能文档结构生成器

基于内容语义分析，自动生成合理的文档层次结构
"""

import re
import json
from typing import List, Dict, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ContentSemanticAnalyzer:
    """内容语义分析器"""

    def __init__(self):
        self.concept_patterns = {
            "definition": [
                r"什么是", r"定义", r"概念", r"指的是", r"含义", r"意思",
                r"是一种", r"是一个", r"简单来说"
            ],
            "problem": [
                r"问题", r"困难", r"挑战", r"限制", r"瓶颈", r"缺陷",
                r"为什么需要", r"为什么要", r"解决了什么"
            ],
            "solution": [
                r"解决方案", r"方法", r"技术", r"实现", r"策略",
                r"如何", r"怎么", r"步骤", r"流程"
            ],
            "example": [
                r"例子", r"示例", r"案例", r"举例", r"比如", r"譬如",
                r"演示", r"实例", r"具体来说"
            ],
            "comparison": [
                r"对比", r"比较", r"区别", r"不同", r"相同", r"类似",
                r"与.*相比", r"而.*则"
            ],
            "summary": [
                r"总结", r"总之", r"综上", r"回顾", r"小结",
                r"最后", r"结论", r"总的来说"
            ],
            "architecture": [
                r"架构", r"结构", r"组成", r"模块", r"组件", r"层级",
                r"系统", r"框架", r"设计"
            ],
            "process": [
                r"流程", r"过程", r"步骤", r"阶段", r"环节",
                r"首先", r"然后", r"接下来", r"最后"
            ]
        }

        self.section_importance = {
            "definition": 9,
            "problem": 8,
            "solution": 8,
            "architecture": 7,
            "process": 6,
            "example": 5,
            "comparison": 4,
            "summary": 3
        }

    def analyze_paragraph_type(self, paragraph: str) -> Tuple[str, float]:
        """分析段落类型和重要度"""
        max_score = 0
        best_type = "content"

        for concept_type, patterns in self.concept_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, paragraph, re.IGNORECASE))
                score += matches

            # 根据段落长度调整分数
            normalized_score = score / (len(paragraph) / 100 + 1)

            if normalized_score > max_score:
                max_score = normalized_score
                best_type = concept_type

        importance = self.section_importance.get(best_type, 1) * max_score
        return best_type, importance

class DocumentStructureGenerator:
    """文档结构生成器"""

    def __init__(self):
        self.analyzer = ContentSemanticAnalyzer()
        self.section_templates = {
            "definition": "## 基本概念\n\n### {title}\n\n{content}",
            "problem": "## 问题分析\n\n### {title}\n\n{content}",
            "solution": "## 解决方案\n\n### {title}\n\n{content}",
            "architecture": "## 系统架构\n\n### {title}\n\n{content}",
            "process": "## 实现流程\n\n### {title}\n\n{content}",
            "example": "## 应用示例\n\n### {title}\n\n{content}",
            "comparison": "## 对比分析\n\n### {title}\n\n{content}",
            "summary": "## 总结\n\n{content}"
        }

    def generate_structure(self, content: str, title: str = "") -> str:
        """生成结构化文档"""
        # 1. 分析内容并提取段落
        paragraphs = self._extract_paragraphs(content)

        # 2. 分析每个段落的类型和重要度
        analyzed_paragraphs = []
        for para in paragraphs:
            if len(para.strip()) < 50:  # 跳过太短的段落
                continue
            para_type, importance = self.analyzer.analyze_paragraph_type(para)
            analyzed_paragraphs.append({
                'content': para,
                'type': para_type,
                'importance': importance
            })

        # 3. 按类型和重要度重新组织
        structured_content = self._organize_by_sections(analyzed_paragraphs, title)

        return structured_content

    def _extract_paragraphs(self, content: str) -> List[str]:
        """提取段落"""
        # 移除现有的markdown标记
        content = re.sub(r'^#{1,6}\s*', '', content, flags=re.MULTILINE)

        # 按空行分割段落
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        # 合并过短的段落
        merged_paragraphs = []
        current_para = ""

        for para in paragraphs:
            if len(para) < 100 and current_para:
                current_para += "\n\n" + para
            else:
                if current_para:
                    merged_paragraphs.append(current_para)
                current_para = para

        if current_para:
            merged_paragraphs.append(current_para)

        return merged_paragraphs

    def _organize_by_sections(self, paragraphs: List[Dict], title: str) -> str:
        """按章节组织内容"""
        # 按类型分组
        sections = {}
        for para in paragraphs:
            para_type = para['type']
            if para_type not in sections:
                sections[para_type] = []
            sections[para_type].append(para)

        # 生成文档结构
        result = []

        # 添加标题
        if title:
            result.append(f"# {title}")
            result.append("")

        # 添加概述（如果有定义类段落）
        if 'definition' in sections:
            result.append("## 概述")
            result.append("")
            for para in sections['definition']:
                result.append(para['content'])
                result.append("")

        # 按预定义顺序添加其他章节
        section_order = ['problem', 'solution', 'architecture', 'process', 'example', 'comparison', 'summary']

        for section_type in section_order:
            if section_type in sections and section_type != 'definition':
                section_title = self._get_section_title(section_type)
                result.append(f"## {section_title}")
                result.append("")

                # 添加子章节
                for i, para in enumerate(sections[section_type]):
                    if len(sections[section_type]) > 1:
                        subsection_title = self._generate_subsection_title(para['content'], section_type)
                        result.append(f"### {subsection_title}")
                        result.append("")

                    result.append(para['content'])
                    result.append("")

        # 添加其他内容
        other_content = []
        for section_type, paras in sections.items():
            if section_type not in ['definition'] + section_order:
                other_content.extend(paras)

        if other_content:
            result.append("## 补充说明")
            result.append("")
            for para in other_content:
                result.append(para['content'])
                result.append("")

        return '\n'.join(result)

    def _get_section_title(self, section_type: str) -> str:
        """获取章节标题"""
        titles = {
            'problem': '问题背景',
            'solution': '解决方案',
            'architecture': '技术架构',
            'process': '实现流程',
            'example': '应用示例',
            'comparison': '技术对比',
            'summary': '总结'
        }
        return titles.get(section_type, section_type.title())

    def _generate_subsection_title(self, content: str, section_type: str) -> str:
        """生成子章节标题"""
        # 提取关键词作为标题
        sentences = re.split(r'[。！？]', content)
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) < 50:
                return first_sentence
            else:
                # 截取前30个字符作为标题
                return first_sentence[:30] + "..."

        return f"{section_type.title()} Detail"

class TechnicalDocumentEnhancer:
    """技术文档增强器"""

    def __init__(self):
        self.structure_generator = DocumentStructureGenerator()

    def enhance_document(self, input_file: str, output_file: str) -> bool:
        """增强单个文档"""
        try:
            # 读取原始文档
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取原标题
            title_match = re.search(r'^#\s*(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else Path(input_file).stem

            # 生成结构化内容
            structured_content = self.structure_generator.generate_structure(content, title)

            # 添加技术文档元数据
            enhanced_content = self._add_metadata(structured_content, title)

            # 写入增强后的文档
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)

            logger.info(f"文档增强完成: {output_file}")
            return True

        except Exception as e:
            logger.error(f"增强文档时出错: {e}")
            return False

    def _add_metadata(self, content: str, title: str) -> str:
        """添加文档元数据"""
        metadata = f"""# {title}

> **文档类型**: 技术文档
> **生成方式**: 基于视频转录优化
> **优化时间**: {Path().cwd()}
> **内容领域**: AI/ML技术

---

"""
        return metadata + content

def main():
    """测试主函数"""
    enhancer = TechnicalDocumentEnhancer()

    # 测试文件路径
    test_input = "/home/dministrator/project/Bili2Text/storage/results/mark_transcripts/markdown/Context_Engineering_概念与技术实现深度解析.md"
    test_output = "/home/dministrator/project/Bili2Text/storage/results/enhanced_transcripts/Context_Engineering_Enhanced.md"

    success = enhancer.enhance_document(test_input, test_output)
    print(f"文档增强{'成功' if success else '失败'}")

if __name__ == "__main__":
    main()