#!/usr/bin/env python3
"""
使用 Gemini 2.5 Flash 优化文档（处理超长文本）
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.optimize.gemini_document_optimizer import GeminiDocumentOptimizer, OptimizationConfig

def optimize_document(input_file, output_file):
    """优化文档"""

    # API密钥
    API_KEY = "AIzaSyDAmHzFbKgZMJVp1nyOkVr89MjXM6ahWnE"

    print("=" * 60)
    print("Gemini 2.5 Flash 文档优化")
    print("=" * 60)

    # 创建配置
    config = OptimizationConfig(
        api_key=API_KEY,
        model_name='models/gemini-2.5-flash',
        temperature=0.3,
        cache_enabled=True,
        max_tokens_per_request=10000  # 减小每次请求的大小
    )

    # 创建优化器
    optimizer = GeminiDocumentOptimizer(config)

    # 读取文件
    print(f"\n📖 读取文件: {input_file}")
    content = Path(input_file).read_text(encoding='utf-8')
    print(f"文件长度: {len(content)} 字符")

    # 先进行基础纠错
    print("\n🔧 第一步：基础纠错...")
    corrected = optimizer.apply_term_corrections(content)

    # 截取前面部分进行AI优化（避免超时）
    print("\n🤖 第二步：AI深度优化（处理前5000字）...")

    # 只处理前5000字符
    sample_text = corrected[:5000]

    try:
        # 分段优化
        chunks = optimizer.split_text(sample_text, max_length=2000)
        optimized_parts = []

        for i, chunk in enumerate(chunks):
            print(f"  处理第 {i+1}/{len(chunks)} 段...")

            # 使用更直接的提示
            import google.generativeai as genai
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('models/gemini-2.5-flash')

            prompt = f"""
请优化以下语音转录文本，使其更专业、结构化：

1. 保持原意不变
2. 改善段落结构
3. 去除口语化表达
4. 使用Markdown格式

原文：
{chunk}

优化后的文本：
"""

            response = model.generate_content(prompt)
            optimized_parts.append(response.text)

            # 避免API限流
            if i < len(chunks) - 1:
                time.sleep(2)

        # 合并结果
        optimized_content = "\n\n".join(optimized_parts)

        # 添加剩余的纠错内容（如果文档很长）
        if len(corrected) > 5000:
            optimized_content += "\n\n[以下为基础纠错内容]\n\n" + corrected[5000:]

        # 保存结果
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(output_file).write_text(optimized_content, encoding='utf-8')

        print(f"\n✅ 优化完成！")
        print(f"输出文件: {output_file}")

        # 显示预览
        print("\n📄 优化结果预览（前500字）：")
        print("-" * 50)
        print(optimized_content[:500])
        print("-" * 50)

        return True

    except Exception as e:
        print(f"\n❌ 优化失败: {e}")

        # 至少保存纠错版本
        fallback_file = output_file.replace('.md', '_corrected_only.md')
        Path(fallback_file).parent.mkdir(parents=True, exist_ok=True)
        Path(fallback_file).write_text(corrected, encoding='utf-8')
        print(f"\n💾 已保存基础纠错版本: {fallback_file}")

        return False


if __name__ == "__main__":
    # 输入输出文件
    input_file = "storage/results/expert_optimized/四大推理大模型数学与编程能力评测 - Grok3、Claude3.7、DeepSeep-R1、o3-mini-high 到底谁的推理能力最强？_深度优化版.md"
    output_file = "storage/results/gemini_optimized/四大推理大模型评测_gemini25_final.md"

    success = optimize_document(input_file, output_file)

    if success:
        print("\n🎉 文档优化成功!")
    else:
        print("\n⚠️ 部分优化失败，请查看输出")