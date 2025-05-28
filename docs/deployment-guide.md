# Bili2Text Web 部署指南

## 📋 部署概述

本指南详细介绍了如何在不同环境中部署Bili2Text Web应用，包括开发环境、测试环境和生产环境的部署方案。

## 🛠️ 系统要求

### 最低配置要求
- **CPU**: 4核心 2.0GHz+
- **内存**: 8GB RAM (推荐16GB+)
- **存储**: 50GB+ 可用空间 (SSD推荐)
- **网络**: 稳定的互联网连接
- **操作系统**: 
  - Ubuntu 20.04+ / CentOS 8+ / Debian 11+
  - Windows 10+ / Windows Server 2019+
  - macOS 10.15+

### 推荐配置
- **CPU**: 8核心 3.0GHz+ (支持AVX指令集)
- **内存**: 32GB RAM
- **GPU**: NVIDIA RTX 3060+ (8GB+ VRAM)
- **存储**: 200GB+ NVMe SSD
- **网络**: 100Mbps+ 带宽

## 🔧 依赖软件安装

### 1. Python 环境

#### Ubuntu/Debian
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装Python 3.11
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# 设置默认Python版本
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

#### CentOS/RHEL
```bash
# 安装EPEL仓库
sudo dnf install epel-release -y

# 安装Python 3.11
sudo dnf install python3.11 python3.11-pip python3.11-devel -y
```

#### Windows
```powershell
# 使用Chocolatey安装
choco install python311 -y

# 或下载官方安装包
# https://www.python.org/downloads/windows/
```

### 2. Redis 服务器

#### Ubuntu/Debian
```bash
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

#### CentOS/RHEL
```bash
sudo dnf install redis -y
sudo systemctl enable redis
sudo systemctl start redis
```

#### Windows
```powershell
# 使用Chocolatey安装
choco install redis-64 -y

# 启动Redis服务
redis-server
```

#### macOS
```bash
# 使用Homebrew安装
brew install redis
brew services start redis
```

### 3. FFmpeg

#### Ubuntu/Debian
```bash
sudo apt install ffmpeg -y
```

#### CentOS/RHEL
```bash
# 启用RPM Fusion仓库
sudo dnf install https://download1.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm -y
sudo dnf install ffmpeg -y
```

#### Windows
```powershell
choco install ffmpeg -y
```

#### macOS
```bash
brew install ffmpeg
```

## 🚀 开发环境部署

### 1. 克隆项目
```bash
git clone https://github.com/ShadyLeaf/Bili2Text.git
cd Bili2Text
```

### 2. 创建虚拟环境
```bash
# 创建虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3. 安装依赖
```bash
# 安装Web应用依赖
pip install -r requirements-web.txt

# 安装PyTorch (根据系统选择)
# CUDA版本 (Linux/Windows with NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# CPU版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# macOS (Apple Silicon)
pip install torch torchvision torchaudio
```

### 4. 配置环境变量
```bash
# 创建环境配置文件
cp .env.example .env

# 编辑配置文件
nano .env
```

`.env` 文件内容：
```bash
# 应用配置
APP_NAME=Bili2Text Web
DEBUG=true
SECRET_KEY=your-secret-key-here

# 数据库配置
DATABASE_URL=sqlite:///./bili2text.db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 存储配置
STORAGE_PATH=./storage
MAX_FILE_SIZE=1073741824

# Whisper配置
DEFAULT_MODEL=medium
MODEL_CACHE_PATH=./.cache/whisper

# 任务配置
MAX_CONCURRENT_TASKS=3
TASK_TIMEOUT=3600

# 代理配置 (可选)
USE_PROXY=false
PROXY_URL=http://127.0.0.1:7890
```

### 5. 初始化数据库
```bash
# 运行数据库迁移
python -m webapp.database.init_db
```

### 6. 启动服务

