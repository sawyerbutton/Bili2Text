"""
Bili2Text Web应用主入口
Flask + WebSocket 实现的视频转录Web服务
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import logging
from datetime import datetime
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webapp.core.config import Config
from webapp.core.database import db, init_db
from webapp.core.task_manager import TaskManager
from webapp.core.file_manager import FileManager
from webapp.core.system_monitor import SystemMonitor
from webapp.core.error_handler import ErrorHandler
from webapp.api.routes import api_bp
from webapp.api.websocket_handlers import register_websocket_handlers

def create_app(config_class=Config):
    """创建Flask应用实例"""
    app = Flask(__name__, 
                template_folder='static/templates',
                static_folder='static')
    
    # 加载配置
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    
    # 初始化错误处理器
    error_handler = ErrorHandler()
    error_handler.init_app(app)
    
    # 创建SocketIO实例
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # 注册蓝图
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 注册WebSocket处理器
    register_websocket_handlers(socketio)
    
    # 初始化数据库
    with app.app_context():
        init_db()
    
    # 初始化核心组件
    app.task_manager = TaskManager()
    app.file_manager = FileManager()
    app.system_monitor = SystemMonitor()
    
    # 配置日志
    setup_logging(app)
    
    # 注册路由
    register_routes(app)
    
    # 存储socketio实例供其他模块使用
    app.socketio = socketio
    
    return app

def setup_logging(app):
    """配置日志系统"""
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    # 配置文件日志处理器
    file_handler = logging.FileHandler(
        os.path.join(log_dir, 'bili2text_web.log'),
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 配置错误日志处理器
    error_handler = logging.FileHandler(
        os.path.join(log_dir, 'error.log'),
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # 配置控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # 添加处理器到应用日志器
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.setLevel(logging.INFO)
    
    app.logger.info('Bili2Text Web 应用启动')

def register_routes(app):
    """注册Web页面路由"""
    
    @app.route('/')
    def index():
        """首页"""
        return render_template('index.html')
    
    @app.route('/history')
    def history():
        """任务历史页面"""
        return render_template('history.html')
    
    @app.route('/system')
    def system():
        """系统状态页面"""
        return render_template('system.html')
    
    @app.route('/error-test')
    def error_test():
        """错误处理测试页面"""
        return render_template('error-test.html')
    
    @app.errorhandler(404)
    def not_found(error):
        """404错误处理"""
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': '页面不存在'
            }
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500错误处理"""
        app.logger.error(f'服务器内部错误: {error}')
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '服务器内部错误'
            }
        }), 500

# 创建应用实例
app = create_app()
socketio = app.socketio

if __name__ == '__main__':
    # 开发模式运行
    socketio.run(app, 
                host='0.0.0.0', 
                port=8000, 
                debug=True,
                allow_unsafe_werkzeug=True) 