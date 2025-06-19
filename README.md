# Bili2Text Web

一个功能强大的哔哩哔哩视频转录Web应用，基于OpenAI Whisper技术，提供现代化的Web界面和完整的任务管理系统。

## ✨ 功能特性

### 🎯 核心功能
- 🎥 **智能视频转录** - 支持B站视频URL一键转录
- 🎙️ **高精度语音识别** - 基于OpenAI Whisper多模型支持
- 📝 **多格式输出** - TXT、Markdown、JSON等多种格式
- 🔄 **实时进度监控** - WebSocket实时状态更新
- 📊 **详细统计分析** - 任务统计、性能监控、使用趋势
- 🗂️ **任务历史管理** - 完整的任务记录和文件管理

### 🌐 Web界面特性
- 🎨 **现代化界面** - 基于Bootstrap 5的响应式设计
- 📱 **移动端适配** - 完整的移动设备支持
- 🌙 **深色模式** - 护眼的深色主题
- ⚡ **实时通信** - WebSocket双向通信
- 📈 **数据可视化** - Chart.js性能图表
- 🔍 **高级搜索** - 多条件筛选和搜索

### 🛠️ 技术特性
- 🔧 **RESTful API** - 标准化的API接口设计
- 🚀 **异步任务处理** - 多线程并发处理
- 💾 **数据持久化** - SQLite数据库存储
- 📁 **智能文件管理** - 自动清理和存储优化
- 🔒 **安全可靠** - 完善的错误处理和验证机制
- 🐳 **容器化部署** - Docker一键部署

## 📋 系统要求

### 🖥️ 最低配置
- **CPU**: 4核心 2.0GHz+
- **内存**: 8GB RAM (推荐16GB+)
- **存储**: 50GB+ 可用空间 (SSD推荐)
- **Python**: 3.9+ (推荐3.11)
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 20.04+

### 🚀 推荐配置
- **CPU**: 8核心 3.0GHz+ (支持AVX指令集)
- **内存**: 32GB RAM
- **GPU**: NVIDIA RTX 3060+ (8GB+ VRAM, 可选)
- **存储**: 200GB+ NVMe SSD
- **网络**: 稳定的互联网连接

### 🔧 核心依赖
- **yt-dlp** - 视频下载引擎
- **FFmpeg** - 音频处理工具
- **OpenAI Whisper** - 语音识别引擎
- **Flask + SocketIO** - Web框架
- **SQLite** - 数据库引擎

## 🚀 快速开始

### 方法一：Docker 部署（推荐）

#### Linux/macOS
```bash
# 克隆项目
git clone https://github.com/your-username/Bili2Text.git
cd Bili2Text

# 一键部署
chmod +x deploy.sh
./deploy.sh deploy

# 查看状态
./deploy.sh status
```

#### Windows
```powershell
# 克隆项目
git clone https://github.com/your-username/Bili2Text.git
cd Bili2Text

# 一键部署
.\deploy.ps1 deploy

# 查看状态
.\deploy.ps1 status
```

部署完成后访问：**http://localhost**

### 方法二：源码部署

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
# 安装Python依赖
pip install -r requirements.txt

# 安装FFmpeg
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg
# Windows: choco install ffmpeg

# 安装yt-dlp
pip install yt-dlp
```

#### 3. 配置环境
```bash
# 复制配置文件
cp env.example .env

# 编辑配置（可选）
nano .env
```

#### 4. 启动服务
```bash
# 测试应用
python test_app.py

# 启动开发服务器
python run.py --debug

