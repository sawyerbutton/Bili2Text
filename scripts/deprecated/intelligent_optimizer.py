#!/usr/bin/env python3
"""
智能文档深度优化系统
使用AI深度理解技术对逐字稿进行智能优化
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ContentType(Enum):
    """内容类型枚举"""
    DEFINITION = "definition"       # 概念定义
    PROBLEM = "problem"             # 问题分析
    SOLUTION = "solution"           # 解决方案
    EXAMPLE = "example"             # 示例说明
    COMPARISON = "comparison"       # 对比分析
    PRINCIPLE = "principle"         # 原理解释
    IMPLEMENTATION = "implementation"  # 实现步骤
    SUMMARY = "summary"             # 总结归纳


@dataclass
class ContentBlock:
    """内容块数据结构"""
    type: ContentType
    title: str
    content: str
    subtopics: List[str] = None

    def __post_init__(self):
        if self.subtopics is None:
            self.subtopics = []


class IntelligentDocumentOptimizer:
    """智能文档优化器"""

    def __init__(self):
        # 口语化词汇库
        self.oral_patterns = {
            # 口播词
            r'大家好[，。]?': '',
            r'今天(给大家|我要|我们要)': '',
            r'别忘了点赞关注': '',
            r'欢迎来到.*?频道': '',
            r'我们下次再见': '',
            r'拜拜': '',

            # 填充词
            r'那么': '',
            r'其实吧?': '',
            r'基本上': '',
            r'可以说': '',
            r'这个呢': '',
            r'那个呢': '',
            r'呢[，。]': '。',

            # 冗余表达
            r'这个就是(.+?)了': r'\1',
            r'(.+?)的话': r'\1',
            r'我们不妨': '',
            r'让我们': '',
            r'接下来': '',

            # 互动语句
            r'你可能会问': '',
            r'相信大家': '',
            r'不知道你是否': '',
            r'大家可能': '',
            r'有没有想过': '',

            # 时间指代
            r'刚才(我们)?': '',
            r'前面(我们)?': '',
            r'后面(我们)?会': '',
            r'之前(提到|说过)': '',
        }

        # 繁简转换字典
        self.traditional_to_simplified = {
            '視頻': '视频', '問題': '问题', '實際': '实际', '這個': '这个',
            '運行': '运行', '執行': '执行', '處理': '处理', '實現': '实现',
            '應用': '应用', '優化': '优化', '結構': '结构', '邏輯': '逻辑',
            '數據': '数据', '網絡': '网络', '請求': '请求', '響應': '响应',
            '設計': '设计', '開發': '开发', '測試': '测试', '調試': '调试',
            '項目': '项目', '產品': '产品', '環境': '环境', '變量': '变量',
            '類型': '类型', '參數': '参数', '返回': '返回', '調用': '调用',
            '創建': '创建', '刪除': '删除', '修改': '修改', '查詢': '查询',
            '導入': '导入', '導出': '导出', '備份': '备份', '恢復': '恢复',
            '啟動': '启动', '關閉': '关闭', '重啟': '重启', '暫停': '暂停',
            '繼續': '继续', '取消': '取消', '確認': '确认', '選擇': '选择',
            '設置': '设置', '配置': '配置', '管理': '管理', '監控': '监控',
            '分析': '分析', '統計': '统计', '報告': '报告', '日誌': '日志',
            '錯誤': '错误', '警告': '警告', '信息': '信息', '成功': '成功',
            '失敗': '失败', '異常': '异常', '正常': '正常', '狀態': '状态',
            '進度': '进度', '完成': '完成', '待辦': '待办', '進行中': '进行中',
            '歷史': '历史', '記錄': '记录', '緩存': '缓存', '內存': '内存',
            '硬盤': '硬盘', '文件': '文件', '目錄': '目录', '路徑': '路径',
            '鏈接': '链接', '地址': '地址', '端口': '端口', '協議': '协议',
            '加密': '加密', '解密': '解密', '認證': '认证', '授權': '授权',
            '權限': '权限', '角色': '角色', '用戶': '用户', '賬號': '账号',
            '密碼': '密码', '登錄': '登录', '註冊': '注册', '退出': '退出',
            '會話': '会话', '連接': '连接', '斷開': '断开', '超時': '超时',
            '並發': '并发', '同步': '同步', '異步': '异步', '隊列': '队列',
            '線程': '线程', '進程': '进程', '服務': '服务', '客戶端': '客户端',
            '服務器': '服务器', '數據庫': '数据库', '表格': '表格', '字段': '字段',
            '索引': '索引', '主鍵': '主键', '外鍵': '外键', '約束': '约束',
            '觸發器': '触发器', '存儲過程': '存储过程', '視圖': '视图', '函數': '函数'
        }

        # 技术术语修正
        self.term_corrections = {
            '方克森靠0': 'Function Calling',
            '方克森Calling': 'Function Calling',
            '材質BT': 'ChatGPT',
            'ChaBT': 'ChatGPT',
            '安斯羅培克': 'Anthropic',
            '大摩星': '大模型',
            'GiveBarkest': 'GetWeather',
            'Closed AI': 'OpenAI',
            'ClawD': 'Claude',
            'Gemnet': 'Gemini',
            '上下輪窗口': 'Context Window',
            '上下轮窗口': 'Context Window',
            'Context and Engineering': 'Context Engineering',
            'MALSEAZEN': 'Multi-Agent',
            'MaltzAgent': 'Multi-Agent',
            'Mouth Agents': 'Multi-Agent',
        }

    def convert_traditional_to_simplified(self, text: str) -> str:
        """繁体转简体"""
        for trad, simp in self.traditional_to_simplified.items():
            text = text.replace(trad, simp)
        return text

    def fix_technical_terms(self, text: str) -> str:
        """修正技术术语"""
        for wrong, correct in self.term_corrections.items():
            text = re.sub(re.escape(wrong), correct, text, flags=re.IGNORECASE)
        return text

    def remove_oral_expressions(self, text: str) -> str:
        """去除口语化表达"""
        for pattern, replacement in self.oral_patterns.items():
            text = re.sub(pattern, replacement, text)

        # 去除多余的空格和换行
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r' ([，。！？；])', r'\1', text)

        return text.strip()

    def identify_content_type(self, text: str) -> ContentType:
        """识别内容类型"""
        text_lower = text.lower()

        # 定义类型识别规则
        patterns = {
            ContentType.DEFINITION: [
                r'是什么', r'什么是', r'定义', r'概念', r'指的是', r'含义',
                r'是一种', r'是一个', r'简单来说'
            ],
            ContentType.PROBLEM: [
                r'问题', r'困难', r'挑战', r'限制', r'瓶颈', r'缺陷',
                r'为什么需要', r'为什么要', r'解决了什么'
            ],
            ContentType.SOLUTION: [
                r'解决方案', r'方法', r'技术', r'实现', r'策略',
                r'如何', r'怎么', r'步骤', r'流程'
            ],
            ContentType.EXAMPLE: [
                r'例子', r'示例', r'案例', r'举例', r'比如', r'譬如'
            ],
            ContentType.COMPARISON: [
                r'对比', r'比较', r'区别', r'不同', r'相同', r'类似',
                r'与.*相比', r'而.*则'
            ],
            ContentType.PRINCIPLE: [
                r'原理', r'机制', r'工作方式', r'底层', r'本质'
            ],
            ContentType.IMPLEMENTATION: [
                r'实施', r'部署', r'配置', r'安装', r'操作'
            ],
            ContentType.SUMMARY: [
                r'总结', r'总之', r'综上', r'回顾', r'小结'
            ]
        }

        # 统计各类型的匹配分数
        scores = {}
        for content_type, pattern_list in patterns.items():
            score = sum(1 for pattern in pattern_list if re.search(pattern, text))
            scores[content_type] = score

        # 返回得分最高的类型
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return ContentType.DEFINITION  # 默认为定义类型

    def extract_key_points(self, text: str) -> List[str]:
        """提取关键要点"""
        sentences = re.split(r'[。！？]', text)
        key_points = []

        # 关键指示词
        key_indicators = [
            '核心', '关键', '重要', '主要', '首先', '其次', '最后',
            '第一', '第二', '第三', '包括', '分为', '由于', '因此'
        ]

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # 过短的句子跳过
                continue

            # 检查是否包含关键指示词
            if any(indicator in sentence for indicator in key_indicators):
                key_points.append(sentence)
            # 或者包含技术术语
            elif any(term in sentence for term in ['API', 'Context', 'Token', 'Agent', 'Model']):
                key_points.append(sentence)

        return key_points[:10]  # 最多返回10个要点

    def organize_content_blocks(self, text: str) -> List[ContentBlock]:
        """组织内容块"""
        # 按段落分割
        paragraphs = re.split(r'\n\n+', text)
        content_blocks = []

        for para in paragraphs:
            if len(para.strip()) < 50:  # 过短的段落跳过
                continue

            # 识别内容类型
            content_type = self.identify_content_type(para)

            # 提取标题（如果有的话）
            title_match = re.match(r'^#+\s*(.+?)(?:\n|$)', para)
            if title_match:
                title = title_match.group(1)
                content = para[title_match.end():].strip()
            else:
                # 根据内容类型生成默认标题
                title = self._generate_title(para, content_type)
                content = para

            # 提取子主题
            subtopics = self.extract_key_points(content)[:3]

            block = ContentBlock(
                type=content_type,
                title=title,
                content=content,
                subtopics=subtopics
            )
            content_blocks.append(block)

        return content_blocks

    def _generate_title(self, text: str, content_type: ContentType) -> str:
        """生成标题"""
        # 提取前20个字作为基础
        preview = text[:50].split('。')[0]

        # 根据类型添加前缀
        type_prefixes = {
            ContentType.DEFINITION: "概念：",
            ContentType.PROBLEM: "问题：",
            ContentType.SOLUTION: "方案：",
            ContentType.EXAMPLE: "示例：",
            ContentType.COMPARISON: "对比：",
            ContentType.PRINCIPLE: "原理：",
            ContentType.IMPLEMENTATION: "实现：",
            ContentType.SUMMARY: "总结："
        }

        prefix = type_prefixes.get(content_type, "")

        # 尝试提取关键概念
        tech_terms = re.findall(r'[A-Z][a-zA-Z]+\s*[A-Z]*[a-zA-Z]*', preview)
        if tech_terms:
            return prefix + tech_terms[0]

        # 使用前几个词
        words = preview.split()[:5]
        return prefix + ' '.join(words)

    def generate_structured_document(self, blocks: List[ContentBlock]) -> str:
        """生成结构化文档"""
        doc = []

        # 按内容类型分组
        grouped = {}
        for block in blocks:
            if block.type not in grouped:
                grouped[block.type] = []
            grouped[block.type].append(block)

        # 定义输出顺序
        output_order = [
            ContentType.DEFINITION,
            ContentType.PROBLEM,
            ContentType.PRINCIPLE,
            ContentType.SOLUTION,
            ContentType.IMPLEMENTATION,
            ContentType.EXAMPLE,
            ContentType.COMPARISON,
            ContentType.SUMMARY
        ]

        # 按顺序输出
        for content_type in output_order:
            if content_type not in grouped:
                continue

            # 添加大章节标题
            section_titles = {
                ContentType.DEFINITION: "## 核心概念",
                ContentType.PROBLEM: "## 问题分析",
                ContentType.PRINCIPLE: "## 技术原理",
                ContentType.SOLUTION: "## 解决方案",
                ContentType.IMPLEMENTATION: "## 实现步骤",
                ContentType.EXAMPLE: "## 应用示例",
                ContentType.COMPARISON: "## 对比分析",
                ContentType.SUMMARY: "## 总结"
            }

            doc.append(section_titles[content_type])
            doc.append("")

            # 输出该类型的所有内容块
            for block in grouped[content_type]:
                # 子标题
                doc.append(f"### {block.title}")
                doc.append("")

                # 内容
                # 优化内容格式
                optimized_content = self._optimize_block_content(block.content)
                doc.append(optimized_content)
                doc.append("")

                # 如果有子要点，以列表形式展示
                if block.subtopics:
                    doc.append("**要点：**")
                    for point in block.subtopics:
                        doc.append(f"- {point}")
                    doc.append("")

        return '\n'.join(doc)

    def _optimize_block_content(self, content: str) -> str:
        """优化块内容"""
        # 分句处理
        sentences = re.split(r'([。！？])', content)
        optimized = []

        current_para = []
        for i in range(0, len(sentences)-1, 2):
            sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '')
            sentence = sentence.strip()

            if not sentence:
                continue

            current_para.append(sentence)

            # 每3-5句分段
            if len(current_para) >= 3 and sentence.endswith('。'):
                optimized.append(''.join(current_para))
                current_para = []

        if current_para:
            optimized.append(''.join(current_para))

        return '\n\n'.join(optimized)

    def optimize_document(self, text: str) -> str:
        """优化文档主流程"""
        logger.info("开始智能文档优化...")

        # Step 1: 繁简转换
        logger.info("Step 1: 繁简体转换")
        text = self.convert_traditional_to_simplified(text)

        # Step 2: 技术术语修正
        logger.info("Step 2: 技术术语修正")
        text = self.fix_technical_terms(text)

        # Step 3: 去除口语化表达
        logger.info("Step 3: 清理口语化内容")
        text = self.remove_oral_expressions(text)

        # Step 4: 识别和组织内容块
        logger.info("Step 4: 内容结构分析")
        blocks = self.organize_content_blocks(text)

        # Step 5: 生成结构化文档
        logger.info("Step 5: 生成优化文档")
        structured_doc = self.generate_structured_document(blocks)

        return structured_doc


def optimize_file(input_path: str, output_path: str) -> bool:
    """优化单个文件"""
    try:
        optimizer = IntelligentDocumentOptimizer()

        # 读取原始文件
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取标题
        lines = content.split('\n')
        title = lines[0].replace('#', '').strip() if lines else Path(input_path).stem

        # 优化内容
        optimized_content = optimizer.optimize_document('\n'.join(lines[1:]))

        # 生成最终文档
        final_doc = f"# {title}\n\n## 概述\n\n本文档基于技术视频逐字稿深度优化生成，去除了口语化内容，重构了逻辑结构。\n\n{optimized_content}"

        # 保存优化后的文档
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_doc)

        logger.info(f"✅ 优化完成: {Path(output_path).name}")
        return True

    except Exception as e:
        logger.error(f"❌ 优化失败: {e}")
        return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='智能文档深度优化')
    parser.add_argument('--input', '-i', required=True, help='输入文件或目录')
    parser.add_argument('--output', '-o', required=True, help='输出文件或目录')

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if input_path.is_file():
        # 处理单个文件
        optimize_file(str(input_path), str(output_path))
    elif input_path.is_dir():
        # 批量处理
        md_files = list(input_path.glob("*.md"))
        success = 0

        for md_file in md_files:
            out_file = output_path / f"intelligent_{md_file.name}"
            if optimize_file(str(md_file), str(out_file)):
                success += 1

        logger.info(f"\n📊 批量优化完成: {success}/{len(md_files)} 成功")
    else:
        logger.error(f"输入路径不存在: {input_path}")


if __name__ == "__main__":
    main()