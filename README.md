# Bili2Text - 哔哩哔哩视频转录工具

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/bili2text/bili2text?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/bili2text/bili2text?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/bili2text/bili2text?style=for-the-badge)
![License](https://img.shields.io/github/license/bili2text/bili2text?style=for-the-badge)

**简洁而强大的哔哩哔哩视频转录工具集，基于OpenAI Whisper技术**

[🚀 快速开始](#-快速开始) • [📖 使用指南](#-使用指南) • [🛠️ 开发说明](#-开发说明)

</div>

## ✨ 项目特色

### 🎯 清晰的项目架构
- 🚀 **v2 现代化版本**: 模块化设计，功能完整，易于维护
- 📂 **Legacy 兼容支持**: 保留所有原版脚本，向后兼容
- 🔧 **专业项目结构**: 清晰分离新旧代码，便于理解和贡献
- ⚡ **统一CLI接口**: 一个命令访问所有功能

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

## 📁 项目结构

```
Bili2Text/
├── README.md                      # 📖 项目说明文档
├── CLAUDE.md                      # 🤖 Claude开发指南
├── LICENSE                        # ⚖️ 开源协议
│
├── bili2text_v2/                  # 🚀 现代化版本 (推荐使用)
│   ├── bili2text.py               #   统一CLI入口
│   ├── simple_transcribe.py       #   简单转录脚本
│   ├── core/                      #   🔧 核心模块
│   │   ├── whisper_transcriber.py #     转录引擎
│   │   ├── bilibili_downloader.py #     下载器
│   │   ├── markdown_generator.py  #     输出生成器
│   │   └── file_manager.py        #     文件管理器
│   ├── workflows/                 #   ⚡ 工作流
│   │   ├── batch_transcribe.py    #     批量转录
│   │   ├── infinity_workflow.py   #     InfinityAcademy专用
│   │   └── ref_info_workflow.py   #     参考信息系列
│   └── tools/                     #   🛠️ 工具
│       ├── setup.py               #     项目设置
│       └── model_downloader.py    #     模型管理
│
└── legacy/                        # 📂 Legacy版本 (兼容保留)
    ├── README.md                  #   Legacy文档
    ├── main.py                    #   原版主程序
    ├── simple_transcribe.py       #   基础转录
    ├── download_videos.py         #   视频下载
    ├── transcribe_infinityacademy_audio.py  # 专用转录
    ├── get_all_dynamics_infinityacademy.py # 动态获取
    ├── install_dependencies.py    #   依赖安装
    └── ... (其他Legacy脚本)
```

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

### 3. 安装依赖 (v2 版本 - 推荐)
```bash
# 一键安装和设置
python bili2text_v2/tools/setup.py

# 或指定模型
python bili2text_v2/tools/setup.py --model medium
```

### 4. 开始使用

#### 🚀 v2 版本 (推荐)
```bash
# 统一CLI接口
python bili2text_v2/bili2text.py setup    # 设置
python bili2text_v2/bili2text.py simple   # 简单转录测试
python bili2text_v2/bili2text.py batch    # 批量处理

# 直接运行
python bili2text_v2/simple_transcribe.py
```

#### 📂 Legacy 版本 (兼容)
```bash
# 传统方式
python legacy/install_dependencies.py
python legacy/simple_transcribe.py
python legacy/main.py
```

## 📖 使用指南

### 🎯 v2 版本功能 (推荐)

#### 统一CLI界面
```bash
# 项目设置
python bili2text_v2/bili2text.py setup
python bili2text_v2/bili2text.py setup --model medium

# 转录功能
python bili2text_v2/bili2text.py simple      # 简单测试
python bili2text_v2/bili2text.py batch       # 批量处理
python bili2text_v2/bili2text.py infinity    # InfinityAcademy工作流
python bili2text_v2/bili2text.py ref-info    # 参考信息系列

# 模型管理
python bili2text_v2/bili2text.py model --list
python bili2text_v2/bili2text.py model --download medium
```

#### 直接模块调用
```bash
# 核心脚本
python bili2text_v2/simple_transcribe.py

# 工作流
python bili2text_v2/workflows/batch_transcribe.py
python bili2text_v2/workflows/infinity_workflow.py
python bili2text_v2/workflows/ref_info_workflow.py

# 工具
python bili2text_v2/tools/setup.py
python bili2text_v2/tools/model_downloader.py --list
```

#### 高级工作流
```bash
# InfinityAcademy 高级选项
python bili2text_v2/workflows/infinity_workflow.py --mode download    # 仅下载
python bili2text_v2/workflows/infinity_workflow.py --mode transcribe  # 仅转录

# 参考信息系列
python bili2text_v2/workflows/ref_info_workflow.py --target latest    # 最新视频
python bili2text_v2/workflows/ref_info_workflow.py --target BV1234567890  # 指定视频
```

### 📂 Legacy 版本功能 (兼容支持)

#### 核心转录脚本
```bash
# 基础转录
python legacy/simple_transcribe.py

# 批量转录
python legacy/main.py

# 专用转录
python legacy/transcribe_infinityacademy_audio.py
```

#### 视频下载脚本
```bash
# 通用下载
python legacy/download_videos.py

# 音频下载
python legacy/download_infinityacademy_audio.py
```

#### 内容发现脚本
```bash
# 动态获取
python legacy/get_all_dynamics_infinityacademy.py

# 引用提取
python legacy/get_ref_from_dynamics.py
```

#### 工具脚本
```bash
# 依赖安装
python legacy/install_dependencies.py

# 模型下载
python legacy/download_whisper_model.py
```

## 🎛️ Whisper模型选择

| 模型 | 大小 | 速度 | 精度 | 适用场景 |
|------|------|------|------|----------|
| `tiny` | 39MB | ⭐⭐⭐⭐⭐ | ⭐⭐ | 快速测试 |
| `base` | 74MB | ⭐⭐⭐⭐ | ⭐⭐⭐ | 平衡选择 |
| `medium` | 769MB | ⭐⭐⭐ | ⭐⭐⭐⭐ | **推荐使用** |
| `large-v3` | 1550MB | ⭐⭐ | ⭐⭐⭐⭐⭐ | 最高质量 |

## 🛠️ 开发说明

### v2 架构优势
- **模块化设计**: 核心功能独立，易于维护
- **统一接口**: 一个CLI访问所有功能
- **无重复代码**: 共享核心模块
- **易于扩展**: 添加新工作流简单
- **专业结构**: 符合Python项目规范

### Legacy 兼容性
- **完全保留**: 所有原版脚本继续可用
- **向后兼容**: 现有用户无需立即迁移
- **渐进升级**: 可以逐步迁移到v2版本

### 脚本定制 (两个版本通用)
```python
# 示例：修改Whisper模型
WHISPER_MODEL = "medium"  # 可改为 "tiny", "base", "large-v3"

# 示例：修改输出目录
OUTPUT_DIR = "./results"  # 自定义输出路径

# 示例：修改并发数量
MAX_WORKERS = 3  # 根据系统性能调整
```

### 版本选择建议
- **新用户**: 推荐使用 `bili2text_v2/` 版本
- **现有用户**: 可继续使用 `legacy/` 版本，或逐步迁移
- **开发贡献**: 建议基于 `bili2text_v2/` 版本进行

## 🔧 常见问题

### Q: 应该选择哪个版本？
A: 新用户推荐 v2 版本 (`bili2text_v2/`)，现有用户可以继续使用 Legacy 版本

### Q: v2 版本和 Legacy 版本有什么区别？
A: v2 版本采用模块化架构，代码更清晰，功能更强大；Legacy 版本保持原有简洁特性

### Q: Whisper模型下载失败？
A: 使用对应版本的模型下载工具，或检查网络连接

### Q: 两个版本可以同时使用吗？
A: 可以，两个版本完全独立，不会相互冲突

## 🚀 迁移指南

### 从 Legacy 到 v2
1. **环境设置**: `python bili2text_v2/tools/setup.py`
2. **测试功能**: `python bili2text_v2/simple_transcribe.py`
3. **熟悉CLI**: `python bili2text_v2/bili2text.py --help`
4. **逐步迁移**: 根据需要迁移具体功能

### v2 版本特有功能
- 统一CLI接口
- 模块化工作流
- 更好的错误处理
- 专业项目结构
- 更易于扩展

## 🤝 贡献指南

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

**开发建议**: 新功能请基于 `bili2text_v2/` 版本开发

## 📜 更新日志

### v3.0.0 - 清晰架构版本
- 🏗️ **项目重构**: 清晰分离 v2 和 Legacy 版本
- 🚀 **v2 版本**: 现代化模块架构，统一CLI接口
- 📂 **Legacy 保留**: 完整保留原版脚本，向后兼容
- 📖 **文档更新**: 全面更新文档，突出版本选择

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

**专业 • 清晰 • 高效**

</div>