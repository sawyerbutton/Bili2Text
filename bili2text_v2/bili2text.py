#!/usr/bin/env python3
"""
Bili2Text - 主入口脚本
提供统一的命令行界面来访问所有功能
"""

import sys
import os
import argparse

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Bili2Text - 哔哩哔哩视频转录工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s setup                          # 一键安装和设置
  %(prog)s simple                         # 简单转录测试
  %(prog)s batch                          # 批量转录工作流
  %(prog)s infinity                       # InfinityAcademy工作流
  %(prog)s ref-info                       # 参考信息系列工作流
  %(prog)s model --list                   # 列出可用模型
  %(prog)s model --download medium        # 下载指定模型
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='项目安装和设置')
    setup_parser.add_argument('--model', help='下载指定的Whisper模型')
    setup_parser.add_argument('--proxy', help='代理URL')
    setup_parser.add_argument('--deps-only', action='store_true', help='仅安装依赖')
    
    # Simple command
    simple_parser = subparsers.add_parser('simple', help='简单转录测试')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='批量转录工作流')
    
    # InfinityAcademy command
    infinity_parser = subparsers.add_parser('infinity', help='InfinityAcademy工作流')
    infinity_parser.add_argument('--mode', choices=['full', 'download', 'transcribe'], 
                                default='full', help='运行模式')
    infinity_parser.add_argument('--model', default='medium', help='Whisper模型')
    infinity_parser.add_argument('--proxy', help='代理URL')
    
    # Reference info command
    ref_parser = subparsers.add_parser('ref-info', help='参考信息系列工作流')
    ref_parser.add_argument('--target', default='latest', help='目标视频')
    ref_parser.add_argument('--model', default='medium', help='Whisper模型')
    ref_parser.add_argument('--proxy', help='代理URL')
    
    # Model command
    model_parser = subparsers.add_parser('model', help='模型管理')
    model_parser.add_argument('--list', action='store_true', help='列出可用模型')
    model_parser.add_argument('--download', help='下载指定模型')
    model_parser.add_argument('--downloaded', action='store_true', help='显示已下载模型')
    model_parser.add_argument('--proxy', help='代理URL')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'setup':
            from tools.setup import SetupTool
            setup_tool = SetupTool()
            
            if args.deps_only:
                success = (
                    setup_tool.check_python_version() and
                    setup_tool.upgrade_pip() and
                    setup_tool.install_dependencies() and
                    setup_tool.setup_directories()
                )
            else:
                download_model = args.model or "base"
                success = setup_tool.run_full_setup(
                    download_model, bool(args.proxy), args.proxy or "http://127.0.0.1:7890"
                )
            
            if not success:
                sys.exit(1)
                
        elif args.command == 'simple':
            # 运行simple_transcribe.py
            from simple_transcribe import simple_transcribe
            success = simple_transcribe()
            if not success:
                sys.exit(1)
                
        elif args.command == 'batch':
            from workflows.batch_transcribe import BatchTranscribeWorkflow
            workflow = BatchTranscribeWorkflow()
            # 这里可以添加配置URL的逻辑
            video_urls = [
                "https://www.bilibili.com/video/BV1LCM3zwEH9/?spm_id_from=333.1391.0.0",
            ]
            results = workflow.run_full_workflow(video_urls)
            
        elif args.command == 'infinity':
            from workflows.infinity_workflow import InfinityAcademyWorkflow
            workflow = InfinityAcademyWorkflow(
                whisper_model=args.model,
                proxy_url=args.proxy
            )
            
            if args.mode == 'full':
                results = workflow.run_full_workflow()
            elif args.mode == 'download':
                results = workflow.run_download_only_workflow()
            elif args.mode == 'transcribe':
                results = workflow.run_transcribe_only_workflow()
                
        elif args.command == 'ref-info':
            from workflows.ref_info_workflow import RefInfoWorkflow
            workflow = RefInfoWorkflow(
                whisper_model=args.model,
                proxy_url=args.proxy
            )
            result = workflow.run_workflow(args.target)
            
        elif args.command == 'model':
            from tools.model_downloader import ModelDownloader
            downloader = ModelDownloader()
            
            if args.list:
                downloader.list_available_models()
            elif args.download:
                success = downloader.download_model(args.download, proxy_url=args.proxy)
                if not success:
                    sys.exit(1)
            elif args.downloaded:
                downloader.show_downloaded_models()
            else:
                downloader.list_available_models()
                print("\\n")
                downloader.show_downloaded_models()
                
    except KeyboardInterrupt:
        print("\\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()