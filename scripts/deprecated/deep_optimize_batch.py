#!/usr/bin/env python3
"""批量深度优化剩余的文档"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
import json

class DeepDocumentOptimizer:
    """深度文档优化器 - 使用更高级的策略"""

    def __init__(self):
        # 口语化词汇库 - 扩展版
        self.oral_patterns = {
            '别担心': '', '你看': '', '好了': '', '那么': '',
            '这个': '', '那个': '', '然后': '', '接下来': '',
            '我们来': '将', '我来': '', '大家': '', '咱们': '',
            '其实': '', '实际上': '', '基本上': '', '总的来说': '',
            '换句话说': '', '也就是说': '即', '所以说': '因此',
            '你会发现': '', '你会看到': '', '你可以': '可以',
            '我觉得': '', '我认为': '', '我想': '', '我建议': '建议',
            '首先': '第一，', '其次': '第二，', '最后': '第三，',
            '今天': '', '这次': '', '这期': '', '本期': '',
            '视频': '', '节目': '', '分享': '', '讲解': '',
            '接著': '接着', '並且': '并且', '當然': '当然',
            '為什麼': '为什么', '這樣': '这样', '還有': '还有'
        }

        # 繁简转换字典 - 扩展版
        self.traditional_to_simplified = {
            '視頻': '视频', '頻道': '频道', '訂閱': '订阅',
            '點擊': '点击', '鏈接': '链接', '評論': '评论',
            '數據': '数据', '網絡': '网络', '計算': '计算',
            '應用': '应用', '開發': '开发', '設計': '设计',
            '實現': '实现', '優化': '优化', '測試': '测试',
            '運行': '运行', '執行': '执行', '處理': '处理',
            '輸入': '输入', '輸出': '输出', '參數': '参数',
            '變量': '变量', '函數': '函数', '類型': '类型',
            '對象': '对象', '屬性': '属性', '方法': '方法',
            '邏輯': '逻辑', '條件': '条件', '循環': '循环',
            '異常': '异常', '錯誤': '错误', '調試': '调试',
            '線程': '线程', '進程': '进程', '內存': '内存',
            '緩存': '缓存', '數據庫': '数据库', '查詢': '查询'
        }

        # 技术术语修正
        self.term_corrections = {
            'Gemani': 'Gemini', 'GPT4': 'GPT-4', 'Claude3': 'Claude 3',
            'deepseek': 'DeepSeek', 'openai': 'OpenAI', 'api': 'API',
            'json': 'JSON', 'xml': 'XML', 'http': 'HTTP', 'url': 'URL',
            'sdk': 'SDK', 'ide': 'IDE', 'cli': 'CLI', 'gui': 'GUI',
            'llm': 'LLM', 'ai': 'AI', 'ml': 'ML', 'dl': 'DL',
            'gpu': 'GPU', 'cpu': 'CPU', 'ram': 'RAM', 'ssd': 'SSD'
        }

    def clean_text(self, text: str) -> str:
        """清理文本：去除口语化、统一繁简体、修正术语"""
        # 繁简转换
        for trad, simp in self.traditional_to_simplified.items():
            text = text.replace(trad, simp)

        # 去除口语化表达
        for oral, replacement in self.oral_patterns.items():
            text = re.sub(rf'\b{re.escape(oral)}\b', replacement, text, flags=re.IGNORECASE)

        # 修正技术术语
        for wrong, correct in self.term_corrections.items():
            text = re.sub(rf'\b{re.escape(wrong)}\b', correct, text, flags=re.IGNORECASE)

        # 清理多余空格和标点
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[。，！？；：]{2,}', '。', text)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def extract_key_points(self, content: str) -> List[str]:
        """提取关键观点"""
        # 识别包含关键信息的句子
        key_patterns = [
            r'[^。]*(?:核心|关键|重要|主要|本质|原理|机制|特点|优势|缺点|问题|解决|方案|方法|步骤|流程)[^。]*。',
            r'[^。]*(?:定义|概念|理解|实现|应用|场景|案例|示例|代码|配置)[^。]*。',
            r'[^。]*(?:第一|第二|第三|首先|其次|最后|另外|此外|而且|但是|然而|因此|所以)[^。]*。'
        ]

        key_points = []
        for pattern in key_patterns:
            matches = re.findall(pattern, content)
            key_points.extend(matches)

        # 去重并保持顺序
        seen = set()
        unique_points = []
        for point in key_points:
            if point not in seen and len(point) > 20:  # 过滤太短的句子
                seen.add(point)
                unique_points.append(point)

        return unique_points[:20]  # 限制数量

    def generate_structure(self, content: str, title: str) -> str:
        """生成结构化文档"""
        # 清理文本
        cleaned_content = self.clean_text(content)

        # 提取关键点
        key_points = self.extract_key_points(cleaned_content)

        # 识别主要主题
        sections = self.identify_sections(cleaned_content)

        # 构建文档结构
        structured = [f"# {title}\n"]

        # 添加概述
        structured.append("## 概述\n")
        if key_points:
            overview = self.generate_overview(key_points[:5])
            structured.append(f"{overview}\n")

        # 添加核心内容
        for section_title, section_content in sections:
            structured.append(f"\n## {section_title}\n")
            # 清理并格式化内容
            formatted_content = self.format_section_content(section_content)
            structured.append(f"{formatted_content}\n")

        # 添加总结
        if len(sections) > 2:
            structured.append("\n## 总结\n")
            summary = self.generate_summary(key_points)
            structured.append(f"{summary}\n")

        return '\n'.join(structured)

    def identify_sections(self, content: str) -> List[Tuple[str, str]]:
        """识别文档的主要章节"""
        # 根据内容特征划分章节
        sections = []

        # 尝试识别现有的章节标记
        existing_sections = re.findall(r'##\s*([^\n]+)\n(.*?)(?=##|\Z)', content, re.DOTALL)
        if existing_sections:
            for title, section_content in existing_sections:
                sections.append((title.strip(), section_content.strip()))
        else:
            # 基于内容长度和段落自动划分
            paragraphs = content.split('\n\n')
            chunk_size = max(3, len(paragraphs) // 5)  # 分成约5个章节

            section_templates = [
                "基础概念", "核心原理", "技术实现", "实践应用", "总结与展望"
            ]

            for i in range(0, len(paragraphs), chunk_size):
                chunk = '\n\n'.join(paragraphs[i:i+chunk_size])
                section_idx = min(i // chunk_size, len(section_templates) - 1)
                sections.append((section_templates[section_idx], chunk))

        return sections

    def format_section_content(self, content: str) -> str:
        """格式化章节内容"""
        lines = content.split('\n')
        formatted = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 识别并格式化代码块
            if '```' in line or 'code' in line.lower():
                formatted.append(line)
            # 识别列表项
            elif re.match(r'^\d+[.、]', line) or line.startswith('-') or line.startswith('*'):
                formatted.append(line)
            # 普通段落
            else:
                # 确保段落有适当的长度
                if len(line) > 30:
                    formatted.append(line)

        return '\n\n'.join(formatted)

    def generate_overview(self, key_points: List[str]) -> str:
        """生成概述段落"""
        if not key_points:
            return "本文档提供了相关技术的详细解析。"

        # 提取最重要的几个点
        overview_points = []
        for point in key_points[:3]:
            cleaned = self.clean_text(point)
            if len(cleaned) > 20:
                overview_points.append(cleaned)

        if overview_points:
            return "本文档" + "，".join(overview_points[:2]) + "。"
        else:
            return "本文档深入探讨了相关技术细节和实现方案。"

    def generate_summary(self, key_points: List[str]) -> str:
        """生成总结段落"""
        if not key_points:
            return "通过本文档的介绍，读者可以全面了解相关技术。"

        summary_points = []
        for point in key_points[-3:]:
            cleaned = self.clean_text(point)
            if len(cleaned) > 20:
                summary_points.append(f"- {cleaned}")

        if summary_points:
            return "核心要点：\n\n" + '\n'.join(summary_points)
        else:
            return "本文档系统地介绍了相关技术的原理与实践。"

    def optimize_document(self, input_path: str, output_path: str):
        """优化单个文档"""
        try:
            # 读取原始内容
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取标题
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1)
            else:
                # 从文件名提取标题
                filename = Path(input_path).stem
                title = filename.replace('intelligent_', '').replace('_', ' ')

            # 生成优化后的文档
            optimized = self.generate_structure(content, title)

            # 保存结果
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(optimized)

            print(f"✅ 优化完成: {Path(input_path).name} -> {Path(output_path).name}")
            return True

        except Exception as e:
            print(f"❌ 优化失败 {input_path}: {e}")
            return False

def main():
    """主函数"""
    input_dir = "storage/results/intelligent_optimized"
    output_dir = "storage/results/expert_optimized"

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 已经完成深度优化的文件
    completed = [
        "A2A协议_深度优化版.md",
        "Context_Engineering_专家优化版.md",
        "MCP_Function_Calling_深度优化版.md",
        "MCP_基础篇_深度优化版.md"
    ]

    # 获取需要优化的文件
    files_to_optimize = []
    for file in os.listdir(input_dir):
        if file.endswith('.md'):
            # 检查是否已经优化过
            output_name = file.replace('intelligent_', '').replace('_optimized', '') + '_深度优化版.md'
            if output_name not in completed and not any(c in file for c in completed):
                files_to_optimize.append(file)

    print(f"发现 {len(files_to_optimize)} 个文档需要深度优化\n")

    # 创建优化器
    optimizer = DeepDocumentOptimizer()

    # 批量优化
    success_count = 0
    for i, file in enumerate(files_to_optimize, 1):
        print(f"[{i}/{len(files_to_optimize)}] 正在优化: {file}")

        input_path = os.path.join(input_dir, file)

        # 生成输出文件名
        output_name = file.replace('intelligent_', '')
        # 清理文件名
        output_name = re.sub(r'，.*', '', output_name)  # 移除长描述
        output_name = output_name.replace('.md', '_深度优化版.md')
        output_path = os.path.join(output_dir, output_name)

        if optimizer.optimize_document(input_path, output_path):
            success_count += 1

    # 打印结果
    print(f"\n{'='*50}")
    print(f"深度优化完成！")
    print(f"成功: {success_count}/{len(files_to_optimize)}")
    print(f"输出目录: {output_dir}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()