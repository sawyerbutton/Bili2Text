#!/bin/bash
# Bili2Text GPU版PyTorch安装脚本

echo "=== 安装GPU版本PyTorch ==="
echo "检测到CUDA 12.9，将安装兼容的PyTorch版本"

# 确保在正确的conda环境中
if [[ "$CONDA_DEFAULT_ENV" != "bili2text-cli" ]]; then
    echo "请先激活conda环境: conda activate bili2text-cli"
    exit 1
fi

# 卸载CPU版本（如果存在）
echo "卸载现有的CPU版本PyTorch..."
pip uninstall -y torch torchvision torchaudio

# 安装GPU版本
echo "安装GPU版本PyTorch (CUDA 12.1兼容)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 验证安装
echo -e "\n=== 验证GPU支持 ==="
python -c "
import torch
print(f'PyTorch版本: {torch.__version__}')
print(f'CUDA可用: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA版本: {torch.version.cuda}')
    print(f'GPU设备: {torch.cuda.get_device_name(0)}')
    print(f'GPU数量: {torch.cuda.device_count()}')
else:
    print('ERROR: CUDA仍然不可用！')
"

echo -e "\n安装完成！"