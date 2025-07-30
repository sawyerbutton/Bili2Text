#!/bin/bash
# Bili2Text GPU环境创建脚本

echo "============================================================"
echo "Bili2Text GPU专用环境创建脚本"
echo "============================================================"

# 环境名称
ENV_NAME="bili2text-gpu"

# 检查conda是否可用
if ! command -v conda &> /dev/null; then
    echo "错误: 未找到conda，请先安装Miniconda或Anaconda"
    exit 1
fi

echo -e "\n1. 创建新的GPU环境..."
# 创建新环境，Python 3.11
conda create -n $ENV_NAME python=3.11 -y

echo -e "\n2. 激活GPU环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $ENV_NAME

echo -e "\n3. 安装基础依赖..."
# 安装ffmpeg
conda install -c conda-forge ffmpeg -y

echo -e "\n4. 安装GPU版PyTorch..."
# 为CUDA 12.x安装PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo -e "\n5. 安装Whisper和其他依赖..."
pip install openai-whisper

echo -e "\n6. 安装B站下载工具..."
pip install bilibili-api-python bilix==0.18.5

echo -e "\n7. 安装其他必要依赖..."
pip install httpx==0.26.0 aiofiles==23.2.1 beautifulsoup4==4.12.2 click==8.1.7 tqdm==4.66.1 rich==13.7.0 numba nvidia-ml-py3

echo -e "\n8. 验证GPU支持..."
python -c "
import torch
import whisper
print('=== GPU环境验证 ===')
print(f'PyTorch版本: {torch.__version__}')
print(f'CUDA可用: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA版本: {torch.version.cuda}')
    print(f'GPU设备: {torch.cuda.get_device_name(0)}')
    print(f'显存大小: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
    print(f'Whisper已安装: {hasattr(whisper, \"load_model\")}')
    print('\\n✅ GPU环境配置成功！')
else:
    print('\\n❌ GPU不可用，请检查CUDA安装')
"

echo -e "\n============================================================"
echo "GPU环境创建完成！"
echo ""
echo "使用方法："
echo "  激活环境: conda activate $ENV_NAME"
echo "  使用GPU转录: python -m cli.main gpu-transcribe --url <URL> --model large"
echo "  切回CPU环境: conda activate bili2text-cli"
echo ""
echo "提示："
echo "  - GPU环境独立于CPU环境，互不影响"
echo "  - GPU环境会占用更多磁盘空间（约4-5GB）"
echo "  - 建议使用medium或large模型以充分利用GPU性能"
echo "============================================================"