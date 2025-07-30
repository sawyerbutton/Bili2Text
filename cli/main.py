#!/usr/bin/env python3
"""
Bili2Text CLI 工具统一入口
提供视频下载、音频转录等命令行功能
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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
  
  # GPU加速转录（新功能）
  bili2text gpu-transcribe --input video.mp4 --model large --device cuda
  bili2text gpu-transcribe --url "https://www.bilibili.com/video/BV1234567890" --model large
  
  # 配置GPU环境
  bili2text setup-gpu
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
    
    # GPU转录命令（新增）
    gpu_parser = subparsers.add_parser('gpu-transcribe', help='GPU加速转录（高性能）')
    # 支持URL或本地文件输入
    gpu_parser.add_argument('--url', '-u', help='B站视频URL')
    gpu_parser.add_argument('--input', '-i', help='本地文件或目录')
    gpu_parser.add_argument('--output', '-o', default='./storage/results',
                           help='输出目录')
    gpu_parser.add_argument('--model', '-m', default='medium',
                           choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v3'],
                           help='Whisper模型选择')
    gpu_parser.add_argument('--device', '-d', default='auto',
                           choices=['auto', 'cuda', 'cpu'],
                           help='计算设备选择')
    gpu_parser.add_argument('--compute-type', default='float16',
                           choices=['float16', 'float32'],
                           help='计算精度（仅GPU有效）')
    gpu_parser.add_argument('--batch', action='store_true',
                           help='批量处理模式')
    
    # GPU设置命令（新增）
    setup_parser = subparsers.add_parser('setup-gpu', help='配置GPU环境')
    setup_parser.add_argument('--check-only', action='store_true',
                            help='仅检查环境，不安装')
    
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
            try:
                from cli.get_dynamics import main as dynamics_main
            except ImportError:
                # 如果无法导入，使用演示版本
                from cli.get_dynamics_demo import main as dynamics_main
            dynamics_main(args)
        elif args.command == 'batch':
            from cli.batch_processor import main as batch_main
            batch_main(args)
        elif args.command == 'transcribe':
            from cli.transcribe_videos import main as transcribe_main
            transcribe_main(args)
        elif args.command == 'gpu-transcribe':
            from cli.gpu_transcribe import main as gpu_main
            # 验证输入参数
            if not args.url and not args.input:
                print("错误: 必须提供 --url 或 --input 参数之一")
                sys.exit(1)
            if args.url and args.input:
                print("错误: --url 和 --input 参数不能同时使用")
                sys.exit(1)
            # 传递参数给gpu_main
            sys.argv = ['gpu_transcribe.py']
            if args.url:
                sys.argv.extend(['--url', args.url])
            else:
                sys.argv.extend(['--input', args.input])
            sys.argv.extend(['--output', args.output])
            sys.argv.extend(['--model', args.model])
            sys.argv.extend(['--device', args.device])
            sys.argv.extend(['--compute-type', args.compute_type])
            if args.batch:
                sys.argv.append('--batch')
            gpu_main()
        elif args.command == 'setup-gpu':
            from cli.setup_gpu import main as setup_main
            setup_main()
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"执行错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 