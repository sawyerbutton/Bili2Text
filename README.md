# Bili2Text - 哔哩哔哩视频转录工具

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/bili2text/bili2text?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/bili2text/bili2text?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/bili2text/bili2text?style=for-the-badge)
![License](https://img.shields.io/github/license/bili2text/bili2text?style=for-the-badge)

**一个功能强大的哔哩哔哩视频转录工具，基于OpenAI Whisper技术**

[🚀 快速开始](#-快速开始) • [📖 使用文档](#-使用指南) • [🛠️ 开发指南](#-开发指南) • [📁 项目结构](#-项目结构)

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

### 🌐 Web界面特性
- 🎨 **现代化UI** - 基于Bootstrap 5的响应式设计
- 📱 **移动端支持** - 完整的移动设备适配
- 🌙 **深色模式** - 护眼的深色主题
- ⚡ **实时通信** - WebSocket双向通信
- 📈 **数据可视化** - Chart.js性能图表

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

### 方法一：Docker 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/your-username/Bili2Text.git
cd Bili2Text

# 使用Docker Compose一键部署
docker-compose up -d

# 访问Web界面
open http://localhost
```

### 方法二：源码安装

#### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/your-username/Bili2Text.git
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

#### 基本命令
```bash
# 音频转录
bili2text audio --url "https://www.bilibili.com/video/BV1234567890" --model medium

# 视频下载
bili2text video --url "https://www.bilibili.com/video/BV1234567890"

# 获取UP主动态
bili2text dynamics --user "UP主用户名" --count 10

# 批量处理
bili2text batch --input-dir ./videos --output-dir ./results --type audio
```

#### 可用模型
- **tiny**: 最快，精度较低（39MB）
- **base**: 平衡模式（74MB）
- **medium**: 推荐模式（769MB）⭐
- **large-v3**: 最高精度（1550MB）

## 📁 项目结构

```
Bili2Text/
├── 🎯 cli/                        # 命令行工具
│   ├── main.py                    # CLI主入口
│   ├── download_audio.py          # 音频下载转录
│   ├── download_video.py          # 视频下载
│   ├── get_dynamics.py           # 动态获取
│   └── batch_processor.py        # 批量处理
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
│   └── temp/                     # 临时文件
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