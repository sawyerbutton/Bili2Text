# InfinityAcademy 音频下载与转录工具

这个工具包含两个脚本，用于自动下载B站UP主 InfinityAcademy 的全部视频音频，并进行语音转录。

## 📁 文件说明

### 主要脚本
- `download_infinityacademy_audio.py` - 音频下载脚本
- `transcribe_infinityacademy_audio.py` - 音频转录脚本  

### 安装和工具脚本
- `install_dependencies.py` - 依赖安装脚本（Python版本）
- `install_dependencies.sh` - 依赖安装脚本（Bash版本）
- `download_whisper_model.py` - Whisper模型下载工具
- `simple_transcribe.py` - 简化版转录工具（网络问题备选）
- `test_transcribe_single.py` - 单文件转录测试工具

## 🚀 快速开始

### 1. 安装依赖

**方式一：使用Python脚本**
```bash
python install_dependencies.py
```

**方式二：使用Bash脚本**
```bash
bash install_dependencies.sh
```

**方式三：手动安装**
```bash
# 安装核心依赖
pip install "pyyaml>=6.0"
pip install bilibili-api-python

# 安装相关依赖
pip install aiohttp bilix
pip install openai-whisper torch torchaudio
```

### 2. 使用步骤

**第一步：下载音频文件**
```bash
python download_infinityacademy_audio.py
```

**第二步：转录音频文件**
```bash
python transcribe_infinityacademy_audio.py
```

## 📊 工作流程

1. **下载脚本**会获取 InfinityAcademy 的全部动态信息
2. 筛选出包含视频的动态
3. 批量下载视频音频文件到 `./audio` 目录
4. 生成视频信息文件供转录脚本使用

5. **转录脚本**会扫描 `./audio` 目录中的音频文件
6. 使用 Whisper 模型进行语音转录
7. 生成格式化的 Markdown 文件到 `./result` 目录

## 📂 目录结构

```
Original_Code/
├── download_infinityacademy_audio.py     # 音频下载脚本
├── transcribe_infinityacademy_audio.py   # 音频转录脚本
├── downloaded_infinityacademy.txt        # 已下载视频列表
├── transcribed_infinityacademy.txt       # 已转录音频列表
├── video_info_infinityacademy.txt        # 视频信息文件
├── audio/                                # 音频文件存储目录
├── temp/                                 # 临时文件目录
└── result/                               # Markdown结果文件目录
```

## ⚙️ 配置说明

### 代理设置

如果需要使用代理，可以在脚本中修改：
```python
# 代理设置
use_proxy = True
if use_proxy:
    settings.proxy = "http://127.0.0.1:7890"  # 修改为您的代理地址
```

### Whisper模型

默认使用 `medium` 模型，您可以在转录脚本中修改：
```python
model_name = "medium"    # 可选：tiny, base, small, medium, large, large-v3
```

## 🔧 断点续传

两个脚本都支持断点续传：
- 下载脚本会跳过已下载的视频
- 转录脚本会跳过已转录的音频文件

## 📝 注意事项

1. 首次运行转录脚本时，会自动下载 Whisper 模型，请耐心等待
2. 建议在网络稳定的环境下运行
3. 转录过程需要较多计算资源，建议使用 GPU 加速
4. 生成的 Markdown 文件包含视频嵌入代码，适合在支持的平台使用

## 🤝 故障排除

### 依赖安装问题

如果遇到依赖安装问题，请：

1. 确保 Python 版本 >= 3.9 (新版API要求)
2. 升级 pip: `pip install --upgrade pip`
3. 使用虚拟环境避免冲突
4. 如果遇到412错误，请：
   - 检查网络连接
   - 暂时禁用代理设置
   - 确认用户UID是否正确
5. 如果 bilibili-api-python 安装失败，尝试：
   ```bash
   pip install bilibili-api-python --upgrade
   ```

### Whisper模型下载问题

如果遇到Whisper模型下载失败，可使用以下方案：

**方案1：使用代理下载**
```bash
python download_whisper_model.py
```

**方案2：手动下载模型**
1. 访问 [Whisper GitHub](https://github.com/openai/whisper)
2. 下载模型文件(.pt)到 `./.cache/whisper/` 目录
3. 推荐下载 `base.pt` 模型（平衡效果和速度）

**方案3：使用简化版转录工具**
```bash
python simple_transcribe.py
```

**方案4：在线转录服务**
- OpenAI API
- Google Speech-to-Text
- Azure Speech Services

### 常见错误解决

- **ConnectionResetError**: 网络连接问题，建议使用代理
- **SSL错误**: 证书验证问题，可临时禁用SSL验证
- **412 Precondition Failed**: B站反爬机制，请检查用户ID和网络

## 📄 许可证

本工具仅供学习和个人使用，请遵守相关法律法规和平台使用条款。 