# 启动生产服务器
python run.py --production --host 0.0.0.0 --port 8000
```

#### 5. 访问应用
打开浏览器访问：**http://localhost:5000**

## 📁 项目结构

```
Bili2Text/
├── 📱 webapp/                     # Web应用主目录
│   ├── 🔌 api/                   # API接口层
│   │   ├── routes.py            # RESTful API路由
│   │   └── websocket_handlers.py # WebSocket事件处理
│   ├── 🧠 core/                  # 核心业务层
│   │   ├── config.py            # 应用配置管理
│   │   ├── database.py          # 数据库模型
│   │   ├── task_manager.py      # 任务处理引擎
│   │   ├── file_manager.py      # 文件存储管理
│   │   ├── system_monitor.py    # 系统监控
│   │   └── error_handler.py     # 错误处理
│   ├── 🎨 static/                # 前端资源
│   │   ├── css/style.css        # 样式表
│   │   ├── js/                  # JavaScript模块
│   │   │   ├── main.js          # 核心工具类
│   │   │   ├── websocket.js     # WebSocket管理
│   │   │   ├── task-manager.js  # 任务管理器
│   │   │   ├── history-manager.js # 历史管理
│   │   │   └── system-monitor.js # 系统监控
│   │   └── templates/           # HTML模板
│   │       ├── base.html        # 基础模板
│   │       ├── index.html       # 主页面
│   │       ├── history.html     # 历史记录
│   │       └── system.html      # 系统状态
│   └── app.py                   # Flask应用入口
├── 💾 storage/                    # 数据存储目录
│   ├── audio/                   # 音频文件存储
│   ├── results/                 # 转录结果存储
│   └── temp/                    # 临时文件
├── 🐳 docker/                     # Docker配置
│   ├── Dockerfile              # 应用镜像
│   ├── docker-compose.yml      # 服务编排
│   └── nginx/                  # Nginx配置
├── 📚 docs/                       # 项目文档
│   ├── project-design.md       # 项目设计
│   ├── architecture-overview.md # 架构概览
│   ├── deployment-guide.md     # 部署指南
│   └── api-documentation.md    # API文档
├── 🛠️ scripts/                    # 部署脚本
│   ├── deploy.sh               # Linux/macOS部署
│   ├── deploy.ps1              # Windows部署
│   └── backup.sh               # 备份脚本
├── 📋 environment*.yml            # Conda环境配置
├── requirements.txt            # Python依赖
├── run.py                      # 启动脚本
└── test_app.py                 # 应用测试
```

## 📖 使用指南

### 🎬 基本使用流程

#### 1. 创建转录任务
- 📝 在主页输入B站视频链接（支持完整URL、短链接、BV号）
- 🎙️ 选择Whisper模型：
  - **tiny**: 快速模式，适合测试
  - **base**: 平衡模式，日常使用
  - **medium**: 推荐模式，质量优先 ⭐
  - **large-v3**: 最高质量，慢速精确
- ⚙️ 配置高级选项（代理、输出格式、语言等）
- 🚀 点击"开始转录"

#### 2. 实时监控进度
- 📊 查看实时下载和转录进度
- ⏱️ 显示预计剩余时间
- 🔄 支持任务暂停和取消
- 📢 接收浏览器通知

#### 3. 获取转录结果
- 👁️ 在线预览转录文本
- 📥 下载多种格式文件（TXT、MD、JSON）
- 🎵 下载原始音频文件（可选）
- 📋 一键复制到剪贴板

#### 4. 管理任务历史
- 📚 查看完整任务历史记录
- 🔍 按状态、日期、关键词搜索
- 🗑️ 批量删除和文件管理
- 📊 查看统计数据和使用趋势

### 🚀 高级功能

#### 📦 批量处理
- 📝 支持批量提交多个视频URL
- ⚡ 智能队列管理和并发控制
- 📊 批量下载和结果导出
- 🎯 统一配置和格式设置

#### 📈 系统监控
- 💻 实时CPU、内存、磁盘使用率
- 📊 任务处理统计和性能趋势
- 🔧 服务状态健康检查
- 📈 可视化性能图表
- 🚨 自动警告和错误监控

#### ⚙️ 灵活配置
- 🌐 代理设置（HTTP/SOCKS代理支持）
- 🎵 音频文件保留选项
- 📄 多种输出格式选择
- 🌍 语言自动检测和手动选择
- 🔧 任务并发数和超时设置

## 🔌 API文档

### 📋 任务管理API

#### 创建转录任务
```http
POST /api/tasks/
Content-Type: application/json

{
    "url": "https://www.bilibili.com/video/BV1234567890",
    "model_name": "medium",
    "options": {
        "use_proxy": false,
        "keep_audio": true,
        "output_format": "txt",
        "language": "auto"
    }
}
```

**响应示例**：
```json
{
    "success": true,
    "data": {
        "id": "task_20240115_143022_abc123",
        "url": "https://www.bilibili.com/video/BV1234567890",
        "status": "pending",
        "model_name": "medium",
        "created_at": "2024-01-15T14:30:22Z"
    },
    "message": "任务创建成功"
}
```

#### 获取任务列表
```http
GET /api/tasks/?page=1&limit=20&status=completed&date_from=2024-01-01
```

#### 获取任务详情
```http
GET /api/tasks/{task_id}
```

#### 取消任务
```http
POST /api/tasks/{task_id}/cancel
```

#### 删除任务
```http
DELETE /api/tasks/{task_id}
```

### 📁 文件操作API

#### 下载转录结果
```http
GET /api/files/{task_id}/result
```

#### 下载音频文件
```http
GET /api/files/{task_id}/audio
```

#### 删除任务文件
```http
DELETE /api/files/{task_id}
```

### 📊 系统状态API

#### 获取系统状态
```http
GET /api/system/status
```

**响应示例**：
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "uptime": 86400,
        "cpu_usage": 25.5,
        "memory_usage": 45.2,
        "disk_usage": 67.8,
        "active_tasks": 2,
        "queue_size": 0
    }
}
```

