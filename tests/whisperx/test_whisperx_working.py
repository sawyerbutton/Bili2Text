#!/usr/bin/env python3
"""测试WhisperX是否正常工作"""
import os
import warnings
warnings.filterwarnings("ignore")

# 设置环境变量
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

print("="*60)
print("WhisperX功能测试")
print("="*60)

try:
    # 1. 导入测试
    print("\n1. 导入测试...")
    import torch
    import whisperx
    import faster_whisper
    print(f"   ✓ PyTorch: {torch.__version__}")
    print(f"   ✓ WhisperX: 导入成功")
    print(f"   ✓ faster-whisper: 导入成功")
    print(f"   ✓ 设备: {'cuda' if torch.cuda.is_available() else 'cpu'}")
    
    # 2. 模型加载测试
    print("\n2. 模型加载测试...")
    device = "cpu"
    compute_type = "int8"
    
    # 直接使用最简单的参数
    model = whisperx.load_model("tiny", device, compute_type=compute_type)
    print("   ✓ 模型加载成功！")
    
    # 3. 音频加载测试
    print("\n3. 音频处理测试...")
    test_audio = "./audio/aac/你妹的，540也排队.aac"
    
    if os.path.exists(test_audio):
        print(f"   测试文件: {test_audio}")
        
        # 加载音频
        audio = whisperx.load_audio(test_audio)
        duration = len(audio) / 16000
        print(f"   ✓ 音频加载成功，长度: {duration:.2f}秒")
        
        # 4. 转录测试
        print("\n4. 转录测试...")
        print("   开始转录（这可能需要一些时间）...")
        
        result = model.transcribe(
            audio,
            batch_size=8,
            language="zh",
            print_progress=True
        )
        
        print(f"   ✓ 转录完成！")
        print(f"   检测到语言: {result.get('language', 'zh')}")
        print(f"   段落数: {len(result.get('segments', []))}")
        
        # 显示前几个转录结果
        segments = result.get('segments', [])
        if segments:
            print("\n   转录结果预览:")
            for i, seg in enumerate(segments[:3]):
                text = seg.get('text', '').strip()
                start = seg.get('start', 0)
                end = seg.get('end', 0)
                print(f"   [{start:.2f} - {end:.2f}] {text}")
            
            if len(segments) > 3:
                print(f"   ... 还有 {len(segments) - 3} 个段落")
        
        print("\n✅ WhisperX完全正常工作！")
        print("\n可以使用以下命令运行完整转录:")
        print("python legacy/transcribe_audio_whisperx_fixed.py")
        
    else:
        print(f"   ⚠️  测试音频文件不存在: {test_audio}")
        print("   但WhisperX模块加载正常")
    
    # 清理
    del model
    import gc
    gc.collect()
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n可能的解决方案:")
    print("1. 确保音频文件存在")
    print("2. 尝试使用CPU模式")
    print("3. 降低batch_size")
    print("4. 检查依赖版本兼容性")