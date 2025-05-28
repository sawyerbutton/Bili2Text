# Bili2Text

🎵 **哔哩哔哩视频音频转录工具** - 使用 OpenAI Whisper 将B站视频转换为文本

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper-green.svg)](https://github.com/openai/whisper)

## 📖 项目简介

Bili2Text 是一个强大的哔哩哔哩视频音频转录工具，基于 OpenAI 的 Whisper 模型实现高质量的语音转文本功能。项目提供两种使用模式：

- **批量处理模式** (`main.py`): 适用于已知视频URL的批量转录
- **动态监控模式** (`get_ref_from_dynamics.py`): 自动监控特定UP主动态，处理特定系列视频

## ✨ 主要功能

### 🔄 批量处理模式 (main.py)
- ✅ 批量下载指定B站视频的音频文件
- ✅ 使用Whisper模型进行高质量语音转录
- ✅ 自动标点符号标准化处理
- ✅ 输出简洁的文本文件格式
- ✅ 自动管理文件目录结构

### 🎯 动态监控模式 (get_ref_from_dynamics.py)
- ✅ 自动获取指定UP主的最新动态
- ✅ 智能筛选"参考信息"系列视频
- ✅ 生成包含视频信息的Markdown文件
- ✅ 支持B站和YouTube双平台嵌入
- ✅ 避免重复处理已转录视频
- ✅ 支持代理网络访问

## 🛠️ 技术栈

- **语音转录**: [OpenAI Whisper](https://github.com/openai/whisper)
- **视频下载**: [bilix](https://github.com/HFrost0/bilix)
- **B站API**: [bilibili-api](https://github.com/Nemo2011/bilibili-api)
- **深度学习**: PyTorch (支持CUDA加速)
- **异步处理**: asyncio

## 📋 系统要求

- **Python**: 3.11+
- **操作系统**: Windows/Linux/macOS
- **硬件**: 推荐使用NVIDIA GPU (支持CUDA)
- **网络**: 稳定的网络连接 (可选代理支持)

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/ShadyLeaf/Bili2Text.git
cd Bili2Text
```

### 2. 环境配置

#### 方法一：使用 Conda (推荐)

```bash
# 创建并激活环境
conda env create -f environment.yml
conda activate bili2text
```

#### 方法二：使用 pip

```bash
# 创建虚拟环境
python -m venv bili2text
source bili2text/bin/activate  # Linux/macOS
# 或
bili2text\Scripts\activate     # Windows

# 安装依赖
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install openai-whisper bilix bilibili-api
```

### 3. 安装 FFmpeg

#### Windows (使用 Chocolatey)
```bash
# 以管理员身份运行
choco install ffmpeg
```

#### macOS (使用 Homebrew)
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

## 📚 使用指南

### 🔄 批量处理模式

适用于已知视频URL的批量转录场景。

1. **配置视频URL列表**

编辑 `main.py` 文件中的 `audio_urls` 列表：

```python
# main.py
audio_urls = [
    "https://www.bilibili.com/video/BV1Fa4y1273F",
    "https://www.bilibili.com/video/BV15N4y1J7CA",
    # 添加更多视频URL...
]
```

2. **运行转录**

```bash
python main.py
```

3. **查看结果**

转录结果将保存在 `./result/` 目录下，每个视频对应一个 `.txt` 文件。

### 🎯 动态监控模式

适用于自动监控特定UP主动态的场景。

1. **配置UP主信息**

编辑 `get_ref_from_dynamics.py` 文件：

```python
# 修改目标UP主的UID
uid = 1556651916  # 小黛晨读的UID，替换为目标UP主

# 配置代理（可选）
use_proxy = True
if use_proxy:
    settings.proxy = "http://127.0.0.1:7890"  # 修改为你的代理地址
```

2. **运行监控**

```bash
python get_ref_from_dynamics.py
```

3. **查看结果**

- 转录结果保存在 `./result/` 目录下的 `.md` 文件
- 音频文件保存在 `./audio/` 目录
- 已处理的视频记录在 `processed.txt` 文件中

## 📁 项目结构

```
Bili2Text/
├── main.py                    # 批量处理模式主程序
├── get_ref_from_dynamics.py   # 动态监控模式主程序
├── environment.yml            # Conda环境配置
├── processed.txt              # 已处理视频记录
├── README.md                  # 项目说明文档
├── LICENSE                    # GPL v3 许可证
├── .gitignore                 # Git忽略文件配置
├── audio/                     # 音频文件存储目录
├── temp/                      # 临时文件目录
└── result/                    # 转录结果输出目录
```

## ⚙️ 配置选项

### Whisper 模型选择

项目支持多种 Whisper 模型，可根据需求选择：

| 模型 | 大小 | 速度 | 精度 | 推荐场景 |
|------|------|------|------|----------|
| `tiny` | 39MB | 最快 | 较低 | 快速测试 |
| `base` | 74MB | 快 | 一般 | 日常使用 |
| `small` | 244MB | 中等 | 良好 | 平衡选择 |
| `medium` | 769MB | 较慢 | 很好 | **推荐** |
| `large-v3` | 1550MB | 最慢 | 最高 | 高质量需求 |

在代码中修改 `model_name` 变量：

```python
model_name = "medium"  # 修改为所需模型
```

### 代理配置

如需使用代理访问B站API，在 `get_ref_from_dynamics.py` 中配置：

```python
use_proxy = True
if use_proxy:
    settings.proxy = "http://127.0.0.1:7890"  # 替换为你的代理地址
```

## 🔧 故障排除

### 常见问题

1. **CUDA 相关错误**
   - 确保安装了正确版本的 PyTorch CUDA 支持
   - 检查 NVIDIA 驱动程序是否最新

2. **网络连接问题**
   - 配置代理服务器
   - 检查防火墙设置

3. **FFmpeg 未找到**
   - 确保 FFmpeg 已正确安装并添加到系统 PATH

4. **内存不足**
   - 使用较小的 Whisper 模型
   - 减少并发处理的视频数量

### 性能优化

- **GPU 加速**: 确保安装 CUDA 版本的 PyTorch
- **模型缓存**: 首次运行会下载模型，后续运行会使用缓存
- **批量处理**: 一次处理多个视频可提高效率

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 [GPL v3](LICENSE) 许可证 - 查看 LICENSE 文件了解详情。

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 强大的语音识别模型
- [bilix](https://github.com/HFrost0/bilix) - 优秀的B站视频下载工具
- [bilibili-api](https://github.com/Nemo2011/bilibili-api) - 完善的B站API封装

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [GitHub Issue](https://github.com/ShadyLeaf/Bili2Text/issues)
- 发起 [GitHub Discussion](https://github.com/ShadyLeaf/Bili2Text/discussions)

---

⭐ 如果这个项目对你有帮助，请给它一个星标！
