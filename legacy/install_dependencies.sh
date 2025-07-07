#!/bin/bash

# InfinityAcademy脚本依赖安装脚本
# 用于快速安装所需的Python依赖库

echo "=== InfinityAcademy脚本依赖安装 ==="
echo "开始安装依赖库..."

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装核心依赖
echo "安装核心依赖..."
pip install "pyyaml>=6.0"
pip install bilibili-api-python

# 安装异步HTTP库
echo "安装异步HTTP库..."
pip install aiohttp

# 安装音频处理依赖
echo "安装音频处理依赖..."
pip install bilix>=0.18.5

# 安装转录依赖（如果需要）
echo "安装音频转录依赖..."
pip install openai-whisper torch torchaudio

echo "=== 依赖安装完成 ==="
echo "现在您可以运行以下命令："
echo "1. 下载音频: python download_infinityacademy_audio.py"
echo "2. 转录音频: python transcribe_infinityacademy_audio.py"
echo ""
echo "注意：首次运行可能需要下载Whisper模型，请耐心等待。" 