# Bili2Text - 哔哩哔哩视频转录工具

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/bili2text/bili2text?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/bili2text/bili2text?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/bili2text/bili2text?style=for-the-badge)
![License](https://img.shields.io/github/license/bili2text/bili2text?style=for-the-badge)

**简洁而强大的哔哩哔哩视频转录工具集，基于OpenAI Whisper技术**

[🚀 快速开始](#-快速开始) • [📖 脚本指南](#-脚本指南) • [🛠️ 开发说明](#-开发说明)

</div>

## ✨ 项目特色

### 🎯 简洁专注的设计理念
- 🎯 **功能专一**: 每个脚本专注解决一个具体问题
- ⚡ **即用即走**: 无需复杂配置，开箱即用
- 🔧 **易于定制**: 代码清晰，便于理解和修改
- 🧪 **经过验证**: 所有脚本都经过实际使用验证

### 🎥 核心功能
- 🎙️ **智能语音识别** - 基于OpenAI Whisper，支持多种模型
- 📹 **视频下载** - 支持B站视频下载为MP4格式
- 🎵 **音频转录** - 提取视频音频并转录为文字
- 📝 **文本输出** - 多种文本格式输出
- 🔄 **批量处理** - 支持批量视频处理
- 📊 **UP主内容发现** - 获取UP主动态和视频列表

## 📋 系统要求

### 🖥️ 基础配置
- **Python**: 3.9+ (推荐3.11)
- **内存**: 4GB+ (使用larger模型需要更多内存)
- **存储**: 根据处理视频数量而定
- **操作系统**: Windows, macOS, Linux

### 🚀 推荐配置
- **内存**: 16GB+ RAM
- **CPU**: 多核处理器
- **存储**: SSD硬盘
- **GPU**: NVIDIA GPU (可选，加速Whisper转录)

## 🚀 快速开始

### 1. 获取项目
```bash
git clone https://github.com/your-username/Bili2Text.git
cd Bili2Text
```

### 2. 环境准备
```bash
# 创建虚拟环境 (推荐)
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
# 自动安装依赖
python Original_Code/install_dependencies.py

# 或手动安装
pip install openai-whisper yt-dlp requests bilix
```

### 4. 开始使用
```bash
# 进入脚本目录
cd Original_Code

# 简单转录测试
python simple_transcribe.py

# 批量处理
python main.py
```

## 📖 脚本指南

### 🎯 核心转录脚本

#### `simple_transcribe.py` - 基础转录
**用途**: 简单的视频转录功能
**适用场景**: 初次使用、单个视频处理
```bash
python simple_transcribe.py
```

#### `main.py` - 批量转录
**用途**: 批量处理多个视频的转录
**适用场景**: 大量视频处理、日常使用
```bash
python main.py
```

#### `transcribe_infinityacademy_audio.py` - 专用转录
**用途**: 专门为InfinityAcademy UP主内容优化
**适用场景**: 处理特定UP主的视频内容
```bash
python transcribe_infinityacademy_audio.py
```

### 📥 视频下载脚本

#### `download_videos.py` - 通用下载
**用途**: 下载B站视频为MP4格式
**适用场景**: 视频收藏、离线观看
```bash
python download_videos.py
```

#### `download_infinityacademy_audio.py` - 音频下载
**用途**: 下载并提取音频用于转录
**适用场景**: 仅需要音频内容的场景
```bash
python download_infinityacademy_audio.py
```

### 🔍 内容发现脚本

#### `get_all_dynamics_infinityacademy.py` - 动态获取
**用途**: 获取UP主的动态内容
**适用场景**: 发现新内容、批量收集
```bash
python get_all_dynamics_infinityacademy.py
```

#### `get_ref_from_dynamics.py` - 引用提取
**用途**: 从动态中提取视频引用链接
**适用场景**: 自动化内容发现
```bash
python get_ref_from_dynamics.py
```

### 🛠️ 工具脚本

#### `install_dependencies.py` - 依赖安装
**用途**: 自动安装所需的Python包
**适用场景**: 环境初始化
```bash
python install_dependencies.py
```

#### `download_whisper_model.py` - 模型下载
**用途**: 预下载Whisper模型
**适用场景**: 离线使用准备
```bash
python download_whisper_model.py
```

## 🎛️ Whisper模型选择

| 模型 | 大小 | 速度 | 精度 | 适用场景 |
|------|------|------|------|----------|
| `tiny` | 39MB | ⭐⭐⭐⭐⭐ | ⭐⭐ | 快速测试 |
| `base` | 74MB | ⭐⭐⭐⭐ | ⭐⭐⭐ | 平衡选择 |
| `medium` | 769MB | ⭐⭐⭐ | ⭐⭐⭐⭐ | **推荐使用** |
| `large-v3` | 1550MB | ⭐⭐ | ⭐⭐⭐⭐⭐ | 最高质量 |

## 📁 项目结构

```
Bili2Text/
├── Original_Code/                 # 🎯 核心脚本集合
│   ├── simple_transcribe.py       # 基础转录功能
│   ├── main.py                    # 批量转录处理
│   ├── download_videos.py         # 视频下载工具
│   ├── download_infinityacademy_audio.py  # 音频下载
│   ├── transcribe_infinityacademy_audio.py # 专用转录
│   ├── get_all_dynamics_infinityacademy.py # 动态获取
│   ├── get_ref_from_dynamics.py   # 引用提取
│   ├── install_dependencies.py    # 依赖安装
│   ├── install_dependencies.sh    # Shell依赖安装
│   ├── download_whisper_model.py  # 模型下载
│   └── README_InfinityAcademy.md  # InfinityAcademy使用说明
├── .gitignore                     # Git忽略规则
├── LICENSE                        # 开源协议
├── README.md                      # 项目说明
└── CLAUDE.md                      # Claude开发指南
```

## 🛠️ 开发说明

### 脚本定制
每个脚本都可以通过修改脚本内的配置变量来定制行为：

```python
# 示例：修改Whisper模型
WHISPER_MODEL = "medium"  # 可改为 "tiny", "base", "large-v3"

# 示例：修改输出目录
OUTPUT_DIR = "./results"  # 自定义输出路径

# 示例：修改并发数量
MAX_WORKERS = 3  # 根据系统性能调整
```

### 添加新功能
1. 复制最相似的现有脚本
2. 修改核心逻辑部分
3. 调整配置参数
4. 测试功能
5. 更新文档

### 调试技巧
- 启用详细日志输出
- 使用小文件测试
- 检查网络连接
- 确认模型文件存在

## 🔧 常见问题

### Q: Whisper模型下载失败？
A: 使用 `download_whisper_model.py` 预下载，或检查网络连接

### Q: 音频转录结果为空？
A: 检查音频文件是否有效，尝试较小的模型

### Q: 下载视频失败？
A: 确认视频链接有效，检查网络连接

### Q: 脚本运行报错？
A: 检查Python版本和依赖安装，查看错误日志

## 🤝 贡献指南

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📜 更新日志

### v2.0.0 - 简化重构版本
- 🧹 **项目简化**: 移除复杂架构，专注核心功能
- 🎯 **脚本集合**: 将项目重构为简洁的脚本集合
- ⚡ **即用即走**: 无需复杂配置，开箱即用
- 📝 **文档更新**: 重写所有文档，突出简洁性

### v1.x.x - 复杂架构版本
- 复杂的Web应用和CLI工具架构
- 详细的配置管理系统
- 完整的部署方案

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别引擎
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 视频下载工具
- [bilix](https://github.com/HFrost0/bilix) - B站专用下载器

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个 Star！**

[报告问题](../../issues) • [功能请求](../../issues) • [讨论](../../discussions)

**简洁 • 专注 • 有效**

</div>