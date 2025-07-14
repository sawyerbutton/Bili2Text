"""最小化测试WhisperX"""
import os
import warnings
warnings.filterwarnings("ignore")

# 设置环境变量
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

print("测试WhisperX最小化导入...")

try:
    print("1. 导入torch...")
    import torch
    print(f"   ✓ PyTorch {torch.__version__}")
    
    print("2. 导入whisperx...")
    import whisperx
    print("   ✓ WhisperX导入成功")
    
    print("3. 尝试加载模型...")
    device = "cpu"
    model = whisperx.load_model(
        "tiny", 
        device,
        compute_type="int8",
        language="zh",
        asr_options={"initial_prompt": "以下是普通话的对话。"}
    )
    print("   ✓ 模型加载成功")
    
    print("\n✅ WhisperX可以正常工作！")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()