#### 方式一：分别启动各服务
```bash
# 终端1: 启动Redis (如果未作为系统服务运行)
redis-server

# 终端2: 启动Celery Worker
celery -A webapp.tasks.celery_app worker --loglevel=info --concurrency=3

# 终端3: 启动Web应用
uvicorn webapp.app:app --reload --host 0.0.0.0 --port 8000
```

#### 方式二：使用启动脚本
```bash
# 创建启动脚本
chmod +x scripts/start-dev.sh
./scripts/start-dev.sh
```

### 7. 验证部署
```bash
# 检查服务状态
curl http://localhost:8000/api/system/status

# 访问Web界面
# 浏览器打开: http://localhost:8000
```

## 🐳 Docker 部署

### 1. 安装Docker和Docker Compose

#### Ubuntu/Debian
```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Windows/macOS
下载并安装 Docker Desktop：
- Windows: https://docs.docker.com/desktop/windows/install/
- macOS: https://docs.docker.com/desktop/mac/install/

### 2. 构建和启动容器

#### 开发环境
```bash
# 构建镜像
docker-compose -f docker-compose.dev.yml build

# 启动服务
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f
```

#### 生产环境
```bash
# 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 启动生产服务
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Docker配置文件

#### Dockerfile
```dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements-web.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements-web.txt

# 安装PyTorch (CPU版本)
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 复制应用代码
COPY . .

# 创建存储目录
RUN mkdir -p storage/audio storage/results storage/temp logs

# 设置权限
RUN chmod +x scripts/*.sh

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["./scripts/start-prod.sh"]
```

#### docker-compose.prod.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=sqlite:///./storage/bili2text.db
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs
    depends_on:
      - redis
    restart: unless-stopped

  worker:
    build: .
    command: celery -A webapp.tasks.celery_app worker --loglevel=info --concurrency=3
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=sqlite:///./storage/bili2text.db
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./storage:/var/www/storage
    depends_on:
      - web
    restart: unless-stopped

volumes:
  redis_data:
```

## 🌐 生产环境部署

### 1. 服务器准备

#### 创建专用用户
```bash
# 创建应用用户
sudo useradd -m -s /bin/bash bili2text
sudo usermod -aG sudo bili2text

# 切换到应用用户
sudo su - bili2text
```

#### 配置防火墙
```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. 使用Nginx反向代理

#### 安装Nginx
```bash
# Ubuntu/Debian
sudo apt install nginx -y

# CentOS/RHEL
sudo dnf install nginx -y
```

#### 配置Nginx
```nginx
# /etc/nginx/sites-available/bili2text
server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL配置
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # 客户端最大上传大小
    client_max_body_size 1G;
    
    # 主应用代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket代理
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态文件直接服务
    location /static/ {
        alias /home/bili2text/Bili2Text/webapp/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 文件下载
    location /downloads/ {
        alias /home/bili2text/Bili2Text/storage/results/;
        add_header Content-Disposition "attachment";
    }
}
```

#### 启用站点
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/bili2text /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 3. 配置SSL证书

#### 使用Let's Encrypt (免费)
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com

# 设置自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 4. 配置系统服务

#### 创建Systemd服务文件

**Web应用服务**
```ini
# /etc/systemd/system/bili2text-web.service
[Unit]
Description=Bili2Text Web Application
After=network.target redis.service

[Service]
Type=exec
User=bili2text
Group=bili2text
WorkingDirectory=/home/bili2text/Bili2Text
Environment=PATH=/home/bili2text/Bili2Text/venv/bin
ExecStart=/home/bili2text/Bili2Text/venv/bin/uvicorn webapp.app:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Celery Worker服务**
```ini
# /etc/systemd/system/bili2text-worker.service
[Unit]
Description=Bili2Text Celery Worker
After=network.target redis.service

