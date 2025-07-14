"""
文件管理器单元测试
"""
import pytest
from pathlib import Path
import json
import shutil

from bili2text_v2.core.file_manager import FileManager


class TestFileManager:
    """测试FileManager类"""
    
    @pytest.fixture
    def file_manager(self, temp_dir):
        """创建FileManager实例"""
        return FileManager(base_dir=str(temp_dir))
    
    def test_init(self, temp_dir):
        """测试初始化"""
        fm = FileManager(base_dir=str(temp_dir))
        
        # 检查目录创建
        assert (temp_dir / "audio").exists()
        assert (temp_dir / "video").exists()
        assert (temp_dir / "result").exists()
        assert (temp_dir / "temp").exists()
        assert (temp_dir / "status").exists()
    
    def test_clean_filename(self, file_manager):
        """测试文件名清理"""
        test_cases = [
            ("测试/文件名.mp4", "测试_文件名.mp4"),
            ("文件名:特殊字符?.mp4", "文件名_特殊字符_.mp4"),
            ("文件名|管道符*.mp4", "文件名_管道符_.mp4"),
            ("正常文件名.mp4", "正常文件名.mp4"),
        ]
        
        for input_name, expected in test_cases:
            result = file_manager.clean_filename(input_name)
            assert result == expected
    
    def test_get_audio_path(self, file_manager):
        """测试获取音频路径"""
        bv_id = "BV1234567890"
        path = file_manager.get_audio_path(bv_id)
        
        assert str(path).endswith(f"{bv_id}.mp3")
        assert "audio" in str(path)
    
    def test_get_video_path(self, file_manager):
        """测试获取视频路径"""
        bv_id = "BV1234567890"
        path = file_manager.get_video_path(bv_id)
        
        assert str(path).endswith(f"{bv_id}.mp4")
        assert "video" in str(path)
    
    def test_get_result_path(self, file_manager):
        """测试获取结果路径"""
        bv_id = "BV1234567890"
        
        # 默认格式（txt）
        path_txt = file_manager.get_result_path(bv_id)
        assert str(path_txt).endswith(f"{bv_id}.txt")
        
        # 指定格式
        path_md = file_manager.get_result_path(bv_id, format="md")
        assert str(path_md).endswith(f"{bv_id}.md")
    
    def test_save_and_load_status(self, file_manager):
        """测试保存和加载状态"""
        status_data = {
            "downloaded": ["BV1111", "BV2222"],
            "transcribed": ["BV1111"],
            "failed": ["BV3333"]
        }
        
        # 保存状态
        status_file = file_manager.save_download_status(status_data)
        assert status_file.exists()
        
        # 加载状态
        loaded_data = file_manager.load_download_status(status_file)
        assert loaded_data == status_data
    
    def test_save_video_info(self, file_manager):
        """测试保存视频信息"""
        video_info = {
            "bvid": "BV1234567890",
            "title": "测试视频",
            "author": "测试作者",
            "duration": 300
        }
        
        file_manager.save_video_info("BV1234567890", video_info)
        
        # 检查文件是否创建
        info_file = file_manager.status_dir / "video_info" / "BV1234567890.json"
        assert info_file.exists()
        
        # 检查内容
        with open(info_file, 'r', encoding='utf-8') as f:
            loaded_info = json.load(f)
        assert loaded_info == video_info
    
    def test_is_downloaded(self, file_manager):
        """测试检查下载状态"""
        bv_id = "BV1234567890"
        
        # 初始状态
        assert not file_manager.is_downloaded(bv_id)
        
        # 创建音频文件
        audio_path = file_manager.get_audio_path(bv_id)
        audio_path.parent.mkdir(exist_ok=True)
        audio_path.touch()
        
        # 应该返回True
        assert file_manager.is_downloaded(bv_id)
    
    def test_is_transcribed(self, file_manager):
        """测试检查转录状态"""
        bv_id = "BV1234567890"
        
        # 初始状态
        assert not file_manager.is_transcribed(bv_id)
        
        # 创建结果文件
        result_path = file_manager.get_result_path(bv_id)
        result_path.parent.mkdir(exist_ok=True)
        result_path.touch()
        
        # 应该返回True
        assert file_manager.is_transcribed(bv_id)
    
    def test_clean_temp(self, file_manager):
        """测试清理临时文件"""
        # 创建临时文件
        temp_file = file_manager.temp_dir / "test_temp.txt"
        temp_file.touch()
        
        assert temp_file.exists()
        
        # 清理
        file_manager.clean_temp()
        
        # 目录应该存在但为空
        assert file_manager.temp_dir.exists()
        assert not list(file_manager.temp_dir.iterdir())
    
    def test_get_all_audio_files(self, file_manager):
        """测试获取所有音频文件"""
        # 创建测试音频文件
        audio_files = ["test1.mp3", "test2.mp3", "test3.wav"]
        for filename in audio_files:
            (file_manager.audio_dir / filename).touch()
        
        # 获取所有音频文件
        all_files = file_manager.get_all_audio_files()
        
        # 检查结果
        assert len(all_files) == 3
        filenames = [f.name for f in all_files]
        assert all(name in filenames for name in audio_files)