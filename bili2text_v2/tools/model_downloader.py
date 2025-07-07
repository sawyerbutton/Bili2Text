#!/usr/bin/env python3
"""
Whisper模型下载工具
专门用于下载和管理Whisper模型
"""

import os
import urllib.request
import ssl
import json
from datetime import datetime
from typing import Dict, Any, Optional


class ModelDownloader:
    """Whisper模型下载器"""
    
    def __init__(self, cache_dir: str = "./.cache/whisper"):
        """
        初始化模型下载器
        
        Args:
            cache_dir: 模型缓存目录
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        self.models = {
            "tiny": {
                "size": "39MB",
                "params": "39M",
                "description": "最快，精度较低",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e/tiny.pt"
            },
            "base": {
                "size": "74MB", 
                "params": "74M",
                "description": "平衡选择，推荐入门",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b8e83c2c73d8/base.pt"
            },
            "small": {
                "size": "244MB",
                "params": "244M", 
                "description": "较好的精度和速度",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d1c41b1b6e2ceefa4e44/small.pt"
            },
            "medium": {
                "size": "769MB",
                "params": "769M",
                "description": "推荐使用，高精度",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt"
            },
            "large": {
                "size": "1550MB",
                "params": "1550M",
                "description": "高精度，速度较慢",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/e4b87e7e0bf463eb8e6956e646f1e277e901512310def2c24bf0e11bd3c28e9a/large.pt"
            },
            "large-v3": {
                "size": "1550MB",
                "params": "1550M",
                "description": "最高精度，最新版本",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt"
            }
        }
    
    def list_available_models(self):
        """列出所有可用的模型"""
        print("=== 可用的Whisper模型 ===")
        print(f"{'模型名称':<12} {'大小':<8} {'参数量':<8} {'描述'}")
        print("-" * 50)
        
        for name, info in self.models.items():
            print(f"{name:<12} {info['size']:<8} {info['params']:<8} {info['description']}")
        
        print("\n推荐选择:")
        print("  • tiny/base: 快速测试和开发")
        print("  • medium: 日常使用，平衡精度和速度")
        print("  • large-v3: 最高质量，适合重要内容")
    
    def list_downloaded_models(self) -> list:
        """列出已下载的模型"""
        if not os.path.exists(self.cache_dir):
            return []
        
        downloaded = []
        for file in os.listdir(self.cache_dir):
            if file.endswith('.pt'):
                model_name = file[:-3]  # 移除.pt扩展名
                if model_name in self.models:
                    file_path = os.path.join(self.cache_dir, file)
                    file_size = os.path.getsize(file_path)
                    downloaded.append({
                        "name": model_name,
                        "file": file,
                        "size": self._format_size(file_size),
                        "path": file_path
                    })
        
        return downloaded
    
    def show_downloaded_models(self):
        """显示已下载的模型"""
        downloaded = self.list_downloaded_models()
        
        if not downloaded:
            print("没有找到已下载的模型")
            return
        
        print("=== 已下载的模型 ===")
        print(f"{'模型名称':<12} {'文件大小':<10} {'文件路径'}")
        print("-" * 60)
        
        for model in downloaded:
            print(f"{model['name']:<12} {model['size']:<10} {model['path']}")
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"
    
    def is_model_downloaded(self, model_name: str) -> bool:
        """检查模型是否已下载"""
        if model_name not in self.models:
            return False
        
        file_path = os.path.join(self.cache_dir, f"{model_name}.pt")
        return os.path.exists(file_path)
    
    def download_model(self, 
                      model_name: str, 
                      force: bool = False,
                      proxy_url: Optional[str] = None) -> bool:
        """
        下载指定的模型
        
        Args:
            model_name: 模型名称
            force: 强制重新下载
            proxy_url: 代理URL
            
        Returns:
            下载是否成功
        """
        if model_name not in self.models:
            print(f"❌ 不支持的模型: {model_name}")
            self.list_available_models()
            return False
        
        model_info = self.models[model_name]
        url = model_info["url"]
        size = model_info["size"]
        
        file_path = os.path.join(self.cache_dir, f"{model_name}.pt")
        
        # 检查是否已存在
        if os.path.exists(file_path) and not force:
            print(f"✅ 模型 {model_name} 已存在: {file_path}")
            return True
        
        print(f"\n=== 下载模型: {model_name} ===")
        print(f"模型大小: {size}")
        print(f"下载地址: {url}")
        
        # 配置代理
        if proxy_url:
            proxy_handler = urllib.request.ProxyHandler({
                'http': proxy_url,
                'https': proxy_url
            })
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)
            print(f"已配置代理: {proxy_url}")
        
        try:
            # 忽略SSL证书验证
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            print("开始下载...")
            start_time = datetime.now()
            
            # 创建临时文件
            temp_file = file_path + ".tmp"
            
            with urllib.request.urlopen(url, context=ssl_context) as response:
                with open(temp_file, 'wb') as f:
                    total_size = int(response.headers.get('Content-Length', 0))
                    downloaded = 0
                    block_size = 8192
                    
                    while True:
                        chunk = response.read(block_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            speed = downloaded / max((datetime.now() - start_time).seconds, 1)
                            speed_str = self._format_size(speed) + "/s"
                            print(f"\r下载进度: {percent:.1f}% ({self._format_size(downloaded)}/{self._format_size(total_size)}) {speed_str}", 
                                  end='', flush=True)
            
            # 下载完成，重命名文件
            os.rename(temp_file, file_path)
            
            end_time = datetime.now()
            duration = (end_time - start_time).seconds
            
            print(f"\n✅ 模型下载完成: {file_path}")
            print(f"下载耗时: {duration} 秒")
            
            # 保存下载记录
            self._save_download_record(model_name, {
                "download_time": datetime.now().isoformat(),
                "file_size": os.path.getsize(file_path),
                "duration": duration
            })
            
            return True
            
        except Exception as e:
            print(f"\n❌ 下载失败: {e}")
            # 清理临时文件
            temp_file = file_path + ".tmp"
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False
    
    def _save_download_record(self, model_name: str, record: Dict[str, Any]):
        """保存下载记录"""
        record_file = os.path.join(self.cache_dir, "download_records.json")
        
        try:
            if os.path.exists(record_file):
                with open(record_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            else:
                records = {}
            
            records[model_name] = record
            
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存下载记录失败: {e}")
    
    def delete_model(self, model_name: str) -> bool:
        """
        删除指定的模型
        
        Args:
            model_name: 模型名称
            
        Returns:
            删除是否成功
        """
        file_path = os.path.join(self.cache_dir, f"{model_name}.pt")
        
        if not os.path.exists(file_path):
            print(f"模型 {model_name} 不存在")
            return False
        
        try:
            file_size = os.path.getsize(file_path)
            os.remove(file_path)
            print(f"✅ 已删除模型 {model_name} (释放空间: {self._format_size(file_size)})")
            return True
        except Exception as e:
            print(f"❌ 删除模型失败: {e}")
            return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        if not os.path.exists(self.cache_dir):
            return {
                "cache_dir": self.cache_dir,
                "total_size": 0,
                "model_count": 0,
                "models": []
            }
        
        models = self.list_downloaded_models()
        total_size = sum(os.path.getsize(model["path"]) for model in models)
        
        return {
            "cache_dir": self.cache_dir,
            "total_size": total_size,
            "total_size_formatted": self._format_size(total_size),
            "model_count": len(models),
            "models": models
        }
    
    def clean_cache(self, confirm: bool = False) -> bool:
        """
        清理缓存目录
        
        Args:
            confirm: 是否确认删除
            
        Returns:
            清理是否成功
        """
        if not confirm:
            cache_info = self.get_cache_info()
            if cache_info["model_count"] == 0:
                print("缓存目录为空，无需清理")
                return True
            
            print(f"将删除 {cache_info['model_count']} 个模型文件")
            print(f"释放空间: {cache_info['total_size_formatted']}")
            confirm = input("确认删除? (y/N): ").lower() == 'y'
            
            if not confirm:
                print("操作已取消")
                return False
        
        try:
            import shutil
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
                os.makedirs(self.cache_dir, exist_ok=True)
                print("✅ 缓存目录已清理")
            return True
        except Exception as e:
            print(f"❌ 清理失败: {e}")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Whisper模型下载工具")
    parser.add_argument("--list", action="store_true", help="列出可用模型")
    parser.add_argument("--downloaded", action="store_true", help="显示已下载的模型")
    parser.add_argument("--download", help="下载指定模型")
    parser.add_argument("--delete", help="删除指定模型")
    parser.add_argument("--force", action="store_true", help="强制重新下载")
    parser.add_argument("--proxy", help="代理URL，如 http://127.0.0.1:7890")
    parser.add_argument("--cache-info", action="store_true", help="显示缓存信息")
    parser.add_argument("--clean", action="store_true", help="清理缓存目录")
    parser.add_argument("--cache-dir", default="./.cache/whisper", help="缓存目录路径")
    
    args = parser.parse_args()
    
    downloader = ModelDownloader(args.cache_dir)
    
    try:
        if args.list:
            downloader.list_available_models()
        elif args.downloaded:
            downloader.show_downloaded_models()
        elif args.download:
            success = downloader.download_model(args.download, args.force, args.proxy)
            if not success:
                exit(1)
        elif args.delete:
            success = downloader.delete_model(args.delete)
            if not success:
                exit(1)
        elif args.cache_info:
            info = downloader.get_cache_info()
            print("=== 缓存信息 ===")
            print(f"缓存目录: {info['cache_dir']}")
            print(f"模型数量: {info['model_count']}")
            print(f"总大小: {info['total_size_formatted']}")
        elif args.clean:
            success = downloader.clean_cache()
            if not success:
                exit(1)
        else:
            # 默认显示帮助和已下载模型
            parser.print_help()
            print("\n")
            downloader.show_downloaded_models()
            
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n操作失败: {e}")
        exit(1)


if __name__ == "__main__":
    main()