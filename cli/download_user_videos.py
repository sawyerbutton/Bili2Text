#!/usr/bin/env python3
"""
Bili2Text - 批量下载UP主所有视频工具
======================================

功能：批量下载指定B站UP主的所有视频
支持：
    - 通过UP主ID(UID)或用户名获取视频列表
    - 批量下载所有视频
    - 支持仅下载音频或完整视频
    - 断点续传，避免重复下载
    - 支持设置代理
"""

import asyncio
import argparse
import os
import sys
import json
from pathlib import Path
from datetime import datetime
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 检查依赖
try:
    from bilibili_api import user, search
    from bilibili_api import request_settings as settings
    from bilix.sites.bilibili import DownloaderBilibili
    DEPS_AVAILABLE = True
except ImportError as e:
    DEPS_AVAILABLE = False
    logger.error(f"缺少必要的依赖库: {e}")
    logger.error("请安装：pip install bilibili-api-python bilix")


class BiliUserVideoDownloader:
    """B站UP主视频批量下载器"""
    
    def __init__(self, uid=None, username=None, output_dir="./storage/video", 
                 audio_only=False, use_proxy=False, proxy_url="http://127.0.0.1:7890"):
        """
        初始化下载器
        
        Args:
            uid: UP主的UID
            username: UP主的用户名（如果没有UID）
            output_dir: 输出目录
            audio_only: 是否仅下载音频
            use_proxy: 是否使用代理
            proxy_url: 代理地址
        """
        self.uid = uid
        self.username = username
        self.output_dir = Path(output_dir)
        self.audio_only = audio_only
        self.use_proxy = use_proxy
        self.proxy_url = proxy_url
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 记录文件路径
        self.record_file = self.output_dir / f"downloaded_{uid or username}.txt"
        
        # 设置代理
        if use_proxy:
            settings.set_proxy(proxy_url)
            logger.info(f"使用代理: {proxy_url}")
    
    def load_downloaded_videos(self):
        """加载已下载的视频列表"""
        if self.record_file.exists():
            with open(self.record_file, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f if line.strip())
        return set()
    
    def save_downloaded_video(self, bvid):
        """保存已下载的视频ID"""
        with open(self.record_file, 'a', encoding='utf-8') as f:
            f.write(f"{bvid}\n")
    
    async def search_user_by_name(self, username):
        """通过用户名搜索用户并获取UID"""
        try:
            logger.info(f"搜索用户: {username}")
            search_result = await search.search_by_type(
                keyword=username,
                search_type=search.SearchObjectType.USER,
                page=1
            )
            
            if not search_result or 'result' not in search_result:
                logger.error(f"未找到用户: {username}")
                return None
            
            users = search_result.get('result', [])
            if not users:
                logger.error(f"未找到用户: {username}")
                return None
            
            # 获取第一个匹配的用户
            target_user = users[0]
            uid = target_user['mid']
            uname = target_user.get('uname', 'Unknown')
            logger.info(f"找到用户: {uname} (UID: {uid})")
            return uid
            
        except Exception as e:
            logger.error(f"搜索用户时出错: {e}")
            return None
    
    async def get_all_videos_from_dynamics(self, uid):
        """从动态中获取所有视频信息"""
        video_list = []
        u = user.User(uid)
        
        try:
            logger.info("开始获取用户动态...")
            
            # 尝试新API
            try:
                result = await u.get_dynamics_new()
                if result and "items" in result:
                    dynamics = result["items"]
                    logger.info(f"获取到 {len(dynamics)} 条动态（新API）")
                    
                    for dynamic in dynamics:
                        if dynamic.get('type') == 'DYNAMIC_TYPE_AV':
                            modules = dynamic.get('modules', {})
                            module_dynamic = modules.get('module_dynamic', {})
                            major = module_dynamic.get('major', {})
                            archive = major.get('archive', {})
                            
                            bvid = archive.get('bvid')
                            title = archive.get('title', '无标题')
                            desc = archive.get('desc', '')
                            
                            if bvid:
                                video_list.append({
                                    'bvid': bvid,
                                    'title': title,
                                    'desc': desc
                                })
            except:
                # 尝试旧API
                logger.info("新API失败，尝试旧API...")
                page = await u.get_dynamics(0)
                if "cards" in page:
                    dynamics = page["cards"]
                    logger.info(f"获取到 {len(dynamics)} 条动态（旧API）")
                    
                    # 获取后续页面
                    offset = page.get("next_offset", 0)
                    while offset > 0:
                        try:
                            page = await u.get_dynamics(offset)
                            if "cards" in page:
                                dynamics.extend(page["cards"])
                            offset = page.get("next_offset", 0)
                        except:
                            break
                    
                    # 提取视频信息
                    for dynamic in dynamics:
                        try:
                            if 'desc' in dynamic and 'bvid' in dynamic['desc']:
                                bvid = dynamic['desc']['bvid']
                                card = dynamic.get('card', {})
                                title = card.get('title', '无标题')
                                desc = card.get('dynamic', '')
                                
                                video_list.append({
                                    'bvid': bvid,
                                    'title': title,
                                    'desc': desc
                                })
                        except:
                            continue
            
            logger.info(f"共找到 {len(video_list)} 个视频")
            return video_list
            
        except Exception as e:
            logger.error(f"获取动态时出错: {e}")
            return video_list
    
    async def get_all_videos_from_space(self, uid):
        """从用户空间获取所有投稿视频"""
        video_list = []
        u = user.User(uid)
        
        try:
            logger.info("获取用户投稿视频...")
            page = 1
            ps = 30  # 每页数量
            
            while True:
                try:
                    # 获取视频列表
                    videos = await u.get_videos(ps=ps, pn=page)
                    
                    if not videos or 'list' not in videos:
                        break
                    
                    vlist = videos['list'].get('vlist', [])
                    if not vlist:
                        break
                    
                    for video in vlist:
                        video_list.append({
                            'bvid': video.get('bvid'),
                            'title': video.get('title', '无标题'),
                            'desc': video.get('description', '')
                        })
                    
                    logger.info(f"第 {page} 页，获取 {len(vlist)} 个视频")
                    
                    # 检查是否还有更多页
                    if len(vlist) < ps:
                        break
                    
                    page += 1
                    
                except Exception as e:
                    logger.warning(f"获取第 {page} 页视频时出错: {e}")
                    break
            
            logger.info(f"共获取 {len(video_list)} 个投稿视频")
            return video_list
            
        except Exception as e:
            logger.error(f"获取投稿视频时出错: {e}")
            return video_list
    
    async def download_video(self, bvid, title):
        """下载单个视频"""
        url = f"https://www.bilibili.com/video/{bvid}"
        
        try:
            logger.info(f"开始下载: {title} ({bvid})")
            
            # 为每个UP主创建单独的目录
            up_dir = self.output_dir / (str(self.uid) if self.uid else self.username)
            up_dir.mkdir(parents=True, exist_ok=True)
            
            async with DownloaderBilibili() as d:
                await d.get_video(url, path=str(up_dir), only_audio=self.audio_only)
            
            logger.info(f"下载完成: {title}")
            return True
            
        except Exception as e:
            logger.error(f"下载失败 {bvid}: {e}")
            return False
    
    async def run(self):
        """执行批量下载"""
        # 如果提供用户名而不是UID，先搜索获取UID
        if not self.uid and self.username:
            self.uid = await self.search_user_by_name(self.username)
            if not self.uid:
                logger.error("无法获取用户UID，退出")
                return
        
        if not self.uid:
            logger.error("请提供UID或用户名")
            return
        
        # 获取用户信息
        u = user.User(self.uid)
        try:
            user_info = await u.get_user_info()
            username = user_info.get('name', 'Unknown')
            logger.info(f"UP主: {username} (UID: {self.uid})")
        except:
            logger.warning("无法获取用户信息")
        
        # 获取视频列表（优先从投稿空间获取，失败则从动态获取）
        video_list = await self.get_all_videos_from_space(self.uid)
        
        if not video_list:
            logger.info("从投稿空间获取失败，尝试从动态获取...")
            video_list = await self.get_all_videos_from_dynamics(self.uid)
        
        if not video_list:
            logger.error("未获取到任何视频")
            return
        
        # 加载已下载记录
        downloaded = self.load_downloaded_videos()
        
        # 统计信息
        total = len(video_list)
        skipped = 0
        success = 0
        failed = 0
        
        # 批量下载
        for i, video in enumerate(video_list, 1):
            bvid = video['bvid']
            title = video['title']
            
            logger.info(f"\n进度: {i}/{total}")
            
            # 检查是否已下载
            if bvid in downloaded:
                logger.info(f"跳过已下载: {title}")
                skipped += 1
                continue
            
            # 下载视频
            if await self.download_video(bvid, title):
                self.save_downloaded_video(bvid)
                success += 1
            else:
                failed += 1
            
            # 添加延时避免请求过快
            await asyncio.sleep(1)
        
        # 输出统计
        logger.info("\n" + "="*50)
        logger.info(f"下载完成统计:")
        logger.info(f"  总计: {total} 个视频")
        logger.info(f"  成功: {success} 个")
        logger.info(f"  跳过: {skipped} 个")
        logger.info(f"  失败: {failed} 个")


