"""
文件管理器
负责文件存储、清理和管理功能
"""

import os
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class FileManager:
    """文件管理器"""
    
    def __init__(self):
        self.storage_paths = {}
        logger.info("文件管理器已初始化")
    
    def initialize_storage(self, config):
        """初始化存储路径"""
        self.storage_paths = {
            'audio': config['AUDIO_STORAGE_PATH'],
            'result': config['RESULT_STORAGE_PATH'],
            'temp': config['TEMP_STORAGE_PATH']
        }
        
        # 确保所有存储目录存在
        for path in self.storage_paths.values():
            os.makedirs(path, exist_ok=True)
        
        logger.info(f"存储路径已初始化: {self.storage_paths}")
    
    def get_task_directory(self, task_id, storage_type='result'):
        """获取任务目录路径"""
        if storage_type not in self.storage_paths:
            raise ValueError(f"不支持的存储类型: {storage_type}")
        
        return os.path.join(self.storage_paths[storage_type], task_id)
    
    def create_task_directory(self, task_id, storage_type='result'):
        """创建任务目录"""
        task_dir = self.get_task_directory(task_id, storage_type)
        os.makedirs(task_dir, exist_ok=True)
        return task_dir
    
    def delete_task_files(self, task_id):
        """删除任务相关的所有文件"""
        deleted_files = []
        
        for storage_type in self.storage_paths:
            task_dir = self.get_task_directory(task_id, storage_type)
            
            if os.path.exists(task_dir):
                try:
                    # 获取目录中的所有文件
                    for root, dirs, files in os.walk(task_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            deleted_files.append(file_path)
                    
                    # 删除整个目录
                    shutil.rmtree(task_dir)
                    logger.info(f"已删除任务目录: {task_dir}")
                    
                except Exception as e:
                    logger.error(f"删除任务目录失败 {task_dir}: {e}")
        
        return deleted_files
    
    def get_file_info(self, file_path):
        """获取文件信息"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'is_file': os.path.isfile(file_path),
            'is_dir': os.path.isdir(file_path)
        }
    
    def get_storage_usage(self):
        """获取存储使用情况"""
        usage = {}
        
        for storage_type, path in self.storage_paths.items():
            if os.path.exists(path):
                total_size = 0
                file_count = 0
                
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                        except (OSError, IOError):
                            continue
                
                usage[storage_type] = {
                    'path': path,
                    'total_size': total_size,
                    'file_count': file_count,
                    'formatted_size': self._format_size(total_size)
                }
            else:
                usage[storage_type] = {
                    'path': path,
                    'total_size': 0,
                    'file_count': 0,
                    'formatted_size': '0 B'
                }
        
        return usage
    
    def cleanup_old_files(self, days=30):
        """清理旧文件"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_files = []
        
        for storage_type, path in self.storage_paths.items():
            if not os.path.exists(path):
                continue
            
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        if file_mtime < cutoff_date:
                            os.remove(file_path)
                            cleaned_files.append(file_path)
                            logger.info(f"已清理旧文件: {file_path}")
                    
                    except (OSError, IOError) as e:
                        logger.warning(f"清理文件失败 {file_path}: {e}")
                
                # 清理空目录
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if not os.listdir(dir_path):  # 目录为空
                            os.rmdir(dir_path)
                            logger.info(f"已清理空目录: {dir_path}")
                    except (OSError, IOError):
                        continue
        
        return cleaned_files
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        temp_path = self.storage_paths.get('temp')
        if not temp_path or not os.path.exists(temp_path):
            return []
        
        cleaned_files = []
        
        try:
            for item in os.listdir(temp_path):
                item_path = os.path.join(temp_path, item)
                
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    cleaned_files.append(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    cleaned_files.append(item_path)
                
                logger.info(f"已清理临时文件: {item_path}")
        
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")
        
        return cleaned_files
    
    def get_disk_usage(self, path):
        """获取磁盘使用情况"""
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(path),
                    ctypes.pointer(free_bytes),
                    ctypes.pointer(total_bytes),
                    None
                )
                total = total_bytes.value
                free = free_bytes.value
                used = total - free
            else:  # Unix/Linux
                statvfs = os.statvfs(path)
                total = statvfs.f_frsize * statvfs.f_blocks
                free = statvfs.f_frsize * statvfs.f_available
                used = total - free
            
            return {
                'total': total,
                'used': used,
                'free': free,
                'usage_percent': (used / total * 100) if total > 0 else 0,
                'formatted': {
                    'total': self._format_size(total),
                    'used': self._format_size(used),
                    'free': self._format_size(free)
                }
            }
        
        except Exception as e:
            logger.error(f"获取磁盘使用情况失败: {e}")
            return None
    
    def validate_file_path(self, file_path, allowed_extensions=None):
        """验证文件路径"""
        if not file_path:
            return False, "文件路径不能为空"
        
        # 检查路径是否在允许的存储目录内
        abs_path = os.path.abspath(file_path)
        allowed = False
        
        for storage_path in self.storage_paths.values():
            if abs_path.startswith(os.path.abspath(storage_path)):
                allowed = True
                break
        
        if not allowed:
            return False, "文件路径不在允许的存储目录内"
        
        # 检查文件扩展名
        if allowed_extensions:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in allowed_extensions:
                return False, f"不支持的文件类型: {file_ext}"
        
        return True, "文件路径有效"
    
    def create_backup(self, source_path, backup_dir=None):
        """创建文件备份"""
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"源文件不存在: {source_path}")
        
        if backup_dir is None:
            backup_dir = os.path.join(self.storage_paths['temp'], 'backups')
        
        os.makedirs(backup_dir, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        source_name = os.path.basename(source_path)
        backup_name = f"{timestamp}_{source_name}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # 复制文件
        if os.path.isfile(source_path):
            shutil.copy2(source_path, backup_path)
        elif os.path.isdir(source_path):
            shutil.copytree(source_path, backup_path)
        
        logger.info(f"已创建备份: {source_path} -> {backup_path}")
        return backup_path
    
    def restore_backup(self, backup_path, target_path):
        """恢复备份"""
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")
        
        # 如果目标已存在，先备份
        if os.path.exists(target_path):
            temp_backup = self.create_backup(target_path)
            logger.info(f"已备份现有文件: {temp_backup}")
        
        # 恢复文件
        if os.path.isfile(backup_path):
            shutil.copy2(backup_path, target_path)
        elif os.path.isdir(backup_path):
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            shutil.copytree(backup_path, target_path)
        
        logger.info(f"已恢复备份: {backup_path} -> {target_path}")
    
    def _format_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
    
    def get_directory_tree(self, path, max_depth=3, current_depth=0):
        """获取目录树结构"""
        if current_depth >= max_depth or not os.path.exists(path):
            return None
        
        tree = {
            'name': os.path.basename(path) or path,
            'path': path,
            'type': 'directory' if os.path.isdir(path) else 'file',
            'size': 0,
            'children': []
        }
        
        if os.path.isfile(path):
            tree['size'] = os.path.getsize(path)
            tree['formatted_size'] = self._format_size(tree['size'])
            return tree
        
        try:
            items = sorted(os.listdir(path))
            total_size = 0
            
            for item in items:
                item_path = os.path.join(path, item)
                child = self.get_directory_tree(item_path, max_depth, current_depth + 1)
                
                if child:
                    tree['children'].append(child)
                    total_size += child.get('size', 0)
            
            tree['size'] = total_size
            tree['formatted_size'] = self._format_size(total_size)
            
        except PermissionError:
            tree['error'] = '权限不足'
        except Exception as e:
            tree['error'] = str(e)
        
        return tree 