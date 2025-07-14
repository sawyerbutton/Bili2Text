"""
Whisper和WhisperX导入测试
使用标准pytest格式
"""
import pytest
import sys


class TestWhisperImport:
    """测试Whisper相关库的导入"""
    
    def test_pytorch_import(self):
        """测试PyTorch导入"""
        try:
            import torch
            assert torch is not None
            print(f"PyTorch版本: {torch.__version__}")
        except ImportError:
            pytest.fail("PyTorch导入失败")
    
    def test_pytorch_cuda_availability(self):
        """测试CUDA可用性"""
        import torch
        cuda_available = torch.cuda.is_available()
        print(f"CUDA可用: {cuda_available}")
        # 不强制要求CUDA，只是检查
        assert isinstance(cuda_available, bool)
    
    def test_whisper_import(self):
        """测试标准Whisper导入"""
        try:
            import whisper
            assert whisper is not None
            print("Whisper导入成功")
        except ImportError:
            pytest.skip("Whisper未安装，跳过测试")
    
    @pytest.mark.whisperx
    def test_whisperx_import(self):
        """测试WhisperX导入"""
        try:
            import whisperx
            assert whisperx is not None
            print("WhisperX导入成功")
        except ImportError:
            pytest.skip("WhisperX未安装，跳过测试")


class TestWhisperModel:
    """测试Whisper模型加载"""
    
    @pytest.mark.requires_model
    @pytest.mark.slow
    def test_load_tiny_model(self):
        """测试加载tiny模型"""
        whisper = pytest.importorskip("whisper")
        
        try:
            model = whisper.load_model("tiny", download_root=".cache/whisper")
            assert model is not None
            
            # 检查模型属性
            assert hasattr(model, 'transcribe')
            assert hasattr(model, 'dims')
            
            # 清理
            del model
            print("Tiny模型加载成功")
        except Exception as e:
            pytest.fail(f"模型加载失败: {e}")
    
    @pytest.mark.whisperx
    @pytest.mark.requires_model
    @pytest.mark.slow
    def test_load_whisperx_model(self):
        """测试加载WhisperX模型"""
        whisperx = pytest.importorskip("whisperx")
        
        try:
            model = whisperx.load_model(
                "tiny", 
                "cpu", 
                compute_type="int8", 
                language="zh"
            )
            assert model is not None
            print("WhisperX模型加载成功")
            
            # 清理
            del model
        except Exception as e:
            pytest.fail(f"WhisperX模型加载失败: {e}")


class TestWhisperTranscribe:
    """测试转录功能"""
    
    @pytest.mark.requires_model
    @pytest.mark.requires_audio
    @pytest.mark.slow
    def test_transcribe_dummy_audio(self, whisper_model_tiny, temp_dir):
        """测试转录虚拟音频"""
        import numpy as np
        
        # 创建虚拟音频数据
        sample_rate = 16000
        duration = 2  # 秒
        audio = np.zeros(sample_rate * duration, dtype=np.float32)
        
        # 转录
        result = whisper_model_tiny.transcribe(audio, language="zh")
        
        # 验证结果格式
        assert isinstance(result, dict)
        assert "text" in result
        assert "segments" in result
        assert isinstance(result["segments"], list)
        
        print(f"转录结果: {result['text']}")
    
    @pytest.mark.requires_model
    @pytest.mark.requires_audio
    @pytest.mark.slow
    def test_transcribe_real_audio(self, whisper_model_tiny, sample_audio_file):
        """测试转录真实音频文件"""
        if not sample_audio_file.exists():
            pytest.skip("没有找到测试音频文件")
        
        # 转录
        result = whisper_model_tiny.transcribe(
            str(sample_audio_file), 
            language="zh"
        )
        
        # 验证结果
        assert isinstance(result, dict)
        assert "text" in result
        assert len(result["text"]) > 0
        assert "segments" in result
        assert len(result["segments"]) > 0
        
        # 验证片段格式
        for segment in result["segments"]:
            assert "id" in segment
            assert "start" in segment
            assert "end" in segment
            assert "text" in segment
            assert segment["end"] > segment["start"]