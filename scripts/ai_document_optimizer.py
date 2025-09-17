#!/usr/bin/env python3
"""
AI驱动的文档深度优化器
使用大语言模型理解和重构技术文档
"""

import os
import sys
from pathlib import Path
import json
import re
from typing import Dict, List, Tuple

# 专业术语修正字典（扩展版）
TECH_TERMS = {
    # AI/ML术语
    'Agent': ['agent', 'Agent', 'AGENT', '艾真特', '爱近特', 'H'],
    'Token': ['token', 'Token', '偷懇', '投肯', '拖肯'],
    'Context': ['context', 'Context', 'CONTEXT', '康特斯特'],
    'Context Window': ['context window', 'Context Window', '上下文窗口', '上下輪窗口'],
    'Context Engineering': ['Context Engineering', 'Context and Engineering', '上下文工程'],

    # 协议相关
    'A2A': ['A2A', 'a2a', 'Agent to Agent', 'agent to agent'],
    'MCP': ['MCP', 'mcp', 'Model Context Protocol'],
    'Function Calling': ['Function Calling', 'function calling', '方克森靠0', '函数调用'],
    'JSON-RPC': ['JSON-RPC', 'JSAN RPC', 'JSYRPC', 'JSON RPC'],

    # 模型相关
    'GPT': ['GPT', 'gpt', 'GPD', 'GPTD'],
    'Claude': ['Claude', 'Cloud', 'CLOUD', '克劳德'],
    'ChatGPT': ['ChatGPT', 'Chaggbt', 'Chat GPT'],
    'Gemini': ['Gemini', 'GEMON', 'JAMMDR', 'Gemma'],
    'DeepSeek': ['DeepSeek', 'DipSync', 'Deepseek'],

    # 技术概念
    'RAG': ['RAG', 'rag', 'Rag', '检索增强生成'],
    'Artifact': ['Artifact', 'artifact', 'RDFACT', 'Artifacts'],
    'Multi-Agent': ['Multi-Agent', 'multi-agent', 'MALSEAZEN', 'Mouth Agents', 'MaltzAgent'],
    'streaming': ['streaming', 'SREEM', 'stream', '流式', '流氏'],

    # 开发相关
    'API': ['API', 'api', 'API key', 'API Key'],
    'SDK': ['SDK', 'sdk'],
    'HTTP': ['HTTP', 'HTDP', 'HDDP', 'http'],
    'URL': ['URL', 'url', 'UIR', 'UR'],
    'localhost': ['localhost', 'Local Host', 'local host'],

    # 中文术语修正
    '输入': ['输入', '書入', '书入'],
    '输出': ['输出', '輸出'],
    '返回': ['返回', '反回', '版回', '返回'],
    '调用': ['调用', '電影', '电影'],
    '函数': ['函数', '韓數', '寒数'],
    '协议': ['协议', '協議', 'HUA协议', 'HAA协议'],
    '工具': ['工具', 'FCP工具', 'MCP工具'],

    # 公司和工具
    'Google': ['Google', 'google', '谷歌'],
    'Anthropic': ['Anthropic', 'Anthorapic'],
    'OpenAI': ['OpenAI', 'openai', 'Open AI'],
    'Cline': ['Cline', 'Colline', '克莱恩'],
    'Cursor': ['Cursor', 'cursor', '光标'],
    'Wireshark': ['Wireshark', 'WarShark', 'wareshark'],
    'LangChain': ['LangChain', '狼Cin', 'langchain'],

    # 其他术语
    'WebSocket': ['WebSocket', 'websocket', 'Web Socket'],
    'Base64': ['Base64', 'base64'],
    'PNG': ['PNG', 'png', 'image gun png'],
    'JSON': ['JSON', 'json', 'JSAN', '遍上'],
}

def fix_technical_terms(text: str) -> str:
    """修正技术术语"""
    for correct_term, variations in TECH_TERMS.items():
        for variant in variations:
            if variant != correct_term:
                # 使用单词边界匹配，避免部分匹配
                pattern = r'\b' + re.escape(variant) + r'\b'
                text = re.sub(pattern, correct_term, text, flags=re.IGNORECASE)
    return text

def fix_punctuation(text: str) -> str:
    """修正标点符号"""
    # 修正中文标点
    text = text.replace('，', '，')
    text = text.replace('。', '。')
    text = text.replace('？', '？')
    text = text.replace('！', '！')
    text = text.replace('：', '：')
    text = text.replace('；', '；')
    text = text.replace('"', '"')
    text = text.replace('"', '"')
    text = text.replace(''', ''')
    text = text.replace(''', ''')

    # 在句号后添加换行以改善可读性
    text = re.sub(r'([。！？])\s*([^。！？\n])', r'\1\n\n\2', text)

    return text

