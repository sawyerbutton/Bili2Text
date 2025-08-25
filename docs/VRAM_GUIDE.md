# Whisper模型显存使用指南

## 显存需求对照表

| 模型 | FP32显存需求 | FP16显存需求 | RTX 4060 (8GB) 兼容性 |
|------|-------------|-------------|---------------------|
| tiny | 1.5 GB | 1.0 GB | ✅ 完美运行 |
| base | 1.5 GB | 1.0 GB | ✅ 完美运行 |
| small | 2.5 GB | 1.5 GB | ✅ 完美运行 |
| medium | 5.0 GB | 3.0 GB | ✅ 推荐使用 |
| large | 10.0 GB | 6.0 GB | ⚠️ 可能OOM |
| large-v3 | 10.0 GB | 6.0 GB | ⚠️ 可能OOM |

## RTX 4060 (8GB) 使用建议

### 推荐配置
```bash
# 最佳选择 - Medium模型
python -m cli.main gpu-transcribe --url "<URL>" --model medium --compute-type float16

# 快速处理 - Small模型
python -m cli.main gpu-transcribe --url "<URL>" --model small --compute-type float16

# 测试用途 - Tiny模型
python -m cli.main gpu-transcribe --url "<URL>" --model tiny
```

### Large模型解决方案

#### 方案1：使用优化脚本
```bash
# 运行优化工具
python cli/gpu_optimize.py

# 使用优化后的脚本
python cli/gpu_transcribe_optimized.py --url "<URL>"
```

#### 方案2：手动优化设置
```bash
# 设置环境变量
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:512

# 清理显存后运行
python -m cli.main gpu-transcribe --url "<URL>" --model large --compute-type float16
```

#### 方案3：使用CPU处理Large模型
```bash
# 切换到CPU环境
conda activate bili2text-cli

# 使用CPU运行large模型（较慢但稳定）
python -m cli.main audio --url "<URL>" --model large
```

## 显存优化技巧

### 1. 释放显存
```bash
# 查看GPU占用
nvidia-smi

# 杀死占用GPU的进程
kill -9 <PID>

# Python中清理显存
import torch
torch.cuda.empty_cache()
```

### 2. 监控显存使用
```bash
# 实时监控
watch -n 1 nvidia-smi

# 或使用Python监控
python -c "import torch; print(f'已用: {torch.cuda.memory_allocated()/1024**3:.1f}GB')"
```

### 3. 批处理优化
- 长音频分段处理
- 降低batch size
- 使用更小的beam size

## 模型选择决策树

```
8GB显存可用？
├─ 是 → 需要最高质量？
│   ├─ 是 → 使用medium + FP16
│   └─ 否 → 使用small + FP16（速度更快）
└─ 否 → 使用CPU或tiny模型
```

## 常见错误解决

### CUDA out of memory
1. 降级到更小的模型
2. 使用FP16精度
3. 清理GPU进程
4. 重启GPU环境

### 模型加载慢
- Large模型约3GB，下载需要时间
- 建议使用medium模型（769MB）

### 转录效果差
- Tiny/Base模型精度较低
- 建议至少使用Small模型
- 中文识别推荐Medium以上

## 性能对比（RTX 4060）

| 模型 | 速度 | 质量 | 显存 | 推荐场景 |
|------|------|------|------|---------|
| tiny | 50x | ★★☆☆☆ | 1GB | 测试/字幕 |
| small | 25x | ★★★☆☆ | 1.5GB | 日常使用 |
| medium | 15x | ★★★★☆ | 3GB | 推荐配置 |
| large | 10x | ★★★★★ | 6GB | 高质量需求 |

## 快速命令

```bash
# 查看可用显存
python -c "import torch; print(f'可用: {(torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0))/1024**3:.1f}GB')"

# 推荐命令（稳定）
python -m cli.main gpu-transcribe --url "<URL>" --model medium

# 测试命令（快速）
python -m cli.main gpu-transcribe --url "<URL>" --model tiny
```