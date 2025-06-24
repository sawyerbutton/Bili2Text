"""
配置管理工具
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """统一配置管理类"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.app_config_dir = self.config_dir / "app"
        self.model_config_dir = self.config_dir / "models"
        self._config_cache = {}
    
    def get_app_config(self, env: str = "default") -> Dict[str, Any]:
        """获取应用配置"""
        config_file = self.app_config_dir / f"{env}.env"
        
        if config_file not in self._config_cache:
            config = {}
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
            
            # 添加环境变量覆盖
            for key, value in config.items():
                env_value = os.getenv(key)
                if env_value:
                    config[key] = env_value
            
            self._config_cache[config_file] = config
        
        return self._config_cache[config_file]
    
    def get_model_config(self) -> Dict[str, Any]:
        """获取模型配置"""
        config_file = self.model_config_dir / "whisper_models.json"
        
        if config_file not in self._config_cache:
            default_config = {
                "models": {
                    "tiny": {"size": "39 MB", "multilingual": True, "english_only": False},
                    "base": {"size": "74 MB", "multilingual": True, "english_only": False},
                    "medium": {"size": "769 MB", "multilingual": True, "english_only": False},
                    "large-v3": {"size": "1550 MB", "multilingual": True, "english_only": False}
                },
                "default_model": "medium",
                "cache_dir": "./.cache/whisper"
            }
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = default_config
                # 创建默认配置文件
                config_file.parent.mkdir(parents=True, exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            self._config_cache[config_file] = config
        
        return self._config_cache[config_file]
    
    def get_storage_paths(self) -> Dict[str, Path]:
        """获取存储路径配置"""
        base_storage = Path("storage")
        return {
            "audio": base_storage / "audio",
            "video": base_storage / "video", 
            "results": base_storage / "results",
            "temp": base_storage / "temp",
            "logs": Path("logs"),
            "database": Path("database")
        }
    
    @property
    def whisper_model_cache_dir(self) -> str:
        """Whisper模型缓存目录"""
        return self.get_model_config().get("cache_dir", "./.cache/whisper")
    
    @property
    def default_whisper_model(self) -> str:
        """默认Whisper模型"""
        return self.get_model_config().get("default_model", "medium")


# 全局配置实例
config = Config() 