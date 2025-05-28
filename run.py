#!/usr/bin/env python3
"""
Bili2Text Web应用启动脚本
"""

import os
import sys
import argparse
import logging
from webapp.app import create_app

def setup_logging(debug=False):
    """设置日志"""
    level = logging.DEBUG if debug else logging.INFO
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('webapp/logs/app.log', encoding='utf-8')
        ]
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Bili2Text Web应用')
    parser.add_argument('--host', default='127.0.0.1', help='监听地址')
    parser.add_argument('--port', type=int, default=5000, help='监听端口')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    parser.add_argument('--production', action='store_true', help='生产模式')
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.debug)
    
    # 创建应用
    app = create_app()
    socketio = app.socketio
    
    if args.production:
        # 生产模式
        print(f"启动生产服务器 - {args.host}:{args.port}")
        socketio.run(
            app,
            host=args.host,
            port=args.port,
            debug=False,
            use_reloader=False
        )
    else:
        # 开发模式
        print(f"启动开发服务器 - {args.host}:{args.port}")
        socketio.run(
            app,
            host=args.host,
            port=args.port,
            debug=args.debug,
            use_reloader=args.debug
        )

if __name__ == '__main__':
    main() 