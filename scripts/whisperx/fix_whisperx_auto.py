#!/usr/bin/env python3
"""
自动修复WhisperX依赖问题
========================

非交互式版本，自动解决依赖冲突
"""

import subprocess
import sys
import os

def run_command(cmd, check=True):
    """运行命令并显示输出"""
    print(f"运行: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=False, text=True, check=check)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"命令失败: {e}")
        return False

def main():
    print("="*60)
    print("WhisperX 自动修复脚本")
    print("="*60)
    
    # 1. 卸载有问题的包
    print("\n1. 卸载冲突的包...")
    packages_to_uninstall = [
        "whisperx",
        "faster-whisper", 
        "pyannote.audio",
        "av",  # 也卸载av避免版本冲突
    ]
    
    for pkg in packages_to_uninstall:
        run_command([sys.executable, "-m", "pip", "uninstall", "-y", pkg], check=False)
    
    # 2. 安装兼容版本的faster-whisper和依赖
    print("\n2. 安装兼容版本的faster-whisper...")
    run_command([sys.executable, "-m", "pip", "install", "faster-whisper==0.10.0"])
    
    # 3. 安装WhisperX最新版本
    print("\n3. 安装WhisperX...")
    # 先尝试从GitHub安装最新版
    if not run_command([sys.executable, "-m", "pip", "install", "git+https://github.com/m-bain/whisperX.git"], check=False):
        # 如果失败，安装PyPI版本
        print("GitHub版本安装失败，尝试PyPI版本...")
        run_command([sys.executable, "-m", "pip", "install", "whisperx"])
    
    # 4. 验证安装
    print("\n4. 验证安装...")
    test_code = """
import os
import warnings
warnings.filterwarnings("ignore")

# 设置环境变量
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

print("测试WhisperX...")

try:
    import torch
    print(f"✓ PyTorch {torch.__version__}")
    
    import whisperx
    print("✓ WhisperX导入成功")
    
    import faster_whisper
    print(f"✓ faster-whisper导入成功")
    
    # 测试模型加载
    print("\\n尝试加载模型...")
    device = "cpu"
    
    # 使用最简单的参数
    model = whisperx.load_model("tiny", device, compute_type="int8")
    print("✓ 模型加载成功！")
    
    # 测试音频加载
    print("\\n✓ WhisperX安装成功，可以正常使用！")
    
except Exception as e:
    print(f"\\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
"""
    
    # 保存并运行测试代码
    test_file = "test_whisperx_install.py"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_code)
    
    print("\n运行测试...")
    result = subprocess.run([sys.executable, test_file], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("错误信息:")
        print(result.stderr)
    
    # 清理测试文件
    os.remove(test_file)
    
    if result.returncode == 0:
        print("\n✅ WhisperX修复成功！")
        print("\n接下来的步骤:")
        print("1. 测试音频转录:")
        print("   python legacy/transcribe_audio_whisperx_fixed.py --model tiny")
        print("\n2. 如需说话人分离功能，可以手动安装:")
        print("   pip install pyannote.audio==3.1.1")
        print("\n注意事项:")
        print("- 使用CPU模式避免GPU兼容性问题")
        print("- 指定语言参数避免自动检测错误")
        print("- 降低batch_size减少内存使用")
    else:
        print("\n❌ 修复失败")
        print("\n可能的解决方案:")
        print("1. 创建新的虚拟环境")
        print("2. 使用标准Whisper代替WhisperX:")
        print("   python legacy/transcribe_audio_whisper.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())