#### 获取可用模型
```http
GET /api/system/models
```

#### 获取统计数据
```http
GET /api/system/stats?period=day
```

### 🔄 WebSocket实时通信

#### 连接管理
```javascript
// 连接到任务房间
socket.emit('join_task', {task_id: 'task_123456'});

// 连接到系统监控房间
socket.emit('join_system');

// 心跳检测
socket.emit('ping');
```

#### 实时事件
```javascript
// 任务状态更新
socket.on('task_update', (data) => {
    console.log('任务更新:', data);
    // {
    //   task_id: 'task_123456',
    //   status: 'transcribing',
    //   progress: 45.5,
    //   stage: '正在转录音频...'
    // }
});

// 任务完成通知
socket.on('task_notification', (data) => {
    console.log('任务完成:', data);
});

// 系统状态更新
socket.on('system_update', (data) => {
    console.log('系统状态:', data);
});
```

### 📝 错误处理

#### 统一错误响应格式
```json
{
    "success": false,
    "error": {
        "code": "TASK_NOT_FOUND",
        "message": "指定的任务不存在",
        "details": {
            "task_id": "invalid_task_id"
        }
    },
    "timestamp": "2024-01-15T14:30:22Z"
}
```

#### 错误代码说明
- `VALIDATION_ERROR` - 请求数据验证失败
- `INVALID_URL` - 无效的视频URL
- `INVALID_MODEL` - 不支持的模型
- `SYSTEM_OVERLOAD` - 系统负载过高
- `TASK_NOT_FOUND` - 任务不存在
- `FILE_NOT_FOUND` - 文件不存在
- `INTERNAL_ERROR` - 内部服务器错误

## ⚙️ 配置说明

### 🌍 环境变量配置

创建 `.env` 文件并配置以下选项：

```bash
# 应用基础配置
APP_NAME=Bili2Text Web
DEBUG=false
SECRET_KEY=your-super-secret-key-here

# 数据库配置
DATABASE_URL=sqlite:///./storage/bili2text.db

# 文件存储配置
STORAGE_ROOT=./storage
MAX_FILE_SIZE=1073741824  # 1GB

# 任务处理配置
MAX_CONCURRENT_TASKS=3
TASK_TIMEOUT=3600  # 1小时

# Whisper模型配置
DEFAULT_MODEL=medium
MODEL_CACHE_PATH=./.cache/whisper

# 网络代理配置（可选）
USE_PROXY=false
PROXY_URL=http://127.0.0.1:7890

# 系统监控配置
SYSTEM_MONITOR_INTERVAL=5
PERFORMANCE_HISTORY_LIMIT=100

# 日志配置
LOG_LEVEL=INFO
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5
```

### 🎛️ Whisper模型配置

```python
WHISPER_MODELS = {
    'tiny': {
        'name': 'tiny',
        'size': '39MB',
        'speed': 'very_fast',
        'accuracy': 'low',
        'memory_required': '1GB',
        'recommended_for': '快速测试、实时转录'
    },
    'base': {
        'name': 'base', 
        'size': '142MB',
        'speed': 'fast',
        'accuracy': 'medium',
        'memory_required': '2GB',
        'recommended_for': '日常使用'
    },
    'medium': {
        'name': 'medium',
        'size': '769MB', 
        'speed': 'medium',
        'accuracy': 'high',
        'memory_required': '5GB',
        'recommended_for': '推荐使用，质量优先',
        'default': True
    },
    'large-v3': {
        'name': 'large-v3',
        'size': '1550MB',
        'speed': 'slow', 
        'accuracy': 'very_high',
        'memory_required': '10GB',
        'recommended_for': '最高质量转录'
    }
}
```

### 🔧 高级配置选项

