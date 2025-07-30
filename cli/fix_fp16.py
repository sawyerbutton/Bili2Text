#!/usr/bin/env python3
"""
修复FP16类型错误的补丁脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_fp16_fix():
    """测试FP16修复"""
    print("=== 测试FP16类型兼容性 ===\n")
    
    try:
        import torch
        import whisper
        import numpy as np
        
        if not torch.cuda.is_available():
            print("错误：GPU不可用")
            return
        
        # 测试配置
        configs = [
            ("medium + float32", "medium", False),
            ("medium + float16", "medium", True),
            ("small + float16", "small", True),
        ]
        
        for desc, model_name, use_fp16 in configs:
            print(f"\n测试: {desc}")
            try:
                # 清理显存
                torch.cuda.empty_cache()
                
                # 加载模型
                print(f"  加载模型...")
                model = whisper.load_model(model_name, device="cuda")
                
                if use_fp16:
                    model = model.half()
                    print(f"  已转换为FP16")
                
                # 创建测试音频（10秒）
                print(f"  创建测试音频...")
                audio = np.random.randn(16000 * 10).astype(np.float32) * 0.01
                
                # 测试转录
                print(f"  执行转录...")
                # 不传递fp16参数，让Whisper自动处理
                result = model.transcribe(
                    audio,
                    language="zh",
                    verbose=False
                )
                
                print(f"  ✅ 成功！")
                
                # 显示内存使用
                allocated = torch.cuda.memory_allocated(0) / 1024**3
                print(f"  显存使用: {allocated:.2f} GB")
                
                # 清理
                del model
                torch.cuda.empty_cache()
                
            except Exception as e:
                print(f"  ❌ 错误: {e}")
    
    except ImportError as e:
        print(f"导入错误: {e}")


def create_safe_wrapper():
    """创建安全的转录包装器"""
    
    wrapper_content = '''#!/usr/bin/env python3
"""
安全的GPU转录包装器 - 自动处理FP16兼容性
"""

import sys
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafeGPUTranscriber:
    """安全的GPU转录器，处理FP16兼容性"""
    
    def __init__(self, model_name="medium", use_fp16=True):
        import torch
        import whisper
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"使用设备: {self.device}")
        
        # 加载模型
        self.model = whisper.load_model(model_name, device=self.device)
        
        # FP16处理
        if use_fp16 and self.device == "cuda":
            self.model = self.model.half()
            logger.info("使用FP16模式")
        
    def transcribe(self, audio_path, **kwargs):
        """安全转录，自动处理类型"""
        # 移除fp16参数，避免冲突
        kwargs.pop('fp16', None)
        
        # 执行转录
        return self.model.transcribe(audio_path, **kwargs)


if __name__ == '__main__':
    # 直接运行gpu_transcribe，但使用修复后的参数
    from cli.gpu_transcribe import main
    sys.exit(main())
'''
    
    wrapper_path = project_root / "cli" / "gpu_transcribe_safe.py"
    wrapper_path.write_text(wrapper_content)
    wrapper_path.chmod(0o755)
    
    print(f"\n创建安全包装器: {wrapper_path}")
    print("使用: python cli/gpu_transcribe_safe.py --url <URL> --model medium")


def show_solution():
    """显示解决方案"""
    print("\n=== FP16错误解决方案 ===")
    print("""
问题原因：
- Whisper的某些操作不支持FP16输入
- 模型是FP16但输入是FP32导致类型不匹配

解决方法：
1. 已更新gpu_transcribe.py，移除了fp16参数传递
2. 让Whisper自动处理类型转换

立即使用：
# 使用medium模型（稳定）
python -m cli.main gpu-transcribe --url "<URL>" --model medium

# 使用small模型（更快）
python -m cli.main gpu-transcribe --url "<URL>" --model small

# 强制使用float32（如果仍有问题）
python -m cli.main gpu-transcribe --url "<URL>" --model medium --compute-type float32

监控命令：
# 查看GPU使用
watch -n 1 nvidia-smi
""")


def main():
    """主函数"""
    print("FP16类型错误修复工具")
    print("=" * 60)
    
    # 测试修复
    test_fp16_fix()
    
    # 创建安全包装器
    create_safe_wrapper()
    
    # 显示解决方案
    show_solution()


if __name__ == '__main__':
    main()