"""
工具模块
提供项目通用工具函数和类
"""

from .path_manager import (
    PathManager,
    path_manager,
    get_project_root,
    get_src_path,
    get_cli_path,
    get_webapp_path,
    get_config_path,
    get_storage_path,
    ensure_storage_subdirs,
    setup_project_paths
)

__all__ = [
    'PathManager',
    'path_manager',
    'get_project_root',
    'get_src_path', 
    'get_cli_path',
    'get_webapp_path',
    'get_config_path',
    'get_storage_path',
    'ensure_storage_subdirs',
    'setup_project_paths'
] 