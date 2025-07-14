"""
pytest配置和共享fixtures
"""
import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "bili2text_v2"))
sys.path.insert(0, str(project_root / "legacy"))


# ==================== 配置常量 ====================
TEST_DATA_DIR = Path(__file__).parent / "fixtures"
TEST_AUDIO_DIR = TEST_DATA_DIR / "audio"
TEST_VIDEO_DIR = TEST_DATA_DIR / "video"
TEMP_OUTPUT_DIR = Path(tempfile.gettempdir()) / "bili2text_test_output"


# ==================== Session级别Fixtures ====================
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 创建测试目录
    TEST_DATA_DIR.mkdir(exist_ok=True)
    TEST_AUDIO_DIR.mkdir(exist_ok=True)
    TEST_VIDEO_DIR.mkdir(exist_ok=True)
    TEMP_OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 设置环境变量
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    
    yield
    
    # 清理临时目录（可选）
    # shutil.rmtree(TEMP_OUTPUT_DIR, ignore_errors=True)


# ==================== 通用Fixtures ====================
@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp_path = tempfile.mkdtemp(dir=TEMP_OUTPUT_DIR)
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_audio_file():
    """提供测试音频文件路径"""
    # 检查是否有测试音频文件
    audio_files = list(TEST_AUDIO_DIR.glob("*.mp3"))
    if not audio_files:
        pytest.skip("没有找到测试音频文件")
    return audio_files[0]


@pytest.fixture
def sample_video_url():
    """提供测试视频URL"""
    return "https://www.bilibili.com/video/BV1xx411c7mD"  # 示例URL


# ==================== Whisper相关Fixtures ====================
@pytest.fixture(scope="session")
def whisper_model_tiny():
    """加载Whisper tiny模型（session级别，只加载一次）"""
    pytest.importorskip("whisper")
    import whisper
    
    try:
        model = whisper.load_model("tiny", download_root=".cache/whisper")
        return model
    except Exception as e:
        pytest.skip(f"无法加载Whisper模型: {e}")


@pytest.fixture
def mock_whisper_result():
    """模拟Whisper转录结果"""
    return {
        "text": "这是一个测试转录结果",
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 2.0,
                "text": "这是一个",
            },
            {
                "id": 1,
                "start": 2.0,
                "end": 4.0,
                "text": "测试转录结果",
            }
        ],
        "language": "zh"
    }


# ==================== 工具函数 ====================
def create_test_audio_file(filepath: Path, duration: int = 5):
    """创建测试用的静音音频文件"""
    try:
        import numpy as np
        import wave
        
        sample_rate = 16000
        samples = np.zeros(sample_rate * duration, dtype=np.int16)
        
        with wave.open(str(filepath), 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(samples.tobytes())
        
        return filepath
    except ImportError:
        pytest.skip("需要numpy和wave库来创建测试音频")


# ==================== 标记相关配置 ====================
def pytest_configure(config):
    """pytest配置钩子"""
    # 添加自定义标记说明
    config.addinivalue_line(
        "markers", "slow: 标记为慢速测试（如完整的转录测试）"
    )
    config.addinivalue_line(
        "markers", "requires_model: 需要下载模型的测试"
    )
    config.addinivalue_line(
        "markers", "requires_audio: 需要音频文件的测试"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试收集，自动添加标记"""
    for item in items:
        # 根据文件路径自动添加标记
        if "whisperx" in str(item.fspath):
            item.add_marker(pytest.mark.whisperx)
        if "mp3" in str(item.fspath):
            item.add_marker(pytest.mark.mp3)
        
        # 根据函数名添加标记
        if "test_transcribe" in item.name:
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.requires_model)