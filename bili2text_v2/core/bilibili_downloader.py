#!/usr/bin/env python3
"""
B站下载核心模块
统一所有B站视频/音频下载功能
"""

import asyncio
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from bilibili_api import sync, user, Credential, request_settings
from bilix.sites.bilibili import DownloaderBilibili


class BilibiliDownloader:
    """B站下载器类"""
    
    def __init__(self, 
                 proxy_url: Optional[str] = None,
                 timeout: float = 10.0):
        """
        初始化B站下载器
        
        Args:
            proxy_url: 代理URL，如 "http://127.0.0.1:7890"
            timeout: 请求超时时间
        """
        self.proxy_url = proxy_url
        self.timeout = timeout
        self._setup_request_settings()
    
    def _setup_request_settings(self):
        """设置请求参数"""
        request_settings.set_timeout(self.timeout)
        
        if self.proxy_url:
            request_settings.set_proxy(self.proxy_url)
            print(f"已配置代理: {self.proxy_url}")
    
    async def download_video_audio(self, 
                                  url: str, 
                                  output_path: str = "./temp",
                                  only_audio: bool = True) -> bool:
        """
        下载B站视频的音频或视频文件
        
        Args:
            url: B站视频URL或BVID
            output_path: 输出目录
            only_audio: 是否只下载音频
            
        Returns:
            下载是否成功
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_path, exist_ok=True)
            
            # 如果传入的是BVID，转换为完整URL
            if not url.startswith("http"):
                url = f"https://www.bilibili.com/video/{url}"
            
            print(f"开始下载: {url}")
            print(f"输出目录: {output_path}")
            print(f"下载模式: {'仅音频' if only_audio else '完整视频'}")
            
            async with DownloaderBilibili() as d:
                await d.get_video(url, path=output_path, only_audio=only_audio)
            
            print(f"下载完成: {url}")
            return True
            
        except Exception as e:
            print(f"下载失败 {url}: {e}")
            return False
    
    def download_video_audio_sync(self, 
                                 url: str, 
                                 output_path: str = "./temp",
                                 only_audio: bool = True) -> bool:
        """
        同步版本的下载方法
        
        Args:
            url: B站视频URL或BVID
            output_path: 输出目录  
            only_audio: 是否只下载音频
            
        Returns:
            下载是否成功
        """
        return asyncio.run(self.download_video_audio(url, output_path, only_audio))
    
    async def get_user_videos(self, uid: int) -> List[Dict[str, Any]]:
        """
        获取指定用户的所有视频信息
        
        Args:
            uid: 用户UID
            
        Returns:
            视频信息列表
        """
        video_info_list = []
        u = user.User(uid)
        
        try:
            print(f"正在获取用户 {uid} 的视频列表...")
            page_num = 1
            
            while True:
                print(f"获取第 {page_num} 页视频...")
                
                videos_page = await u.get_videos(pn=page_num)
                
                if not videos_page or "list" not in videos_page:
                    print("没有更多视频数据")
                    break
                
                videos = videos_page["list"]["vlist"]
                if not videos:
                    print("当前页没有视频")
                    break
                
                print(f"第 {page_num} 页获取到 {len(videos)} 个视频")
                
                # 处理视频信息
                for video in videos:
                    try:
                        bvid = video.get("bvid", "")
                        title = video.get("title", "无标题")
                        desc = video.get("description", "无描述")
                        
                        if bvid:
                            video_info_list.append({
                                "bvid": bvid,
                                "title": title,
                                "desc": desc,
                                "url": f"https://www.bilibili.com/video/{bvid}"
                            })
                            
                    except Exception as e:
                        print(f"处理视频信息时出错: {e}")
                        continue
                
                # 检查是否有下一页
                page_count = videos_page["page"]["count"]
                page_size = videos_page["page"]["ps"]
                total_pages = (page_count + page_size - 1) // page_size
                
                if page_num >= total_pages:
                    print("已获取所有视频页面")
                    break
                
                page_num += 1
                await asyncio.sleep(1)  # 避免请求过快
                
        except Exception as e:
            print(f"获取用户视频列表失败: {e}")
            
            # 备用方案：从动态中获取视频信息
            print("尝试从动态中获取视频信息...")
            try:
                dynamics_videos = await self.get_user_dynamics_videos(uid)
                video_info_list.extend(dynamics_videos)
            except Exception as e2:
                print(f"从动态获取视频信息也失败: {e2}")
        
        print(f"共找到 {len(video_info_list)} 个视频")
        return video_info_list
    
    async def get_user_dynamics_videos(self, uid: int) -> List[Dict[str, Any]]:
        """
        从用户动态中获取视频信息
        
        Args:
            uid: 用户UID
            
        Returns:
            视频信息列表
        """
        video_info_list = []
        u = user.User(uid)
        
        try:
            page_num = 1
            offset = ""
            
            while True:
                print(f"获取第 {page_num} 页动态...")
                
                if page_num == 1:
                    page = await u.get_dynamics(0)
                else:
                    page = await u.get_dynamics(offset)
                
                if not page or "cards" not in page:
                    print("没有更多动态数据")
                    break
                
                cards = page["cards"]
                if not cards:
                    print("当前页没有动态卡片")
                    break
                
                print(f"第 {page_num} 页获取到 {len(cards)} 条动态")
                
                # 提取动态中的视频信息
                for i, dynamic in enumerate(cards):
                    try:
                        if "desc" not in dynamic or "card" not in dynamic:
                            continue
                        
                        desc_info = dynamic["desc"]
                        card_info = dynamic["card"]
                        
                        if "bvid" not in desc_info:
                            continue
                        
                        bvid = desc_info["bvid"]
                        title = card_info.get("title", "无标题")
                        desc = card_info.get("dynamic", card_info.get("desc", "无描述"))
                        
                        video_info_list.append({
                            "bvid": bvid,
                            "title": title,
                            "desc": desc,
                            "url": f"https://www.bilibili.com/video/{bvid}"
                        })
                        
                    except Exception as e:
                        print(f"处理第 {i+1} 条动态时出错: {e}")
                        continue
                
                # 检查是否有下一页
                if "next_offset" in page and page["next_offset"]:
                    offset = page["next_offset"]
                    page_num += 1
                    await asyncio.sleep(1)
                else:
                    print("已获取所有动态页面")
                    break
                    
        except Exception as e:
            print(f"获取用户动态失败: {e}")
        
        return video_info_list
    
    def get_user_videos_sync(self, uid: int) -> List[Dict[str, Any]]:
        """
        同步版本的获取用户视频方法
        
        Args:
            uid: 用户UID
            
        Returns:
            视频信息列表
        """
        return asyncio.run(self.get_user_videos(uid))
    
    async def batch_download_videos(self, 
                                   video_infos: List[Dict[str, Any]],
                                   output_path: str = "./temp",
                                   only_audio: bool = True,
                                   max_concurrent: int = 3) -> Dict[str, bool]:
        """
        批量下载视频
        
        Args:
            video_infos: 视频信息列表
            output_path: 输出目录
            only_audio: 是否只下载音频
            max_concurrent: 最大并发数
            
        Returns:
            下载结果字典，BVID为键，成功/失败为值
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        results = {}
        
        async def download_single(video_info):
            async with semaphore:
                bvid = video_info["bvid"]
                url = video_info["url"]
                success = await self.download_video_audio(url, output_path, only_audio)
                results[bvid] = success
                return success
        
        tasks = [download_single(video_info) for video_info in video_infos]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for success in results.values() if success)
        print(f"批量下载完成！成功下载 {success_count}/{len(video_infos)} 个视频")
        
        return results
    
    def batch_download_videos_sync(self, 
                                  video_infos: List[Dict[str, Any]],
                                  output_path: str = "./temp",
                                  only_audio: bool = True,
                                  max_concurrent: int = 3) -> Dict[str, bool]:
        """
        同步版本的批量下载方法
        """
        return asyncio.run(self.batch_download_videos(
            video_infos, output_path, only_audio, max_concurrent
        ))


