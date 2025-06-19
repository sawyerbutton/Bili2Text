# Bili2Text Web应用项目设计文档

## 📋 项目概述

### 🎯 设计目标
将现有的命令行工具 `main.py` 转换为一个用户友好的Web应用，提供以下核心功能：
- 🌐 Web界面提交视频URL
- ⚡ 后台异步任务处理
- 📊 实时任务状态监控
- 📥 转录结果文件下载
- 🔄 任务历史记录管理

### 🏗️ 整体架构设计

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │   后端API      │    │   任务处理器    │
│   (Web UI)      │◄──►│   (FastAPI)     │◄──►│   (Celery)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   静态文件      │    │   数据库        │    │   文件存储      │
│   (HTML/CSS/JS) │    │   (SQLite)      │    │   (本地文件)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ 技术栈选择

### 后端框架
- **FastAPI**: 现代、快速的Python Web框架
  - 自动API文档生成
  - 异步支持
  - 类型提示支持
  - WebSocket支持（实时状态更新）

### 任务队列
- **Celery**: 分布式任务队列
  - 异步任务处理
  - 任务状态跟踪
  - 失败重试机制
- **Redis**: 消息代理和结果存储
  - 高性能内存数据库
  - 支持任务状态缓存

### 数据库
- **SQLite**: 轻量级关系数据库
  - 无需额外配置
  - 适合单机部署
  - 支持并发读取

### 前端技术
- **HTML5 + CSS3 + JavaScript**: 原生Web技术
  - 无需复杂框架
  - 轻量级实现
  - 易于维护
- **Bootstrap**: CSS框架
  - 响应式设计
  - 现代UI组件

## 📁 项目结构设计

```
Bili2Text/
├── 📄 main.py                          # 原始批量处理脚本
├── 📄 get_ref_from_dynamics.py         # 原始动态监控脚本
├── 📁 webapp/                          # Web应用主目录
│   ├── 📄 app.py                       # FastAPI应用入口
│   ├── 📄 config.py                    # 配置文件
│   ├── 📄 models.py                    # 数据模型定义
│   ├── 📁 api/                         # API路由
│   │   ├── 📄 __init__.py
│   │   ├── 📄 tasks.py                 # 任务相关API
│   │   ├── 📄 files.py                 # 文件下载API
│   │   └── 📄 status.py                # 状态查询API
│   ├── 📁 core/                        # 核心业务逻辑
│   │   ├── 📄 __init__.py
│   │   ├── 📄 transcriber.py           # 转录核心逻辑
│   │   ├── 📄 downloader.py            # 下载核心逻辑
│   │   └── 📄 file_manager.py          # 文件管理
│   ├── 📁 tasks/                       # Celery任务
│   │   ├── 📄 __init__.py
│   │   ├── 📄 celery_app.py            # Celery应用配置
│   │   └── 📄 transcription_tasks.py   # 转录任务定义
│   ├── 📁 database/                    # 数据库相关
│   │   ├── 📄 __init__.py
│   │   ├── 📄 connection.py            # 数据库连接
│   │   ├── 📄 crud.py                  # 数据库操作
│   │   └── 📄 schemas.py               # 数据模式
│   └── 📁 static/                      # 静态文件
│       ├── 📁 css/
│       │   └── 📄 style.css
│       ├── 📁 js/
│       │   ├── 📄 main.js
│       │   └── 📄 websocket.js
│       └── 📁 templates/
│           ├── 📄 index.html           # 主页面
│           ├── 📄 task_detail.html     # 任务详情页
│           └── 📄 history.html         # 历史记录页
├── 📁 storage/                         # 文件存储目录
│   ├── 📁 audio/                       # 音频文件
│   ├── 📁 results/                     # 转录结果
│   └── 📁 temp/                        # 临时文件
├── 📁 logs/                            # 日志文件
├── 📁 docs/                            # 项目文档
│   ├── 📄 project-design.md            # 本设计文档
│   ├── 📄 api-documentation.md         # API文档
│   ├── 📄 deployment-guide.md          # 部署指南
│   └── 📄 user-manual.md               # 用户手册
├── 📄 requirements-web.txt             # Web应用依赖
├── 📄 docker-compose.yml               # Docker部署配置
└── 📄 Dockerfile                       # Docker镜像配置
```

## 🔄 核心功能模块设计

### 1. 任务管理模块

