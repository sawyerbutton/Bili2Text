#!/usr/bin/env python3
"""
修复WhisperX依赖问题
====================

解决faster-whisper版本不兼容和其他依赖冲突
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
    print("WhisperX 依赖修复脚本")
    print("="*60)
    
    # 1. 卸载有问题的包
    print("\n1. 卸载冲突的包...")
    packages_to_uninstall = [
        "whisperx",
        "faster-whisper",
        "pyannote.audio",
    ]
    
    for pkg in packages_to_uninstall:
        run_command([sys.executable, "-m", "pip", "uninstall", "-y", pkg], check=False)
    
    # 2. 安装兼容版本的faster-whisper
    print("\n2. 安装兼容版本的faster-whisper...")
    run_command([sys.executable, "-m", "pip", "install", "faster-whisper==0.10.0"])
    
    # 3. 安装WhisperX（不自动安装依赖）
    print("\n3. 安装WhisperX...")
    run_command([sys.executable, "-m", "pip", "install", "whisperx", "--no-deps"])
    
    # 4. 安装其他必需的依赖
    print("\n4. 安装其他依赖...")
    deps = [
        "pyannote.core>=5.0.0",
        "ctranslate2>=3.22.0",
    ]
    
    for dep in deps:
        run_command([sys.executable, "-m", "pip", "install", dep])
    
    # 5. 可选：安装pyannote.audio（用于说话人分离）
    print("\n5. 是否安装说话人分离功能？")
    response = input("安装pyannote.audio？可能有兼容性问题 (y/n): ").lower()
    if response == 'y':
        print("安装pyannote.audio 3.1.1...")
        run_command([sys.executable, "-m", "pip", "install", "pyannote.audio==3.1.1"])
    
    # 6. 验证安装
    print("\n6. 验证安装...")
    test_code = """
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import whisperx
import torch

print("✓ WhisperX导入成功")
print(f"✓ 设备: {'cuda' if torch.cuda.is_available() else 'cpu'}")

# 测试模型加载
try:
    model = whisperx.load_model("tiny", "cpu", compute_type="int8")
    print("✓ 模型加载成功！")
    del model
except Exception as e:
    print(f"✗ 模型加载失败: {e}")
"""
    
    # 保存测试代码
    with open("test_whisperx_fixed.py", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    # 运行测试
    print("\n运行测试...")
    result = subprocess.run([sys.executable, "test_whisperx_fixed.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("错误信息:")
        print(result.stderr)
    
    if result.returncode == 0:
        print("\n✅ WhisperX修复成功！")
        print("\n使用说明:")
        print("1. 基本转录:")
        print("   python legacy/transcribe_audio_whisperx_fixed.py")
        print("\n2. 指定参数:")
        print("   python legacy/transcribe_audio_whisperx_fixed.py --model base --device cpu")
        print("\n3. 批量处理:")
        print("   python legacy/download_and_transcribe_whisperx.py")
    else:
        print("\n❌ 修复失败，请检查错误信息")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())