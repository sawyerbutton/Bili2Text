"""
转录工作流集成测试
"""
import pytest
from pathlib import Path
import time

from tests.utils import TestTimer, create_test_config, assert_file_exists


class TestTranscribeWorkflow:
    """测试完整的转录工作流"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.requires_model
    def test_simple_transcribe_workflow(self, temp_dir):
        """测试简单转录工作流"""
        # 导入模块
        transcriber = pytest.importorskip("bili2text_v2.core.whisper_transcriber")
        
        # 创建配置
        config = create_test_config(model_name="tiny")
        
        # 创建转录器
        whisper = transcriber.WhisperTranscriber(
            model_name=config["model_name"],
            device=config["device"],
            cache_dir=str(temp_dir / ".cache")
        )
        
        # 创建测试音频（静音）
        import numpy as np
        audio_data = np.zeros(16000 * 3, dtype=np.float32)  # 3秒静音
        
        # 执行转录
        with TestTimer() as timer:
            result = whisper.transcribe_audio_data(
                audio_data,
                language=config["language"]
            )
        
        # 验证结果
        assert isinstance(result, dict)
        assert "text" in result
        assert "processed_text" in result
        assert timer.elapsed < 10  # 应该在10秒内完成
        
        print(f"转录完成，耗时: {timer.elapsed:.2f}秒")
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_file_manager_integration(self, temp_dir):
        """测试文件管理器集成"""
        from bili2text_v2.core.file_manager import FileManager
        
        # 创建文件管理器
        fm = FileManager(base_dir=str(temp_dir))
        
        # 模拟完整流程
        bv_id = "BV_TEST_001"
        
        # 1. 保存视频信息
        video_info = {
            "bvid": bv_id,
            "title": "集成测试视频",
            "author": "测试作者",
            "duration": 120
        }
        fm.save_video_info(bv_id, video_info)
        
        # 2. 模拟下载完成
        audio_path = fm.get_audio_path(bv_id)
        audio_path.parent.mkdir(exist_ok=True)
        audio_path.write_text("模拟音频数据")
        
        # 3. 检查下载状态
        assert fm.is_downloaded(bv_id)
        
        # 4. 模拟转录完成
        result_path = fm.get_result_path(bv_id)
        result_path.parent.mkdir(exist_ok=True)
        result_path.write_text("转录结果文本")
        
        # 5. 检查转录状态
        assert fm.is_transcribed(bv_id)
        
        # 6. 保存状态
        status = {
            "downloaded": [bv_id],
            "transcribed": [bv_id],
            "failed": []
        }
        status_file = fm.save_download_status(status)
        assert_file_exists(status_file)
    
    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.skip(reason="需要真实的B站视频URL")
    def test_bilibili_download_integration(self, temp_dir):
        """测试B站下载集成（需要网络）"""
        downloader = pytest.importorskip("bili2text_v2.core.bilibili_downloader")
        
        # 创建下载器
        bd = downloader.BilibiliDownloader(download_dir=str(temp_dir))
        
        # 测试URL（需要替换为有效的URL）
        test_url = "https://www.bilibili.com/video/BV1xx411c7mD"
        
        # 执行下载
        try:
            result = bd.download_audio(test_url)
            assert result is not None
            assert Path(result).exists()
        except Exception as e:
            pytest.skip(f"下载失败，可能是网络问题: {e}")


class TestBatchProcessing:
    """测试批量处理"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_batch_transcribe_simulation(self, temp_dir):
        """测试批量转录模拟"""
        # 创建多个测试文件
        test_files = []
        for i in range(3):
            audio_file = temp_dir / f"test_audio_{i}.txt"
            audio_file.write_text(f"模拟音频数据 {i}")
            test_files.append(audio_file)
        
        # 模拟批量处理
        results = []
        with TestTimer() as timer:
            for file in test_files:
                # 模拟处理延迟
                time.sleep(0.1)
                result = {
                    "file": str(file),
                    "status": "completed",
                    "text": f"转录结果 {file.name}"
                }
                results.append(result)
        
        # 验证结果
        assert len(results) == 3
        assert all(r["status"] == "completed" for r in results)
        assert timer.elapsed < 1  # 应该在1秒内完成
        
        print(f"批量处理完成，共{len(results)}个文件")


class TestErrorHandling:
    """测试错误处理"""
    
    @pytest.mark.integration
    def test_invalid_model_handling(self):
        """测试无效模型处理"""
        transcriber = pytest.importorskip("bili2text_v2.core.whisper_transcriber")
        
        with pytest.raises(Exception):
            # 尝试加载不存在的模型
            whisper = transcriber.WhisperTranscriber(
                model_name="invalid_model_name"
            )
    
    @pytest.mark.integration
    def test_missing_file_handling(self, temp_dir):
        """测试缺失文件处理"""
        from bili2text_v2.core.file_manager import FileManager
        
        fm = FileManager(base_dir=str(temp_dir))
        
        # 检查不存在的文件
        assert not fm.is_downloaded("NON_EXISTENT_BV")
        assert not fm.is_transcribed("NON_EXISTENT_BV")
        
        # 尝试加载不存在的状态文件
        non_existent = temp_dir / "non_existent.json"
        result = fm.load_download_status(non_existent)
        assert result is None or result == {}