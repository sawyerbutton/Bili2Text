#!/usr/bin/env python3
"""
真实测试 Gemini 2.5 Flash 文档优化
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.optimize.gemini_document_optimizer import GeminiDocumentOptimizer, OptimizationConfig


def run_real_test(api_key):
    """运行真实的Gemini API测试"""

    print("="*60)
    print("Gemini 2.5 Flash 文档优化测试")
    print("="*60)

    # 创建配置
    config = OptimizationConfig(
        api_key=api_key,
        model_name='models/gemini-2.5-flash',  # 使用 Gemini 2.5 Flash
        temperature=0.3,
        cache_enabled=True
    )

    print(f"\n配置信息:")
    print(f"- 模型: {config.model_name}")
    print(f"- Temperature: {config.temperature}")
    print(f"- 缓存: {'启用' if config.cache_enabled else '禁用'}")

    # 创建优化器
    optimizer = GeminiDocumentOptimizer(config)

    # 测试文件路径
    input_file = "test_sample_transcript.md"
    output_file = "test_sample_optimized.md"

    if not Path(input_file).exists():
        print(f"\n错误：找不到测试文件 {input_file}")
        return False

    print(f"\n输入文件: {input_file}")
    print(f"输出文件: {output_file}")

    try:
        # 读取原始内容
        original_content = Path(input_file).read_text(encoding='utf-8')
        print(f"\n原始文档预览 (前500字):")
        print("-"*50)
        print(original_content[:500])
        print("-"*50)

        # 执行优化
        print("\n开始优化文档...")
        optimizer.optimize_file(input_file, output_file)

        # 读取优化结果
        if Path(output_file).exists():
            optimized_content = Path(output_file).read_text(encoding='utf-8')

            print(f"\n✅ 优化成功!")
            print(f"\n优化后文档预览 (前1000字):")
            print("="*50)
            print(optimized_content[:1000])
            print("="*50)

            # 统计信息
            print(f"\n统计信息:")
            print(f"- 原始文档长度: {len(original_content)} 字符")
            print(f"- 优化后文档长度: {len(optimized_content)} 字符")

            # 检查关键纠错
            corrections_found = []
            if "DeepSeek" in optimized_content and "Dipsyc" not in optimized_content:
                corrections_found.append("Dipsyc → DeepSeek")
            if "Grok" in optimized_content and "Gorax" not in optimized_content:
                corrections_found.append("Gorax → Grok")
            if "Claude" in optimized_content and "Klaus" not in optimized_content:
                corrections_found.append("Klaus → Claude")
            if "LeetCode" in optimized_content and "LiCo" not in optimized_content:
                corrections_found.append("LiCo → LeetCode")
            if "o3-mini-high" in optimized_content:
                corrections_found.append("O3 Mini Hide → o3-mini-high")

            if corrections_found:
                print(f"\n✅ 成功纠正的专有名词:")
                for correction in corrections_found:
                    print(f"  - {correction}")

            return True
        else:
            print(f"\n❌ 优化失败：输出文件未生成")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    # 从环境变量获取API密钥
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("错误：未设置 GEMINI_API_KEY 环境变量")
        print("\n请使用以下命令设置:")
        print("export GEMINI_API_KEY='your-api-key-here'")
        print("\n或在运行时传入:")
        print("GEMINI_API_KEY='your-api-key' python run_gemini_test.py")
        return 1

    # 运行测试
    success = run_real_test(api_key)

    if success:
        print("\n🎉 测试完成! Gemini 2.5 Flash 工作正常!")
        print("\n你可以使用以下命令优化更多文档:")
        print("./optimize_with_gemini.sh -i your_file.md -o optimized.md")
        return 0
    else:
        print("\n测试未完全通过，请检查错误信息")
        return 1


if __name__ == '__main__':
    exit(main())