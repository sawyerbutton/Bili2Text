"""
配置管理器
负责加载、合并和管理配置
"""
import os
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, Union
from functools import lru_cache

from .schema import AppConfig


class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self._config: Optional[AppConfig] = None
        self._env_config: Dict[str, Any] = {}
        
    def load_from_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        从文件加载配置
        
        Args:
            file_path: 文件路径
            
        Returns:
            配置字典
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        # 根据文件扩展名选择加载方式
        if file_path.suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif file_path.suffix in ['.yml', '.yaml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            raise ValueError(f"不支持的配置文件格式: {file_path.suffix}")
    
    def load_from_env(self) -> Dict[str, Any]:
        """
        从环境变量加载配置
        
        Returns:
            配置字典
        """
        config = {}
        prefix = "BILI2TEXT_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # 移除前缀并转换为小写
                config_key = key[len(prefix):].lower()
                # 处理嵌套配置（使用双下划线）
                if "__" in config_key:
                    parts = config_key.split("__")
                    current = config
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = self._parse_env_value(value)
                else:
                    config[config_key] = self._parse_env_value(value)
        
        return config
    
    def _parse_env_value(self, value: str) -> Any:
        """解析环境变量值"""
        # 尝试解析为JSON
        try:
            return json.loads(value)
        except:
            pass
        
        # 布尔值
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # 数字
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except:
            pass
        
        # 字符串
        return value
    
    def merge_configs(self, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并多个配置字典
        
        Args:
            *configs: 配置字典列表
            
        Returns:
            合并后的配置
        """
        result = {}
        
        for config in configs:
            if config:
                self._deep_merge(result, config)
        
        return result
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]):
        """深度合并字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    @lru_cache(maxsize=1)
    def get_config(self) -> AppConfig:
        """
        获取配置（带缓存）
        
        Returns:
            应用配置对象
        """
        if self._config is None:
            self.load()
        return self._config
    
    def load(self):
        """加载配置"""
        configs = []
        
        # 1. 加载默认配置
        default_config = {}
        
        # 2. 加载配置文件
        if self.config_path:
            try:
                file_config = self.load_from_file(self.config_path)
                configs.append(file_config)
            except Exception as e:
                print(f"警告: 加载配置文件失败: {e}")
        else:
            # 尝试加载默认位置的配置文件
            for config_file in ['config.yml', 'config.yaml', 'config.json', '.bili2text.yml']:
                if Path(config_file).exists():
                    try:
                        file_config = self.load_from_file(config_file)
                        configs.append(file_config)
                        break
                    except:
                        pass
        
        # 3. 加载环境变量配置
        env_config = self.load_from_env()
        if env_config:
            configs.append(env_config)
        
        # 4. 合并所有配置
        merged_config = self.merge_configs(default_config, *configs)
        
        # 5. 创建配置对象
        self._config = AppConfig(**merged_config)
    
    def save(self, file_path: Union[str, Path], format: str = 'yaml'):
        """
        保存配置到文件
        
        Args:
            file_path: 文件路径
            format: 文件格式 (yaml/json)
        """
        if self._config is None:
            raise RuntimeError("配置尚未加载")
        
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_dict = self._config.dict()
        
        if format == 'json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)
        elif format in ['yaml', 'yml']:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def reload(self):
        """重新加载配置"""
        self._config = None
        self.get_config.cache_clear()
        self.load()
    
    def update(self, updates: Dict[str, Any]):
        """
        更新配置
        
        Args:
            updates: 更新的配置项
        """
        if self._config is None:
            self.load()
        
        # 获取当前配置字典
        current_config = self._config.dict()
        
        # 合并更新
        self._deep_merge(current_config, updates)
        
        # 重新创建配置对象
        self._config = AppConfig(**current_config)
        
        # 清除缓存
        self.get_config.cache_clear()


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AppConfig:
    """获取应用配置"""
    return get_config_manager().get_config()


def init_config(config_path: Optional[Union[str, Path]] = None):
    """
    初始化配置
    
    Args:
        config_path: 配置文件路径
    """
    global _config_manager
    _config_manager = ConfigManager(config_path)
    _config_manager.load()