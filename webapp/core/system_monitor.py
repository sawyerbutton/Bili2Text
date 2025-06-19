"""
系统监控器
负责监控系统资源使用情况、任务状态等
"""

import os
import time
import threading
import logging
import psutil
from datetime import datetime, timedelta
from collections import deque

from webapp.core.database import db, Task, SystemStatus, get_tasks_by_status

logger = logging.getLogger(__name__)

class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.monitoring = False
        self.monitor_thread = None
        self.performance_history = {
            'cpu': deque(maxlen=100),
            'memory': deque(maxlen=100),
            'disk': deque(maxlen=100),
            'timestamps': deque(maxlen=100)
        }
        
        logger.info("系统监控器已初始化")
    
    def start_monitoring(self, interval=5):
        """开始监控"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info(f"系统监控已启动，监控间隔: {interval}秒")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("系统监控已停止")
    
    def _monitor_loop(self, interval):
        """监控循环"""
        while self.monitoring:
            try:
                # 收集系统信息
                system_info = self._collect_system_info()
                
                # 保存到数据库
                self._save_system_status(system_info)
                
                # 更新性能历史
                self._update_performance_history(system_info)
                
                # 广播系统状态更新
                self._broadcast_system_update(system_info)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"系统监控循环错误: {e}")
                time.sleep(interval)
    
    def _collect_system_info(self):
        """收集系统信息"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # GPU信息（如果可用）
            gpu_available = False
            gpu_memory_usage = 0
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_available = True
                    gpu_memory_usage = gpus[0].memoryUtil * 100
            except ImportError:
                pass
            
            # 任务统计
            task_stats = self._get_task_statistics()
            
            # 运行时间
            uptime = int((datetime.utcnow() - self.start_time).total_seconds())
            
            return {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'disk_usage': disk_usage,
                'gpu_available': gpu_available,
                'gpu_memory_usage': gpu_memory_usage,
                'active_tasks': task_stats['active'],
                'pending_tasks': task_stats['pending'],
                'completed_tasks': task_stats['completed'],
                'failed_tasks': task_stats['failed'],
                'uptime': uptime,
                'version': '2.0.0',
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"收集系统信息失败: {e}")
            return self._get_default_system_info()
    
    def _get_default_system_info(self):
        """获取默认系统信息"""
        uptime = int((datetime.utcnow() - self.start_time).total_seconds())
        task_stats = self._get_task_statistics()
        
        return {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0,
            'gpu_available': False,
            'gpu_memory_usage': 0.0,
            'active_tasks': task_stats['active'],
            'pending_tasks': task_stats['pending'],
            'completed_tasks': task_stats['completed'],
            'failed_tasks': task_stats['failed'],
            'uptime': uptime,
            'version': '2.0.0',
            'timestamp': datetime.utcnow()
        }
    
    def _get_task_statistics(self):
        """获取任务统计"""
        try:
            active_count = Task.query.filter(
                Task.status.in_(['downloading', 'transcribing'])
            ).count()
            
            pending_count = Task.query.filter_by(status='pending').count()
            completed_count = Task.query.filter_by(status='completed').count()
            failed_count = Task.query.filter_by(status='failed').count()
            
            return {
                'active': active_count,
                'pending': pending_count,
                'completed': completed_count,
                'failed': failed_count
            }
        except Exception as e:
            logger.error(f"获取任务统计失败: {e}")
            return {
                'active': 0,
                'pending': 0,
                'completed': 0,
                'failed': 0
            }
    
    def _save_system_status(self, system_info):
        """保存系统状态到数据库"""
        try:
            status = SystemStatus(
                cpu_usage=system_info['cpu_usage'],
                memory_usage=system_info['memory_usage'],
                disk_usage=system_info['disk_usage'],
                gpu_available=system_info['gpu_available'],
                gpu_memory_usage=system_info['gpu_memory_usage'],
                active_tasks=system_info['active_tasks'],
                pending_tasks=system_info['pending_tasks'],
                completed_tasks=system_info['completed_tasks'],
                failed_tasks=system_info['failed_tasks'],
                uptime=system_info['uptime'],
                version=system_info['version']
            )
            
            db.session.add(status)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"保存系统状态失败: {e}")
            db.session.rollback()
    
    def _update_performance_history(self, system_info):
        """更新性能历史数据"""
        timestamp = system_info['timestamp']
        
        self.performance_history['cpu'].append(system_info['cpu_usage'])
        self.performance_history['memory'].append(system_info['memory_usage'])
        self.performance_history['disk'].append(system_info['disk_usage'])
        self.performance_history['timestamps'].append(timestamp)
    
    def _broadcast_system_update(self, system_info):
        """广播系统状态更新"""
        try:
            from flask import current_app
            from webapp.api.websocket_handlers import broadcast_system_update
            
            if hasattr(current_app, 'socketio'):
                broadcast_system_update(current_app.socketio, system_info)
                
        except Exception as e:
            logger.warning(f"广播系统状态更新失败: {e}")
    
    def get_current_status(self):
        """获取当前系统状态"""
        return self._collect_system_info()
    
    def get_performance_history(self, hours=1):
        """获取性能历史数据"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # 从数据库获取历史数据
        try:
            history_records = SystemStatus.query.filter(
                SystemStatus.timestamp >= cutoff_time
            ).order_by(SystemStatus.timestamp.asc()).all()
            
            history_data = {
                'cpu': [record.cpu_usage for record in history_records],
                'memory': [record.memory_usage for record in history_records],
                'disk': [record.disk_usage for record in history_records],
                'timestamps': [record.timestamp.isoformat() for record in history_records]
            }
            
            return history_data
            
        except Exception as e:
            logger.error(f"获取性能历史数据失败: {e}")
            
            # 返回内存中的数据
            return {
                'cpu': list(self.performance_history['cpu']),
                'memory': list(self.performance_history['memory']),
                'disk': list(self.performance_history['disk']),
                'timestamps': [ts.isoformat() for ts in self.performance_history['timestamps']]
            }
    
    def get_system_health(self):
        """获取系统健康状态"""
        try:
            current_status = self.get_current_status()
            
            # 健康评分计算
            health_score = 100
            warnings = []
            
            # CPU使用率检查
            if current_status['cpu_usage'] > 90:
                health_score -= 30
                warnings.append('CPU使用率过高')
            elif current_status['cpu_usage'] > 70:
                health_score -= 15
                warnings.append('CPU使用率较高')
            
            # 内存使用率检查
            if current_status['memory_usage'] > 90:
                health_score -= 30
                warnings.append('内存使用率过高')
            elif current_status['memory_usage'] > 80:
                health_score -= 15
                warnings.append('内存使用率较高')
            
            # 磁盘使用率检查
            if current_status['disk_usage'] > 95:
                health_score -= 25
                warnings.append('磁盘空间不足')
            elif current_status['disk_usage'] > 85:
                health_score -= 10
                warnings.append('磁盘空间较少')
            
            # 任务队列检查
            if current_status['pending_tasks'] > 10:
                health_score -= 10
                warnings.append('任务队列积压')
            
            # 确定健康状态
            if health_score >= 80:
                status = 'healthy'
            elif health_score >= 60:
                status = 'warning'
            else:
                status = 'critical'
            
            return {
                'status': status,
                'score': max(0, health_score),
                'warnings': warnings,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取系统健康状态失败: {e}")
            return {
                'status': 'unknown',
                'score': 0,
                'warnings': ['无法获取系统状态'],
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_service_status(self):
        """获取服务状态"""
        services = {}
        
        # 检查数据库连接
        try:
            db.session.execute('SELECT 1')
            services['database'] = {
                'status': 'running',
                'message': '数据库连接正常'
            }
        except Exception as e:
            services['database'] = {
                'status': 'error',
                'message': f'数据库连接失败: {str(e)}'
            }
        
        # 检查任务管理器
        try:
            from flask import current_app
            if hasattr(current_app, 'task_manager'):
                active_tasks = len(current_app.task_manager.get_active_tasks())
                queue_size = current_app.task_manager.get_queue_size()
                services['task_manager'] = {
                    'status': 'running',
                    'message': f'活跃任务: {active_tasks}, 队列: {queue_size}'
                }
            else:
                services['task_manager'] = {
                    'status': 'error',
                    'message': '任务管理器未初始化'
                }
        except Exception as e:
            services['task_manager'] = {
                'status': 'error',
                'message': f'任务管理器错误: {str(e)}'
            }
        
        # 检查文件管理器
        try:
            from flask import current_app
            if hasattr(current_app, 'file_manager'):
                storage_usage = current_app.file_manager.get_storage_usage()
                total_files = sum(usage['file_count'] for usage in storage_usage.values())
                services['file_manager'] = {
                    'status': 'running',
                    'message': f'管理文件: {total_files}'
                }
            else:
                services['file_manager'] = {
                    'status': 'error',
                    'message': '文件管理器未初始化'
                }
        except Exception as e:
            services['file_manager'] = {
                'status': 'error',
                'message': f'文件管理器错误: {str(e)}'
            }
        
        # 检查Whisper
        try:
            import whisper
            services['whisper'] = {
                'status': 'running',
                'message': 'Whisper可用'
            }
        except ImportError:
            services['whisper'] = {
                'status': 'warning',
                'message': 'Whisper未安装，使用模拟模式'
            }
        
        # 检查yt-dlp
        try:
            import subprocess
            result = subprocess.run(['yt-dlp', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                services['yt_dlp'] = {
                    'status': 'running',
                    'message': f'yt-dlp {version}'
                }
            else:
                services['yt_dlp'] = {
                    'status': 'error',
                    'message': 'yt-dlp不可用'
                }
        except Exception as e:
            services['yt_dlp'] = {
                'status': 'error',
                'message': f'yt-dlp检查失败: {str(e)}'
            }
        
        return services
    
    def cleanup_old_records(self, days=7):
        """清理旧的监控记录"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            deleted_count = SystemStatus.query.filter(
                SystemStatus.timestamp < cutoff_date
            ).delete()
            
            db.session.commit()
            logger.info(f"已清理 {deleted_count} 条旧的系统状态记录")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理旧记录失败: {e}")
            db.session.rollback()
            return 0
    
    def get_resource_alerts(self):
        """获取资源警告"""
        alerts = []
        current_status = self.get_current_status()
        
        # CPU警告
        if current_status['cpu_usage'] > 90:
            alerts.append({
                'type': 'cpu',
                'level': 'critical',
                'message': f'CPU使用率过高: {current_status["cpu_usage"]:.1f}%',
                'value': current_status['cpu_usage']
            })
        elif current_status['cpu_usage'] > 70:
            alerts.append({
                'type': 'cpu',
                'level': 'warning',
                'message': f'CPU使用率较高: {current_status["cpu_usage"]:.1f}%',
                'value': current_status['cpu_usage']
            })
        
        # 内存警告
        if current_status['memory_usage'] > 90:
            alerts.append({
                'type': 'memory',
                'level': 'critical',
                'message': f'内存使用率过高: {current_status["memory_usage"]:.1f}%',
                'value': current_status['memory_usage']
            })
        elif current_status['memory_usage'] > 80:
            alerts.append({
                'type': 'memory',
                'level': 'warning',
                'message': f'内存使用率较高: {current_status["memory_usage"]:.1f}%',
                'value': current_status['memory_usage']
            })
        
        # 磁盘警告
        if current_status['disk_usage'] > 95:
            alerts.append({
                'type': 'disk',
                'level': 'critical',
                'message': f'磁盘空间不足: {current_status["disk_usage"]:.1f}%',
                'value': current_status['disk_usage']
            })
        elif current_status['disk_usage'] > 85:
            alerts.append({
                'type': 'disk',
                'level': 'warning',
                'message': f'磁盘空间较少: {current_status["disk_usage"]:.1f}%',
                'value': current_status['disk_usage']
            })
        
        return alerts 