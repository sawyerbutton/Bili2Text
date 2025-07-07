#!/usr/bin/env python3
"""
Bili2Text CLI 工具统一入口
提供视频下载、音频转录等命令行功能
"""

import argparse
import sys
from pathlib import Path

# 初始化项目路径管理
from src.utils import setup_project_paths
setup_project_paths()

def main():
    """CLI主入口函数"""
    parser = argparse.ArgumentParser(
        prog='bili2text',
        description='B站视频转录工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 下载音频并转录
  bili2text audio --url "https://www.bilibili.com/video/BV1234567890"
  
  # 下载视频文件
  bili2text video --url "https://www.bilibili.com/video/BV1234567890"
  
  # 获取动态推荐视频
  bili2text dynamics --user "UP主用户名"
  
  # 批量处理
  bili2text batch --input-dir ./videos --output-dir ./results
  
  # 转录本地视频文件
  bili2text transcribe --input-dir ./storage/video --output-dir ./storage/results/result
        """
    )
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 音频下载和转录命令
    audio_parser = subparsers.add_parser('audio', help='下载音频并转录')
    audio_parser.add_argument('--url', required=True, help='B站视频URL')
    audio_parser.add_argument('--model', default='medium', 
                             choices=['tiny', 'base', 'medium', 'large-v3'],
                             help='Whisper模型选择')
    audio_parser.add_argument('--output-dir', default='./storage/results',
                             help='输出目录')
    
    # 视频下载命令
    video_parser = subparsers.add_parser('video', help='下载视频文件')
    video_parser.add_argument('--url', required=True, help='B站视频URL')
    video_parser.add_argument('--output-dir', default='./storage/video',
                             help='输出目录')
    
    # 动态获取命令
    dynamics_parser = subparsers.add_parser('dynamics', help='获取动态推荐视频')
    dynamics_parser.add_argument('--user', required=True, help='UP主用户名')
    dynamics_parser.add_argument('--count', type=int, default=10, help='获取数量')
    
    # 批量处理命令
    batch_parser = subparsers.add_parser('batch', help='批量处理文件')
    batch_parser.add_argument('--input-dir', required=True, help='输入目录')
    batch_parser.add_argument('--output-dir', required=True, help='输出目录')
    batch_parser.add_argument('--type', choices=['audio', 'video'], 
                             default='audio', help='处理类型')
    
    # 转录本地视频文件命令
    transcribe_parser = subparsers.add_parser('transcribe', help='转录本地视频文件')
    transcribe_parser.add_argument('--input-dir', 
                                  default='./storage/video',
                                  help='视频文件输入目录')
    transcribe_parser.add_argument('--output-dir',
                                  default='./storage/results/result',
                                  help='转录结果输出目录')
    transcribe_parser.add_argument('--model', default='medium',
                                  choices=['tiny', 'base', 'medium', 'large-v3'],
                                  help='Whisper模型选择')
    transcribe_parser.add_argument('--force-cpu', action='store_true',
                                  help='强制使用CPU (即使有GPU可用)')
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 根据命令执行相应功能
    try:
        if args.command == 'audio':
            from cli.download_audio import main as audio_main
            audio_main(args)
        elif args.command == 'video':
            from cli.download_video import main as video_main
            video_main(args)
        elif args.command == 'dynamics':
            from cli.get_dynamics import main as dynamics_main
            dynamics_main(args)
        elif args.command == 'batch':
            from cli.batch_processor import main as batch_main
            batch_main(args)
        elif args.command == 'transcribe':
            from cli.transcribe_videos import main as transcribe_main
            transcribe_main(args)
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"执行错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 