#### 任务状态定义
```python
class TaskStatus(Enum):
    PENDING = "pending"         # 等待处理
    DOWNLOADING = "downloading" # 下载中
    TRANSCRIBING = "transcribing" # 转录中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"          # 失败
    CANCELLED = "cancelled"    # 已取消
```

#### 任务数据模型
```python
class TranscriptionTask:
    id: str                    # 任务唯一ID
    url: str                   # 视频URL
    status: TaskStatus         # 任务状态
    progress: float            # 进度百分比 (0-100)
    created_at: datetime       # 创建时间
    started_at: datetime       # 开始时间
    completed_at: datetime     # 完成时间
    error_message: str         # 错误信息
    result_file_path: str      # 结果文件路径
    audio_file_path: str       # 音频文件路径
    model_name: str            # 使用的模型
    file_size: int             # 文件大小
    duration: float            # 音频时长
```

### 2. 文件管理模块

#### 文件存储策略
- **音频文件**: `storage/audio/{task_id}/`
- **结果文件**: `storage/results/{task_id}/`
- **临时文件**: `storage/temp/{task_id}/`
- **文件命名**: `{video_title}_{timestamp}.{ext}`

#### 文件清理策略
- 临时文件：任务完成后立即清理
- 音频文件：保留7天后自动清理
- 结果文件：永久保留（可配置）

### 3. 实时通信模块

#### WebSocket连接管理
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket, task_id: str)
    async def disconnect(self, websocket: WebSocket)
    async def send_task_update(self, task_id: str, data: dict)
    async def broadcast_system_status(self, data: dict)
```

#### 实时更新事件
- 任务状态变更
- 进度更新
- 错误通知
- 完成通知

## 🎨 用户界面设计

### 主页面 (index.html)
```
┌─────────────────────────────────────────────────────────────┐
│                    Bili2Text Web 转录工具                    │
├─────────────────────────────────────────────────────────────┤
│  📹 视频URL输入                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ https://www.bilibili.com/video/BV...                   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  🎙️ 模型选择                                                │
│  ○ tiny (快速)  ○ base  ● medium (推荐)  ○ large-v3 (精确) │
│                                                             │
│  ⚙️ 高级选项                                                │
│  □ 启用代理  □ 保留音频文件  □ 自定义输出格式                │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  开始转录   │  │  任务历史   │  │  系统状态   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  📊 当前任务状态                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 任务ID: task_123456                                    │ │
│  │ 状态: 转录中... ████████████░░░░ 75%                   │ │
│  │ 预计剩余时间: 2分30秒                                   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 任务历史页面 (history.html)
```
┌─────────────────────────────────────────────────────────────┐
│  📋 任务历史记录                                             │
├─────────────────────────────────────────────────────────────┤
│  🔍 筛选: [全部▼] [今天▼] [成功▼]          🔄 刷新          │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐   │
│  │ ✅ BV15N4y1J7CA - 【参考信息】某某视频                │   │
│  │    2024-01-15 14:30  |  medium模型  |  3.2MB          │   │
│  │    [📥 下载结果] [🔍 查看详情] [🗑️ 删除]              │   │
│  └───────────────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ ⏳ BV1Fa4y1273F - 正在处理中...                       │   │
│  │    2024-01-15 14:25  |  medium模型  |  进度: 45%      │   │
│  │    [⏸️ 暂停] [❌ 取消] [🔍 查看详情]                  │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🔌 API接口设计

### RESTful API端点

#### 任务管理
- `POST /api/tasks/` - 创建新任务
- `GET /api/tasks/` - 获取任务列表
- `GET /api/tasks/{task_id}` - 获取任务详情
- `DELETE /api/tasks/{task_id}` - 删除任务
- `POST /api/tasks/{task_id}/cancel` - 取消任务

#### 文件操作
- `GET /api/files/{task_id}/result` - 下载结果文件
- `GET /api/files/{task_id}/audio` - 下载音频文件
- `DELETE /api/files/{task_id}` - 删除任务文件

#### 系统状态
- `GET /api/system/status` - 获取系统状态
- `GET /api/system/models` - 获取可用模型列表
- `GET /api/system/stats` - 获取统计信息

### WebSocket端点
- `WS /ws/tasks/{task_id}` - 任务状态实时更新
- `WS /ws/system` - 系统状态实时更新

## 🔧 配置管理

### 应用配置 (config.py)
```python
class Settings:
    # 应用基础配置
    APP_NAME: str = "Bili2Text Web"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./bili2text.db"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 文件存储配置
    STORAGE_PATH: str = "./storage"
    MAX_FILE_SIZE: int = 1024 * 1024 * 1024  # 1GB
    CLEANUP_INTERVAL: int = 24 * 60 * 60     # 24小时
    
    # Whisper配置
    DEFAULT_MODEL: str = "medium"
    AVAILABLE_MODELS: List[str] = ["tiny", "base", "small", "medium", "large-v3"]
    MODEL_CACHE_PATH: str = "./.cache/whisper"
    
    # 任务配置
    MAX_CONCURRENT_TASKS: int = 3
    TASK_TIMEOUT: int = 3600  # 1小时
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
```

## 🚀 部署方案

### 开发环境部署
```bash
# 1. 安装依赖
pip install -r requirements-web.txt

