#!/usr/bin/env python3
"""
B站下载核心模块 - 使用新的日志和错误处理系统
统一所有B站视频/音频下载功能
"""

import asyncio
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from bilibili_api import sync, user, Credential, request_settings
from bilix.sites.bilibili import DownloaderBilibili

from .logger import get_logger, log_execution_time, LogContext
from .exceptions import (
    DownloadError, NetworkError, VideoNotFoundError,
    FileOperationError, ValidationError, URLValidationError,
    retry_on_error
)
from .error_handler import error_handler, error_context, ErrorCollector


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
        self.logger = get_logger(__name__)
        self.proxy_url = proxy_url
        self.timeout = timeout
        self._setup_request_settings()
        
        self.logger.info(
            "B站下载器初始化完成",
            extra={
                "proxy": self.proxy_url,
                "timeout": self.timeout
            }
        )
    
    def _setup_request_settings(self):
        """设置请求参数"""
        request_settings.set_timeout(self.timeout)
        
        if self.proxy_url:
            request_settings.set_proxy(self.proxy_url)
            self.logger.info(f"已配置代理: {self.proxy_url}")
    
    @retry_on_error(exceptions=(NetworkError,), max_retries=3, delay=2.0)
    @log_execution_time()
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
        with LogContext(self.logger, download_url=url, output_path=output_path):
            # 参数验证
            if not url:
                raise URLValidationError("下载URL不能为空")
            
            try:
                # 确保输出目录存在
                with error_context("创建输出目录", FileOperationError, logger_name=__name__):
                    os.makedirs(output_path, exist_ok=True)
                
                # 如果传入的是BVID，转换为完整URL
                if not url.startswith("http"):
                    url = f"https://www.bilibili.com/video/{url}"
                    self.logger.debug(f"BVID转换为完整URL: {url}")
                
                self.logger.info(
                    "开始下载视频",
                    extra={
                        "url": url,
                        "output_path": output_path,
                        "mode": "audio_only" if only_audio else "full_video"
                    }
                )
                
                async with DownloaderBilibili() as d:
                    await d.get_video(url, path=output_path, only_audio=only_audio)
                
                self.logger.info(f"下载成功: {url}")
                return True
                
            except Exception as e:
                # 转换为自定义异常
                if "404" in str(e) or "不存在" in str(e):
                    raise VideoNotFoundError(url) from e
                elif "网络" in str(e) or "timeout" in str(e).lower():
                    raise NetworkError(f"网络请求失败: {e}") from e
                else:
                    raise DownloadError(f"下载失败: {e}", details={"url": url}) from e
    
    @error_handler(
        exceptions=(DownloadError,),
        default_return=False,
        raise_on_error=False,
        error_message="同步下载失败"
    )
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
    
    @log_execution_time()
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
        
        # 使用错误收集器
        error_collector = ErrorCollector(logger_name=__name__)
        
        try:
            self.logger.info(f"开始获取用户 {uid} 的视频列表")
            page_num = 1
            
            while True:
                self.logger.debug(f"获取第 {page_num} 页视频")
                
                try:
                    videos_page = await u.get_videos(pn=page_num)
                except Exception as e:
                    error_collector.add_error(e, {"page": page_num})
                    break
                
                if not videos_page or "list" not in videos_page:
                    self.logger.debug("没有更多视频数据")
                    break
                
                videos = videos_page["list"]["vlist"]
                if not videos:
                    self.logger.debug("当前页没有视频")
                    break
                
                self.logger.info(f"第 {page_num} 页获取到 {len(videos)} 个视频")
                
                # 处理视频信息
                for video in videos:
                    with error_collector:
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
                
                # 检查是否有下一页
                page_count = videos_page["page"]["count"]
                page_size = videos_page["page"]["ps"]
                total_pages = (page_count + page_size - 1) // page_size
                
                if page_num >= total_pages:
                    self.logger.debug("已获取所有视频页面")
                    break
                
                page_num += 1
                await asyncio.sleep(1)  # 避免请求过快
                
        except Exception as e:
            self.logger.error(f"获取用户视频列表失败: {e}", exc_info=True)
            
            # 备用方案：从动态中获取视频信息
            self.logger.info("尝试从动态中获取视频信息")
            try:
                dynamics_videos = await self.get_user_dynamics_videos(uid)
                video_info_list.extend(dynamics_videos)
            except Exception as e2:
                error_collector.add_error(e2, {"source": "dynamics"})
        
        # 检查是否有错误但仍继续处理
        if error_collector.has_errors():
            self.logger.warning(
                f"获取视频过程中遇到 {len(error_collector.get_errors())} 个错误",
                extra={"errors": error_collector.get_errors()}
            )
        
        self.logger.info(
            f"获取视频完成",
            extra={
                "uid": uid,
                "total_videos": len(video_info_list),
                "errors": len(error_collector.get_errors())
            }
        )
        
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
        
        with error_context(
            f"获取用户 {uid} 的动态视频",
            NetworkError,
            logger_name=__name__,
            raise_on_error=False
        ):
            page_num = 1
            offset = ""
            
            while True:
                self.logger.debug(f"获取第 {page_num} 页动态")
                
                try:
                    if page_num == 1:
                        page = await u.get_dynamics(0)
                    else:
                        page = await u.get_dynamics(offset)
                except Exception as e:
                    self.logger.error(f"获取动态页失败: {e}")
                    break
                
                if not page or "cards" not in page:
                    break
                
                cards = page["cards"]
                if not cards:
                    break
                
                self.logger.debug(f"第 {page_num} 页获取到 {len(cards)} 条动态")
                
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
                        self.logger.debug(f"处理第 {i+1} 条动态时出错: {e}")
                        continue
                
                # 检查是否有下一页
                if "next_offset" in page and page["next_offset"]:
                    offset = page["next_offset"]
                    page_num += 1
                    await asyncio.sleep(1)
                else:
                    break
        
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
    
    @log_execution_time()
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
        if not video_infos:
            self.logger.warning("视频列表为空，无法下载")
            return {}
        
        semaphore = asyncio.Semaphore(max_concurrent)
        results = {}
        error_collector = ErrorCollector(logger_name=__name__)
        
        async def download_single(video_info):
            async with semaphore:
                bvid = video_info["bvid"]
                url = video_info["url"]
                
                try:
                    success = await self.download_video_audio(url, output_path, only_audio)
                    results[bvid] = success
                    return success
                except Exception as e:
                    error_collector.add_error(e, {"bvid": bvid, "url": url})
                    results[bvid] = False
                    return False
        
        self.logger.info(
            f"开始批量下载",
            extra={
                "total_videos": len(video_infos),
                "max_concurrent": max_concurrent,
                "output_path": output_path
            }
        )
        
        tasks = [download_single(video_info) for video_info in video_infos]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for success in results.values() if success)
        
        self.logger.info(
            f"批量下载完成",
            extra={
                "success": success_count,
                "failed": len(video_infos) - success_count,
                "total": len(video_infos),
                "errors": len(error_collector.get_errors())
            }
        )
        
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
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    @error_handler(
        exceptions=(FileOperationError,),
        default_return=[],
        raise_on_error=False
    )
    def move_downloaded_files(self, 
                             temp_path: str, 
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
        with error_context("创建目标目录", FileOperationError, logger_name=__name__):
            os.makedirs(target_path, exist_ok=True)
        
        if not os.path.exists(temp_path):
            raise FileOperationError(f"临时目录不存在: {temp_path}")
        
        temp_files = os.listdir(temp_path)
        moved_files = []
        error_collector = ErrorCollector(logger_name=__name__)
        
        self.logger.info(
            f"开始移动文件",
            extra={
                "source": temp_path,
                "target": target_path,
                "file_count": len(temp_files)
            }
        )
        
        for file_name in temp_files:
            with error_collector:
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
                    self.logger.debug(f"文件已移动: {file_name} -> {target_file_path}")
        
        self.logger.info(
            f"文件移动完成",
            extra={
                "moved": len(moved_files),
                "errors": len(error_collector.get_errors())
            }
        )
        
        return moved_files
    
    @error_handler(
        exceptions=(FileOperationError,),
        raise_on_error=False,
        error_message="清理临时目录失败"
    )
    def clean_temp_directory(self, temp_path: str):
        """清理临时目录"""
        if not os.path.exists(temp_path):
            self.logger.warning(f"临时目录不存在: {temp_path}")
            return
        
        file_count = 0
        error_count = 0
        
        for file in os.listdir(temp_path):
            file_path = os.path.join(temp_path, file)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    file_count += 1
                except Exception as e:
                    self.logger.error(f"删除文件失败 {file_path}: {e}")
                    error_count += 1
        
        self.logger.info(
            f"临时目录清理完成",
            extra={
                "path": temp_path,
                "deleted": file_count,
                "errors": error_count
            }
        )


# 便捷函数
@error_handler(
    exceptions=(DownloadError,),
    default_return=False,
    logger_name=__name__
)
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
    logger = get_logger(__name__)
    
    try:
        downloader = BilibiliDownloader(proxy_url=proxy_url)
        return downloader.get_user_videos_sync(uid)
    except Exception as e:
        logger.error(f"获取用户视频失败: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    # 测试代码
    logger = get_logger(__name__)
    logger.info("=== B站下载器测试 ===")
    
    # 测试单个视频下载
    test_url = "https://www.bilibili.com/video/BV1LCM3zwEH9"
    
    try:
        logger.info(f"测试下载: {test_url}")
        success = download_single_video(test_url, "./test_temp", only_audio=True)
        
        if success:
            logger.info("下载测试成功！")
            
            # 测试文件移动
            file_manager = FileManager()
            moved_files = file_manager.move_downloaded_files("./test_temp", "./test_audio")
            logger.info(f"移动文件: {moved_files}")
            
            # 清理临时目录
            file_manager.clean_temp_directory("./test_temp")
        else:
            logger.error("下载测试失败")
            
    except Exception as e:
        logger.error(f"测试过程出错: {e}", exc_info=True)