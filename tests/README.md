# 测试目录说明

本目录包含项目的所有测试代码和测试结果。

## 目录结构

```
tests/
├── unit/              # 单元测试
├── integration/       # 集成测试
├── whisperx/         # WhisperX相关测试
├── mp3/              # MP3转录测试
├── results/          # 测试结果文件
└── fixtures/         # 测试数据和固定资源
```

## 测试分类

### WhisperX测试 (`whisperx/`)
- test_whisperx.py - 基础WhisperX功能测试
- test_whisperx_final.py - 最终版本测试
- test_whisperx_minimal.py - 最小化测试用例
- test_whisperx_simple.py - 简单功能测试
- test_whisperx_working.py - 工作版本测试

### MP3测试 (`mp3/`)
- test_mp3_transcription.py - MP3转录测试
- test_single_mp3.py - 单个MP3文件测试
- simple_mp3_test.py - 简单MP3测试
- batch_transcribe_mp3.py - 批量MP3转录测试

### 集成测试 (`integration/`)
- test_single_transcription.py - 单个转录集成测试

## 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定类别的测试
pytest tests/whisperx/
pytest tests/mp3/

# 运行单个测试文件
pytest tests/whisperx/test_whisperx.py
```

## 注意事项

1. 所有新的测试文件都应该放在相应的子目录下
2. 测试结果文件应该放在 `results/` 目录
3. 测试用的固定数据放在 `fixtures/` 目录
4. 避免在项目根目录创建测试文件