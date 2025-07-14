# 实验性代码目录

本目录包含各种实验性质的代码和不同版本的尝试。这些代码不是主要功能的一部分，但保留下来作为参考。

## 目录结构

```
experimental/
├── whisperx/         # WhisperX相关实验
│   ├── transcribe_audio_whisperx.py        # 初始版本
│   ├── transcribe_audio_whisperx_v2.py     # 第二版
│   ├── transcribe_audio_whisperx_fixed.py  # 修复版
│   ├── transcribe_audio_whisperx_final.py  # 最终版
│   └── download_and_transcribe_whisperx.py # 集成版本
└── install/          # 安装脚本变种
    ├── install_whisperx.py        # 基础版本
    ├── install_whisperx_auto.py   # 自动化版本
    └── install_whisperx_stable.py # 稳定版本
```

## 说明

### WhisperX实验 (`whisperx/`)

这些是尝试集成WhisperX（Whisper的增强版本）的不同版本：
- WhisperX提供了更精确的时间戳对齐
- 多个版本反映了集成过程中的迭代改进
- 最终版本（final）可能是最稳定的实现

### 安装脚本 (`install/`)

不同的WhisperX安装方法尝试：
- 基础版：手动安装步骤
- 自动版：自动化安装流程
- 稳定版：经过测试的稳定安装方法

## 使用建议

1. **这些代码仅供参考**，不保证能正常工作
2. 如需使用WhisperX功能，建议先测试`transcribe_audio_whisperx_final.py`
3. 安装WhisperX时，推荐使用`install_whisperx_stable.py`
4. 在使用前请查看代码了解具体实现

## 注意事项

- 这些实验性代码可能包含未完成的功能
- 可能存在依赖问题或兼容性问题
- 使用时请做好备份和测试