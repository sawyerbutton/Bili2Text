#!/usr/bin/env python3
"""
GPU优化脚本 - 解决large模型显存问题
===================================
"""

import os
import sys
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def optimize_large_model():
    """为large模型优化GPU设置"""
    print("=== Large模型GPU优化 ===")
    
    # 设置环境变量
    optimizations = {
        'PYTORCH_CUDA_ALLOC_CONF': 'expandable_segments:True,max_split_size_mb:512',
        'CUDA_LAUNCH_BLOCKING': '0',
        'TORCH_CUDA_ARCH_LIST': '8.6',  # RTX 4060
    }
    
    for key, value in optimizations.items():
        os.environ[key] = value
        print(f"设置 {key}={value}")
    
    print("\n测试优化后的显存使用...")
    
    try:
        import torch
        import whisper
        
        # 清理显存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"显存总量: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            
            # 测试不同配置
            configs = [
                ("large + FP16", "large", True),
                ("medium + FP16", "medium", True),
                ("large + FP32", "large", False),
            ]
            
            for desc, model_name, use_fp16 in configs:
                print(f"\n测试配置: {desc}")
                try:
                    torch.cuda.empty_cache()
                    
                    # 加载模型
                    model = whisper.load_model(model_name, device="cuda")
                    if use_fp16:
                        model = model.half()
                    
                    # 显示内存使用
                    allocated = torch.cuda.memory_allocated(0) / 1024**3
                    reserved = torch.cuda.memory_reserved(0) / 1024**3
                    print(f"✓ 成功加载！")
                    print(f"  已分配显存: {allocated:.2f} GB")
                    print(f"  保留显存: {reserved:.2f} GB")
                    
                    # 清理
                    del model
                    torch.cuda.empty_cache()
                    
                except Exception as e:
                    print(f"✗ 失败: {str(e)[:100]}...")
        
    except ImportError:
        print("请在GPU环境中运行此脚本")


def create_optimized_script():
    """创建优化的转录脚本"""
    script_content = '''#!/usr/bin/env python3
"""
优化的Large模型转录脚本
"""
import os
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True,max_split_size_mb:512'

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 使用优化设置运行转录
if __name__ == '__main__':
    from cli.gpu_transcribe import main
    # 强制使用medium模型以确保稳定性
    if '--model' in sys.argv:
        idx = sys.argv.index('--model')
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1] in ['large', 'large-v3']:
            print("注意: 8GB显存建议使用medium模型，自动切换...")
            sys.argv[idx + 1] = 'medium'
    else:
        sys.argv.extend(['--model', 'medium'])
    
    sys.exit(main())
'''
    
    script_path = project_root / "cli" / "gpu_transcribe_optimized.py"
    script_path.write_text(script_content)
    script_path.chmod(0o755)
    print(f"\n创建优化脚本: {script_path}")
    print("使用方法: python cli/gpu_transcribe_optimized.py --url <URL>")


def show_recommendations():
    """显示使用建议"""
    print("\n=== RTX 4060 (8GB) 使用建议 ===")
    print("""
1. 推荐模型选择：
   - 最稳定: medium + FP16 (需要3GB显存)
   - 平衡: small + FP16 (需要1.5GB显存) 
   - 最快: tiny + FP16 (需要1GB显存)

2. Large模型注意事项：
   - large模型需要6GB显存(FP16)或10GB(FP32)
   - 8GB显卡运行large模型可能不稳定
   - 建议使用medium模型代替

3. 优化技巧：
   - 关闭其他GPU程序（浏览器、游戏等）
   - 使用FP16精度（--compute-type float16）
   - 处理长音频时分段处理

4. 命令示例：
   # 使用medium模型（推荐）
   python -m cli.main gpu-transcribe --url "<URL>" --model medium
   
   # 使用优化脚本
   python cli/gpu_transcribe_optimized.py --url "<URL>"
   
   # 监控GPU使用
   watch -n 1 nvidia-smi
""")


def main():
    """主函数"""
    print("GPU优化工具 - 解决Large模型显存问题")
    print("=" * 50)
    
    # 运行优化测试
    optimize_large_model()
    
    # 创建优化脚本
    create_optimized_script()
    
    # 显示建议
    show_recommendations()


if __name__ == '__main__':
    main()