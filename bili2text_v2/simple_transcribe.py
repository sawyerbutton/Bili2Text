#!/usr/bin/env python3
"""
简化版转录脚本
使用新的模块化架构，提供简单的转录功能
"""

import sys
import os

# 添加core模块到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from core.whisper_transcriber import WhisperTranscriber
    from core.file_manager import FileManager
except ImportError:
    print("请先运行: python tools/setup.py 安装依赖")
    sys.exit(1)


def simple_transcribe():
    """简单转录功能"""
    print("=== 简化版转录工具 ===")
    
    # 初始化组件
    file_manager = FileManager(".")
    file_manager.setup_directories()
    
    # 获取音频文件
    audio_files = file_manager.get_audio_files()
    
    if not audio_files:
        print("没有找到音频文件")
        print("请将音频文件放到 ./audio 目录中")
        print("\n支持的格式: .mp3, .wav, .m4a, .aac, .flac, .ogg, .wma")
        return False
    
    print(f"找到 {len(audio_files)} 个音频文件:")
    for i, file in enumerate(audio_files[:5], 1):
        print(f"  {i}. {file}")
    if len(audio_files) > 5:
        print(f"  ... 还有 {len(audio_files)-5} 个文件")
    
    # 尝试转录第一个文件
    try:
        print("\n开始转录测试...")
        transcriber = WhisperTranscriber(model_name="tiny")  # 使用最小模型测试
        
        test_file = audio_files[0]
        audio_path = os.path.join(file_manager.audio_dir, test_file)
        
        print(f"测试文件: {test_file}")
        result = transcriber.transcribe_audio(audio_path)
        
        print("\n转录成功！结果预览:")
        print("-" * 50)
        preview_text = result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"]
        print(preview_text)
        print("-" * 50)
        
        # 保存结果
        result_file = os.path.join(file_manager.result_dir, f"{test_file}.txt")
        with open(result_file, "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        print(f"完整结果已保存到: {result_file}")
        return True
        
    except Exception as e:
        print(f"\n转录失败: {e}")
        print("\n可能的解决方案:")
        print("1. 运行 python tools/setup.py --model tiny 下载模型")
        print("2. 运行 python tools/model_downloader.py --download tiny")
        print("3. 检查音频文件是否损坏")
        print("4. 使用 python workflows/batch_transcribe.py 进行批量处理")
        return False


if __name__ == "__main__":
    try:
        success = simple_transcribe()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n运行失败: {e}")
        sys.exit(1)
