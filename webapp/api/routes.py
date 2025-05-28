"""
API路由定义
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from datetime import datetime, timedelta
import os
import re

from webapp.core.database import (
    db, Task, SystemStatus, TaskStatistics,
    get_task_by_id, get_tasks_by_status, get_recent_tasks,
    get_task_statistics, update_task_statistics
)
from webapp.core.error_handler import (
    BusinessException, ValidationException, NotFoundException, SystemOverloadException,
    ErrorCode, handle_database_error, handle_file_operation_error,
    validate_request_data, rate_limit_error_handler
)

api_bp = Blueprint('api', __name__)

def success_response(data=None, message="操作成功"):
    """成功响应格式"""
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    if data is not None:
        response['data'] = data
    return jsonify(response)

def validate_bilibili_url(url):
    """验证哔哩哔哩URL"""
    patterns = [
        r'^https?://www\.bilibili\.com/video/BV[\w]+',
        r'^https?://b23\.tv/[\w]+',
        r'^BV[\w]+$'
    ]
    return any(re.match(pattern, url) for pattern in patterns)

# 任务管理API
@api_bp.route('/tasks/', methods=['POST'])
@validate_request_data(required_fields=['url'], optional_fields={'model_name': str, 'options': dict})
@handle_database_error
@rate_limit_error_handler
def create_task():
    """创建转录任务"""
    data = request.get_json()
    
    # 验证URL
    url = data.get('url', '').strip()
    if not url:
        raise ValidationException('视频URL不能为空', field='url')
    
    if not validate_bilibili_url(url):
        raise BusinessException(
            ErrorCode.INVALID_URL,
            '请输入有效的哔哩哔哩视频链接',
            {'url': url, 'supported_formats': [
                'https://www.bilibili.com/video/BV...',
                'https://b23.tv/...',
                'BV...'
            ]}
        )
    
    # 验证模型
    model_name = data.get('model_name', 'medium')
    if model_name not in current_app.config['WHISPER_MODELS']:
        raise BusinessException(
            ErrorCode.INVALID_MODEL,
            f'不支持的模型: {model_name}',
            {
                'provided_model': model_name,
                'supported_models': list(current_app.config['WHISPER_MODELS'].keys())
            }
        )
    
    # 检查系统负载
    active_tasks = Task.query.filter(
        Task.status.in_(['pending', 'downloading', 'transcribing'])
    ).count()
    
    if active_tasks >= current_app.config['MAX_CONCURRENT_TASKS']:
        raise SystemOverloadException(
            f'当前有{active_tasks}个任务正在处理，已达到最大并发数{current_app.config["MAX_CONCURRENT_TASKS"]}'
        )
    
    # 创建任务
    options = data.get('options', {})
    task = Task(url=url, model_name=model_name)
    task.set_options(options)
    
    db.session.add(task)
    db.session.commit()
    
    # 提交任务到任务管理器
    current_app.task_manager.submit_task(task)
    
    # 更新统计
    stats = get_task_statistics()
    stats.tasks_created += 1
    db.session.commit()
    
    current_app.logger.info(f'任务创建成功: {task.task_id}', extra={
        'task_id': task.task_id,
        'url': url,
        'model': model_name
    })
    
    return success_response(task.to_dict(), '任务创建成功')

@api_bp.route('/tasks/', methods=['GET'])
@handle_database_error
def get_tasks():
    """获取任务列表"""
    # 获取和验证查询参数
    try:
        page = max(1, int(request.args.get('page', 1)))
        limit = min(max(1, int(request.args.get('limit', 20))), 100)
    except ValueError:
        raise ValidationException('页码和限制数必须为正整数')
    
    status = request.args.get('status', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    search = request.args.get('search', '')
    
    # 构建查询
    query = Task.query
    
    # 状态筛选
    if status:
        valid_statuses = ['pending', 'downloading', 'transcribing', 'completed', 'failed', 'cancelled']
        if status not in valid_statuses:
            raise ValidationException(f'无效的状态值: {status}', details={
                'provided_status': status,
                'valid_statuses': valid_statuses
            })
        query = query.filter(Task.status == status)
    
    # 日期筛选
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Task.created_at >= date_from_obj)
        except ValueError:
            raise ValidationException('开始日期格式错误，请使用YYYY-MM-DD格式', field='date_from')
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Task.created_at < date_to_obj)
        except ValueError:
            raise ValidationException('结束日期格式错误，请使用YYYY-MM-DD格式', field='date_to')
    
    # 搜索筛选
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                Task.title.like(search_term),
                Task.url.like(search_term),
                Task.task_id.like(search_term)
            )
        )
    
    # 排序和分页
    query = query.order_by(Task.created_at.desc())
    total = query.count()
    tasks = query.offset((page - 1) * limit).limit(limit).all()
    
    return success_response({
        'tasks': [task.to_dict() for task in tasks],
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit
    })

@api_bp.route('/tasks/<task_id>', methods=['GET'])
@handle_database_error
def get_task(task_id):
    """获取任务详情"""
    task = get_task_by_id(task_id)
    if not task:
        raise NotFoundException('任务', task_id)
    
    return success_response(task.to_dict())

@api_bp.route('/tasks/<task_id>/cancel', methods=['POST'])
@handle_database_error
def cancel_task(task_id):
    """取消任务"""
    task = get_task_by_id(task_id)
    if not task:
        raise NotFoundException('任务', task_id)
    
    if task.status not in ['pending', 'downloading', 'transcribing']:
        raise BusinessException(
            ErrorCode.VALIDATION_ERROR,
            f'任务状态为"{task.status}"，无法取消',
            {
                'current_status': task.status,
                'cancellable_statuses': ['pending', 'downloading', 'transcribing']
            },
            409
        )
    
    # 取消任务
    current_app.task_manager.cancel_task(task_id)
    task.update_status('cancelled', stage='任务已取消')
    
    current_app.logger.info(f'任务已取消: {task_id}')
    
    return success_response(task.to_dict(), '任务已取消')

@api_bp.route('/tasks/<task_id>', methods=['DELETE'])
@handle_database_error
@handle_file_operation_error
def delete_task(task_id):
    """删除任务"""
    task = get_task_by_id(task_id)
    if not task:
        raise NotFoundException('任务', task_id)
    
    # 如果任务正在运行，先取消
    if task.status in ['pending', 'downloading', 'transcribing']:
        current_app.task_manager.cancel_task(task_id)
    
    # 删除相关文件
    deleted_files = current_app.file_manager.delete_task_files(task_id)
    
    # 删除数据库记录
    db.session.delete(task)
    db.session.commit()
    
    current_app.logger.info(f'任务已删除: {task_id}', extra={
        'deleted_files_count': len(deleted_files)
    })
    
    return success_response({
        'deleted_files': deleted_files
    }, '任务删除成功')

# 文件操作API
@api_bp.route('/files/<task_id>/result', methods=['GET'])
@handle_file_operation_error
def download_result(task_id):
    """下载转录结果"""
    task = get_task_by_id(task_id)
    if not task:
        raise NotFoundException('任务', task_id)
    
    if not task.result_file_path:
        raise BusinessException(
            ErrorCode.FILE_NOT_FOUND,
            '转录结果尚未生成',
            {'task_status': task.status}
        )
    
    if not os.path.exists(task.result_file_path):
        raise NotFoundException('结果文件')
    
    filename = f"{task.title or task.task_id}_transcript.txt"
    return send_file(
        task.result_file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='text/plain'
    )

@api_bp.route('/files/<task_id>/audio', methods=['GET'])
@handle_file_operation_error
def download_audio(task_id):
    """下载音频文件"""
    task = get_task_by_id(task_id)
    if not task:
        raise NotFoundException('任务', task_id)
    
    if not task.audio_file_path:
        raise BusinessException(
            ErrorCode.FILE_NOT_FOUND,
            '音频文件不可用',
            {'reason': '音频文件未保留或任务未完成'}
        )
    
    if not os.path.exists(task.audio_file_path):
        raise NotFoundException('音频文件')
    
    filename = f"{task.title or task.task_id}_audio.m4a"
    return send_file(
        task.audio_file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='audio/mp4'
    )

@api_bp.route('/files/<task_id>', methods=['DELETE'])
@handle_database_error
@handle_file_operation_error
def delete_files(task_id):
    """删除任务文件"""
    task = get_task_by_id(task_id)
    if not task:
        raise NotFoundException('任务', task_id)
    
    deleted_files = current_app.file_manager.delete_task_files(task_id)
    
    # 更新数据库记录
    task.result_file_path = None
    task.audio_file_path = None
    db.session.commit()
    
    return success_response({
        'deleted_files': deleted_files
    }, '文件删除成功')

# 系统状态API
@api_bp.route('/system/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    try:
        status = current_app.system_monitor.get_current_status()
        return success_response(status)
    except Exception as e:
        current_app.logger.error(f'获取系统状态失败: {e}')
        raise BusinessException(
            ErrorCode.INTERNAL_ERROR,
            '无法获取系统状态',
            {'error': str(e)},
            500
        )

@api_bp.route('/system/models', methods=['GET'])
def get_models():
    """获取可用模型"""
    models = []
    for model_name, model_info in current_app.config['WHISPER_MODELS'].items():
        models.append(model_info)
    
    return success_response({'models': models})

@api_bp.route('/system/stats', methods=['GET'])
@handle_database_error
def get_stats():
    """获取统计信息"""
    period = request.args.get('period', 'day')
    
    if period not in ['day', 'week', 'month']:
        raise ValidationException('无效的统计周期', details={
            'provided_period': period,
            'valid_periods': ['day', 'week', 'month']
        })
    
    if period == 'day':
        stats = get_task_statistics()
        return success_response({
            'period': period,
            'date': stats.date.isoformat(),
            'stats': stats.to_dict()
        })
    elif period == 'week':
        # 获取本周统计
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        
        week_stats = TaskStatistics.query.filter(
            TaskStatistics.date >= week_start,
            TaskStatistics.date <= today
        ).all()
        
        # 汇总统计
        total_stats = {
            'tasks_created': sum(s.tasks_created for s in week_stats),
            'tasks_completed': sum(s.tasks_completed for s in week_stats),
            'tasks_failed': sum(s.tasks_failed for s in week_stats),
            'total_processing_time': sum(s.total_processing_time for s in week_stats),
            'total_audio_duration': sum(s.total_audio_duration for s in week_stats),
            'total_file_size': sum(s.total_file_size for s in week_stats),
            'model_usage': {}
        }
        
        # 合并模型使用统计
        for stats in week_stats:
            model_usage = stats.get_model_usage()
            for model, count in model_usage.items():
                total_stats['model_usage'][model] = total_stats['model_usage'].get(model, 0) + count
        
        total_stats['average_processing_speed'] = (
            total_stats['total_audio_duration'] / total_stats['total_processing_time']
            if total_stats['total_processing_time'] > 0 else 0
        )
        
        return success_response({
            'period': period,
            'date_range': f"{week_start.isoformat()} - {today.isoformat()}",
            'stats': total_stats
        })

# 错误日志API
@api_bp.route('/logs/error', methods=['POST'])
@validate_request_data(required_fields=['timestamp', 'context', 'code', 'message'])
def log_client_error():
    """记录客户端错误"""
    data = request.get_json()
    
    # 记录客户端错误
    current_app.logger.error(f"Client error: {data['code']} - {data['message']}", extra={
        'client_error': True,
        'context': data['context'],
        'user_agent': request.headers.get('User-Agent'),
        'remote_addr': request.remote_addr,
        'client_data': data
    })
    
    return success_response(message='错误日志已记录')

# 错误报告API
@api_bp.route('/errors/report', methods=['POST'])
@validate_request_data(required_fields=['errorId', 'error'])
def report_error():
    """报告错误"""
    data = request.get_json()
    
    # 记录错误报告
    current_app.logger.info(f"Error report submitted: {data['errorId']}", extra={
        'error_report': True,
        'error_id': data['errorId'],
        'user_feedback': data.get('userFeedback', ''),
        'error_data': data['error']
    })
    
    return success_response(message='错误报告已提交，感谢您的反馈！') 