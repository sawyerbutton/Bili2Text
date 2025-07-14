#!/usr/bin/env python3
"""
测试运行脚本
提供便捷的测试运行命令
"""
import sys
import subprocess
import argparse


def run_command(cmd):
    """运行命令并打印输出"""
    print(f"\n运行命令: {' '.join(cmd)}")
    print("-" * 60)
    result = subprocess.run(cmd, text=True)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="运行Bili2Text测试")
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration", "whisperx", "mp3", "quick", "coverage"],
        help="测试类型"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出"
    )
    parser.add_argument(
        "-k", "--keyword",
        help="只运行包含关键词的测试"
    )
    parser.add_argument(
        "-x", "--stop",
        action="store_true",
        help="第一个失败后停止"
    )
    
    args = parser.parse_args()
    
    # 基础命令
    base_cmd = ["pytest"]
    
    # 添加通用选项
    if args.verbose:
        base_cmd.append("-vv")
    else:
        base_cmd.append("-v")
    
    if args.stop:
        base_cmd.append("-x")
    
    if args.keyword:
        base_cmd.extend(["-k", args.keyword])
    
    # 根据测试类型添加参数
    if args.test_type == "all":
        # 运行所有测试
        cmd = base_cmd + ["tests/"]
    
    elif args.test_type == "unit":
        # 只运行单元测试
        cmd = base_cmd + ["-m", "unit", "tests/"]
    
    elif args.test_type == "integration":
        # 只运行集成测试
        cmd = base_cmd + ["-m", "integration", "tests/"]
    
    elif args.test_type == "whisperx":
        # 只运行WhisperX相关测试
        cmd = base_cmd + ["-m", "whisperx", "tests/"]
    
    elif args.test_type == "mp3":
        # 只运行MP3相关测试
        cmd = base_cmd + ["-m", "mp3", "tests/"]
    
    elif args.test_type == "quick":
        # 快速测试（跳过慢速测试）
        cmd = base_cmd + ["-m", "not slow", "tests/"]
    
    elif args.test_type == "coverage":
        # 运行覆盖率测试
        cmd = base_cmd + [
            "--cov=bili2text_v2",
            "--cov=legacy",
            "--cov-report=html",
            "--cov-report=term-missing",
            "tests/"
        ]
        print("\n覆盖率报告将生成在 htmlcov/index.html")
    
    # 运行测试
    return_code = run_command(cmd)
    
    if args.test_type == "coverage" and return_code == 0:
        print("\n✅ 测试完成！覆盖率报告已生成。")
        print("使用浏览器打开 htmlcov/index.html 查看详细报告。")
    
    return return_code


if __name__ == "__main__":
    sys.exit(main())