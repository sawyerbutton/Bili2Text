"""
数据库模型定义
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import uuid

db = SQLAlchemy()

class Task(db.Model):
    """任务模型"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # 基本信息
    url = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(500))
    model_name = db.Column(db.String(50), nullable=False)
    
    # 状态信息
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    progress = db.Column(db.Float, default=0.0)
    current_stage = db.Column(db.String(100))
    error_message = db.Column(db.Text)
    
    # 时间信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # 文件信息
    file_size = db.Column(db.BigInteger)
    duration = db.Column(db.Float)
    result_file_path = db.Column(db.String(500))
    audio_file_path = db.Column(db.String(500))
    
    # 配置选项（JSON格式存储）
    options = db.Column(db.Text)
    
    # 视频信息（JSON格式存储）
    video_info = db.Column(db.Text)
    
    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)
        if not self.task_id:
            self.task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'url': self.url,
            'title': self.title,
            'model_name': self.model_name,
            'status': self.status,
            'progress': self.progress,
            'current_stage': self.current_stage,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'file_size': self.file_size,
            'duration': self.duration,
            'result_file_path': self.result_file_path,
            'audio_file_path': self.audio_file_path,
            'options': json.loads(self.options) if self.options else {},
            'video_info': json.loads(self.video_info) if self.video_info else {}
        }
    
    def set_options(self, options_dict):
        """设置选项"""
        self.options = json.dumps(options_dict) if options_dict else None
    
    def get_options(self):
        """获取选项"""
        return json.loads(self.options) if self.options else {}
    
    def set_video_info(self, video_info_dict):
        """设置视频信息"""
        self.video_info = json.dumps(video_info_dict) if video_info_dict else None
    
    def get_video_info(self):
        """获取视频信息"""
        return json.loads(self.video_info) if self.video_info else {}
    
    def update_status(self, status, progress=None, stage=None, error=None):
        """更新任务状态"""
        self.status = status
        if progress is not None:
            self.progress = progress
        if stage is not None:
            self.current_stage = stage
        if error is not None:
            self.error_message = error
        
        # 更新时间戳
        if status == 'transcribing' and not self.started_at:
            self.started_at = datetime.utcnow()
        elif status in ['completed', 'failed', 'cancelled'] and not self.completed_at:
            self.completed_at = datetime.utcnow()
        
        db.session.commit()

class SystemStatus(db.Model):
    """系统状态模型"""
    __tablename__ = 'system_status'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 系统资源
    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Float)
    disk_usage = db.Column(db.Float)
    gpu_available = db.Column(db.Boolean, default=False)
    gpu_memory_usage = db.Column(db.Float)
    
    # 任务统计
    active_tasks = db.Column(db.Integer, default=0)
    pending_tasks = db.Column(db.Integer, default=0)
    completed_tasks = db.Column(db.Integer, default=0)
    failed_tasks = db.Column(db.Integer, default=0)
    
    # 系统信息
    uptime = db.Column(db.Integer)  # 运行时间（秒）
    version = db.Column(db.String(20))
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'disk_usage': self.disk_usage,
            'gpu_available': self.gpu_available,
            'gpu_memory_usage': self.gpu_memory_usage,
            'active_tasks': self.active_tasks,
            'pending_tasks': self.pending_tasks,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'uptime': self.uptime,
            'version': self.version
        }

class TaskStatistics(db.Model):
    """任务统计模型"""
    __tablename__ = 'task_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date, index=True)
    
    # 任务统计
    tasks_created = db.Column(db.Integer, default=0)
    tasks_completed = db.Column(db.Integer, default=0)
    tasks_failed = db.Column(db.Integer, default=0)
    
    # 处理统计
    total_processing_time = db.Column(db.Integer, default=0)  # 秒
    total_audio_duration = db.Column(db.Integer, default=0)  # 秒
    total_file_size = db.Column(db.BigInteger, default=0)  # 字节
    
    # 模型使用统计（JSON格式）
    model_usage = db.Column(db.Text)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'tasks_created': self.tasks_created,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'total_processing_time': self.total_processing_time,
            'total_audio_duration': self.total_audio_duration,
            'total_file_size': self.total_file_size,
            'model_usage': json.loads(self.model_usage) if self.model_usage else {},
            'average_processing_speed': (
                self.total_audio_duration / self.total_processing_time 
                if self.total_processing_time > 0 else 0
            )
        }
    
    def set_model_usage(self, usage_dict):
        """设置模型使用统计"""
        self.model_usage = json.dumps(usage_dict) if usage_dict else None
    
    def get_model_usage(self):
        """获取模型使用统计"""
        return json.loads(self.model_usage) if self.model_usage else {}

def init_db():
    """初始化数据库"""
    db.create_all()
    
    # 创建默认的系统状态记录
    if not SystemStatus.query.first():
        status = SystemStatus(
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0,
            version='2.0.0'
        )
        db.session.add(status)
        db.session.commit()

def get_task_by_id(task_id):
    """根据任务ID获取任务"""
    return Task.query.filter_by(task_id=task_id).first()

def get_tasks_by_status(status, limit=None):
    """根据状态获取任务列表"""
    query = Task.query.filter_by(status=status).order_by(Task.created_at.desc())
    if limit:
        query = query.limit(limit)
    return query.all()

def get_recent_tasks(limit=10):
    """获取最近的任务"""
    return Task.query.order_by(Task.created_at.desc()).limit(limit).all()

def get_task_statistics(date=None):
    """获取任务统计"""
    if date is None:
        date = datetime.utcnow().date()
    
    stats = TaskStatistics.query.filter_by(date=date).first()
    if not stats:
        stats = TaskStatistics(date=date)
        db.session.add(stats)
        db.session.commit()
    
    return stats

def update_task_statistics(task):
    """更新任务统计"""
    stats = get_task_statistics()
    
    if task.status == 'completed':
        stats.tasks_completed += 1
        if task.duration:
            stats.total_audio_duration += int(task.duration)
        if task.file_size:
            stats.total_file_size += task.file_size
        
        # 更新处理时间
        if task.started_at and task.completed_at:
            processing_time = (task.completed_at - task.started_at).total_seconds()
            stats.total_processing_time += int(processing_time)
        
        # 更新模型使用统计
        model_usage = stats.get_model_usage()
        model_usage[task.model_name] = model_usage.get(task.model_name, 0) + 1
        stats.set_model_usage(model_usage)
    
    elif task.status == 'failed':
        stats.tasks_failed += 1
    
    db.session.commit()

def cleanup_old_records(days=30):
    """清理旧记录"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # 清理旧的系统状态记录
    SystemStatus.query.filter(SystemStatus.timestamp < cutoff_date).delete()
    
    # 清理旧的任务统计记录
    TaskStatistics.query.filter(TaskStatistics.date < cutoff_date.date()).delete()
    
    db.session.commit() 