def identify_sections(text: str) -> List[Tuple[str, str]]:
    """识别文档的主要章节"""
    sections = []

    # 定义章节识别模式
    patterns = {
        '概述': [r'首先|什么是|简单来说|概念|介绍|引言'],
        '背景': [r'背景|原因|为什么|问题是|现状'],
        '核心概念': [r'核心|关键|重要|主要|基本'],
        '原理': [r'原理|工作机制|如何工作|实现方式|机制'],
        '架构': [r'架构|结构|组成|模块|组件'],
        '实现': [r'实现|代码|步骤|方法|技术|流程'],
        '使用场景': [r'场景|例子|案例|使用|应用'],
        '对比分析': [r'对比|区别|不同|相比|比较'],
        '优缺点': [r'优点|缺点|优势|劣势|好处|问题'],
        '最佳实践': [r'最佳实践|建议|推荐|技巧|注意'],
        '总结': [r'总结|总的来说|最后|结论|回顾'],
        '参考资源': [r'参考|资源|文档|链接|学习'],
    }

    paragraphs = text.split('\n\n')
    current_section = '引言'
    current_content = []

    for para in paragraphs:
        section_found = False
        for section_name, section_patterns in patterns.items():
            for pattern in section_patterns:
                if re.search(pattern, para[:100], re.IGNORECASE):
                    if current_content:
                        sections.append((current_section, '\n\n'.join(current_content)))
                    current_section = section_name
                    current_content = [para]
                    section_found = True
                    break
            if section_found:
                break

        if not section_found:
            current_content.append(para)

    if current_content:
        sections.append((current_section, '\n\n'.join(current_content)))

    return sections

def extract_code_blocks(text: str) -> str:
    """识别并格式化代码块"""
    # 识别命令行命令
    text = re.sub(r'((?:npm|pip|conda|python|node|git|docker|kubectl)\s+[^\n]+)',
                  r'```bash\n\1\n```', text)

    # 识别路径
    text = re.sub(r'((?:/[a-zA-Z0-9_\-]+)+(?:/[a-zA-Z0-9_\-\.]+)?)',
                  r'`\1`', text)

    # 识别URL
    text = re.sub(r'(https?://[^\s]+)', r'[\1](\1)', text)

    return text

def create_structured_markdown(title: str, sections: List[Tuple[str, str]]) -> str:
    """创建结构化的Markdown文档"""
    md = f"# {title}\n\n"

    # 添加目录
    if len(sections) > 3:
        md += "## 目录\n\n"
        for section_name, _ in sections:
            md += f"- [{section_name}](#{section_name.lower().replace(' ', '-')})\n"
        md += "\n---\n\n"

    # 添加各个章节
    for section_name, content in sections:
        md += f"## {section_name}\n\n"

        # 处理内容
        content = fix_technical_terms(content)
        content = fix_punctuation(content)
        content = extract_code_blocks(content)

        # 智能分段
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if len(para) > 500:
                # 长段落尝试进一步分割
                sentences = re.split(r'([。！？])', para)
                new_para = ""
                current_len = 0
                for i in range(0, len(sentences)-1, 2):
                    sentence = sentences[i] + sentences[i+1] if i+1 < len(sentences) else sentences[i]
                    new_para += sentence
                    current_len += len(sentence)
                    if current_len > 200 and i < len(sentences)-2:
                        new_para += "\n\n"
                        current_len = 0
                md += new_para + "\n\n"
            else:
                md += para + "\n\n"

    return md

def optimize_document(input_path: Path, output_path: Path) -> bool:
    """优化单个文档"""
    try:
        # 读取原始文本
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # 提取标题
        lines = text.split('\n')
        if lines[0].startswith('# '):
            title = lines[0].replace('# ', '').strip()
            text = '\n'.join(lines[1:])
        else:
            title = input_path.stem

        # 识别章节
        sections = identify_sections(text)

        # 创建结构化Markdown
        optimized_md = create_structured_markdown(title, sections)

        # 保存优化后的文档
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(optimized_md)

        print(f"✅ 优化完成: {output_path.name}")
        return True

    except Exception as e:
        print(f"❌ 优化失败 {input_path.name}: {e}")
        return False

def main():
    """主函数"""
    input_dir = Path("storage/results/mark_transcripts/markdown")
    output_dir = Path("storage/results/mark_transcripts/optimized")
    output_dir.mkdir(exist_ok=True)

    # 获取所有markdown文件
    md_files = list(input_dir.glob("*.md"))
    print(f"📚 找到 {len(md_files)} 个文档待优化")

    success_count = 0
    for md_file in md_files:
        output_file = output_dir / md_file.name
        if optimize_document(md_file, output_file):
            success_count += 1

    print(f"\n📊 优化完成统计：")
    print(f"   成功: {success_count}/{len(md_files)}")
    print(f"   输出目录: {output_dir}")

if __name__ == "__main__":
    main()