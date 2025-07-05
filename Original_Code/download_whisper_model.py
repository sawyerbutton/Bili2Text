#!/usr/bin/env python3
"""
Whisper模型下载脚本
使用代理或直接下载Whisper模型
"""

import os
import urllib.request
import ssl

def download_model_with_proxy():
    """使用代理下载模型"""
    print("=== Whisper模型下载工具 ===")
    
    # 配置代理
    proxy_url = "http://127.0.0.1:7890"  # 修改为您的代理地址
    use_proxy = input("是否使用代理下载？(y/n): ").lower() == 'y'
    
    if use_proxy:
        proxy_handler = urllib.request.ProxyHandler({
            'http': proxy_url,
            'https': proxy_url
        })
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)
        print(f"已配置代理: {proxy_url}")
    
    # 创建缓存目录
    cache_dir = "./.cache/whisper"
    os.makedirs(cache_dir, exist_ok=True)
    
    # Whisper模型下载链接
    models = {
        "tiny": "https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e/tiny.pt",
        "base": "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b8e83c2c73d8/base.pt",
        "small": "https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d1c41b1b6e2ceefa4e44/small.pt",
        "medium": "https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt"
    }
    
    model_name = input("选择要下载的模型 (tiny/base/small/medium) [推荐base]: ").strip() or "base"
    
    if model_name not in models:
        print("无效的模型名称")
        return
    
    url = models[model_name]
    filename = f"{model_name}.pt"
    filepath = os.path.join(cache_dir, filename)
    
    if os.path.exists(filepath):
        print(f"模型 {model_name} 已存在: {filepath}")
        return
    
    try:
        print(f"正在下载 {model_name} 模型...")
        print(f"下载地址: {url}")
        
        # 忽略SSL证书验证（如果有问题）
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
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
                        print(f"\r下载进度: {percent:.1f}% ({downloaded}/{total_size})", end='', flush=True)
        
        print(f"\n模型下载完成: {filepath}")
        print("现在可以尝试运行转录脚本了")
        
    except Exception as e:
        print(f"\n下载失败: {e}")
        print("请检查网络连接或代理设置")

if __name__ == "__main__":
    download_model_with_proxy()
