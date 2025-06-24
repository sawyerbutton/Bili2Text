# Bili2Text Web Docker镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=webapp.app
ENV FLASK_ENV=production

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装yt-dlp
RUN pip install --no-cache-dir yt-dlp

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p storage/audio storage/results storage/temp webapp/logs

# 设置权限
RUN chmod +x run.py

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/system/status || exit 1

# 启动命令
CMD ["python", "run.py", "--production", "--host", "0.0.0.0", "--port", "8000"] 