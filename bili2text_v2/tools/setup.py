#!/usr/bin/env python3
"""
统一的安装和设置工具
合并原来的install_dependencies.py和download_whisper_model.py功能
"""

import subprocess
import sys
import os
import urllib.request
import ssl
from datetime import datetime


class SetupTool:
    """安装和设置工具类"""
    
    def __init__(self):
        """初始化设置工具"""
        self.python_packages = [
            "openai-whisper",
            "torch",
            "torchaudio", 
            "bilix>=0.18.5",
            "bilibili-api-python",
            "aiohttp",
            "requests",
            "PyYAML>=6.0"
        ]
        
        self.whisper_models = {
            "tiny": {
                "size": "39MB",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e/tiny.pt"
            },
            "base": {
                "size": "74MB", 
                "url": "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b8e83c2c73d8/base.pt"
            },
            "small": {
                "size": "244MB",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d1c41b1b6e2ceefa4e44/small.pt"
            },
            "medium": {
                "size": "769MB",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt"
            },
            "large": {
                "size": "1550MB",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/e4b87e7e0bf463eb8e6956e646f1e277e901512310def2c24bf0e11bd3c28e9a/large.pt"
            },
            "large-v3": {
                "size": "1550MB",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt"
            }
        }
    
    def run_command(self, command: str, description: str = "") -> bool:
        """
        运行命令并显示输出
        
        Args:
            command: 要执行的命令
            description: 命令描述
            
        Returns:
            命令是否执行成功
        """
        if description:
            print(f"\n{description}")
        print(f"执行命令: {command}")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                check=True, 
                capture_output=True, 
                text=True
            )
            
            if result.stdout:
                print(result.stdout)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"命令执行失败: {e}")
            if e.stdout:
                print("标准输出:", e.stdout)
            if e.stderr:
                print("错误输出:", e.stderr)
            return False
    
    def check_python_version(self) -> bool:
        """检查Python版本"""
        print("=== 检查Python版本 ===")
        
        major = sys.version_info.major
        minor = sys.version_info.minor
        
        print(f"当前Python版本: {major}.{minor}")
        
        if major < 3 or (major == 3 and minor < 9):
            print("❌ Python版本过低，需要Python 3.9或更高版本")
            return False
        else:
            print("✅ Python版本满足要求")
            return True
    
    def upgrade_pip(self) -> bool:
        """升级pip"""
        print("\n=== 升级pip ===")
        return self.run_command("pip install --upgrade pip", "升级pip到最新版本")
    
    def install_dependencies(self) -> bool:
        """安装Python依赖包"""
        print("\n=== 安装Python依赖包 ===")
        
        all_success = True
        
        for package in self.python_packages:
            print(f"\n安装 {package}...")
            success = self.run_command(f"pip install {package}")
            if not success:
                print(f"❌ {package} 安装失败")
                all_success = False
            else:
                print(f"✅ {package} 安装成功")
        
        return all_success
    
    def setup_directories(self) -> bool:
        """设置项目目录结构"""
        print("\n=== 设置项目目录结构 ===")
        
        directories = [
            "audio",
            "video", 
            "temp",
            "result",
            ".cache",
            ".cache/whisper"
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ 目录已创建: {directory}")
            except Exception as e:
                print(f"❌ 创建目录失败 {directory}: {e}")
                return False
        
        return True
    
    def download_whisper_model(self, model_name: str = "base", use_proxy: bool = False, proxy_url: str = "http://127.0.0.1:7890") -> bool:
        """
        下载Whisper模型
        
        Args:
            model_name: 模型名称
            use_proxy: 是否使用代理
            proxy_url: 代理URL
            
        Returns:
            下载是否成功
        """
        print(f"\n=== 下载Whisper模型: {model_name} ===")
        
        if model_name not in self.whisper_models:
            print(f"❌ 不支持的模型: {model_name}")
            print(f"支持的模型: {list(self.whisper_models.keys())}")
            return False
        
        model_info = self.whisper_models[model_name]
        url = model_info["url"]
        size = model_info["size"]
        
        cache_dir = "./.cache/whisper"
        os.makedirs(cache_dir, exist_ok=True)
        
        filename = f"{model_name}.pt"
        filepath = os.path.join(cache_dir, filename)
        
        if os.path.exists(filepath):
            print(f"✅ 模型 {model_name} 已存在: {filepath}")
            return True
        
        print(f"模型大小: {size}")
        print(f"下载地址: {url}")
        
        # 配置代理
        if use_proxy:
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
            
            with urllib.request.urlopen(url, context=ssl_context) as response:
                with open(filepath, 'wb') as f:
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
                            print(f"\r下载进度: {percent:.1f}% ({downloaded:,}/{total_size:,})", end='', flush=True)
            
            end_time = datetime.now()
            duration = (end_time - start_time).seconds
            
            print(f"\n✅ 模型下载完成: {filepath}")
            print(f"下载耗时: {duration} 秒")
            return True
            
        except Exception as e:
            print(f"\n❌ 下载失败: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return False
    
    def verify_installation(self) -> bool:
        """验证安装是否成功"""
        print("\n=== 验证安装 ===")
        
        # 检查核心包
        try:
            import whisper
            import torch
            import bilix
            from bilibili_api import user
            print("✅ 核心依赖包导入成功")
        except ImportError as e:
            print(f"❌ 依赖包导入失败: {e}")
            return False
        
        # 检查Whisper模型
        cache_dir = "./.cache/whisper"
        if os.path.exists(cache_dir):
            models = [f for f in os.listdir(cache_dir) if f.endswith('.pt')]
            if models:
                print(f"✅ 找到Whisper模型: {models}")
            else:
                print("⚠️  没有找到Whisper模型文件")
        else:
            print("⚠️  Whisper缓存目录不存在")
        
        # 检查目录结构
        required_dirs = ["audio", "video", "temp", "result"]
        missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
        
        if missing_dirs:
            print(f"⚠️  缺少目录: {missing_dirs}")
        else:
            print("✅ 目录结构完整")
        
        return True
    
    def run_full_setup(self, download_model: str = None, use_proxy: bool = False, proxy_url: str = "http://127.0.0.1:7890") -> bool:
        """
        运行完整的安装设置流程
        
        Args:
            download_model: 要下载的Whisper模型，None表示不下载
            use_proxy: 是否使用代理下载模型
            proxy_url: 代理URL
            
        Returns:
            安装是否成功
        """
        print("=" * 60)
        print("Bili2Text 项目安装和设置工具")
        print("=" * 60)
        
        steps = [
            ("检查Python版本", self.check_python_version),
            ("升级pip", self.upgrade_pip),
            ("安装Python依赖", self.install_dependencies),
            ("设置目录结构", self.setup_directories)
        ]
        
        # 添加模型下载步骤
        if download_model:
            steps.append((
                f"下载Whisper模型({download_model})", 
                lambda: self.download_whisper_model(download_model, use_proxy, proxy_url)
            ))
        
        steps.append(("验证安装", self.verify_installation))
        
        success_count = 0
        total_steps = len(steps)
        
        for step_name, step_func in steps:
            print(f"\n[{success_count + 1}/{total_steps}] {step_name}")
            if step_func():
                success_count += 1
            else:
                print(f"❌ 步骤失败: {step_name}")
                break
        
        print(f"\n{'=' * 60}")
        if success_count == total_steps:
            print("🎉 安装完成！所有步骤都成功执行")
            print("\n可以开始使用以下命令：")
            print("  python workflows/batch_transcribe.py          # 批量转录")
            print("  python workflows/infinity_workflow.py        # InfinityAcademy工作流")
            print("  python workflows/ref_info_workflow.py        # 参考信息工作流")
            print("  python core/whisper_transcriber.py           # 测试转录功能")
            return True
        else:
            print(f"❌ 安装失败！完成 {success_count}/{total_steps} 个步骤")
            print("\n请检查错误信息并重新运行安装程序")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bili2Text 项目安装和设置工具")
    parser.add_argument("--model", choices=["tiny", "base", "small", "medium", "large", "large-v3"],
                       help="下载指定的Whisper模型")
    parser.add_argument("--proxy", action="store_true", help="使用代理下载模型")
    parser.add_argument("--proxy-url", default="http://127.0.0.1:7890", help="代理URL")
    parser.add_argument("--deps-only", action="store_true", help="仅安装依赖，不下载模型")
    parser.add_argument("--model-only", help="仅下载指定模型，不安装依赖")
    
    args = parser.parse_args()
    
    setup_tool = SetupTool()
    
    try:
        if args.model_only:
            # 仅下载模型
            success = setup_tool.download_whisper_model(
                args.model_only, args.proxy, args.proxy_url
            )
        elif args.deps_only:
            # 仅安装依赖
            success = (
                setup_tool.check_python_version() and
                setup_tool.upgrade_pip() and
                setup_tool.install_dependencies() and
                setup_tool.setup_directories() and
                setup_tool.verify_installation()
            )
        else:
            # 完整安装
            download_model = args.model or "base"  # 默认下载base模型
            success = setup_tool.run_full_setup(
                download_model, args.proxy, args.proxy_url
            )
        
        if success:
            print("\n✅ 操作成功完成！")
        else:
            print("\n❌ 操作失败，请检查错误信息")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n设置过程中出现错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()