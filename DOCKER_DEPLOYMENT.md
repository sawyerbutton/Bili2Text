# Bili2Text Web Docker部署指南

## 📋 概述

本指南将帮助您使用Docker快速部署Bili2Text Web应用。我们提供了完整的Docker化解决方案，包括Web应用、Redis缓存、Nginx反向代理等组件。

## 🛠️ 系统要求

### 最低要求
- **操作系统**: Linux、macOS、Windows 10/11
- **内存**: 4GB RAM（推荐8GB+）
- **存储**: 10GB可用空间
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### 推荐配置
- **CPU**: 4核心+
- **内存**: 8GB RAM+
- **存储**: 50GB+ SSD
- **网络**: 稳定的互联网连接

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd Bili2Text
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp env.example .env

# 编辑配置文件
nano .env
```

### 3. 一键部署

#### Linux/macOS
```bash
# 给脚本执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh deploy
```

#### Windows
```powershell
# 执行PowerShell脚本
.\deploy.ps1 deploy
```

### 4. 访问应用
部署完成后，访问以下地址：
- **Web界面**: http://localhost
- **API接口**: http://localhost/api
- **系统状态**: http://localhost/api/system/status

## 📁 项目结构

```
Bili2Text/
├── Dockerfile              # 应用镜像构建文件
├── docker-compose.yml      # 服务编排文件
├── .dockerignore           # Docker忽略文件
├── env.example             # 环境变量模板
├── deploy.sh               # Linux/macOS部署脚本
├── deploy.ps1              # Windows部署脚本
├── nginx/                  # Nginx配置
│   ├── nginx.conf          # 主配置文件
│   ├── conf.d/             # 站点配置
│   ├── ssl/                # SSL证书目录
│   └── logs/               # 日志目录
├── storage/                # 文件存储目录
│   ├── audio/              # 音频文件
│   ├── results/            # 转录结果
│   └── temp/               # 临时文件
└── data/                   # 数据库文件
```

## ⚙️ 配置说明

### 环境变量配置

编辑`.env`文件配置以下参数：

```bash
# 应用基础配置
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# 数据库配置
DATABASE_URL=sqlite:///data/bili2text.db

# 任务配置
MAX_CONCURRENT_TASKS=3
TASK_TIMEOUT=3600

# 代理配置（可选）
USE_PROXY=false
PROXY_URL=http://proxy.example.com:8080

# 域名配置
DOMAIN_NAME=your-domain.com
```

### Nginx配置

#### HTTP配置
默认配置支持HTTP访问，适用于内网部署。

#### HTTPS配置
1. 将SSL证书文件放入`nginx/ssl/`目录：
   - `cert.pem` - 证书文件
   - `key.pem` - 私钥文件

2. 编辑`nginx/conf.d/bili2text.conf`，取消HTTPS配置的注释

3. 重启服务：
   ```bash
   ./deploy.sh restart
   ```

## 🔧 服务管理

### 基本命令

```bash
# 启动服务
./deploy.sh start

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看状态
./deploy.sh status

# 查看日志
./deploy.sh logs

# 查看特定服务日志
./deploy.sh logs bili2text-web
```

### 高级操作

```bash
# 重新构建镜像
./deploy.sh build

# 备份数据
./deploy.sh backup

# 恢复数据
./deploy.sh restore backup_20240101_120000.tar.gz

# 清理所有数据
./deploy.sh clean

# 更新应用
./deploy.sh update
```

## 📊 监控和维护

### 健康检查

应用内置了健康检查端点：
- **应用健康**: http://localhost/api/system/status
- **Nginx健康**: http://localhost/health

### 日志管理

#### 查看实时日志
```bash
# 所有服务日志
docker-compose logs -f

# 特定服务日志
docker-compose logs -f bili2text-web
docker-compose logs -f nginx
docker-compose logs -f redis
```

#### 日志文件位置
- **应用日志**: `webapp/logs/`
- **Nginx日志**: `nginx/logs/`
- **容器日志**: 通过`docker-compose logs`查看

### 性能监控

#### 资源使用情况
```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
df -h

