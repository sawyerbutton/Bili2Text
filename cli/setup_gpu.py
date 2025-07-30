#!/usr/bin/env python3
"""
GPU环境配置和测试脚本
=====================

功能：
    - 检测CUDA和GPU环境
    - 安装GPU版本的PyTorch
    - 测试Whisper GPU加速
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, check=True):
    """运行命令并返回结果"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"错误: {result.stderr}")
        return False, result.stderr
    
    return True, result.stdout


def check_nvidia_smi():
    """检查NVIDIA驱动"""
    print("\n=== 检查NVIDIA驱动 ===")
    success, output = run_command("nvidia-smi", check=False)
    
    if success:
        print(output)
        return True
    else:
        print("未检测到NVIDIA驱动或nvidia-smi命令")
        return False


def check_cuda():
    """检查CUDA安装"""
    print("\n=== 检查CUDA ===")
    success, output = run_command("nvcc --version", check=False)
    
    if success:
        print(output)
        # 从输出中提取CUDA版本
        import re
        match = re.search(r'release (\d+\.\d+)', output)
        if match:
            cuda_version = match.group(1)
            print(f"检测到CUDA版本: {cuda_version}")
            return cuda_version
    
    print("未检测到CUDA编译器(nvcc)")
    return None


def check_python_gpu():
    """检查Python GPU支持"""
    print("\n=== 检查Python GPU支持 ===")
    
    test_script = """
import sys
try:
    import torch
    print(f"PyTorch版本: {torch.__version__}")
    print(f"CUDA可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA版本: {torch.version.cuda}")
        print(f"GPU数量: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
            props = torch.cuda.get_device_properties(i)
            print(f"  - 计算能力: {props.major}.{props.minor}")
            print(f"  - 显存: {props.total_memory / 1024**3:.1f} GB")
except ImportError:
    print("PyTorch未安装")
    sys.exit(1)
"""
    
    # 写入临时文件
    temp_file = Path("test_gpu.py")
    temp_file.write_text(test_script)
    
    try:
        success, output = run_command(f"{sys.executable} test_gpu.py", check=False)
        print(output)
        return success
    finally:
        temp_file.unlink(missing_ok=True)


def install_pytorch_gpu():
    """安装GPU版本的PyTorch"""
    print("\n=== 安装GPU版本PyTorch ===")
    
    # 检测CUDA版本并选择合适的PyTorch
    cuda_version = check_cuda()
    
    if cuda_version:
        # 根据CUDA版本选择PyTorch版本
        if cuda_version.startswith("12"):
            index_url = "https://download.pytorch.org/whl/cu121"
            print("为CUDA 12.x安装PyTorch")
        elif cuda_version.startswith("11.8"):
            index_url = "https://download.pytorch.org/whl/cu118"
            print("为CUDA 11.8安装PyTorch")
        elif cuda_version.startswith("11.7"):
            index_url = "https://download.pytorch.org/whl/cu117"
            print("为CUDA 11.7安装PyTorch")
        else:
            index_url = "https://download.pytorch.org/whl/cu118"
            print(f"CUDA {cuda_version} - 使用默认CUDA 11.8版本")
    else:
        print("未检测到CUDA，将安装CPU版本")
        index_url = None
    
    # 构建安装命令
    if index_url:
        cmd = f"{sys.executable} -m pip install torch torchvision torchaudio --index-url {index_url}"
    else:
        cmd = f"{sys.executable} -m pip install torch torchvision torchaudio"
    
    print(f"\n执行安装命令:")
    print(cmd)
    
    response = input("\n是否继续安装? (y/n): ")
    if response.lower() == 'y':
        success, output = run_command(cmd)
        if success:
            print("\nPyTorch安装成功!")
        else:
            print("\nPyTorch安装失败!")
            print(output)


def install_whisper():
    """安装OpenAI Whisper"""
    print("\n=== 安装OpenAI Whisper ===")
    
    cmd = f"{sys.executable} -m pip install openai-whisper"
    print(f"执行: {cmd}")
    
    success, output = run_command(cmd)
    if success:
        print("Whisper安装成功!")
    else:
        print("Whisper安装失败!")
        print(output)