def main(args):
    """主函数"""
    if not DEPS_AVAILABLE:
        logger.error("缺少必要的依赖，请先安装：")
        logger.error("pip install bilibili-api-python bilix")
        return 1
    
    # 创建下载器
    downloader = BiliUserVideoDownloader(
        uid=args.uid,
        username=args.user,
        output_dir=args.output,
        audio_only=args.audio_only,
        use_proxy=args.proxy,
        proxy_url=args.proxy_url
    )
    
    # 运行下载
    try:
        asyncio.run(downloader.run())
        return 0
    except KeyboardInterrupt:
        logger.info("\n用户中断下载")
        return 1
    except Exception as e:
        logger.error(f"执行出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='批量下载B站UP主所有视频')
    
    # 用户标识（二选一）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--uid', type=int, help='UP主的UID')
    group.add_argument('--user', type=str, help='UP主的用户名')
    
    # 下载选项
    parser.add_argument('--output', default='./storage/video',
                        help='输出目录 (默认: ./storage/video)')
    parser.add_argument('--audio-only', action='store_true',
                        help='仅下载音频')
    
    # 代理设置
    parser.add_argument('--proxy', action='store_true',
                        help='使用代理')
    parser.add_argument('--proxy-url', default='http://127.0.0.1:7890',
                        help='代理地址 (默认: http://127.0.0.1:7890)')
    
    args = parser.parse_args()
    sys.exit(main(args))