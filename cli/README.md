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
├── gpu_transcribe.py      # GPU加速转录工具（新增）
├── setup_gpu.py           # GPU环境配置脚本（新增）
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
- **gpu-transcribe**: GPU加速转录（新增）
- **setup-gpu**: 配置GPU环境（新增）

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

# GPU加速转录（推荐）
# 从URL下载并转录
python -m cli.main gpu-transcribe --url "https://www.bilibili.com/video/BV1234567890" --model large

# 转录本地文件
python -m cli.main gpu-transcribe --input audio.mp3 --model large --device cuda

# 批量GPU转录
python -m cli.main gpu-transcribe --input ./videos --model medium --batch

# 配置GPU环境
python -m cli.main setup-gpu
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

### gpu_transcribe.py（新增）
- GPU加速的Whisper转录
- 支持B站URL和本地文件输入
- 支持FP16混合精度推理
- GPU内存管理和监控
- 批量处理优化
- 自动fallback到CPU

### setup_gpu.py（新增）
- 检测CUDA和GPU环境
- 自动安装GPU版PyTorch
- 测试Whisper GPU功能
- 生成requirements文件

## GPU加速说明

### 环境要求
- NVIDIA GPU（推荐显存4GB+）
- CUDA 11.8 或 12.1+
- NVIDIA驱动 450.80.02+

### 性能对比
| 模型 | CPU耗时 | GPU耗时 | 加速比 |
|------|---------|---------|--------|
| tiny | 2分钟 | 20秒 | 6x |
| base | 4分钟 | 30秒 | 8x |
| medium | 15分钟 | 1分钟 | 15x |
| large | 45分钟 | 2分钟 | 22x |

### GPU设置步骤
1. 运行环境检测：`python -m cli.main setup-gpu`
2. 安装GPU依赖（如需要）
3. 使用GPU转录：
   - URL方式：`python -m cli.main gpu-transcribe --url "https://www.bilibili.com/video/BV1234567890"`
   - 本地文件：`python -m cli.main gpu-transcribe --input video.mp4`

## 依赖要求

### 基础依赖
- Python 3.9+
- bilibili-api-python
- bilix
- openai-whisper
- ffmpeg

### GPU支持（可选）
- torch (GPU版本)
- CUDA 11.8 或 12.1+
- 推荐显存：4GB+（medium模型）