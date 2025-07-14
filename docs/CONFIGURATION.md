# 配置管理指南

## 概述

Bili2Text v3 引入了全新的配置管理系统，支持：
- 🎯 类型安全的配置验证
- 🔄 多种配置源（文件、环境变量）
- 📝 灵活的配置格式（YAML、JSON）
- 🌍 多环境支持

## 快速开始

### 1. 生成默认配置

```bash
# 生成配置文件
python bili2text_v2/tools/config_tool.py generate

# 生成配置文件和环境变量示例
python bili2text_v2/tools/config_tool.py generate --env
```

### 2. 查看当前配置

```bash
# 树形显示
python bili2text_v2/tools/config_tool.py show

# JSON格式
python bili2text_v2/tools/config_tool.py show -f json

# YAML格式
python bili2text_v2/tools/config_tool.py show -f yaml
```

### 3. 验证配置文件

```bash
python bili2text_v2/tools/config_tool.py validate config.yml
```

## 配置结构

### 完整配置示例

```yaml
# config.yml
app_name: Bili2Text
version: 3.1.0
debug: false

# Whisper 模型配置
whisper:
  model_name: medium      # 可选: tiny, base, small, medium, large, large-v2, large-v3
  device: null           # null 表示自动选择 (cuda/cpu)
  language: zh           # 转录语言
  initial_prompt: "简体中文,加上标点"
  cache_dir: .cache/whisper

# 下载配置
download:
  proxy_url: null        # 代理URL
  concurrent_downloads: 3
  timeout: 300
  retry_times: 3
  only_audio: true
  audio_quality: "192k"

# 存储配置
storage:
  base_dir: "."
  audio_dir: audio
  video_dir: video
  result_dir: result
  temp_dir: temp
  status_dir: status

# 日志配置
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_path: null
  max_bytes: 10485760
  backup_count: 5

# 工作流配置
workflow:
  batch_size: 10
  skip_downloaded: true
  skip_transcribed: true
  output_format: txt
  save_segments: false
```

## 配置优先级

配置按以下优先级加载（后面的覆盖前面的）：

1. **默认配置** - 内置的默认值
2. **配置文件** - `config.yml`、`config.json`等
3. **环境变量** - `BILI2TEXT_`开头的环境变量
4. **命令行参数** - 直接传递的参数

## 环境变量配置

### 命名规则

环境变量使用 `BILI2TEXT_` 前缀，嵌套配置使用双下划线 `__` 分隔：

```bash
# 设置Whisper模型
export BILI2TEXT_WHISPER__MODEL_NAME=large

# 设置代理
export BILI2TEXT_DOWNLOAD__PROXY_URL=http://127.0.0.1:7890

# 设置日志级别
export BILI2TEXT_LOGGING__LEVEL=DEBUG
```

### 使用 .env 文件

创建 `.env` 文件：

```bash
# .env
BILI2TEXT_DEBUG=true
BILI2TEXT_WHISPER__MODEL_NAME=large
BILI2TEXT_WHISPER__DEVICE=cuda
BILI2TEXT_DOWNLOAD__PROXY_URL=http://127.0.0.1:7890
```

## 在代码中使用配置

### 获取全局配置

```python
from bili2text_v2.config import get_config

# 获取配置
config = get_config()

# 访问配置值
model_name = config.whisper.model_name
proxy_url = config.download.proxy_url
```

### 使用特定配置

```python
from bili2text_v2.config import WhisperConfig
from bili2text_v2.core.whisper_transcriber_v2 import WhisperTranscriber

# 创建自定义配置
whisper_config = WhisperConfig(
    model_name="large-v3",
    device="cuda",
    language="en"
)

# 使用配置
transcriber = WhisperTranscriber(config=whisper_config)
```

### 初始化配置

```python
from bili2text_v2.config import init_config

# 从指定文件加载配置
init_config("path/to/config.yml")

# 或使用默认位置
init_config()
```

## 配置工具命令

### 生成配置

```bash
# 生成 YAML 配置
python bili2text_v2/tools/config_tool.py generate -o config.yml

# 生成 JSON 配置
python bili2text_v2/tools/config_tool.py generate -o config.json

# 同时生成环境变量示例
python bili2text_v2/tools/config_tool.py generate --env
```

### 验证配置

```bash
# 验证配置文件
python bili2text_v2/tools/config_tool.py validate config.yml

# 显示详细信息
python bili2text_v2/tools/config_tool.py validate config.yml -v
```

### 比较配置

```bash
# 查看当前配置与默认配置的差异
python bili2text_v2/tools/config_tool.py diff
```

## 多环境配置

### 开发环境

```yaml
# config.dev.yml
debug: true
whisper:
  model_name: tiny  # 使用小模型加快开发
logging:
  level: DEBUG
  file_path: logs/dev.log
```

### 生产环境

```yaml
# config.prod.yml
debug: false
whisper:
  model_name: large-v3
  device: cuda
logging:
  level: WARNING
  file_path: logs/prod.log
download:
  concurrent_downloads: 5
```

### 切换环境

```bash
# 使用环境变量指定配置文件
export BILI2TEXT_CONFIG_FILE=config.prod.yml

# 或在代码中
init_config("config.prod.yml")
```

## 配置最佳实践

1. **不要在代码中硬编码配置值**
   ```python
   # ❌ 错误
   model = whisper.load_model("medium")
   
   # ✅ 正确
   config = get_config()
   model = whisper.load_model(config.whisper.model_name)
   ```

2. **敏感信息使用环境变量**
   ```bash
   # 不要将代理密码等信息写入配置文件
   export BILI2TEXT_DOWNLOAD__PROXY_URL=http://user:pass@proxy.com:8080
   ```

3. **为不同环境创建不同配置**
   - `config.yml` - 默认/开发配置
   - `config.prod.yml` - 生产配置
   - `config.test.yml` - 测试配置

4. **使用配置验证**
   ```bash
   # 部署前验证配置
   python bili2text_v2/tools/config_tool.py validate config.prod.yml
   ```

5. **文档化自定义配置**
   - 在 README 中说明必需的配置项
   - 提供配置示例

## 常见问题

### Q: 如何查看当前使用的配置？
```bash
python bili2text_v2/tools/config_tool.py show
```

### Q: 配置文件放在哪里？
默认查找顺序：
1. `config.yml`
2. `config.yaml`
3. `config.json`
4. `.bili2text.yml`

### Q: 如何临时修改配置？
使用环境变量：
```bash
BILI2TEXT_WHISPER__MODEL_NAME=tiny python bili2text_v2/simple_transcribe.py
```

### Q: 如何添加新的配置项？
1. 在 `schema.py` 中添加字段
2. 更新默认配置文件
3. 在代码中使用新配置

### Q: 配置不生效？
检查：
1. 配置文件路径是否正确
2. 环境变量名称是否正确（注意双下划线）
3. 使用 `show` 命令确认当前配置