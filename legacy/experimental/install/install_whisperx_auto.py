"""
WhisperX 自动安装脚本
=====================

自动安装WhisperX及其依赖项，无需交互
"""

import subprocess
import sys
import os
import platform


def run_command(cmd, check=True):
    """运行命令并显示输出"""
    print(f"运行命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=False, text=True, check=check)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        return False


def main():
    print("="*50)
    print("WhisperX 自动安装脚本")
    print("="*50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8或更高版本")
        return 1
    
    print(f"Python版本: {sys.version}")
    print(f"操作系统: {platform.system()}")
    
    # 升级pip
    print("\n1. 升级pip...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # 安装PyTorch（如果尚未安装）
    print("\n2. 检查PyTorch...")
    try:
        import torch
        print(f"PyTorch已安装: {torch.__version__}")
        print(f"CUDA可用: {torch.cuda.is_available()}")
    except ImportError:
        print("安装PyTorch...")
        if platform.system() == "Darwin":  # macOS
            run_command([sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio"])
        else:  # Linux/Windows
            run_command([sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio"])
    
    # 安装核心依赖
    print("\n3. 安装核心依赖...")
    dependencies = [
        "numpy<1.24",
        "transformers>=4.30.0",
        "torchaudio",
        "ffmpeg-python",
        "pandas",
        "tqdm",
        "more-itertools",
    ]
    
    for dep in dependencies:
        print(f"安装 {dep}...")
        run_command([sys.executable, "-m", "pip", "install", dep])
    
    # 安装WhisperX
    print("\n4. 安装WhisperX...")
    run_command([sys.executable, "-m", "pip", "install", "whisperx"])
    
    # 验证安装
    print("\n5. 验证安装...")
    try:
        import whisperx
        print("✓ WhisperX安装成功")
        
        import torch
        print(f"✓ PyTorch版本: {torch.__version__}")
        print(f"✓ CUDA可用: {torch.cuda.is_available()}")
        
    except ImportError as e:
        print(f"✗ 安装验证失败: {e}")
        return 1
    
    print("\n安装完成！")
    return 0


if __name__ == "__main__":
    sys.exit(main())