def test_whisper_gpu():
    """测试Whisper GPU功能"""
    print("\n=== 测试Whisper GPU ===")
    
    test_script = """
import whisper
import torch

print(f"Whisper版本: {whisper.__version__}")
print(f"使用设备: {'CUDA' if torch.cuda.is_available() else 'CPU'}")

if torch.cuda.is_available():
    # 测试加载小模型
    print("\\n测试加载tiny模型...")
    model = whisper.load_model("tiny", device="cuda")
    print(f"模型设备: {next(model.parameters()).device}")
    
    # 显示GPU内存使用
    allocated = torch.cuda.memory_allocated(0) / 1024**3
    print(f"GPU内存使用: {allocated:.2f} GB")
    
    print("\\nWhisper GPU测试成功!")
else:
    print("\\n警告: GPU不可用，Whisper将使用CPU")
"""
    
    # 写入临时文件
    temp_file = Path("test_whisper.py")
    temp_file.write_text(test_script)
    
    try:
        success, output = run_command(f"{sys.executable} test_whisper.py", check=False)
        print(output)
    finally:
        temp_file.unlink(missing_ok=True)


def create_requirements():
    """创建requirements文件"""
    print("\n=== 创建requirements文件 ===")
    
    # 创建requirements目录
    req_dir = Path("../requirements")
    req_dir.mkdir(exist_ok=True)
    
    # CLI requirements (包含GPU支持)
    cli_gpu_requirements = """# Bili2Text CLI Requirements (GPU Support)
# B站相关
bilibili-api-python
bilix==0.18.5

# 网络和异步
httpx==0.26.0
aiofiles==23.2.1

# 数据处理
beautifulsoup4==4.12.2
click==8.1.7

# 进度显示
tqdm==4.66.1
rich==13.7.0

# GPU加速的Whisper支持
# PyTorch - 请根据CUDA版本选择合适的安装命令:
# CUDA 12.1: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
# CUDA 11.8: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# CPU only: pip install torch torchvision torchaudio

# Whisper
openai-whisper

# 性能优化
numba
"""
    
    # CLI requirements (仅CPU)
    cli_cpu_requirements = """# Bili2Text CLI Requirements (CPU Only)
# B站相关
bilibili-api-python
bilix==0.18.5

# 网络和异步
httpx==0.26.0
aiofiles==23.2.1

# 数据处理
beautifulsoup4==4.12.2
click==8.1.7

# 进度显示
tqdm==4.66.1
rich==13.7.0

# CPU版本的Whisper支持
torch==2.1.0+cpu
torchvision==0.16.0+cpu
torchaudio==2.1.0+cpu
openai-whisper
"""
    
    # 写入文件
    (req_dir / "cli-gpu.txt").write_text(cli_gpu_requirements)
    (req_dir / "cli-cpu.txt").write_text(cli_cpu_requirements)
    
    print(f"已创建requirements文件:")
    print(f"  - {req_dir / 'cli-gpu.txt'} (GPU版本)")
    print(f"  - {req_dir / 'cli-cpu.txt'} (CPU版本)")


def main():
    """主函数"""
    print("=" * 60)
    print("Bili2Text GPU环境配置脚本")
    print("=" * 60)
    
    # 1. 检查NVIDIA驱动
    has_nvidia = check_nvidia_smi()
    
    # 2. 检查CUDA
    cuda_version = check_cuda()
    
    # 3. 检查Python GPU支持
    has_pytorch_gpu = check_python_gpu()
    
    # 4. 提供安装选项
    if not has_pytorch_gpu and has_nvidia:
        print("\n检测到GPU但PyTorch未安装GPU支持")
        response = input("是否安装GPU版本的PyTorch? (y/n): ")
        if response.lower() == 'y':
            install_pytorch_gpu()
            # 重新检查
            has_pytorch_gpu = check_python_gpu()
    
    # 5. 安装Whisper
    try:
        import whisper
        print("\nWhisper已安装")
    except ImportError:
        response = input("\nWhisper未安装，是否安装? (y/n): ")
        if response.lower() == 'y':
            install_whisper()
    
    # 6. 测试Whisper GPU
    if has_pytorch_gpu:
        test_whisper_gpu()
    
    # 7. 创建requirements文件
    response = input("\n是否创建requirements文件? (y/n): ")
    if response.lower() == 'y':
        create_requirements()
    
    print("\n配置完成!")
    
    # 提供使用示例
    if has_pytorch_gpu:
        print("\n使用GPU转录示例:")
        print("python cli/gpu_transcribe.py --input audio.mp3 --model medium --device cuda")
    else:
        print("\n使用CPU转录示例:")
        print("python cli/gpu_transcribe.py --input audio.mp3 --model medium --device cpu")


if __name__ == '__main__':
    main()