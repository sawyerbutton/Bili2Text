# Bili2Text

🎵 **哔哩哔哩视频音频转录工具** - 使用 OpenAI Whisper 将B站视频转换为文本

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper-green.svg)](https://github.com/openai/whisper)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/ShadyLeaf/Bili2Text)

## 📖 项目简介

Bili2Text 是一个强大的哔哩哔哩视频音频转录工具，基于 OpenAI 的 Whisper 模型实现高质量的语音转文本功能。项目提供两种使用模式，支持多平台部署，并针对不同硬件配置进行了优化。

### 🎯 **两种工作模式**

- **🔄 批量处理模式** (`main.py`): 适用于已知视频URL的批量转录
- **🎯 动态监控模式** (`get_ref_from_dynamics.py`): 自动监控特定UP主动态，处理特定系列视频

### 🌍 **多平台支持**

- **Windows**: 完整的CUDA GPU加速支持
- **Linux**: 服务器级CUDA GPU加速支持  
- **macOS**: Apple Silicon MPS加速支持
- **跨平台**: CPU-only版本，适用于所有平台

## ✨ 主要功能

### 🔄 批量处理模式 (main.py)
- ✅ 批量下载指定B站视频的音频文件
- ✅ 使用Whisper模型进行高质量语音转录
- ✅ 自动标点符号标准化处理（英文→中文标点）
- ✅ 输出简洁的文本文件格式
- ✅ 自动管理文件目录结构
- ✅ 支持多种Whisper模型选择
- ✅ GPU/CPU自动检测和优化

### 🎯 动态监控模式 (get_ref_from_dynamics.py)
- ✅ 自动获取指定UP主的最新动态
- ✅ 智能筛选"参考信息"系列视频
- ✅ 生成包含视频信息的Markdown文件
- ✅ 支持B站和YouTube双平台嵌入模板
- ✅ 避免重复处理已转录视频
- ✅ 支持代理网络访问
- ✅ 自动生成YAML前置信息
- ✅ 时间戳和元数据管理

## 🛠️ 技术栈

- **🎙️ 语音转录**: [OpenAI Whisper](https://github.com/openai/whisper) - 最先进的语音识别模型
- **📹 视频下载**: [bilix](https://github.com/HFrost0/bilix) - 高效的B站视频下载工具
- **🔗 B站API**: [bilibili-api](https://github.com/Nemo2011/bilibili-api) - 完善的B站API封装
- **🧠 深度学习**: PyTorch 2.1.2 (支持CUDA 12.1/MPS加速)
- **⚡ 异步处理**: asyncio - 高性能异步编程
- **🔧 媒体处理**: FFmpeg - 专业音视频处理

## 📋 系统要求

### 🖥️ **基础要求**
- **Python**: 3.11+
- **操作系统**: Windows 10+/Linux/macOS 10.15+
- **内存**: 最低 4GB RAM，推荐 8GB+
- **存储**: 至少 5GB 可用空间

### 🚀 **性能要求**
- **GPU加速** (推荐): 
  - NVIDIA GPU (支持CUDA 12.1)
  - Apple Silicon (M1/M2/M3 with MPS)
- **CPU模式**: 任何现代多核处理器
- **网络**: 稳定的网络连接 (可选代理支持)

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/ShadyLeaf/Bili2Text.git
cd Bili2Text
```

### 2. 环境配置

#### 🎯 **方法一：使用 Conda (强烈推荐)**

我们为不同平台和硬件配置提供了优化的环境文件：

**🪟 Windows (NVIDIA GPU)**
```bash
conda env create -f environment-windows.yml
conda activate bili2text-windows
```

**🐧 Linux (NVIDIA GPU)**
```bash
conda env create -f environment-linux.yml
conda activate bili2text-linux
```

**🍎 macOS (Apple Silicon/Intel)**
```bash
conda env create -f environment-macos.yml
conda activate bili2text-macos
```

**💻 仅CPU版本 (所有平台)**
```bash
conda env create -f environment-cpu-only.yml
conda activate bili2text-cpu
```

**📝 原始配置文件 (Windows专用，包含所有依赖)**
```bash
conda env create -f environment.yml
conda activate bili2text
```

#### 🔧 **方法二：使用 pip**

```bash
# 创建虚拟环境
python -m venv bili2text
source bili2text/bin/activate  # Linux/macOS
# 或
bili2text\Scripts\activate     # Windows

# 安装PyTorch (根据你的平台选择)
# CUDA版本 (Windows/Linux with NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# CPU版本 (所有平台)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 安装其他依赖
pip install openai-whisper bilix bilibili-api httpx beautifulsoup4 pydantic
```

### 3. 安装 FFmpeg

#### 🪟 **Windows (使用 Chocolatey)**
```bash
# 以管理员身份运行PowerShell
choco install ffmpeg
```

#### 🍎 **macOS (使用 Homebrew)**
```bash
brew install ffmpeg
```

#### 🐧 **Linux (Ubuntu/Debian)**
```bash
sudo apt update
sudo apt install ffmpeg
```

#### 🐧 **Linux (CentOS/RHEL)**
```bash
sudo yum install epel-release
sudo yum install ffmpeg
```

## 📚 详细使用指南

### 🔄 批量处理模式

适用于已知视频URL的批量转录场景，支持同时处理多个视频。

#### **1. 配置视频URL列表**

编辑 `main.py` 文件中的 `audio_urls` 列表：

```python
# main.py
audio_urls = [
    "https://www.bilibili.com/video/BV1Fa4y1273F",
    "https://www.bilibili.com/video/BV15N4y1J7CA",
    "https://www.bilibili.com/video/BV1234567890",  # 添加更多视频URL
    # 支持任意数量的URL
]
```

#### **2. 选择Whisper模型**

在 `main.py` 中修改模型配置：

```python
# 可选模型：tiny, base, small, medium, large-v3
model_name = "medium"  # 推荐：平衡速度和精度
```

#### **3. 运行转录**

```bash
python main.py
```

#### **4. 查看结果**

- 转录结果保存在 `./result/` 目录
- 每个视频对应一个 `.txt` 文件
- 音频文件保存在 `./audio/` 目录
- 临时文件自动清理

### 🎯 动态监控模式

适用于自动监控特定UP主动态，智能筛选和处理特定系列视频。

#### **1. 配置UP主信息**

编辑 `get_ref_from_dynamics.py` 文件：

```python
# 修改目标UP主的UID
uid = 1556651916  # 小黛晨读的UID，替换为目标UP主

# 配置代理（可选）
use_proxy = True
if use_proxy:
    settings.proxy = "http://127.0.0.1:7890"  # 修改为你的代理地址
```

#### **2. 自定义筛选条件**

```python
# 修改视频标题筛选条件
if "参考信息" in title_ori:  # 可以修改为其他关键词
    # 标题格式化规则
    title = re.sub(r"【参考信息第(.*?)期】(.*?)", r"【参考信息\1】\2", title_ori)
```

#### **3. 运行监控**

```bash
python get_ref_from_dynamics.py
```

#### **4. 查看结果**

- **Markdown文件**: `./result/` 目录下的 `.md` 文件
- **音频文件**: `./audio/` 目录
- **处理记录**: `processed.txt` 文件记录已处理的视频
- **自动嵌入**: 支持B站和YouTube播放器嵌入

## 📁 项目结构

```
Bili2Text/
├── 📄 main.py                      # 批量处理模式主程序
├── 📄 get_ref_from_dynamics.py     # 动态监控模式主程序
├── ⚙️ environment.yml              # 原始Conda环境配置 (Windows详细版)
├── ⚙️ environment-windows.yml      # Windows优化配置 (推荐)
├── ⚙️ environment-linux.yml        # Linux优化配置
├── ⚙️ environment-macos.yml        # macOS优化配置
├── ⚙️ environment-cpu-only.yml     # 仅CPU版本配置
├── 📝 processed.txt                # 已处理视频记录
├── 📖 README.md                    # 项目说明文档
├── 📜 LICENSE                      # GPL v3 许可证
├── 🚫 .gitignore                   # Git忽略文件配置
├── 📁 audio/                       # 音频文件存储目录
├── 📁 temp/                        # 临时文件目录
└── 📁 result/                      # 转录结果输出目录
```

## ⚙️ 高级配置

### 🎙️ **Whisper 模型选择**

项目支持多种 Whisper 模型，可根据需求和硬件配置选择：

| 模型 | 大小 | 速度 | 精度 | 内存需求 | 推荐场景 |
|------|------|------|------|----------|----------|
| `tiny` | 39MB | ⚡⚡⚡⚡⚡ | ⭐⭐ | ~1GB | 快速测试、实时转录 |
| `base` | 74MB | ⚡⚡⚡⚡ | ⭐⭐⭐ | ~1GB | 日常使用、快速处理 |
| `small` | 244MB | ⚡⚡⚡ | ⭐⭐⭐⭐ | ~2GB | 平衡选择 |
| `medium` | 769MB | ⚡⚡ | ⭐⭐⭐⭐⭐ | ~5GB | **推荐**，质量优先 |
| `large-v3` | 1550MB | ⚡ | ⭐⭐⭐⭐⭐ | ~10GB | 最高质量需求 |

**配置方法**：
```python
# 在 main.py 或 get_ref_from_dynamics.py 中修改
model_name = "medium"  # 修改为所需模型
```

### 🌐 **代理配置**

如需使用代理访问B站API，在 `get_ref_from_dynamics.py` 中配置：

```python
use_proxy = True
if use_proxy:
    settings.proxy = "http://127.0.0.1:7890"  # HTTP代理
    # 或
    settings.proxy = "socks5://127.0.0.1:1080"  # SOCKS5代理
```

### 🎯 **自定义输出格式**

#### **批量模式输出自定义**
```python
# 在 main.py 中修改保存格式
result_file_path = result_folder_path + "/" + audio_name + ".txt"
# 可以改为其他格式，如 .md, .json 等
```

#### **动态模式输出自定义**
```python
# 在 get_ref_from_dynamics.py 中修改Markdown模板
# 可以自定义YAML前置信息、视频嵌入格式等
```

## 🔧 故障排除

### ❗ **常见问题**

#### **1. CUDA 相关错误**
```bash
# 检查CUDA版本
nvidia-smi
# 重新安装PyTorch CUDA版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### **2. 网络连接问题**
- 配置代理服务器
- 检查防火墙设置
- 尝试使用VPN或更换网络

#### **3. FFmpeg 未找到**
```bash
# 检查FFmpeg是否安装
ffmpeg -version
# 确保FFmpeg在系统PATH中
```

#### **4. 内存不足**
- 使用较小的 Whisper 模型 (`tiny`, `base`, `small`)
- 减少并发处理的视频数量
- 关闭其他占用内存的程序

#### **5. 权限问题**
```bash
# Linux/macOS 权限问题
chmod +x main.py get_ref_from_dynamics.py
# Windows 以管理员身份运行
```

### 🚀 **性能优化**

#### **GPU 加速优化**
- 确保安装正确版本的 PyTorch CUDA 支持
- 检查 NVIDIA 驱动程序是否最新
- 使用 `nvidia-smi` 监控GPU使用情况

#### **CPU 优化**
- 使用多核处理器
- 关闭不必要的后台程序
- 考虑使用较小的模型

#### **存储优化**
- 定期清理 `./temp/` 目录
- 使用SSD存储以提高I/O性能
- 确保有足够的磁盘空间

## 📋 环境配置文件详细说明

| 配置文件 | 适用平台 | GPU支持 | 特点 | 推荐用户 |
|----------|----------|---------|------|----------|
| `environment.yml` | Windows | NVIDIA CUDA | 原始详细配置，包含所有依赖 | 开发者、完整功能需求 |
| `environment-windows.yml` | Windows | NVIDIA CUDA | 优化版本，更快安装 | **Windows用户推荐** |
| `environment-linux.yml` | Linux | NVIDIA CUDA | Linux系统优化 | **Linux服务器推荐** |
| `environment-macos.yml` | macOS | Apple MPS | Apple Silicon优化 | **macOS用户推荐** |
| `environment-cpu-only.yml` | 所有平台 | 无 | 最大兼容性 | **无GPU用户推荐** |

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 📝 **如何贡献**

1. **Fork** 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 **Pull Request**

### 🐛 **报告问题**

- 使用 [GitHub Issues](https://github.com/ShadyLeaf/Bili2Text/issues) 报告bug
- 提供详细的错误信息和复现步骤
- 包含系统信息和环境配置

### 💡 **功能建议**

- 在 [GitHub Discussions](https://github.com/ShadyLeaf/Bili2Text/discussions) 中讨论新功能
- 详细描述功能需求和使用场景

## 📄 许可证

本项目采用 [GPL v3](LICENSE) 许可证。

**这意味着：**
- ✅ 可以自由使用、修改和分发
- ✅ 可以用于商业用途
- ❗ 修改后的代码必须开源
- ❗ 必须保留原始许可证声明

## 🙏 致谢

感谢以下开源项目的支持：

- **[OpenAI Whisper](https://github.com/openai/whisper)** - 革命性的语音识别模型
- **[bilix](https://github.com/HFrost0/bilix)** - 优秀的B站视频下载工具
- **[bilibili-api](https://github.com/Nemo2011/bilibili-api)** - 完善的B站API封装
- **[PyTorch](https://pytorch.org/)** - 强大的深度学习框架
- **[FFmpeg](https://ffmpeg.org/)** - 专业的音视频处理工具

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 🐛 **Bug报告**: [GitHub Issues](https://github.com/ShadyLeaf/Bili2Text/issues)
- 💬 **功能讨论**: [GitHub Discussions](https://github.com/ShadyLeaf/Bili2Text/discussions)
- 📧 **邮件联系**: [项目维护者邮箱]

## 📊 项目统计

- 🌟 **支持平台**: Windows, Linux, macOS
- 🎯 **支持模式**: 批量处理 + 动态监控
- 🚀 **加速支持**: CUDA, MPS, CPU
- 📦 **配置文件**: 5个优化版本
- 🎙️ **模型支持**: 5种Whisper模型

---

⭐ **如果这个项目对你有帮助，请给它一个星标！**

🔄 **定期更新，持续优化，欢迎关注项目动态！**