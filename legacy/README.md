# Legacy Scripts - 历史脚本存档

## 📁 目录说明

这个目录包含 Bili2Text 项目的**历史版本脚本**，这些脚本在 v2.0.0 模块化重构之前使用。

## 🔄 为什么需要重构？

### 重构前的问题
在模块化重构之前，项目存在以下问题：

#### 1. **代码重复严重**
- 🔴 **Whisper转录逻辑**在4个文件中重复实现
- 🔴 **B站下载逻辑**在4个文件中重复实现  
- 🔴 **Markdown生成逻辑**在3个文件中重复实现
- 🔴 **文件管理逻辑**在多个文件中分散实现

#### 2. **功能边界混乱**
- 🔴 `get_all_dynamics_infinityacademy.py` 一个文件包含：动态获取 + 音频下载 + 语音转录
- 🔴 `main.py` 和 `transcribe_infinityacademy_audio.py` 功能高度重叠
- 🔴 配置和设置分散在各个文件中，难以统一管理

#### 3. **维护困难**
- 🔴 修改核心逻辑需要在多个文件中同步更新
- 🔴 错误处理不一致，有些文件处理完善，有些简陋
- 🔴 新增功能需要复制大量现有代码

#### 4. **用户体验不佳**
- 🔴 需要手动安装依赖，容易出错
- 🔴 脚本之间没有状态共享，重复处理
- 🔴 配置分散，难以自定义

## 🎯 重构后的改进

### 新的模块化架构 (v2.0.0)
```
bili2text_v2/
├── core/                    # 🔧 核心模块
├── workflows/               # ⚡ 高级工作流
├── tools/                   # 🛠️ 管理工具
├── simple_transcribe.py     # 📝 简化入口脚本
└── bili2text.py            # 🎯 统一CLI入口

legacy/                      # 📂 历史脚本（本目录）
├── experimental/           # 🧪 实验性代码
│   ├── whisperx/          # WhisperX相关实验
│   └── install/           # 安装脚本变种
└── （核心功能脚本）        # 经过验证的功能脚本
```

### 解决的问题
- ✅ **消除代码重复**：核心逻辑统一实现，所有脚本共享
- ✅ **清晰的功能分离**：每个模块职责单一明确
- ✅ **统一的配置管理**：集中配置，易于自定义
- ✅ **一致的错误处理**：标准化的异常处理机制
- ✅ **简化的用户体验**：一键安装，智能状态管理

## 📋 历史脚本列表

### 转录脚本
- **`main.py`** - 原始批量转录脚本
  - 🔄 **替代方案**: `workflows/batch_transcribe.py`
- **`transcribe_infinityacademy_audio.py`** - InfinityAcademy转录脚本
  - 🔄 **替代方案**: `workflows/infinity_workflow.py --mode transcribe`

### 下载脚本
- **`download_videos.py`** - 通用视频下载脚本
  - 🔄 **替代方案**: `workflows/batch_transcribe.py` (包含下载功能)
- **`download_infinityacademy_audio.py`** - InfinityAcademy音频下载脚本
  - 🔄 **替代方案**: `workflows/infinity_workflow.py --mode download`

### 内容发现脚本
- **`get_all_dynamics_infinityacademy.py`** - 动态获取+下载+转录一体脚本
  - 🔄 **替代方案**: `workflows/infinity_workflow.py` (完整工作流)
- **`get_ref_from_dynamics.py`** - 参考信息系列处理脚本
  - 🔄 **替代方案**: `workflows/ref_info_workflow.py`

### 工具脚本
- **`install_dependencies.py/.sh`** - 依赖安装脚本
  - 🔄 **替代方案**: `tools/setup.py`
- **`download_whisper_model.py`** - 模型下载脚本
  - 🔄 **替代方案**: `tools/model_downloader.py`

### 文档
- **`README_InfinityAcademy.md`** - InfinityAcademy使用说明
  - 🔄 **替代方案**: 主项目README和CLAUDE.md中的新文档

## 🔄 迁移指南

### 如果你正在使用老脚本
**好消息**: 所有历史脚本都保留在这里，依然可以使用！

### 推荐迁移到新架构
```bash
# 老方式 (仍然可用)
python legacy/main.py

# 新方式 (推荐)
python workflows/batch_transcribe.py
```

### 迁移的好处
- 🚀 **更快的处理速度**：优化的核心逻辑
- 🛡️ **更好的错误处理**：统一的异常管理
- 🔧 **更易的配置**：集中的参数管理  
- 📊 **更详细的进度显示**：改进的用户界面
- 🔄 **更智能的状态管理**：避免重复处理

## ⚠️ 重要说明

1. **向后兼容性**：历史脚本会继续维护，确保现有工作流不受影响
2. **逐步迁移**：你可以按自己的节奏迁移到新架构
3. **功能对等**：新架构包含了所有历史功能，并有所增强
4. **支持获取**：如果迁移过程中遇到问题，可以参考主项目文档

## 📅 版本历史

- **v1.x.x** (历史版本) - 独立脚本架构，功能分散
- **v2.0.0** (当前版本) - 模块化架构，统一核心逻辑

---

*这些脚本见证了 Bili2Text 项目的发展历程，从简单的功能脚本集合发展为结构化的模块化项目。虽然它们已经"退役"，但它们的价值和贡献永远不会被忘记。* 💙