"""
任务管理器
负责任务队列管理、视频下载、音频转录等核心功能
"""

import os
import sys
import threading
import queue
import time
import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 初始化项目路径管理
from src.utils import setup_project_paths
setup_project_paths()

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logging.warning("Whisper未安装，将使用模拟模式")

from webapp.core.database import db, get_task_by_id, update_task_statistics
from webapp.api.websocket_handlers import broadcast_task_update, notify_task_completion

logger = logging.getLogger(__name__)

class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.task_queue = queue.Queue()
        self.active_tasks = {}
        self.cancelled_tasks = set()
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.running = True
        
        # 启动任务处理线程
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        
        logger.info("任务管理器已启动")
    
    def submit_task(self, task):
        """提交任务到队列"""
        try:
            self.task_queue.put(task.task_id)
            logger.info(f"任务已提交到队列: {task.task_id}")
        except Exception as e:
            logger.error(f"提交任务失败: {e}")
            raise
    
    def cancel_task(self, task_id):
        """取消任务"""
        try:
            self.cancelled_tasks.add(task_id)
            
            # 如果任务正在执行，尝试停止
            if task_id in self.active_tasks:
                future = self.active_tasks[task_id]
                future.cancel()
                logger.info(f"已取消正在执行的任务: {task_id}")
            
            logger.info(f"任务已标记为取消: {task_id}")
        except Exception as e:
            logger.error(f"取消任务失败: {e}")
            raise
    
    def get_active_tasks(self):
        """获取活跃任务列表"""
        return list(self.active_tasks.keys())
    
    def get_queue_size(self):
        """获取队列大小"""
        return self.task_queue.qsize()
    
    def _worker_loop(self):
        """工作线程主循环"""
        while self.running:
            try:
                # 从队列获取任务
                task_id = self.task_queue.get(timeout=1)
                
                # 检查任务是否已被取消
                if task_id in self.cancelled_tasks:
                    self.cancelled_tasks.remove(task_id)
                    continue
                
                # 提交任务到线程池
                future = self.executor.submit(self._process_task, task_id)
                self.active_tasks[task_id] = future
                
                # 任务完成后清理
                future.add_done_callback(lambda f: self._cleanup_task(task_id))
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"工作线程错误: {e}")
    
    def _cleanup_task(self, task_id):
        """清理完成的任务"""
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
        if task_id in self.cancelled_tasks:
            self.cancelled_tasks.remove(task_id)
    
    def _process_task(self, task_id):
        """处理单个任务"""
        task = None
        try:
            # 获取任务信息
            task = get_task_by_id(task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return
            
            logger.info(f"开始处理任务: {task_id}")
            
            # 检查是否被取消
            if task_id in self.cancelled_tasks:
                task.update_status('cancelled', stage='任务已取消')
                return
            
            # 更新任务状态为下载中
            task.update_status('downloading', progress=0, stage='正在下载视频...')
            self._broadcast_update(task_id, 'downloading', 0, '正在下载视频...')
            
            # 下载视频
            audio_path, video_info = self._download_video(task)
            
            # 检查是否被取消
            if task_id in self.cancelled_tasks:
                self._cleanup_files(audio_path)
                task.update_status('cancelled', stage='任务已取消')
                return
            
            # 更新视频信息
            task.set_video_info(video_info)
            task.title = video_info.get('title', '')
            task.duration = video_info.get('duration', 0)
            
            # 更新任务状态为转录中
            task.update_status('transcribing', progress=10, stage='正在转录音频...')
            self._broadcast_update(task_id, 'transcribing', 10, '正在转录音频...')
            
            # 转录音频
            result_path = self._transcribe_audio(task, audio_path)
            
            # 检查是否被取消
            if task_id in self.cancelled_tasks:
                self._cleanup_files(audio_path, result_path)
                task.update_status('cancelled', stage='任务已取消')
                return
            
            # 保存文件路径
            task.result_file_path = result_path
            options = task.get_options()
            if options.get('keep_audio', True):
                task.audio_file_path = audio_path
            else:
                self._cleanup_files(audio_path)
            
            # 获取文件大小
            if result_path.exists():
                task.file_size = result_path.stat().st_size
            
            # 更新任务状态为完成
            task.update_status('completed', progress=100, stage='转录完成')
            self._broadcast_update(task_id, 'completed', 100, '转录完成')
            
            # 更新统计信息
            update_task_statistics(task)
            
            # 发送完成通知
            self._notify_completion(task_id, True, '任务完成')
            
            logger.info(f"任务处理完成: {task_id}")
            
        except Exception as e:
            logger.error(f"任务处理失败 {task_id}: {e}")
            
            if task:
                task.update_status('failed', stage='处理失败', error=str(e))
                self._broadcast_update(task_id, 'failed', None, '处理失败', str(e))
                self._notify_completion(task_id, False, f'任务失败: {str(e)}')
                
                # 更新统计信息
                update_task_statistics(task)
    
    def _download_video(self, task):
        """下载视频并提取音频"""
        try:
            from flask import current_app
            
            # 创建任务目录（使用路径管理器）
            from src.utils import get_storage_path
            storage_path = get_storage_path()
            task_dir = storage_path / 'audio' / task.task_id
            task_dir.mkdir(parents=True, exist_ok=True)
            
            # 音频输出路径
            audio_path = task_dir / 'audio.m4a'
            
            # 构建yt-dlp命令
            cmd = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'm4a',
                '--audio-quality', '0',
                '--output', str(audio_path).replace('.m4a', '.%(ext)s'),
                '--write-info-json',
                '--no-playlist'
            ]
            
            # 添加代理设置
            options = task.get_options()
            if options.get('use_proxy') and current_app.config.get('PROXY_URL'):
                cmd.extend(['--proxy', current_app.config['PROXY_URL']])
            
            cmd.append(task.url)
            
            # 执行下载
            logger.info(f"执行下载命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30分钟超时
            
            if result.returncode != 0:
                raise Exception(f"下载失败: {result.stderr}")
            
            # 检查音频文件是否存在
            if not audio_path.exists():
                raise Exception("音频文件下载失败")
            
            # 读取视频信息
            info_path = audio_path.with_suffix('.info.json')
            video_info = {}
            if info_path.exists():
                try:
                    with open(info_path, 'r', encoding='utf-8') as f:
                        info_data = json.load(f)
                        video_info = {
                            'title': info_data.get('title', ''),
                            'uploader': info_data.get('uploader', ''),
                            'duration': info_data.get('duration', 0),
                            'view_count': info_data.get('view_count', 0),
                            'upload_date': info_data.get('upload_date', ''),
                            'description': info_data.get('description', '')[:500]  # 限制描述长度
                        }
                    # 删除信息文件
                    info_path.unlink()
                except Exception as e:
                    logger.warning(f"读取视频信息失败: {e}")
            
            return audio_path, video_info
            
        except subprocess.TimeoutExpired:
            raise Exception("下载超时")
        except Exception as e:
            logger.error(f"下载视频失败: {e}")
            raise
    
    def _transcribe_audio(self, task, audio_path):
        """转录音频"""
        try:
            from flask import current_app
            
            # 创建结果目录（使用路径管理器）
            from src.utils import get_storage_path
            storage_path = get_storage_path()
            result_dir = storage_path / 'results' / task.task_id
            result_dir.mkdir(parents=True, exist_ok=True)
            
            options = task.get_options()
            output_format = options.get('output_format', 'txt')
            
            if WHISPER_AVAILABLE:
                # 使用真实的Whisper进行转录
                result_path = self._whisper_transcribe(task, audio_path, result_dir, output_format)
            else:
                # 模拟转录过程
                result_path = self._simulate_transcribe(task, audio_path, result_dir, output_format)
            
            return result_path
            
        except Exception as e:
            logger.error(f"转录音频失败: {e}")
            raise
    
    def _whisper_transcribe(self, task, audio_path, result_dir, output_format):
        """使用Whisper进行真实转录"""
        try:
            # 加载模型
            model = whisper.load_model(task.model_name)
            
            # 获取语言设置
            options = task.get_options()
            language = options.get('language')
            
            # 转录参数
            transcribe_options = {}
            if language and language != 'auto':
                transcribe_options['language'] = language
            
            # 执行转录
            logger.info(f"开始Whisper转录: {task.task_id}")
            result = model.transcribe(audio_path, **transcribe_options)
            
            # 保存结果
            result_path = result_dir / f'result.{output_format}'
            
            if output_format == 'txt':
                with open(result_path, 'w', encoding='utf-8') as f:
                    f.write(result['text'])
            elif output_format == 'md':
                with open(result_path, 'w', encoding='utf-8') as f:
                    f.write(f"# 转录结果\n\n")
                    f.write(f"**视频标题**: {task.title}\n\n")
                    f.write(f"**转录时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"**使用模型**: {task.model_name}\n\n")
                    f.write("## 内容\n\n")
                    f.write(result['text'])
            elif output_format == 'json':
                with open(result_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'text': result['text'],
                        'segments': result.get('segments', []),
                        'language': result.get('language', ''),
                        'task_info': {
                            'task_id': task.task_id,
                            'model': task.model_name,
                            'timestamp': datetime.now().isoformat()
                        }
                    }, f, ensure_ascii=False, indent=2)
            
            return result_path
            
        except Exception as e:
            logger.error(f"Whisper转录失败: {e}")
            raise
    
    def _simulate_transcribe(self, task, audio_path, result_dir, output_format):
        """模拟转录过程（用于开发测试）"""
        try:
            # 模拟转录进度
            for progress in range(20, 100, 10):
                if task.task_id in self.cancelled_tasks:
                    return None
                
                task.update_status('transcribing', progress=progress, stage=f'转录进度 {progress}%')
                self._broadcast_update(task.task_id, 'transcribing', progress, f'转录进度 {progress}%')
                time.sleep(1)  # 模拟处理时间
            
            # 生成模拟结果
            result_path = result_dir / f'result.{output_format}'
            
            mock_text = f"""这是一个模拟的转录结果。

任务ID: {task.task_id}
视频URL: {task.url}
使用模型: {task.model_name}
转录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

由于Whisper未安装，这是一个模拟的转录内容。
在实际部署时，请确保安装了openai-whisper包。

模拟转录内容：
大家好，欢迎观看这个视频。今天我们要讨论的话题是人工智能在现代社会中的应用。
人工智能技术正在快速发展，它已经深入到我们生活的各个方面。
从智能手机的语音助手，到自动驾驶汽车，再到医疗诊断系统，AI无处不在。
让我们一起探索这个令人兴奋的技术领域。"""
            
            if output_format == 'txt':
                with open(result_path, 'w', encoding='utf-8') as f:
                    f.write(mock_text)
            elif output_format == 'md':
                with open(result_path, 'w', encoding='utf-8') as f:
                    f.write(f"# 转录结果\n\n")
                    f.write(f"**视频标题**: {task.title or '未知标题'}\n\n")
                    f.write(f"**转录时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"**使用模型**: {task.model_name}\n\n")
                    f.write("## 内容\n\n")
                    f.write(mock_text)
            elif output_format == 'json':
                with open(result_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'text': mock_text,
                        'segments': [
                            {
                                'start': 0.0,
                                'end': 5.0,
                                'text': '大家好，欢迎观看这个视频。'
                            },
                            {
                                'start': 5.0,
                                'end': 10.0,
                                'text': '今天我们要讨论的话题是人工智能在现代社会中的应用。'
                            }
                        ],
                        'language': 'zh',
                        'task_info': {
                            'task_id': task.task_id,
                            'model': task.model_name,
                            'timestamp': datetime.now().isoformat(),
                            'note': '这是模拟转录结果'
                        }
                    }, f, ensure_ascii=False, indent=2)
            
            return result_path
            
        except Exception as e:
            logger.error(f"模拟转录失败: {e}")
            raise
    
    def _cleanup_files(self, *file_paths):
        """清理文件"""
        for file_path in file_paths:
            if file_path:
                # 支持字符串和Path对象
                path_obj = Path(file_path) if not isinstance(file_path, Path) else file_path
                if path_obj.exists():
                    try:
                        path_obj.unlink()
                        logger.info(f"已删除文件: {path_obj}")
                    except Exception as e:
                        logger.warning(f"删除文件失败 {path_obj}: {e}")
    
    def _broadcast_update(self, task_id, status, progress=None, stage=None, error=None):
        """广播任务更新"""
        try:
            from flask import current_app
            if hasattr(current_app, 'socketio'):
                broadcast_task_update(current_app.socketio, task_id, status, progress, stage, error)
        except Exception as e:
            logger.warning(f"广播任务更新失败: {e}")
    
    def _notify_completion(self, task_id, success, message):
        """发送完成通知"""
        try:
            from flask import current_app
            if hasattr(current_app, 'socketio'):
                notify_task_completion(current_app.socketio, task_id, success, message)
        except Exception as e:
            logger.warning(f"发送完成通知失败: {e}")
    
    def shutdown(self):
        """关闭任务管理器"""
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("任务管理器已关闭") 