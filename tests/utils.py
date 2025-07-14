"""
测试工具函数
"""
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional


class TestTimer:
    """测试计时器"""
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
    
    @property
    def elapsed(self) -> float:
        """获取经过的时间（秒）"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


def compare_transcripts(transcript1: str, transcript2: str, threshold: float = 0.8) -> float:
    """
    比较两个转录文本的相似度
    
    Args:
        transcript1: 第一个转录文本
        transcript2: 第二个转录文本
        threshold: 相似度阈值
    
    Returns:
        相似度分数（0-1）
    """
    # 简单的字符级相似度计算
    # 实际项目中可以使用更复杂的算法如编辑距离
    chars1 = set(transcript1)
    chars2 = set(transcript2)
    
    if not chars1 or not chars2:
        return 0.0
    
    intersection = chars1.intersection(chars2)
    union = chars1.union(chars2)
    
    return len(intersection) / len(union)


def save_test_result(result: Dict[str, Any], output_path: Path):
    """
    保存测试结果到JSON文件
    
    Args:
        result: 测试结果字典
        output_path: 输出路径
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def load_test_result(input_path: Path) -> Dict[str, Any]:
    """
    从JSON文件加载测试结果
    
    Args:
        input_path: 输入路径
    
    Returns:
        测试结果字典
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_test_config(
    model_name: str = "tiny",
    device: str = "cpu",
    language: str = "zh",
    **kwargs
) -> Dict[str, Any]:
    """
    创建测试配置
    
    Args:
        model_name: 模型名称
        device: 设备类型
        language: 语言代码
        **kwargs: 其他配置项
    
    Returns:
        配置字典
    """
    config = {
        "model_name": model_name,
        "device": device,
        "language": language,
        "test_mode": True
    }
    config.update(kwargs)
    return config


def mock_download_progress(total_size: int = 1000000, chunk_size: int = 1024):
    """
    模拟下载进度生成器
    
    Args:
        total_size: 总大小（字节）
        chunk_size: 块大小（字节）
    
    Yields:
        下载进度（0-100）
    """
    downloaded = 0
    while downloaded < total_size:
        downloaded += chunk_size
        progress = min(100, (downloaded / total_size) * 100)
        yield progress
        time.sleep(0.01)  # 模拟网络延迟


def assert_file_exists(filepath: Path, message: Optional[str] = None):
    """
    断言文件存在
    
    Args:
        filepath: 文件路径
        message: 错误消息
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise AssertionError(message or f"文件不存在: {filepath}")


def assert_directory_structure(root_dir: Path, expected_structure: Dict[str, Any]):
    """
    断言目录结构符合预期
    
    Args:
        root_dir: 根目录
        expected_structure: 预期的目录结构
    
    Example:
        expected = {
            "audio": {"test.mp3": None},
            "result": {"test.txt": None}
        }
    """
    root_dir = Path(root_dir)
    
    def check_structure(current_dir: Path, structure: Dict[str, Any]):
        for name, sub_structure in structure.items():
            path = current_dir / name
            if sub_structure is None:
                # 文件
                assert path.is_file(), f"文件不存在: {path}"
            else:
                # 目录
                assert path.is_dir(), f"目录不存在: {path}"
                check_structure(path, sub_structure)
    
    check_structure(root_dir, expected_structure)