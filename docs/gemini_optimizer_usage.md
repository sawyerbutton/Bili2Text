# Gemini API 文档优化器使用指南

## 概述

Gemini API 文档优化器是一个智能文档处理系统，专门用于优化语音转录后的文档质量。它能够：

- **智能纠错**：修正ASR识别错误，特别是技术术语和专有名词
- **结构化重组**：将口语化内容转换为结构化的技术文档
- **内容优化**：去除冗余，提取关键信息，生成专业文档

## 快速开始

### 1. 设置API密钥

```bash
# 方式1：环境变量
export GEMINI_API_KEY="your-api-key-here"

# 方式2：配置文件
# 编辑 config/gemini_config.json
```

### 2. 安装依赖

```bash
pip install google-generativeai
```

### 3. 基本使用

#### 优化单个文件

```bash
# 使用命令行
python scripts/optimize/gemini_document_optimizer.py \
  "storage/results/expert_optimized/your_file.md" \
  -o "storage/results/gemini_optimized/output.md"

# 使用Python脚本
from scripts.optimize.gemini_document_optimizer import GeminiDocumentOptimizer, OptimizationConfig

config = OptimizationConfig(api_key="your-key")
optimizer = GeminiDocumentOptimizer(config)
optimizer.optimize_file("input.md", "output.md")
```

#### 批量优化

```bash
# 优化整个目录
python scripts/optimize/gemini_batch_optimizer.py \
  "storage/results/expert_optimized" \
  -o "storage/results/gemini_optimized"
```

## 主要功能

### 1. 智能纠错系统

自动修正常见的ASR识别错误：

| 错误识别 | 正确内容 |
|---------|---------|
| Dipsyc R1 | DeepSeek R1 |
| Gorax 3 | Grok 3 |
| Klaus 3.7 | Claude 3.7 |
| O3 Mini Hide | o3-mini-high |
| LiCo | LeetCode |

### 2. 文档结构优化

- **段落重组**：智能划分段落，改善阅读体验
- **标题层级**：自动生成合理的标题结构
- **信息提取**：提取关键点、结论和建议

### 3. 内容质量提升

- **去除口语化**：移除"嗯"、"啊"等口语词
- **消除重复**：合并重复内容
- **专业化表达**：使用技术写作风格

## 配置选项

### 基础配置

```json
{
  "api_key": "your-key",
  "model_name": "gemini-1.5-flash",  // 或 gemini-1.5-pro
  "temperature": 0.3,                 // 创造性（0-1）
  "cache_enabled": true,              // 启用缓存
  "cache_dir": "storage/cache/gemini"
}
```

### 模型选择

- **gemini-1.5-flash**：快速、经济，适合大批量处理
- **gemini-1.5-pro**：更高质量，适合重要文档

### 自定义纠错词典

编辑 `config/gemini_config.json` 中的 `term_corrections`：

```json
{
  "term_corrections": {
    "错误词": "正确词",
    "Deep Seek": "DeepSeek"
  }
}
```

## 处理流程

1. **预处理**：应用基础纠错词典
2. **信息提取**：分析文档结构和关键信息
3. **分段处理**：智能分割长文本，避免超出API限制
4. **AI优化**：使用Gemini API进行深度优化
5. **后处理**：格式化输出，生成最终文档

## 输出格式

优化后的文档包含：

```markdown
---
title: 文档标题
date: 2024-01-01
source: 原始文件路径
---

# 主标题

> **摘要**: 简短的内容概述

## 关键要点
- 要点1
- 要点2

## 详细内容
[优化后的主体内容]

## 测试结果汇总
| 模型 | 算法测试 | 工程测试 |
|------|---------|---------|

## 结论
- 主要发现

## 使用建议
- 实践建议
```

## 性能优化

### 缓存机制

系统自动缓存处理结果，避免重复调用API：

```bash
# 清理缓存
rm -rf storage/cache/gemini/*

# 禁用缓存
python scripts/optimize/gemini_document_optimizer.py input.md --no-cache
```

### 批处理建议

- 设置合理的并发数（默认为1）
- 大文件自动分段处理
- 实施速率限制避免超出配额

## 常见问题

### Q: API调用失败怎么办？

检查：
1. API密钥是否正确
2. 网络连接是否正常
3. 是否超出API配额

### Q: 如何处理超大文件？

系统会自动分段处理，每段不超过30000字符。

### Q: 可以自定义优化规则吗？

可以通过修改配置文件中的：
- `term_corrections`：纠错词典
- `temperature`：调整创造性
- 修改提示词模板

## 示例对比

### 原始文本
```
Dipsyc R1開原了他的推理模型之後各大AI廠商迅速跟進紛紛发布各自的推理模型...
```

### 优化后
```
# DeepSeek R1 引领推理模型新纪元

## 概述
DeepSeek R1 开源其推理模型后，各大AI厂商迅速跟进，纷纷发布各自的推理模型...

## 关键发展
- **1月13日**：OpenAI 推出 o3-mini-high
- **2月19日**：马斯克发布 Grok 3
- **2月25日**：Anthropic 发布 Claude 3.7
```

## 最佳实践

1. **预处理检查**：确保输入文件编码为UTF-8
2. **分批处理**：大量文件分批处理，避免API限流
3. **质量验证**：重要文档人工复核
4. **增量优化**：利用缓存机制进行增量处理
5. **监控日志**：关注处理日志，及时发现问题

## 集成到工作流

### 与转录流程集成

```python
# 转录后自动优化
def transcribe_and_optimize(video_url):
    # 1. 下载和转录
    transcript = transcribe_video(video_url)

    # 2. 保存原始转录
    save_transcript(transcript, "raw.md")

    # 3. Gemini优化
    optimizer = GeminiDocumentOptimizer(config)
    optimized = optimizer.optimize_file("raw.md", "optimized.md")

    return optimized
```

### 批量处理脚本

```bash
#!/bin/bash
# 批量优化所有转录文件

export GEMINI_API_KEY="your-key"

# 优化所有待处理文件
python scripts/optimize/gemini_batch_optimizer.py \
  storage/results/gpu_transcripts \
  -o storage/results/gemini_optimized \
  -w 1

echo "优化完成！"
```

## 注意事项

1. **API配额**：注意Gemini API的调用限制
2. **隐私安全**：敏感内容建议本地处理
3. **成本控制**：大量文档建议使用flash模型
4. **质量校验**：关键文档需要人工审核

## 技术支持

- GitHub Issues: [提交问题](https://github.com/your-repo/issues)
- 文档更新: 查看最新文档
- 社区讨论: 加入讨论组