# 2. 启动Redis
redis-server

# 3. 启动Celery Worker
celery -A webapp.tasks.celery_app worker --loglevel=info

# 4. 启动Web应用
uvicorn webapp.app:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境部署 (Docker)
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs
    environment:
      - REDIS_URL=redis://redis:6379/0
  
  worker:
    build: .
    command: celery -A webapp.tasks.celery_app worker --loglevel=info
    depends_on:
      - redis
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs
    environment:
      - REDIS_URL=redis://redis:6379/0
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## 📊 性能优化策略

### 1. 任务队列优化
- 任务优先级管理
- 并发任务数量限制
- 失败任务重试机制
- 任务超时处理

### 2. 文件存储优化
- 分片上传大文件
- 文件压缩存储
- 定期清理过期文件
- CDN加速文件下载

### 3. 数据库优化
- 索引优化
- 连接池管理
- 查询缓存
- 定期数据清理

### 4. 前端优化
- 静态资源压缩
- 浏览器缓存策略
- 异步加载
- 进度条优化

## 🔒 安全考虑

### 1. 输入验证
- URL格式验证
- 文件类型检查
- 参数范围验证
- SQL注入防护

### 2. 访问控制
- 请求频率限制
- IP白名单机制
- 文件访问权限
- 任务所有权验证

### 3. 数据保护
- 敏感信息加密
- 安全的文件存储
- 日志脱敏处理
- 定期安全扫描

## 📈 监控和日志

### 1. 应用监控
- 任务执行状态
- 系统资源使用
- API响应时间
- 错误率统计

### 2. 日志管理
- 结构化日志记录
- 日志级别分类
- 日志轮转策略
- 集中日志收集

### 3. 告警机制
- 任务失败告警
- 系统异常告警
- 资源不足告警
- 性能下降告警

## 🔄 扩展性设计

### 1. 水平扩展
- 多Worker节点支持
- 负载均衡配置
- 分布式文件存储
- 数据库集群

### 2. 功能扩展
- 多语言支持
- 批量任务处理
- 定时任务调度
- 第三方集成API

### 3. 插件系统
- 自定义转录模型
- 后处理插件
- 通知插件
- 存储插件

## 📋 开发计划

### Phase 1: 核心功能 (2-3周)
- [ ] 基础Web框架搭建
- [ ] 任务队列系统
- [ ] 核心转录功能迁移
- [ ] 基础前端界面

### Phase 2: 完善功能 (2-3周)
- [ ] 实时状态更新
- [ ] 文件下载功能
- [ ] 任务历史管理
- [ ] 错误处理优化

### Phase 3: 优化部署 (1-2周)
- [ ] Docker容器化
- [ ] 性能优化
- [ ] 安全加固
- [ ] 文档完善

### Phase 4: 扩展功能 (按需)
- [ ] 用户认证系统
- [ ] 批量处理功能
- [ ] API接口开放
- [ ] 移动端适配

---

## 📝 总结

本设计文档提供了将Bili2Text从命令行工具转换为Web应用的完整方案。通过采用现代的Python Web技术栈，我们可以构建一个用户友好、功能完善、易于部署的转录服务平台。

设计的核心优势：
- 🎯 **用户友好**: Web界面降低使用门槛
- ⚡ **高性能**: 异步任务处理，支持并发
- 🔧 **易维护**: 模块化设计，代码结构清晰
- 🚀 **易部署**: Docker容器化，一键部署
- 📈 **可扩展**: 支持水平扩展和功能扩展

下一步将根据此设计文档开始具体的代码实现工作。