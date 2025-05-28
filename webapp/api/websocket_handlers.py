"""
WebSocket事件处理器
"""

from flask_socketio import emit, join_room, leave_room, disconnect
from flask import current_app, request
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def register_websocket_handlers(socketio):
    """注册WebSocket事件处理器"""
    
    @socketio.on('connect')
    def handle_connect():
        """客户端连接事件"""
        logger.info(f'客户端连接: {request.sid}')
        emit('connected', {
            'message': '连接成功',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """客户端断开连接事件"""
        logger.info(f'客户端断开连接: {request.sid}')
    
    @socketio.on('ping')
    def handle_ping(data):
        """心跳检测"""
        emit('pong', {
            'timestamp': datetime.utcnow().isoformat(),
            'client_timestamp': data.get('timestamp') if data else None
        })
    
    @socketio.on('join_task')
    def handle_join_task(data):
        """加入任务房间"""
        task_id = data.get('task_id')
        if task_id:
            room = f'task_{task_id}'
            join_room(room)
            logger.info(f'客户端 {request.sid} 加入任务房间: {room}')
            emit('joined_task', {
                'task_id': task_id,
                'message': f'已加入任务 {task_id} 的监听'
            })
        else:
            emit('error', {'message': '无效的任务ID'})
    
    @socketio.on('leave_task')
    def handle_leave_task(data):
        """离开任务房间"""
        task_id = data.get('task_id')
        if task_id:
            room = f'task_{task_id}'
            leave_room(room)
            logger.info(f'客户端 {request.sid} 离开任务房间: {room}')
            emit('left_task', {
                'task_id': task_id,
                'message': f'已离开任务 {task_id} 的监听'
            })
    
    @socketio.on('join_system')
    def handle_join_system():
        """加入系统监控房间"""
        room = 'system_monitor'
        join_room(room)
        logger.info(f'客户端 {request.sid} 加入系统监控房间')
        emit('joined_system', {
            'message': '已加入系统监控'
        })
    
    @socketio.on('leave_system')
    def handle_leave_system():
        """离开系统监控房间"""
        room = 'system_monitor'
        leave_room(room)
        logger.info(f'客户端 {request.sid} 离开系统监控房间')
        emit('left_system', {
            'message': '已离开系统监控'
        })
    
    @socketio.on('get_task_status')
    def handle_get_task_status(data):
        """获取任务状态"""
        task_id = data.get('task_id')
        if task_id:
            from webapp.core.database import get_task_by_id
            task = get_task_by_id(task_id)
            if task:
                emit('task_status', {
                    'type': 'task_status',
                    'task_id': task_id,
                    'status': task.status,
                    'progress': task.progress,
                    'current_stage': task.current_stage,
                    'timestamp': datetime.utcnow().isoformat()
                })
            else:
                emit('error', {'message': '任务不存在'})
        else:
            emit('error', {'message': '无效的任务ID'})
    
    @socketio.on('get_system_status')
    def handle_get_system_status():
        """获取系统状态"""
        try:
            status = current_app.system_monitor.get_current_status()
            emit('system_status', {
                'type': 'system_status',
                'data': status,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f'获取系统状态失败: {e}')
            emit('error', {'message': '获取系统状态失败'})

def broadcast_task_update(socketio, task_id, status, progress=None, stage=None, error=None):
    """广播任务状态更新"""
    room = f'task_{task_id}'
    data = {
        'type': 'task_update',
        'task_id': task_id,
        'status': status,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if progress is not None:
        data['progress'] = progress
    if stage is not None:
        data['current_stage'] = stage
    if error is not None:
        data['error_message'] = error
    
    logger.info(f'广播任务更新: {task_id} - {status}')
    socketio.emit('task_update', data, room=room)

def broadcast_system_update(socketio, system_data):
    """广播系统状态更新"""
    room = 'system_monitor'
    data = {
        'type': 'system_update',
        'data': system_data,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    socketio.emit('system_update', data, room=room)

def notify_task_completion(socketio, task_id, success=True, message=None):
    """通知任务完成"""
    room = f'task_{task_id}'
    data = {
        'type': 'task_notification',
        'task_id': task_id,
        'success': success,
        'message': message or ('任务完成' if success else '任务失败'),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    socketio.emit('task_notification', data, room=room)

def notify_system_alert(socketio, alert_type, message, level='warning'):
    """发送系统警告"""
    room = 'system_monitor'
    data = {
        'type': 'system_alert',
        'alert_type': alert_type,
        'message': message,
        'level': level,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    socketio.emit('system_alert', data, room=room) 