[Service]
Type=exec
User=bili2text
Group=bili2text
WorkingDirectory=/home/bili2text/Bili2Text
Environment=PATH=/home/bili2text/Bili2Text/venv/bin
ExecStart=/home/bili2text/Bili2Text/venv/bin/celery -A webapp.tasks.celery_app worker --loglevel=info --concurrency=3
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### 启动服务
```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动并启用服务
sudo systemctl start bili2text-web
sudo systemctl enable bili2text-web

sudo systemctl start bili2text-worker
sudo systemctl enable bili2text-worker

# 检查服务状态
sudo systemctl status bili2text-web
sudo systemctl status bili2text-worker
```

### 5. 配置日志轮转

```bash
# 创建logrotate配置
sudo nano /etc/logrotate.d/bili2text
```

```
/home/bili2text/Bili2Text/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 bili2text bili2text
    postrotate
        systemctl reload bili2text-web
        systemctl reload bili2text-worker
    endscript
}
```

## 📊 监控和维护

### 1. 系统监控

#### 安装监控工具
```bash
# 安装htop和iotop
sudo apt install htop iotop -y

# 安装nvidia-smi (如果有GPU)
sudo apt install nvidia-utils-* -y
```

#### 监控脚本
```bash
#!/bin/bash
# scripts/monitor.sh

echo "=== 系统状态 ==="
echo "CPU使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')"
echo "内存使用: $(free -h | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
echo "磁盘使用: $(df -h / | awk 'NR==2{print $5}')"

echo -e "\n=== 服务状态 ==="
systemctl is-active bili2text-web
systemctl is-active bili2text-worker
systemctl is-active redis
systemctl is-active nginx

echo -e "\n=== 任务队列状态 ==="
celery -A webapp.tasks.celery_app inspect active

echo -e "\n=== 最近错误日志 ==="
tail -n 10 /home/bili2text/Bili2Text/logs/error.log
```

### 2. 备份策略

#### 数据库备份
```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/home/bili2text/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
cp /home/bili2text/Bili2Text/storage/bili2text.db $BACKUP_DIR/bili2text_$DATE.db

# 备份配置文件
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    /home/bili2text/Bili2Text/.env \
    /etc/nginx/sites-available/bili2text \
    /etc/systemd/system/bili2text-*.service

# 清理30天前的备份
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "备份完成: $DATE"
```

#### 设置定时备份
```bash
# 添加到crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /home/bili2text/Bili2Text/scripts/backup.sh >> /home/bili2text/Bili2Text/logs/backup.log 2>&1
```

### 3. 性能优化

#### 系统优化
```bash
# 增加文件描述符限制
echo "bili2text soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "bili2text hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# 优化内核参数
echo "net.core.somaxconn = 65535" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

#### 应用优化
```bash
# 调整Celery worker数量
# 根据CPU核心数调整 --concurrency 参数

# 调整Uvicorn worker数量
# uvicorn webapp.app:app --workers 4 --host 127.0.0.1 --port 8000
```

## 🔧 故障排除

### 常见问题解决

#### 1. 服务无法启动
```bash
# 检查日志
sudo journalctl -u bili2text-web -f
sudo journalctl -u bili2text-worker -f

# 检查端口占用
sudo netstat -tlnp | grep :8000

# 检查权限
ls -la /home/bili2text/Bili2Text/
```

#### 2. 任务处理失败
```bash
# 检查Celery状态
celery -A webapp.tasks.celery_app inspect stats

# 检查Redis连接
redis-cli ping

# 查看错误日志
tail -f /home/bili2text/Bili2Text/logs/celery.log
```

#### 3. 文件下载问题
```bash
# 检查文件权限
ls -la /home/bili2text/Bili2Text/storage/

# 检查Nginx配置
sudo nginx -t

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/error.log
```

## 📞 技术支持

如遇到部署问题，请提供以下信息：
- 操作系统版本
- Python版本
- 错误日志
- 系统资源使用情况
- 网络环境信息

联系方式：
- GitHub Issues: [项目Issues页面]
- 邮件支持: [技术支持邮箱]