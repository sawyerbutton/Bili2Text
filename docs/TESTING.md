# 测试指南

## 概述

Bili2Text使用pytest作为测试框架，提供了完整的单元测试、集成测试和端到端测试。

## 快速开始

### 安装测试依赖

```bash
pip install -r requirements-test.txt
```

### 运行测试

```bash
# 运行所有测试
pytest

# 使用便捷脚本
python run_tests.py all        # 运行所有测试
python run_tests.py unit       # 只运行单元测试
python run_tests.py quick      # 快速测试（跳过慢速）
python run_tests.py coverage   # 生成覆盖率报告
```

## 测试结构

```
tests/
├── unit/                # 单元测试
│   ├── test_whisper_import.py
│   └── test_file_manager.py
├── integration/         # 集成测试
│   ├── test_transcribe_workflow.py
│   └── test_single_transcription.py
├── whisperx/           # WhisperX相关测试
├── mp3/                # MP3处理测试
├── conftest.py         # pytest配置和fixtures
└── utils.py            # 测试工具函数
```

## 测试标记

我们使用pytest标记来分类测试：

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.slow` - 慢速测试（如模型加载）
- `@pytest.mark.whisperx` - WhisperX相关
- `@pytest.mark.mp3` - MP3处理相关
- `@pytest.mark.requires_model` - 需要下载模型
- `@pytest.mark.requires_audio` - 需要音频文件
- `@pytest.mark.network` - 需要网络连接

### 运行特定标记的测试

```bash
# 只运行单元测试
pytest -m unit

# 跳过慢速测试
pytest -m "not slow"

# 只运行WhisperX测试
pytest -m whisperx
```

## 编写测试

### 单元测试示例

```python
import pytest
from bili2text_v2.core.file_manager import FileManager

class TestFileManager:
    def test_clean_filename(self):
        fm = FileManager()
        assert fm.clean_filename("test/file.mp4") == "test_file.mp4"
```

### 使用Fixtures

```python
def test_with_temp_dir(temp_dir):
    # temp_dir是一个临时目录fixture
    test_file = temp_dir / "test.txt"
    test_file.write_text("test content")
    assert test_file.exists()
```

### 集成测试示例

```python
@pytest.mark.integration
@pytest.mark.slow
def test_full_workflow(temp_dir):
    # 测试完整的下载和转录流程
    pass
```

## 测试覆盖率

生成覆盖率报告：

```bash
# 运行测试并生成覆盖率
python run_tests.py coverage

# 或手动运行
pytest --cov=bili2text_v2 --cov=legacy --cov-report=html
```

覆盖率报告会生成在 `htmlcov/index.html`。

## Mock和测试数据

### 使用pytest-mock

```python
def test_download(mocker):
    # Mock下载函数
    mock_download = mocker.patch('bili2text_v2.core.bilibili_downloader.download')
    mock_download.return_value = "path/to/file.mp3"
    
    # 测试代码
    result = download_audio("test_url")
    assert result == "path/to/file.mp3"
```

### 测试数据

测试数据放在 `tests/fixtures/` 目录：

- `audio/` - 测试音频文件
- `video/` - 测试视频文件
- `data/` - 其他测试数据

## 持续集成

项目使用GitHub Actions进行持续集成：

- 每次推送和PR都会运行测试
- 支持多平台（Linux, Windows, macOS）
- 支持多Python版本（3.9, 3.10, 3.11）
- 自动生成覆盖率报告

## 测试最佳实践

1. **保持测试独立** - 每个测试应该独立运行
2. **使用描述性名称** - 测试名称应该清楚说明测试内容
3. **遵循AAA模式** - Arrange, Act, Assert
4. **合理使用Mock** - 只Mock外部依赖
5. **测试边界情况** - 不只测试正常流程
6. **保持测试简单** - 一个测试只测试一件事

## 常见问题

### Q: 测试运行很慢？
A: 使用 `pytest -m "not slow"` 跳过慢速测试

### Q: 如何调试失败的测试？
A: 使用 `pytest -vv --tb=long` 获取详细错误信息

### Q: 如何只运行特定测试？
A: 使用 `pytest -k "test_name"` 或 `pytest path/to/test.py::TestClass::test_method`

### Q: 测试需要网络连接？
A: 标记为 `@pytest.mark.network` 并在离线环境使用 `pytest -m "not network"`