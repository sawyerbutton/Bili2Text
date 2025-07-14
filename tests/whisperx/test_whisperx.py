"""测试WhisperX安装"""
import sys
import warnings
warnings.filterwarnings("ignore")

print("测试WhisperX安装...")

try:
    import torch
    print(f"✓ PyTorch版本: {torch.__version__}")
    print(f"✓ CUDA可用: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"✗ PyTorch导入失败: {e}")
    sys.exit(1)

try:
    import whisperx
    print("✓ WhisperX导入成功")
except ImportError as e:
    print(f"✗ WhisperX导入失败: {e}")
    sys.exit(1)

try:
    print("\n尝试加载tiny模型...")
    model = whisperx.load_model("tiny", "cpu", compute_type="int8", language="zh")
    print("✓ 模型加载成功！")
    
    # 清理
    del model
    print("\n✓ WhisperX可以正常工作")
except Exception as e:
    print(f"✗ 模型加载失败: {e}")
    sys.exit(1)