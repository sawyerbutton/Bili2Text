# Bili2Text GPU环境指南

## 概述

为了避免CPU和GPU环境冲突，我们采用独立conda环境的方案：
- **bili2text-cli**: CPU环境（原有）
- **bili2text-gpu**: GPU专用环境（新建）

## 快速开始

### 1. 创建GPU环境

```bash
# 运行自动化脚本
./setup_gpu_env.sh

# 或手动创建
conda env create -f config/environment/bili2text-gpu.yml
```

### 2. 环境切换

```bash
# 切换到GPU环境
conda activate bili2text-gpu

# 切换回CPU环境
conda activate bili2text-cli
```

### 3. 使用GPU转录

```bash
# 激活GPU环境后
python -m cli.main gpu-transcribe --url "https://www.bilibili.com/video/BV1234567890" --model large
```

## 环境对比

| 特性 | CPU环境 (bili2text-cli) | GPU环境 (bili2text-gpu) |
|------|------------------------|-------------------------|
| PyTorch | 2.7.1+cpu | 2.7.1+cu121 |
| 磁盘占用 | ~1GB | ~5GB |
| 转录速度 | 基准速度 | 15-22倍提升 |
| 内存需求 | 4GB+ | 8GB+ |
| 显存需求 | 无 | 4GB+ |
| 适用场景 | 少量/短视频 | 批量/长视频 |

## 环境管理工具

```bash
# 运行环境管理器
python gpu_env_manager.py

功能包括：
1. 检查当前环境
2. 列出所有环境  
3. 环境对比
4. 创建快捷别名
5. 性能测试
```

## 推荐别名设置

添加到 `~/.bashrc` 或 `~/.zshrc`：

```bash
# Bili2Text 环境切换
alias bili-cpu='conda activate bili2text-cli'
alias bili-gpu='conda activate bili2text-gpu'

# 快速转录命令
alias bili-transcribe-gpu='conda activate bili2text-gpu && python -m cli.main gpu-transcribe'
alias bili-transcribe-cpu='conda activate bili2text-cli && python -m cli.main transcribe'
```

## 使用建议

### 何时使用CPU环境
- 转录少量短视频（<10分钟）
- 系统资源受限
- 不需要快速处理
- 测试和开发

### 何时使用GPU环境
- 批量转录任务
- 长视频处理（>30分钟）
- 需要快速处理结果
- 使用large模型

## 性能对比示例

| 视频长度 | CPU (medium) | GPU (medium) | 加速比 |
|---------|-------------|--------------|--------|
| 10分钟 | 2.5分钟 | 10秒 | 15x |
| 30分钟 | 7.5分钟 | 30秒 | 15x |
| 60分钟 | 15分钟 | 1分钟 | 15x |

## 故障排除

### GPU环境创建失败
```bash
# 清理并重试
conda env remove -n bili2text-gpu
./setup_gpu_env.sh
```

### CUDA版本不匹配
```bash
# 检查CUDA版本
nvidia-smi
nvcc --version

# 根据版本选择合适的PyTorch
# CUDA 12.x: --index-url https://download.pytorch.org/whl/cu121
# CUDA 11.8: --index-url https://download.pytorch.org/whl/cu118
```

### 显存不足
- 使用更小的模型（tiny, base）
- 减少batch size
- 关闭其他GPU程序

## 最佳实践

1. **保持环境独立**：不要在CPU环境安装GPU包
2. **定期更新**：GPU驱动和CUDA工具包
3. **监控资源**：使用`nvidia-smi`监控GPU使用
4. **选择合适模型**：根据显存大小选择模型
   - 4GB显存: tiny, base
   - 6GB显存: small, medium  
   - 8GB+显存: large

## 命令速查

```bash
# 创建GPU环境
./setup_gpu_env.sh

# 激活GPU环境
conda activate bili2text-gpu

# GPU转录（URL）
python -m cli.main gpu-transcribe --url "<URL>" --model medium

# GPU转录（本地）
python -m cli.main gpu-transcribe --input video.mp4 --model medium

# 批量GPU转录
python -m cli.main gpu-transcribe --input ./videos --batch

# 切回CPU环境
conda activate bili2text-cli
```