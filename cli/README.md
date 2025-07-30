# Bili2Text CLI 工具

## 目录结构

```
cli/
├── main.py                # CLI主入口，提供统一的命令行接口
├── download_audio.py      # 音频下载和Whisper转录功能
├── download_video.py      # 视频文件下载功能
├── get_dynamics.py        # 获取UP主动态视频列表
├── get_dynamics_demo.py   # 动态获取演示版本（无需依赖）
├── transcribe_videos.py   # 本地视频文件批量转录
├── data/                  # 数据文件目录
│   └── dynamics_demo.json # 演示数据
└── deprecated/            # 已废弃的旧版本代码
```

## 使用方法

### 1. 使用统一入口

```bash
python -m cli.main <command> [options]
```

### 2. 可用命令

- **audio**: 下载音频并转录
- **video**: 下载视频文件
- **dynamics**: 获取UP主动态
- **transcribe**: 转录本地视频
- **batch**: 批量处理

### 3. 示例

```bash
# 获取UP主动态
python -m cli.main dynamics --user "老师好我叫何同学" --count 5

# 下载音频并转录
python -m cli.main audio --url "https://www.bilibili.com/video/BV1234567890" --model base

# 下载视频
python -m cli.main video --url "https://www.bilibili.com/video/BV1234567890"

# 转录本地视频
python -m cli.main transcribe --input-dir ./videos --model medium
```

## 模块说明

### main.py
- CLI主入口，处理命令行参数
- 路由到不同的子命令
- 提供统一的帮助信息

### download_audio.py
- 从视频URL下载音频
- 使用Whisper模型进行语音识别
- 保存转录结果为文本文件

### download_video.py
- 下载完整的视频文件
- 支持批量下载
- 保存为MP4格式

### get_dynamics.py
- 获取指定UP主的最新动态
- 筛选视频类动态
- 返回视频信息列表

### transcribe_videos.py
- 批量处理本地视频文件
- 提取音频并转录
- 支持多种视频格式

## 依赖要求

- Python 3.9+
- bilibili-api-python
- bilix
- openai-whisper
- torch (CPU或GPU版本)
- ffmpeg