# Bili2Text Web

Bili2Text Web是一个基于Web的哔哩哔哩视频转录工具，使用OpenAI Whisper进行语音识别，提供现代化的Web界面和实时任务监控。

## 功能特性

### 核心功能
- 🎥 支持哔哩哔哩视频URL转录
- 🎙️ 基于OpenAI Whisper的高精度语音识别
- 📝 多种输出格式（TXT、Markdown、JSON）
- 🔄 实时任务进度监控
- 📊 系统性能监控和统计

### 技术特性
- 🌐 现代化响应式Web界面
- ⚡ WebSocket实时通信
- 🔧 RESTful API设计
- 📱 移动端适配
- 🎨 Bootstrap 5 UI框架
- 📈 Chart.js数据可视化

### 系统特性
- 🚀 异步任务处理
- 💾 SQLite数据库存储
- 📁 智能文件管理
- 🔍 任务历史查询
- ⚙️ 灵活配置选项
- 🛡️ 错误处理和重试机制

## 系统要求

### 基础要求
- Python 3.8+
- 4GB+ RAM（推荐8GB+）
- 2GB+ 可用磁盘空间

### 依赖工具
- yt-dlp（视频下载）
- FFmpeg（音频处理）
- OpenAI Whisper（语音识别）

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd Bili2Text
```

### 2. 安装依赖
```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装FFmpeg（Windows）
# 下载并安装FFmpeg，确保添加到PATH

# 安装FFmpeg（Ubuntu/Debian）
sudo apt update
sudo apt install ffmpeg

# 安装FFmpeg（macOS）
brew install ffmpeg
```

### 3. 初始化数据库
```bash
python -c "from webapp.app import create_app; from webapp.core.database import init_db; app = create_app(); init_db(app)"
```

### 4. 启动应用
```bash
# 开发模式
python run.py --debug

# 生产模式
python run.py --production --host 0.0.0.0 --port 8000
```

### 5. 访问应用
打开浏览器访问：http://localhost:5000

## 项目结构

```
Bili2Text/
├── webapp/                 # Web应用主目录
│   ├── api/               # API路由和WebSocket处理
│   │   ├── routes.py      # RESTful API路由
│   │   └── websocket_handlers.py  # WebSocket事件处理
│   ├── core/              # 核心功能模块
│   │   ├── config.py      # 应用配置
│   │   ├── database.py    # 数据库模型
│   │   ├── task_manager.py # 任务管理器
│   │   ├── file_manager.py # 文件管理器
│   │   └── system_monitor.py # 系统监控
│   ├── static/            # 静态资源
│   │   ├── css/          # 样式文件
│   │   ├── js/           # JavaScript文件
│   │   ├── images/       # 图片资源
│   │   └── templates/    # HTML模板
│   ├── logs/             # 日志文件
│   └── app.py            # Flask应用入口
├── storage/              # 文件存储目录
│   ├── audio/           # 音频文件
│   ├── results/         # 转录结果
│   └── temp/            # 临时文件
├── docs/                # 项目文档
├── requirements.txt     # Python依赖
├── run.py              # 启动脚本
└── README.md           # 项目说明
```

## 使用指南

### 基本使用流程

1. **提交转录任务**
   - 在主页输入哔哩哔哩视频URL
   - 选择Whisper模型（tiny/base/medium/large-v3）
   - 配置高级选项（代理、输出格式等）
   - 点击"开始转录"

2. **监控任务进度**
   - 实时查看下载和转录进度
   - 支持任务取消和重试
   - 接收浏览器通知

3. **查看转录结果**
   - 在线预览转录文本
   - 下载多种格式文件
   - 复制文本到剪贴板

4. **管理历史任务**
   - 查看所有历史任务
   - 按状态和日期筛选
   - 批量操作和删除

### 高级功能

#### 批量处理
- 支持同时提交多个视频URL
- 自动队列管理和并发控制
- 批量下载和导出

#### 系统监控
- 实时CPU、内存使用率
- 任务处理统计和趋势
- 服务状态监控
- 性能图表展示

#### 配置选项
- 代理设置（支持HTTP/SOCKS代理）
- 音频保留选项
- 输出格式选择
- 语言检测设置

## API文档

### 任务管理API

#### 创建任务
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

#### 获取任务列表
```http
GET /api/tasks/?page=1&limit=20&status=completed
```

#### 获取任务详情
```http
GET /api/tasks/{task_id}
```

#### 取消任务
```http
POST /api/tasks/{task_id}/cancel
```

### 文件操作API

#### 下载转录结果
```http
GET /api/files/{task_id}/result
```

#### 下载音频文件
```http
GET /api/files/{task_id}/audio
```

### 系统状态API

#### 获取系统状态
```http
GET /api/system/status
```

#### 获取可用模型
```http
GET /api/system/models
```

## WebSocket事件

### 客户端事件
- `join_task` - 加入任务监听
- `leave_task` - 离开任务监听
- `join_system` - 加入系统监控
- `ping` - 心跳检测

### 服务端事件
- `task_update` - 任务状态更新
- `task_notification` - 任务完成通知
- `system_update` - 系统状态更新
- `system_alert` - 系统警告

## 配置说明

### 环境变量
```bash
# 数据库配置
DATABASE_URL=sqlite:///bili2text.db

# 安全配置
SECRET_KEY=your-secret-key

# 代理配置
PROXY_URL=http://proxy.example.com:8080

# 文件存储配置
STORAGE_ROOT=/path/to/storage

# 任务配置
MAX_CONCURRENT_TASKS=3
TASK_TIMEOUT=3600
```

### 应用配置
主要配置在 `webapp/core/config.py` 中：

```python
class Config:
    # Whisper模型配置
    WHISPER_MODELS = {
        'tiny': {...},
        'base': {...},
        'medium': {...},
        'large-v3': {...}
    }
    
    # 任务配置
    MAX_CONCURRENT_TASKS = 3
    TASK_TIMEOUT = 3600
    
    # 文件配置
    MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB
    ALLOWED_EXTENSIONS = ['.txt', '.md', '.json']
```

## 部署指南

### Docker部署
```bash
# 构建镜像
docker build -t bili2text-web .

# 运行容器
docker run -d \
  --name bili2text-web \
  -p 8000:8000 \
  -v $(pwd)/storage:/app/storage \
  -v $(pwd)/logs:/app/webapp/logs \
  bili2text-web
```

### Nginx配置
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /socket.io/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 系统服务
```ini
# /etc/systemd/system/bili2text-web.service
[Unit]
Description=Bili2Text Web Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/Bili2Text
ExecStart=/path/to/python run.py --production --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 故障排除

### 常见问题

1. **Whisper模型下载失败**
   - 检查网络连接
   - 配置代理设置
   - 手动下载模型文件

2. **视频下载失败**
   - 检查yt-dlp版本
   - 验证视频URL有效性
   - 配置代理设置

3. **音频转录失败**
   - 检查FFmpeg安装
   - 验证音频文件完整性
   - 检查系统内存使用

4. **WebSocket连接失败**
   - 检查防火墙设置
   - 验证代理配置
   - 检查浏览器兼容性

### 日志查看
```bash
# 应用日志
tail -f webapp/logs/app.log

# 系统日志
journalctl -u bili2text-web -f
```

## 开发指南

### 开发环境设置
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 启动开发服务器
python run.py --debug

# 运行测试
python -m pytest tests/

# 代码格式化
black webapp/
flake8 webapp/
```

### 贡献指南
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别引擎
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 视频下载工具
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Bootstrap](https://getbootstrap.com/) - UI框架

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 加入讨论群