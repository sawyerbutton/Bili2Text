#!/usr/bin/env python3
"""
简化版转录脚本
专门处理网络问题，提供多种解决方案
"""

import os
import sys

def try_transcribe_with_alternatives():
    """尝试多种方式进行转录"""
    print("=== 简化版转录工具 ===")
    
    # 检查音频文件
    audio_folder = "./audio"
    if not os.path.exists(audio_folder):
        print("音频文件夹不存在")
        return
    
    audio_files = [f for f in os.listdir(audio_folder) if f.endswith('.aac')]
    if not audio_files:
        print("没有找到音频文件")
        return
    
    print(f"找到 {len(audio_files)} 个音频文件")
    
    # 方案1: 使用本地已下载的模型
    try:
        print("\n=== 方案1: 尝试使用本地模型 ===")
        import whisper
        import torch
        
        # 检查本地模型
        cache_dir = "./.cache/whisper"
        if os.path.exists(cache_dir):
            model_files = [f for f in os.listdir(cache_dir) if f.endswith('.pt')]
            print(f"找到本地模型: {model_files}")
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"使用设备: {device}")
        
        # 尝试加载最小的模型
        model = whisper.load_model("tiny", device=device, download_root=cache_dir)
        print("tiny 模型加载成功！")
        
        # 测试第一个文件
        test_file = audio_files[0]
        audio_path = os.path.join(audio_folder, test_file)
        print(f"测试转录: {test_file}")
        
        result = model.transcribe(
            audio_path,
            verbose=False,
            initial_prompt='简体中文,加上标点'
        )
        
        print("转录成功！结果预览:")
        print("-" * 50)
        text = result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"]
        print(text)
        print("-" * 50)
        return True
        
    except Exception as e:
        print(f"方案1失败: {e}")
    
    # 方案2: 提供手动解决方案
    print("\n=== 方案2: 手动解决方案 ===")
    print("Whisper模型下载失败，请尝试以下解决方案：")
    print()
    print("1. 使用代理下载模型：")
    print("   python download_whisper_model.py")
    print()
    print("2. 手动下载模型文件：")
    print("   访问 https://github.com/openai/whisper 获取模型链接")
    print("   下载后放到 ./.cache/whisper/ 目录")
    print()
    print("3. 使用在线转录服务：")
    print("   - OpenAI API")
    print("   - Google Speech-to-Text")
    print("   - Azure Speech Services")
    print()
    print("4. 当前音频文件列表：")
    for i, file in enumerate(audio_files[:5], 1):
        print(f"   {i}. {file}")
    if len(audio_files) > 5:
        print(f"   ... 还有 {len(audio_files)-5} 个文件")
    
    return False

if __name__ == "__main__":
    try_transcribe_with_alternatives()