class FileManager:
    """文件管理器，处理下载后的文件移动和整理"""
    
    @staticmethod
    def move_downloaded_files(temp_path: str, 
                             target_path: str,
                             file_prefix: Optional[str] = None) -> List[str]:
        """
        移动下载的文件到目标目录
        
        Args:
            temp_path: 临时目录
            target_path: 目标目录
            file_prefix: 文件前缀（可选）
            
        Returns:
            移动的文件列表
        """
        os.makedirs(target_path, exist_ok=True)
        
        if not os.path.exists(temp_path):
            print(f"临时目录不存在: {temp_path}")
            return []
        
        temp_files = os.listdir(temp_path)
        moved_files = []
        
        for file_name in temp_files:
            if os.path.isfile(os.path.join(temp_path, file_name)):
                temp_file_path = os.path.join(temp_path, file_name)
                
                # 添加前缀（如果指定）
                if file_prefix:
                    name, ext = os.path.splitext(file_name)
                    new_file_name = f"{file_prefix}_{file_name}"
                else:
                    new_file_name = file_name
                
                target_file_path = os.path.join(target_path, new_file_name)
                
                # 如果目标文件已存在，添加时间戳
                if os.path.exists(target_file_path):
                    name, ext = os.path.splitext(new_file_name)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    target_file_path = os.path.join(target_path, f"{name}_{timestamp}{ext}")
                
                shutil.move(temp_file_path, target_file_path)
                moved_files.append(target_file_path)
                print(f"文件已移动到: {target_file_path}")
        
        return moved_files
    
    @staticmethod
    def clean_temp_directory(temp_path: str):
        """清理临时目录"""
        if os.path.exists(temp_path):
            for file in os.listdir(temp_path):
                file_path = os.path.join(temp_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)


# 便捷函数
def download_single_video(url_or_bvid: str, 
                         output_path: str = "./audio",
                         only_audio: bool = True,
                         proxy_url: Optional[str] = None) -> bool:
    """
    下载单个视频的便捷函数
    
    Args:
        url_or_bvid: 视频URL或BVID
        output_path: 输出目录
        only_audio: 是否只下载音频
        proxy_url: 代理URL
        
    Returns:
        下载是否成功
    """
    downloader = BilibiliDownloader(proxy_url=proxy_url)
    return downloader.download_video_audio_sync(url_or_bvid, output_path, only_audio)


def get_user_all_videos(uid: int, proxy_url: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    获取用户所有视频的便捷函数
    
    Args:
        uid: 用户UID
        proxy_url: 代理URL
        
    Returns:
        视频信息列表
    """
    downloader = BilibiliDownloader(proxy_url=proxy_url)
    return downloader.get_user_videos_sync(uid)


if __name__ == "__main__":
    # 测试代码
    print("=== B站下载器测试 ===")
    
    # 测试单个视频下载
    test_url = "https://www.bilibili.com/video/BV1LCM3zwEH9"
    downloader = BilibiliDownloader()
    
    print(f"测试下载: {test_url}")
    success = downloader.download_video_audio_sync(test_url, "./test_temp", only_audio=True)
    
    if success:
        print("下载测试成功！")
        
        # 测试文件移动
        file_manager = FileManager()
        moved_files = file_manager.move_downloaded_files("./test_temp", "./test_audio")
        print(f"移动文件: {moved_files}")
        
        # 清理临时目录
        file_manager.clean_temp_directory("./test_temp")
        print("临时目录已清理")
    else:
        print("下载测试失败")