# 查看内存使用
free -h
```

#### 系统监控
访问Web界面的系统状态页面查看详细监控信息。

## 🔒 安全配置

### 基础安全

1. **更改默认密钥**
   ```bash
   # 生成随机密钥
   openssl rand -hex 32
   
   # 更新.env文件中的SECRET_KEY
   ```

2. **限制访问**
   - 配置防火墙规则
   - 使用VPN或内网访问
   - 配置Nginx访问控制

3. **SSL/TLS加密**
   - 使用Let's Encrypt免费证书
   - 配置HTTPS重定向
   - 启用HSTS安全头

### 高级安全

1. **容器安全**
   ```bash
   # 以非root用户运行
   # 已在Dockerfile中配置
   
   # 限制容器权限
   # 已在docker-compose.yml中配置
   ```

2. **网络安全**
   ```bash
   # 使用内部网络
   # 已在docker-compose.yml中配置
   
   # 限制端口暴露
   # 只暴露必要的80/443端口
   ```

## 🚨 故障排除

### 常见问题

#### 1. 容器启动失败
```bash
# 查看详细错误信息
docker-compose logs bili2text-web

# 检查端口占用
netstat -tlnp | grep :8000

# 重新构建镜像
./deploy.sh build
```

#### 2. 数据库连接失败
```bash
# 检查数据目录权限
ls -la data/

# 重新初始化数据库
docker-compose exec bili2text-web python -c "from webapp.core.database import init_db; init_db()"
```

#### 3. Nginx配置错误
```bash
# 测试Nginx配置
docker-compose exec nginx nginx -t

# 重新加载配置
docker-compose exec nginx nginx -s reload
```

#### 4. 文件权限问题
```bash
# 修复存储目录权限
sudo chown -R 1000:1000 storage/
sudo chown -R 1000:1000 data/
```

### 性能问题

#### 1. 内存不足
```bash
# 增加交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 2. 磁盘空间不足
```bash
# 清理Docker缓存
docker system prune -a

# 清理应用数据
./deploy.sh clean
```

## 📈 扩展部署

### 负载均衡

#### 多实例部署
```yaml
# docker-compose.yml
services:
  bili2text-web-1:
    build: .
    # ... 配置
  
  bili2text-web-2:
    build: .
    # ... 配置
  
  nginx:
    # 配置负载均衡
```

#### Nginx负载均衡配置
```nginx
upstream bili2text_backend {
    server bili2text-web-1:8000;
    server bili2text-web-2:8000;
    keepalive 32;
}
```

### 数据库扩展

#### PostgreSQL部署
```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: bili2text
      POSTGRES_USER: bili2text
      POSTGRES_PASSWORD: password
    volumes:
      - postgres-data:/var/lib/postgresql/data
```

#### Redis集群
```yaml
# docker-compose.yml
services:
  redis-master:
    image: redis:7-alpine
    # 主节点配置
  
  redis-slave:
    image: redis:7-alpine
    # 从节点配置
```

## 🔄 备份和恢复

### 自动备份

#### 创建备份脚本
```bash
#!/bin/bash
# backup-cron.sh

cd /path/to/Bili2Text
./deploy.sh backup

# 保留最近7天的备份
find . -name "backup_*.tar.gz" -mtime +7 -delete
```

#### 设置定时任务
```bash
# 编辑crontab
crontab -e

# 添加每日备份任务
0 2 * * * /path/to/backup-cron.sh
```

### 灾难恢复

#### 完整恢复流程
1. 重新部署应用
2. 恢复数据备份
3. 验证服务状态
4. 更新DNS配置

## 📞 技术支持

### 获取帮助

1. **查看文档**: 阅读完整的项目文档
2. **检查日志**: 查看详细的错误日志
3. **社区支持**: 提交Issue或参与讨论
4. **专业支持**: 联系技术支持团队

### 报告问题

提交Issue时请包含：
- 操作系统和版本
- Docker版本信息
- 错误日志和截图
- 复现步骤
- 配置文件（隐藏敏感信息）

---

## 📝 更新日志

### v2.0.0 (2024-01-15)
- 初始Docker化版本
- 支持完整的容器化部署
- 集成Nginx反向代理
- 添加Redis缓存支持
- 提供自动化部署脚本

---

**祝您部署顺利！** 🎉 