```python
# 支持的输出格式
SUPPORTED_OUTPUT_FORMATS = ['txt', 'md', 'json']

# 支持的语言
SUPPORTED_LANGUAGES = {
    'auto': '自动检测',
    'zh': '中文',
    'en': '英文', 
    'ja': '日文',
    'ko': '韩文',
    'fr': '法文',
    'de': '德文',
    'es': '西班牙文',
    'ru': '俄文'
}

# WebSocket配置
WEBSOCKET_HEARTBEAT_INTERVAL = 30  # 秒
WEBSOCKET_TIMEOUT = 60  # 秒

# 安全配置
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CORS_ORIGINS = ['*']

# 缓存配置
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 300  # 5分钟
```

## 🚀 部署指南

### 🐳 Docker快速部署（推荐）

#### 使用自动化部署脚本
```bash
# Linux/macOS
./deploy.sh deploy

# Windows PowerShell
.\deploy.ps1 deploy

# 管理命令
./deploy.sh status    # 查看状态
./deploy.sh logs      # 查看日志
./deploy.sh backup    # 备份数据
./deploy.sh restart   # 重启服务
```

#### 手动Docker部署
```bash
# 克隆项目
git clone https://github.com/your-username/Bili2Text.git
cd Bili2Text

# 配置环境变量
cp env.example .env
nano .env

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f bili2text-web
```

#### 服务架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx反向代理  │◄──►│  Bili2Text App  │◄──►│  Redis缓存服务  │
│   (端口:80/443)  │    │   (端口:8000)   │    │   (端口:6379)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   静态文件服务   │    │   文件存储      │    │   SQLite数据库  │
│   (CSS/JS)      │    │   (音频/结果)   │    │   (任务记录)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### ⚙️ 生产环境配置

#### Nginx反向代理配置
```nginx
# /etc/nginx/sites-available/bili2text
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL配置
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # 性能优化
    client_max_body_size 1G;
    keepalive_timeout 65;
    
    # 应用代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket支持
    location /socket.io/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 静态文件缓存
    location /static/ {
        alias /path/to/Bili2Text/webapp/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 系统服务配置
```ini
# /etc/systemd/system/bili2text-web.service
[Unit]
Description=Bili2Text Web Application
After=network.target

[Service]
Type=exec
User=bili2text
Group=bili2text
WorkingDirectory=/home/bili2text/Bili2Text
Environment=PATH=/home/bili2text/Bili2Text/venv/bin
ExecStart=/home/bili2text/Bili2Text/venv/bin/python run.py --production --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 🔒 安全配置

#### SSL证书配置
```bash
# 使用Let's Encrypt免费SSL
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

#### 防火墙配置
```bash
# Ubuntu/Debian
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 🔧 故障排除

### ❓ 常见问题解决

#### 1. 🎙️ Whisper模型相关问题
```bash
# 问题：模型下载失败
# 解决方案：
# 1. 检查网络连接
ping huggingface.co

# 2. 配置代理（如果需要）
export HTTPS_PROXY=http://127.0.0.1:7890

# 3. 手动下载模型
python -c "import whisper; whisper.load_model('medium')"

# 4. 清理缓存重新下载
rm -rf ~/.cache/whisper/
```

#### 2. 📹 视频下载问题
```bash
# 问题：视频下载失败
# 解决方案：
# 1. 更新yt-dlp到最新版本
pip install --upgrade yt-dlp

# 2. 测试URL有效性
yt-dlp --list-formats "https://www.bilibili.com/video/BV1234567890"

# 3. 使用代理
yt-dlp --proxy "http://127.0.0.1:7890" [URL]

# 4. 检查FFmpeg安装
ffmpeg -version
```

#### 3. ⚡ 系统性能问题
```bash
# 问题：内存不足或CPU使用率过高
# 解决方案：
# 1. 检查系统资源
htop
free -h
df -h

# 2. 调整并发任务数
# 在.env文件中设置：
MAX_CONCURRENT_TASKS=1

# 3. 使用更小的模型
# 选择tiny或base模型

# 4. 增加虚拟内存
sudo fallocate -l 2G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 4. 🌐 网络连接问题
```bash
# 问题：WebSocket连接失败
# 解决方案：
# 1. 检查防火墙设置
sudo ufw status
sudo ufw allow 8000

# 2. 检查代理配置
curl -I http://localhost:8000/api/system/status

# 3. 验证浏览器兼容性
# 使用Chrome/Firefox最新版本

# 4. 检查Nginx配置
sudo nginx -t
sudo systemctl status nginx
```

### 📋 日志分析

#### 应用日志查看
```bash
# 实时查看应用日志
tail -f webapp/logs/bili2text_web.log

