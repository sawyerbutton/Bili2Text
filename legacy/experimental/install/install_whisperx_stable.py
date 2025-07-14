"""
WhisperX 稳定版安装脚本
=======================

安装兼容版本的WhisperX及其依赖项，避免版本冲突
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


def uninstall_packages():
    """卸载可能冲突的包"""
    print("\n清理可能冲突的包...")
    packages_to_remove = [
        "whisperx",
        "pyannote.audio",
        "pyannote.core",
        "pyannote.database",
        "pyannote.metrics",
        "pyannote.pipeline",
    ]
    
    for package in packages_to_remove:
        run_command([sys.executable, "-m", "pip", "uninstall", "-y", package], check=False)


def main():
    print("="*50)
    print("WhisperX 稳定版安装脚本")
    print("="*50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8或更高版本")
        return 1
    
    print(f"Python版本: {sys.version}")
    print(f"操作系统: {platform.system()}")
    
    # 询问是否清理旧版本
    response = input("\n是否清理已安装的WhisperX相关包？(y/n): ").lower()
    if response == 'y':
        uninstall_packages()
    
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
        elif platform.system() == "Windows":
            # Windows CUDA 11.8
            run_command([sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", 
                        "--index-url", "https://download.pytorch.org/whl/cu118"])
        else:  # Linux
            run_command([sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio"])
    
    # 安装特定版本的依赖以避免冲突
    print("\n3. 安装核心依赖...")
    dependencies = [
        "numpy<1.24",  # 避免新版本的兼容性问题
        "transformers>=4.30.0",
        "torchaudio",
        "ffmpeg-python",
        "pandas",
        "tqdm",
        "more-itertools",
    ]
    
    for dep in dependencies:
        print(f"安装 {dep}...")
        if not run_command([sys.executable, "-m", "pip", "install", dep]):
            print(f"警告：{dep} 安装失败")
    
    # 安装WhisperX（不包含pyannote.audio以避免冲突）
    print("\n4. 安装WhisperX...")
    
    # 首先尝试安装稳定版本
    if not run_command([sys.executable, "-m", "pip", "install", "whisperx==3.1.1", "--no-deps"]):
        print("稳定版本安装失败，尝试最新版本...")
        run_command([sys.executable, "-m", "pip", "install", "git+https://github.com/m-bain/whisperX.git", "--no-deps"])
    
    # 安装WhisperX的依赖（排除pyannote.audio）
    whisperx_deps = [
        "faster-whisper>=0.10.0",
        "pyannote.core>=5.0.0",
        "ctranslate2>=3.22.0",
    ]
    
    for dep in whisperx_deps:
        print(f"安装 {dep}...")
        run_command([sys.executable, "-m", "pip", "install", dep])
    
    # 可选：安装说话人分离支持（注意版本）
    print("\n5. 安装说话人分离支持（可选）...")
    response = input("是否安装说话人分离功能？可能会有兼容性问题 (y/n): ").lower()
    if response == 'y':
        # 安装兼容版本的pyannote.audio
        run_command([sys.executable, "-m", "pip", "install", "pyannote.audio==2.1.1"])
    
    # 验证安装
    print("\n6. 验证安装...")
    try:
        import whisperx
        print("✓ WhisperX安装成功")
        
        import torch
        print(f"✓ PyTorch版本: {torch.__version__}")
        print(f"✓ CUDA可用: {torch.cuda.is_available()}")
        
        import faster_whisper
        print("✓ faster-whisper已安装")
        
        try:
            import pyannote.audio
            print("✓ 说话人分离模块已安装")
        except ImportError:
            print("ℹ 说话人分离模块未安装（可选功能）")
        
    except ImportError as e:
        print(f"✗ 安装验证失败: {e}")
        return 1
    
    # 创建测试脚本
    print("\n7. 创建测试脚本...")
    test_script = """
import whisperx
import torch

print("WhisperX导入成功")
print(f"设备: {'cuda' if torch.cuda.is_available() else 'cpu'}")

# 尝试加载一个小模型测试
try:
    print("尝试加载tiny模型进行测试...")
    model = whisperx.load_model("tiny", "cpu", compute_type="int8", language="zh")
    print("模型加载成功！")
except Exception as e:
    print(f"模型加载失败: {e}")
"""
    
    with open("test_whisperx.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("测试脚本已创建: test_whisperx.py")
    
    # 提示说明
    print("\n" + "="*50)
    print("安装完成！")
    print("\n重要提示：")
    print("1. 如遇到segmentation fault错误，请使用修复版脚本：")
    print("   python transcribe_audio_whisperx_fixed.py")
    print("\n2. 建议使用参数：")
    print("   --language zh  # 指定中文避免自动检测")
    print("   --batch-size 8  # 减小批处理大小")
    print("   --device cpu  # 如GPU有问题可尝试CPU")
    print("\n3. 测试安装：")
    print("   python test_whisperx.py")
    print("\n4. 基本使用：")
    print("   python transcribe_audio_whisperx_fixed.py --audio-dir ./audio")
    print("\n5. 如需说话人分离功能：")
    print("   export HF_TOKEN=your_huggingface_token")
    print("   注意：说话人分离可能有兼容性问题")
    print("="*50)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())