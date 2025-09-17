# Gemini 文档优化系统使用指南

## 📋 概述

本系统使用 Google Gemini 2.5 Flash 模型对 ASR（自动语音识别）转录的文档进行智能优化，包括错误纠正、格式美化、结构优化等功能。

## 🚀 快速开始

### 1. 设置 API 密钥

```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 2. 批量优化 TXT 文件

```bash
# 优化 ASR 输出的 TXT 文件，转换为专业 Markdown
python batch_optimize_txt_to_markdown.py \
  --input storage/results/gpu_transcripts \
  --output storage/results/professional_markdown
```

### 3. 优化现有 Markdown 文件

```bash
# 优化 mark_transcripts 目录下的所有 Markdown 文件
python batch_optimize_mark_transcripts.py
```

## 🔧 核心组件

### ProfessionalGeminiOptimizer

位于 `scripts/optimize/professional_gemini_optimizer.py`，这是系统的核心优化引擎。

#### 主要特性

- **超大上下文窗口**：支持 100 万 tokens（约 75 万中文字符）
- **专业提示词模板**：专门针对视频逐字稿优化设计的 6 步处理流程
- **智能纠错**：80+ 技术术语和 AI 模型名称自动纠正
- **确定性输出**：temperature=0.0 确保一致的优化结果

#### 使用示例

```python
from scripts.optimize.professional_gemini_optimizer import (
    ProfessionalGeminiOptimizer,
    ProfessionalOptConfig
)

# 配置优化器
config = ProfessionalOptConfig(
    api_key="your-api-key",
    temperature=0.0,  # 确定性输出
    max_document_size=100000  # 10万字符限制
)

# 创建优化器实例
optimizer = ProfessionalGeminiOptimizer(config)

# 优化单个文件
optimizer.optimize_file("input.txt", "output.md")

# 优化文本内容
optimized_text = optimizer.optimize_text(raw_text)
```

## 📂 批量处理脚本

### batch_optimize_txt_to_markdown.py

专门用于批量处理 ASR 输出的 TXT 文件。

#### 功能特点

- 自动检测多个可能的输入目录
- 智能预处理 TXT 内容
- 生成详细的优化报告
- API 速率限制保护（5秒间隔）

#### 命令行参数

```bash
python batch_optimize_txt_to_markdown.py \
  --input INPUT_DIR \    # 输入目录（可选，自动检测）
  --output OUTPUT_DIR \  # 输出目录（默认：storage/results/professional_markdown）
  --pattern "*.txt"      # 文件匹配模式
```

### batch_optimize_mark_transcripts.py

用于优化已有的 Markdown 转录文档。

```bash
python batch_optimize_mark_transcripts.py
```

## 🎯 优化策略

### 六步优化流程

1. **错别字纠正**：修正 ASR 识别错误
2. **专有名词修正**：统一技术术语和产品名称
3. **段落重组**：每段 3-5 句话，逻辑清晰
4. **口语化内容处理**：去除"嗯"、"啊"等语气词
5. **结构化优化**：添加章节标题和层级
6. **格式美化**：Markdown 格式规范化

### 术语纠错字典

系统内置 80+ 常见错误纠正规则：

```python
{
    "GEMD": "Gemini",
    "Dipsyc": "DeepSeek",
    "Klaus": "Claude",
    "LAMA": "Llama",
    "O1": "o1",
    # ... 更多纠错规则
}
```

## 📊 优化报告

每次批量处理后会生成 `OPTIMIZATION_REPORT.md`，包含：

- 处理统计（成功/失败/跳过）
- 平均处理时间
- 文档大小分布
- 详细的处理日志

## ⚠️ 注意事项

### API 限制

- **速率限制**：每分钟 15 个请求（免费套餐）
- **Token 限制**：单次请求最大 100 万 tokens
- **建议**：批量处理时使用 5 秒间隔

### 文件大小限制

- 单个文件建议不超过 10 万字符
- 超大文件会自动跳过
- 可通过配置调整限制

### 错误处理

- 配额超限自动等待 60 秒
- 一般错误等待 10 秒后重试
- 所有错误记录在报告中

## 🔍 故障排查

### 常见问题

1. **API 密钥无效**
   ```bash
   # 检查环境变量
   echo $GEMINI_API_KEY

   # 重新设置
   export GEMINI_API_KEY="your-correct-key"
   ```

2. **配额超限**
   - 等待一段时间后重试
   - 考虑升级到付费套餐

3. **文档过大**
   - 检查文件大小
   - 考虑分割文档

4. **编码问题**
   - 脚本自动尝试 UTF-8 和 GBK 编码
   - 如仍有问题，手动转换编码

## 📈 性能优化建议

1. **使用 GPU 环境**：虽然 Gemini API 在云端运行，本地预处理可受益于 GPU
2. **批量大小**：建议每批 10-20 个文档
3. **并行处理**：当前使用串行处理避免 API 限制，付费用户可考虑并行
4. **缓存机制**：已处理文档自动跳过，避免重复处理

## 🔄 更新日志

### 2025-09-17
- 初始版本发布
- 集成 Gemini 2.5 Flash
- 支持 TXT 到 Markdown 转换
- 添加专业视频逐字稿优化模板
- 实现批量处理和报告生成

## 📝 相关文档

- [README.md](../README.md) - 项目主文档
- [CLAUDE.md](../CLAUDE.md) - Claude 开发指南
- [scripts/optimize/](../scripts/optimize/) - 优化脚本源码