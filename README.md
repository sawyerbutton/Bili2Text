# Bili2Text - 哔哩哔哩视频转录工具

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/sawyerbutton/Bili2Text?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/sawyerbutton/Bili2Text?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/sawyerbutton/Bili2Text?style=for-the-badge)
![License](https://img.shields.io/github/license/sawyerbutton/Bili2Text?style=for-the-badge)

**一个功能强大的哔哩哔哩视频转录工具，基于OpenAI Whisper技术**

[🚀 快速开始](#-快速开始) • [📖 使用文档](#-使用指南) • [🛠️ 开发指南](#-开发指南) • [📁 项目结构](#-项目结构) • [📚 更多文档](docs/)

</div>

## ✨ 功能特性

### 🎯 双重使用模式
- 🖥️ **Web应用** - 现代化的浏览器界面，适合交互式使用
- ⌨️ **命令行工具** - 强大的CLI工具，适合批量处理和自动化

### 🎥 核心功能
- 🎙️ **智能语音识别** - 基于OpenAI Whisper，支持多种模型
- 📹 **视频下载** - 支持B站视频批量下载为MP4格式
- 🎵 **音频提取** - 自动提取视频音频并转录为文字
- 📝 **多格式输出** - TXT、Markdown、JSON等多种格式
- 🔄 **实时进度** - WebSocket实时状态更新和CLI进度条
- 📊 **任务管理** - 完整的任务历史和文件管理
- 🎬 **批量下载UP主视频** - 支持一键下载UP主所有投稿视频

### 🌐 Web界面特性
- 🎨 **现代化UI** - 基于Bootstrap 5的响应式设计
- 📱 **移动端支持** - 完整的移动设备适配
- 🌙 **深色模式** - 护眼的深色主题
- ⚡ **实时通信** - WebSocket双向通信
- 📈 **数据可视化** - Chart.js性能图表

## 🆕 最新功能 (2025-09-17更新)

### 📄 智能文档优化系统
- 🤖 **Gemini 2.5 Flash集成** - 使用Google最新AI模型优化文档（100万tokens上下文）
- 🔧 **专业转录优化** - 专门针对视频逐字稿的优化提示词模板
- 📊 **批量处理** - 支持批量优化TXT和Markdown文档
- 🔄 **ASR纠错** - 80+技术术语和AI模型名称自动纠正
- 📝 **格式美化** - 智能段落分割、章节结构化、去除口语化内容
- ⚡ **TXT转Markdown** - 支持ASR输出的TXT文件直接转换为专业Markdown文档

#### 使用示例
```bash
# 设置API密钥
export GEMINI_API_KEY="your-api-key"

# 批量优化TXT文件到Markdown
python batch_optimize_txt_to_markdown.py --input storage/results/gpu_transcripts --output storage/results/professional_markdown

# 优化现有Markdown文件
python batch_optimize_mark_transcripts.py

# 使用核心优化器
from scripts.optimize.professional_gemini_optimizer import ProfessionalGeminiOptimizer, ProfessionalOptConfig

config = ProfessionalOptConfig(api_key="your-key", temperature=0.0)
optimizer = ProfessionalGeminiOptimizer(config)
optimizer.optimize_file("input.txt", "output.md")
```

详见 [文档优化指南](docs/gemini_optimizer_usage.md)

## 📋 系统要求

### 🖥️ 最低配置
- **CPU**: 4核心 2.0GHz+
- **内存**: 8GB RAM (推荐16GB+)
- **存储**: 50GB+ 可用空间
- **Python**: 3.9+ (推荐3.11)
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 20.04+

### 🚀 推荐配置
- **CPU**: 8核心 3.0GHz+ (支持AVX指令集)
- **内存**: 32GB RAM
- **GPU**: NVIDIA RTX 3060+ (8GB+ VRAM, 可选)
- **存储**: 200GB+ NVMe SSD

## 🚀 快速开始

### 方法一：使用Conda环境（推荐CLI工具）

#### 1. 安装Miniconda
```bash
# Linux/macOS
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
export PATH="$HOME/miniconda3/bin:$PATH"

# Windows
# 下载并安装 Miniconda3-latest-Windows-x86_64.exe
```

#### 2. 创建并激活环境
```bash
# 创建专用环境
conda create -n bili2text-cli python=3.11 -y
conda activate bili2text-cli

# 安装依赖包
pip install bilibili-api-python bilix httpx beautifulsoup4 lxml
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install openai-whisper
```

#### 3. 设置快捷命令
```bash
# Linux/macOS
chmod +x bili2text.sh
./bili2text.sh --help

# Windows
# 使用 python -m cli.main 替代
```

### 方法二：Docker 部署（推荐Web应用）

```bash
# 克隆项目
git clone https://github.com/sawyerbutton/Bili2Text.git
cd Bili2Text

# 使用Docker Compose一键部署
docker-compose up -d

# 访问Web界面
open http://localhost
```

### 方法三：源码安装

#### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/sawyerbutton/Bili2Text.git
cd Bili2Text

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
```

#### 2. 安装依赖
```bash
# 选择安装模式
# Web应用模式
pip install -r requirements/web.txt

# CLI工具模式  
pip install -r requirements/cli.txt

# 开发模式
pip install -r requirements/dev.txt
```

#### 3. 配置环境
```bash
# 复制配置文件
cp config/app/default.env config/app/development.env

# 编辑配置（可选）
nano config/app/development.env
```

#### 4. 启动服务

**Web应用模式：**
```bash
# 开发模式
python run.py --debug

# 生产模式
python run.py --production --host 0.0.0.0 --port 8000
```

**CLI工具模式：**
```bash
# 查看帮助
python -m cli.main --help

# 下载并转录音频
python -m cli.main audio --url "https://www.bilibili.com/video/BV1234567890"

# 下载视频文件
python -m cli.main video --url "https://www.bilibili.com/video/BV1234567890"
```

## 📖 使用指南

### 🌐 Web界面使用

1. **访问应用**: 打开浏览器访问 `http://localhost:5000`
2. **创建任务**: 输入B站视频链接，选择Whisper模型
3. **监控进度**: 实时查看下载和转录进度
4. **查看结果**: 在结果页面查看和下载转录文件
5. **历史管理**: 查看所有历史任务和文件

### ⌨️ CLI工具使用

#### 快速开始
```bash
# 使用conda环境
conda activate bili2text-cli

# 或使用便捷脚本（Linux/macOS）
./bili2text.sh --help
```

#### 核心命令

##### 1. 获取UP主动态视频
```bash
# 获取指定UP主的最新动态
./bili2text.sh dynamics --user "老师好我叫何同学" --count 5

# 输出示例：
# ✅ 成功获取 5 个动态视频:
# 1. BV1JDMQzUEwy - 【何同学】为了不用倒垃圾，我们做了这个...
# 2. BV1iZ42187bG - 【何同学】我找到了我最喜欢的数码产品...
```

##### 2. 下载音频并转录
```bash
# 基本用法
./bili2text.sh audio --url "https://www.bilibili.com/video/BV1JDMQzUEwy"

# 指定模型
./bili2text.sh audio --url "视频URL" --model base --output-dir ./results

# 输出示例：
# 🎵 正在下载音频...
# ✅ 音频下载完成
# 🔄 正在加载Whisper模型 (base)...
# 🎙️ 正在转录音频...
# ✅ 转录完成！结果已保存到: ./results/视频标题_转录结果.txt
```

##### 3. 下载视频文件
```bash
# 下载单个视频
./bili2text.sh video --url "https://www.bilibili.com/video/BV1JDMQzUEwy"

# 指定输出目录
./bili2text.sh video --url "视频URL" --output-dir ./downloads
```

##### 4. 批量下载UP主视频（新功能）
```bash
# 通过UID下载所有视频
./bili2text.sh user-videos --uid 3546737620814672

# 通过用户名下载
./bili2text.sh user-videos --user "梵公子Game学"

# 仅下载音频文件
./bili2text.sh user-videos --uid 123456 --audio-only

# 指定输出目录
./bili2text.sh user-videos --user "UP主名称" --output ./my_videos

# 使用代理下载
./bili2text.sh user-videos --uid 123456 --proxy --proxy-url http://127.0.0.1:7890

# 输出示例：
# ✅ UP主: 梵公子Game学 (UID: 3546737620814672)
# 📊 共获取 48 个投稿视频
# 📥 下载进度: 1/48
# ✅ 下载完成统计:
#   总计: 48 个视频
#   成功: 45 个
#   跳过: 3 个（已存在）
```

##### 5. 转录本地视频
```bash
# 转录已下载的视频文件
./bili2text.sh transcribe --input-dir ./storage/video --output-dir ./storage/results

# 使用指定模型
./bili2text.sh transcribe --input-dir ./videos --model medium
```

#### Whisper模型选择

| 模型 | 大小 | 速度 | 准确度 | 推荐场景 |
|------|------|------|---------|----------|
| **tiny** | 39MB | 最快 | ★★☆☆☆ | 快速测试、英文内容 |
| **base** | 74MB | 快速 | ★★★☆☆ | 日常使用推荐 ⭐ |
| **medium** | 769MB | 中等 | ★★★★☆ | 需要高质量转录 |
| **large-v3** | 1550MB | 慢 | ★★★★★ | 专业用途、最高精度 |

#### 实际性能参考
基于5分钟中文视频测试（CPU模式）：
- **音频下载**: 约10秒
- **模型加载**: base模型约90秒（首次）
- **转录处理**: base模型约50秒
- **总耗时**: 约2.5分钟

#### 高级用法

##### GPU批量转写（新功能）
```bash
# 一键转写所有已下载的视频（使用GPU加速）
./transcribe_all.sh

# 支持断点续传，如果中断可以直接重新运行
# 结果保存在: storage/results/gpu_transcripts/
```

##### 批量处理
```bash
# 批量下载UP主所有视频的音频并转录
./bili2text.sh dynamics --user "UP主名称" --count 20 > video_list.txt
# 然后使用脚本批量处理...
```

##### 自定义工作流
```bash
# 1. 先下载视频
./bili2text.sh video --url "URL" --output-dir ./raw_videos

# 2. 批量转录
./bili2text.sh transcribe --input-dir ./raw_videos --output-dir ./transcripts --model medium

# 3. 查看结果
ls -la ./transcripts/
```

#### 常见问题

**Q: 首次运行很慢？**
A: 首次使用需要下载Whisper模型，根据网络情况可能需要几分钟。模型会缓存在本地，后续使用会很快。

**Q: 如何加速转录？**
A: 
- 使用较小的模型（tiny或base）
- 如果有NVIDIA GPU，可以安装CUDA版本的PyTorch
- 考虑批量处理以复用模型加载时间

**Q: 内存不足？**
A: 
- 使用更小的模型
- 关闭其他应用程序
- 考虑增加系统swap空间

## 📁 项目结构

```
Bili2Text/
├── 🔧 bin/                       # 可执行脚本
│   └── bili2text.sh              # CLI启动脚本
├── 🎯 cli/                       # 命令行工具
│   ├── main.py                   # CLI主入口
│   ├── download_audio_new.py     # 音频下载转录
│   ├── download_video.py         # 视频下载
│   ├── get_dynamics_new.py       # 动态获取
│   ├── data/                     # CLI数据文件
│   └── transcribe_videos.py      # 本地视频转录
├── 📱 webapp/                     # Web应用
│   ├── api/                      # RESTful API
│   ├── core/                     # 核心业务逻辑
│   ├── static/                   # 前端资源
│   └── app.py                    # Flask应用入口
├── 🧠 src/                        # 共享核心库
│   ├── transcriber/              # 转录引擎
│   ├── downloader/               # 下载引擎
│   ├── utils/                    # 工具类
│   └── models/                   # 数据模型
├── 📂 storage/                    # 数据存储
│   ├── audio/                    # 音频文件
│   ├── video/                    # 视频文件
│   ├── results/                  # 转录结果
│   │   ├── gpu_transcripts/      # GPU批量转写结果
│   │   ├── professional_markdown/# Gemini优化后的文档
│   │   ├── mark_transcripts_professional/ # 优化后的转录文档
│   │   └── gemini_optimized/     # Gemini优化文档
│   └── temp/                     # 临时文件
├── 🔨 scripts/                    # 工具脚本
│   ├── transcribe/               # 转写脚本
│   ├── optimize/                 # 文档优化脚本
│   │   ├── professional_gemini_optimizer.py # 核心优化引擎
│   │   └── gemini_document_optimizer.py     # Gemini优化器
│   ├── deprecated/               # 已弃用的脚本
│   ├── setup/                    # 设置脚本
│   └── test/                     # 测试脚本
├── 🐳 deployment/                 # 部署配置
│   ├── docker/                   # Docker配置
│   ├── scripts/                  # 部署脚本
│   └── kubernetes/               # K8s配置
├── 📋 config/                     # 配置文件
│   ├── environment/              # 环境依赖
│   ├── app/                      # 应用配置
│   └── models/                   # 模型配置
├── 🧪 tests/                      # 测试代码
├── 📚 docs/                       # 项目文档
├── 💽 database/                   # 数据库文件
├── 📊 logs/                       # 日志文件
└── requirements/                  # 依赖管理
    ├── base.txt                  # 基础依赖
    ├── web.txt                   # Web依赖
    ├── cli.txt                   # CLI依赖
    └── dev.txt                   # 开发依赖
```

## 🛠️ 开发指南

### 环境搭建
```bash
# 安装开发依赖
pip install -r requirements/dev.txt

# 安装pre-commit钩子
pre-commit install

# 运行测试
pytest tests/

# 代码格式化
black src/ cli/ webapp/
isort src/ cli/ webapp/
```

### 项目架构
- **模块化设计**: CLI工具和Web应用共享核心库
- **配置管理**: 统一的配置系统，支持多环境
- **异步处理**: 支持并发下载和转录
- **错误处理**: 完善的异常处理和日志记录

### 添加新功能
1. 在 `src/` 中实现核心逻辑
2. 在 `cli/` 中添加命令行接口
3. 在 `webapp/api/` 中添加Web API
4. 编写测试用例
5. 更新文档

### 文档优化功能（新增）
使用Google Gemini 2.5 Flash优化转录后的文档：

```bash
# 设置API密钥
export GEMINI_API_KEY="your-api-key"

# 优化单个文档
python optimize_document_gemini25.py

# 批量优化（推荐）
python serial_batch_optimize.py

# 使用Shell脚本
./optimize_with_gemini.sh -i input.md -o output.md
```

详细使用说明见 [Gemini优化器文档](docs/gemini_optimizer_usage.md)

## 📄 API文档

### RESTful API

```bash
# 创建转录任务
POST /api/tasks
{
    "url": "https://www.bilibili.com/video/BV1234567890",
    "model": "medium"
}

# 查询任务状态
GET /api/tasks/{task_id}

# 获取转录结果
GET /api/tasks/{task_id}/result

# 下载结果文件
GET /api/tasks/{task_id}/download
```

### WebSocket事件

```javascript
// 连接WebSocket
const socket = io('/tasks');

// 监听任务进度
socket.on('task_progress', (data) => {
    console.log('进度:', data.progress);
});

// 监听任务完成
socket.on('task_completed', (data) => {
    console.log('任务完成:', data.result);
});
```

## 🔧 配置说明

### 应用配置
```bash
# config/app/development.env
WHISPER_MODEL=medium
STORAGE_PATH=./storage
MAX_CONCURRENT_TASKS=3
ENABLE_GPU=true
```

### 模型配置
```json
// config/models/whisper_models.json
{
    "models": {
        "medium": {
            "size": "769 MB",
            "multilingual": true,
            "recommended": true
        }
    },
    "default_model": "medium",
    "cache_dir": "./.cache/whisper"
}
```

## 🤝 贡献指南

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📜 更新日志

### v1.0.0 (2024-01-XX)
- ✨ 重构项目结构，分离CLI和Web应用
- 🔧 统一配置管理系统
- 📦 模块化依赖管理
- 🐳 完善Docker部署支持
- 📚 完整的项目文档

### v0.9.0 (2023-12-XX)
- 🎯 添加CLI工具支持
- 📱 优化Web界面体验
- 🔄 改进任务管理系统

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别引擎
- [bilix](https://github.com/HFrost0/bilix) - B站视频下载
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Bootstrap](https://getbootstrap.com/) - UI框架

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个 Star！**

[报告问题](../../issues) • [功能请求](../../issues) • [讨论](../../discussions)

</div>