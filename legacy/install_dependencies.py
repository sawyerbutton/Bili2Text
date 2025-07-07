#!/usr/bin/env python3
"""
InfinityAcademy脚本依赖安装脚本
用于快速安装所需的Python依赖库
"""

import subprocess
import sys

def run_command(command):
    """运行命令并显示输出"""
    print(f"运行命令: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stdout:
            print("标准输出:", e.stdout)
        if e.stderr:
            print("错误输出:", e.stderr)
        return False

def main():
    """主函数"""
    print("=== InfinityAcademy脚本依赖安装 ===")
    print("开始安装依赖库...")
    
    # 升级pip
    print("\n1. 升级pip...")
    run_command("pip install --upgrade pip")
    
    # 安装核心依赖
    print("\n2. 安装核心依赖...")
    run_command('pip install "pyyaml>=6.0"')
    run_command("pip install bilibili-api-python")
    
    # 安装异步HTTP库
    print("\n3. 安装异步HTTP库...")
    run_command("pip install aiohttp")
    
    # 安装音频处理依赖
    print("\n4. 安装音频处理依赖...")
    run_command("pip install bilix>=0.18.5")
    
    # 安装转录依赖（如果需要）
    print("\n5. 安装音频转录依赖...")
    run_command("pip install openai-whisper torch torchaudio")
    
    print("\n=== 依赖安装完成 ===")
    print("现在您可以运行以下命令：")
    print("1. 下载音频: python download_infinityacademy_audio.py")
    print("2. 转录音频: python transcribe_infinityacademy_audio.py")
    print("")
    print("注意：首次运行可能需要下载Whisper模型，请耐心等待。")

if __name__ == "__main__":
    main() 