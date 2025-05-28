"""
应用配置文件
"""

import os
from datetime import timedelta

class Config:
    """基础配置类"""
    
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bili2text-web-secret-key-2024'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bili2text.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件存储配置
    STORAGE_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'storage')
    AUDIO_STORAGE_PATH = os.path.join(STORAGE_ROOT, 'audio')
    RESULT_STORAGE_PATH = os.path.join(STORAGE_ROOT, 'results')
    TEMP_STORAGE_PATH = os.path.join(STORAGE_ROOT, 'temp')
    
    # 确保存储目录存在
    for path in [AUDIO_STORAGE_PATH, RESULT_STORAGE_PATH, TEMP_STORAGE_PATH]:
        os.makedirs(path, exist_ok=True)
    
    # Whisper模型配置
    WHISPER_MODELS = {
        'tiny': {
            'name': 'tiny',
            'size': '39MB',
            'speed': 'very_fast',
            'accuracy': 'low',
            'memory_required': '1GB',
            'recommended_for': '快速测试、实时转录'
        },
        'base': {
            'name': 'base',
            'size': '142MB',
            'speed': 'fast',
            'accuracy': 'medium',
            'memory_required': '2GB',
            'recommended_for': '日常使用'
        },
        'medium': {
            'name': 'medium',
            'size': '769MB',
            'speed': 'medium',
            'accuracy': 'high',
            'memory_required': '5GB',
            'recommended_for': '推荐使用，质量优先',
            'default': True
        },
        'large-v3': {
            'name': 'large-v3',
            'size': '1550MB',
            'speed': 'slow',
            'accuracy': 'very_high',
            'memory_required': '10GB',
            'recommended_for': '最高质量转录'
        }
    }
    
    # 任务配置
    MAX_CONCURRENT_TASKS = int(os.environ.get('MAX_CONCURRENT_TASKS', 3))
    TASK_TIMEOUT = int(os.environ.get('TASK_TIMEOUT', 3600))  # 1小时
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 1024 * 1024 * 1024))  # 1GB
    
    # 代理配置
    USE_PROXY = os.environ.get('USE_PROXY', 'false').lower() == 'true'
    PROXY_URL = os.environ.get('PROXY_URL', '')
    
    # 支持的输出格式
    SUPPORTED_OUTPUT_FORMATS = ['txt', 'md', 'json']
    
    # 支持的语言
    SUPPORTED_LANGUAGES = {
        'auto': '自动检测',
        'zh': '中文',
        'en': '英文',
        'ja': '日文',
        'ko': '韩文',
        'fr': '法文',
        'de': '德文',
        'es': '西班牙文',
        'ru': '俄文'
    }
    
    # WebSocket配置
    WEBSOCKET_HEARTBEAT_INTERVAL = 30  # 秒
    WEBSOCKET_TIMEOUT = 60  # 秒
    
    # 系统监控配置
    SYSTEM_MONITOR_INTERVAL = 5  # 秒
    PERFORMANCE_HISTORY_LIMIT = 100  # 保留最近100个数据点
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_MAX_SIZE = int(os.environ.get('LOG_MAX_SIZE', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # 安全配置
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # 缓存配置
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))  # 5分钟

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 生产环境使用更安全的密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    
    # 生产环境数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/bili2text_web'

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    
    # 测试数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # 测试存储路径
    STORAGE_ROOT = '/tmp/bili2text_test'

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 