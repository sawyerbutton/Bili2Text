"""
统一路径管理器
负责项目中所有模块的路径管理，避免使用sys.path.insert
"""

import os
import sys
from pathlib import Path
from typing import Optional


class PathManager:
    """统一路径管理器"""
    
    _instance: Optional['PathManager'] = None
    _initialized = False
    
    def __new__(cls) -> 'PathManager':
        """单例模式确保全局唯一的路径管理器"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化路径管理器"""
        if not self._initialized:
            self._setup_paths()
            PathManager._initialized = True
    
    def _setup_paths(self):
        """设置项目路径"""
        # 获取项目根目录
        current_file = Path(__file__).resolve()
        self._project_root = current_file.parent.parent.parent
        
        # 重要路径定义
        self._src_path = self._project_root / 'src'
        self._cli_path = self._project_root / 'cli'
        self._webapp_path = self._project_root / 'webapp'
        self._config_path = self._project_root / 'config'
        self._storage_path = self._project_root / 'storage'
        
        # 确保项目根目录在Python路径中
        self._ensure_path_in_sys_path(str(self._project_root))
    
    def _ensure_path_in_sys_path(self, path: str):
        """确保路径在sys.path中，但不重复添加"""
        if path not in sys.path:
            sys.path.insert(0, path)
    
    @property
    def project_root(self) -> Path:
        """项目根目录"""
        return self._project_root
    
    @property
    def src_path(self) -> Path:
        """源码目录"""
        return self._src_path
    
    @property
    def cli_path(self) -> Path:
        """CLI目录"""
        return self._cli_path
    
    @property
    def webapp_path(self) -> Path:
        """Web应用目录"""
        return self._webapp_path
    
    @property
    def config_path(self) -> Path:
        """配置目录"""
        return self._config_path
    
    @property
    def storage_path(self) -> Path:
        """存储目录"""
        return self._storage_path
    
    def get_storage_subpath(self, subdir: str) -> Path:
        """获取存储子目录路径"""
        return self._storage_path / subdir
    
    def ensure_directory_exists(self, path: Path) -> Path:
        """确保目录存在，如果不存在则创建"""
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_relative_path(self, absolute_path: Path) -> Path:
        """获取相对于项目根目录的相对路径"""
        try:
            return absolute_path.relative_to(self._project_root)
        except ValueError:
            # 如果路径不在项目根目录下，返回绝对路径
            return absolute_path


# 全局路径管理器实例
path_manager = PathManager()


def get_project_root() -> Path:
    """获取项目根目录"""
    return path_manager.project_root


def get_src_path() -> Path:
    """获取源码目录"""
    return path_manager.src_path


def get_cli_path() -> Path:
    """获取CLI目录"""
    return path_manager.cli_path


def get_webapp_path() -> Path:
    """获取Web应用目录"""
    return path_manager.webapp_path


def get_config_path() -> Path:
    """获取配置目录"""
    return path_manager.config_path


def get_storage_path() -> Path:
    """获取存储目录"""
    return path_manager.storage_path


def ensure_storage_subdirs() -> dict:
    """确保所有存储子目录存在"""
    subdirs = {
        'audio': 'audio',
        'video': 'video', 
        'results': 'results',
        'temp': 'temp'
    }
    
    paths = {}
    for key, subdir in subdirs.items():
        path = path_manager.get_storage_subpath(subdir)
        paths[key] = path_manager.ensure_directory_exists(path)
    
    return paths


def setup_project_paths():
    """初始化项目路径结构（供其他模块调用）"""
    # 触发路径管理器初始化
    _ = path_manager
    # 确保存储目录结构存在
    ensure_storage_subdirs()
    return path_manager