# 查看错误日志
tail -f webapp/logs/error.log

# Docker环境查看日志
docker-compose logs -f bili2text-web

# 系统服务日志
sudo journalctl -u bili2text-web -f --no-pager
```

## 🛠️ 开发指南

### 💻 开发环境搭建

```bash
# 1. 克隆开发分支
git clone -b develop https://github.com/your-username/Bili2Text.git
cd Bili2Text

# 2. 创建开发环境
python3.11 -m venv venv-dev
source venv-dev/bin/activate

# 3. 安装开发依赖
pip install -r requirements.txt

# 4. 运行测试
python test_app.py
pytest tests/ -v

# 5. 启动开发服务器
python run.py --debug
```

### 🤝 贡献指南

#### 提交规范
```bash
# 提交消息格式：
# type(scope): description
# 
# 类型说明：
# feat: 新功能
# fix: 修复bug
# docs: 文档更新
# style: 代码格式调整
# refactor: 代码重构
# test: 测试相关

# 示例：
git commit -m "feat(api): add batch processing endpoint"
git commit -m "fix(websocket): resolve connection timeout issue"
```

#### 贡献流程
1. 🍴 **Fork项目** - 在GitHub上Fork本项目
2. 🌿 **创建分支** - `git checkout -b feature/your-feature-name`
3. 💻 **开发功能** - 编写代码并确保测试通过
4. 📝 **提交代码** - 遵循提交规范
5. 🔀 **创建PR** - 提交Pull Request并描述更改
- [Bootstrap](https://getbootstrap.com/) - UI框架

## 🔧 维护和监控

### 📊 性能监控
```bash
# 检查系统资源使用
htop
free -h
df -h

# 监控应用性能
curl -s http://localhost:8000/api/system/status | jq .

# 查看活跃任务
curl -s http://localhost:8000/api/tasks/?status=pending,downloading,transcribing

# Docker容器监控
docker stats bili2text-web
```

### 🔄 备份和恢复
```bash
# 备份数据库
cp storage/bili2text.db backup/bili2text_$(date +%Y%m%d_%H%M%S).db

# 备份存储文件
tar -czf backup/storage_$(date +%Y%m%d_%H%M%S).tar.gz storage/

# 恢复数据（停止服务）
./deploy.sh stop
cp backup/bili2text_20240115_143022.db storage/bili2text.db
./deploy.sh start
```

## 📄 许可证

本项目采用 **MIT 许可证**，详见 [LICENSE](LICENSE) 文件。

### 许可证要点
- ✅ 商业使用
- ✅ 修改代码
- ✅ 分发代码
- ✅ 私人使用
- ❗ 需要包含许可证和版权声明
- ❗ 软件"按原样"提供，无任何保证

## 🙏 致谢

### 核心技术栈
- 🎙️ [**OpenAI Whisper**](https://github.com/openai/whisper) - 强大的语音识别引擎
- 📹 [**yt-dlp**](https://github.com/yt-dlp/yt-dlp) - 可靠的视频下载工具
- 🌐 [**Flask**](https://flask.palletsprojects.com/) - 轻量级Web框架
- ⚡ [**Flask-SocketIO**](https://flask-socketio.readthedocs.io/) - 实时通信支持
- 🎨 [**Bootstrap 5**](https://getbootstrap.com/) - 现代UI框架
- 📊 [**Chart.js**](https://www.chartjs.org/) - 数据可视化库

### 开发工具
- 🐳 [**Docker**](https://www.docker.com/) - 容器化部署
- 🔧 [**pytest**](https://docs.pytest.org/) - 测试框架
- 📦 [**pip**](https://pip.pypa.io/) - 包管理工具

## 📞 联系方式

### 🤝 获取帮助
- 📋 [**提交Issue**](https://github.com/your-username/Bili2Text/issues) - 报告Bug或功能请求
- 💬 [**讨论区**](https://github.com/your-username/Bili2Text/discussions) - 社区讨论和Q&A
- 📧 **邮件支持** - your-email@example.com

### 🌟 支持项目
如果这个项目对您有帮助，请考虑：
- ⭐ 给项目点个Star
- 🍴 Fork项目并参与贡献
- 📢 推荐给其他开发者

---

<div align="center">

**⚡ 快速部署 | 🎯 智能转录 | 🌐 现代界面 | 🔒 安全可靠**

Made with ❤️ by the Bili2Text Team

</div>