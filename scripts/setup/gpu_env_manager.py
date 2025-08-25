#!/usr/bin/env python3
"""
GPU环境管理工具
==============

帮助管理和切换CPU/GPU环境
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, shell=True):
    """运行命令并返回结果"""
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr


def check_current_env():
    """检查当前conda环境"""
    env = os.environ.get('CONDA_DEFAULT_ENV', 'base')
    print(f"当前环境: {env}")
    
    # 检查PyTorch
    try:
        import torch
        print(f"PyTorch版本: {torch.__version__}")
        print(f"CUDA可用: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("PyTorch未安装")
    
    return env


def list_environments():
    """列出所有conda环境"""
    success, stdout, _ = run_command("conda env list")
    if success:
        print("\n可用的conda环境:")
        print(stdout)
    

def create_aliases():
    """创建便捷的别名"""
    aliases = """
# Bili2Text 环境切换别名
alias bili-cpu='conda activate bili2text-cli'
alias bili-gpu='conda activate bili2text-gpu'
alias bili-transcribe-gpu='conda activate bili2text-gpu && python -m cli.main gpu-transcribe'
alias bili-transcribe-cpu='conda activate bili2text-cli && python -m cli.main transcribe'
"""
    
    print("\n建议添加以下别名到 ~/.bashrc 或 ~/.zshrc:")
    print(aliases)
    
    response = input("\n是否自动添加到 ~/.bashrc? (y/n): ")
    if response.lower() == 'y':
        bashrc = Path.home() / '.bashrc'
        with open(bashrc, 'a') as f:
            f.write(f"\n{aliases}")
        print("✅ 别名已添加，请运行 'source ~/.bashrc' 生效")


def compare_environments():
    """比较CPU和GPU环境"""
    print("\n=== 环境对比 ===")
    
    envs = {
        'bili2text-cli': 'CPU环境',
        'bili2text-gpu': 'GPU环境'
    }
    
    for env_name, desc in envs.items():
        print(f"\n{desc} ({env_name}):")
        
        # 获取包列表
        success, stdout, _ = run_command(f"conda list -n {env_name} | grep -E '(torch|whisper)'")
        if success:
            print(stdout)
        else:
            print("  环境不存在或无法访问")


def quick_test():
    """快速测试当前环境的转录能力"""
    print("\n=== 快速性能测试 ===")
    
    test_script = """
import time
import numpy as np

try:
    import torch
    import whisper
    
    # 检测设备
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用设备: {device}")
    
    # 加载tiny模型测试
    print("加载tiny模型...")
    start = time.time()
    model = whisper.load_model("tiny", device=device)
    load_time = time.time() - start
    print(f"模型加载时间: {load_time:.2f}秒")
    
    # 测试推理速度
    print("\\n测试推理速度...")
    # 创建30秒的静音测试
    audio = np.zeros(16000 * 30, dtype=np.float32)
    
    start = time.time()
    result = model.transcribe(audio, language="zh", fp16=(device=="cuda"))
    inference_time = time.time() - start
    print(f"30秒音频推理时间: {inference_time:.2f}秒")
    print(f"实时倍速: {30/inference_time:.1f}x")
    
    if device == "cuda":
        print(f"\\nGPU内存使用: {torch.cuda.memory_allocated()/1024**3:.2f} GB")
        
except ImportError as e:
    print(f"错误: {e}")
    print("请确保在正确的环境中运行")
"""
    
    with open("quick_test.py", "w") as f:
        f.write(test_script)
    
    subprocess.run([sys.executable, "quick_test.py"])
    os.remove("quick_test.py")


def main():
    """主函数"""
    print("=" * 60)
    print("Bili2Text 环境管理工具")
    print("=" * 60)
    
    while True:
        print("\n选项:")
        print("1. 检查当前环境")
        print("2. 列出所有环境")
        print("3. 环境对比")
        print("4. 创建快捷别名")
        print("5. 快速性能测试")
        print("6. 显示使用建议")
        print("0. 退出")
        
        choice = input("\n请选择 (0-6): ")
        
        if choice == '0':
            break
        elif choice == '1':
            check_current_env()
        elif choice == '2':
            list_environments()
        elif choice == '3':
            compare_environments()
        elif choice == '4':
            create_aliases()
        elif choice == '5':
            quick_test()
        elif choice == '6':
            print("\n=== 使用建议 ===")
            print("1. 日常少量转录: 使用CPU环境 (bili2text-cli)")
            print("2. 批量/长视频转录: 使用GPU环境 (bili2text-gpu)")
            print("3. 环境切换: conda activate <环境名>")
            print("4. GPU环境的优势:")
            print("   - medium模型: 15倍速度提升")
            print("   - large模型: 22倍速度提升")
            print("   - 支持批量并行处理")


if __name__ == '__main__':
    main()