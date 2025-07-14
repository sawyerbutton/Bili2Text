"""
WhisperX 安装脚本
=================

用于安装WhisperX及其依赖项
"""

import subprocess
import sys
import os


def run_command(cmd):
    """运行命令并显示输出"""
    print(f"运行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False, text=True)
    if result.returncode != 0:
        print(f"命令执行失败，返回码: {result.returncode}")
        return False
    return True


def check_cuda():
    """检查CUDA是否可用"""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ CUDA可用，GPU: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("✗ CUDA不可用，将使用CPU版本")
            return False
    except ImportError:
        print("PyTorch未安装，稍后将安装")
        return False


def main():
    print("="*50)
    print("WhisperX 安装脚本")
    print("="*50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8或更高版本")
        return 1
    
    print(f"Python版本: {sys.version}")
    
    # 升级pip
    print("\n1. 升级pip...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # 安装PyTorch
    print("\n2. 安装PyTorch...")
    cuda_available = check_cuda()
    
    if not cuda_available:
        # 尝试安装CUDA版本的PyTorch
        print("尝试安装CUDA版本的PyTorch...")
        # 根据系统选择合适的安装命令
        if sys.platform == "win32":
            run_command([sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", 
                        "--index-url", "https://download.pytorch.org/whl/cu118"])
        else:
            run_command([sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio"])
    
    # 安装WhisperX
    print("\n3. 安装WhisperX...")
    if not run_command([sys.executable, "-m", "pip", "install", "whisperx"]):
        print("WhisperX安装失败，尝试从GitHub安装...")
        run_command([sys.executable, "-m", "pip", "install", "git+https://github.com/m-bain/whisperX.git"])
    
    # 安装其他依赖
    print("\n4. 安装其他依赖...")
    dependencies = [
        "ffmpeg-python",  # 音频处理
        "pyannote.audio",  # 说话人分离（可选）
    ]
    
    for dep in dependencies:
        print(f"安装 {dep}...")
        run_command([sys.executable, "-m", "pip", "install", dep])
    
    # 验证安装
    print("\n5. 验证安装...")
    try:
        import whisperx
        print("✓ WhisperX安装成功")
        
        import torch
        print(f"✓ PyTorch版本: {torch.__version__}")
        print(f"✓ CUDA可用: {torch.cuda.is_available()}")
        
        try:
            import pyannote.audio
            print("✓ 说话人分离模块已安装")
        except ImportError:
            print("✗ 说话人分离模块未安装（可选功能）")
        
    except ImportError as e:
        print(f"✗ 安装验证失败: {e}")
        return 1
    
    # 提示说明
    print("\n" + "="*50)
    print("安装完成！")
    print("\n使用说明：")
    print("1. 基础转录：")
    print("   python transcribe_audio_whisperx.py")
    print("\n2. 下载并转录：")
    print("   python download_and_transcribe_whisperx.py --urls <URL1> <URL2>")
    print("\n3. 启用说话人分离（需要HuggingFace token）：")
    print("   export HF_TOKEN=your_token")
    print("   python transcribe_audio_whisperx.py --enable-diarization")
    print("\n注意事项：")
    print("- 首次运行会自动下载模型文件（约1.5GB）")
    print("- GPU加速需要CUDA支持")
    print("- 说话人分离需要HuggingFace账号和token")
    print("="*50)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())