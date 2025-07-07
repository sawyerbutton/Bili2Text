#!/usr/bin/env python3
"""
InfinityAcademy专用工作流
替代原来的get_all_dynamics_infinityacademy.py和相关脚本
"""

import sys
import os

# 添加core模块到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.whisper_transcriber import WhisperTranscriber
from core.bilibili_downloader import BilibiliDownloader
from core.markdown_generator import MarkdownGenerator
from core.file_manager import FileManager, StatusTracker, VideoInfoManager


class InfinityAcademyWorkflow:
    """InfinityAcademy专用工作流类"""
    
    def __init__(self, 
                 base_dir: str = ".",
                 whisper_model: str = "medium",
                 proxy_url: str = None,
                 uid: int = 10642220):
        """
        初始化InfinityAcademy工作流
        
        Args:
            base_dir: 工作目录
            whisper_model: Whisper模型名称
            proxy_url: 代理URL
            uid: InfinityAcademy的B站UID
        """
        self.base_dir = base_dir
        self.whisper_model = whisper_model
        self.proxy_url = proxy_url
        self.uid = uid
        
        # 初始化各个组件
        self.file_manager = FileManager(base_dir)
        self.downloader = BilibiliDownloader(proxy_url=proxy_url)
        self.transcriber = WhisperTranscriber(model_name=whisper_model)
        self.md_generator = MarkdownGenerator(
            output_dir=os.path.join(base_dir, "result")
        )
        
        # 状态跟踪器
        self.downloaded_tracker = StatusTracker(
            os.path.join(base_dir, "downloaded_infinityacademy.txt")
        )
        self.transcribed_tracker = StatusTracker(
            os.path.join(base_dir, "transcribed_infinityacademy.txt")
        )
        
        # 视频信息管理器
        self.video_info_manager = VideoInfoManager(
            os.path.join(base_dir, "video_info_infinityacademy.json")
        )
    
    def setup_environment(self):
        """设置工作环境"""
        print("=== InfinityAcademy 工作流 ===")
        print(f"目标用户UID: {self.uid}")
        print("设置工作环境...")
        self.file_manager.setup_directories()
        
        print(f"工作目录: {os.path.abspath(self.base_dir)}")
        print(f"Whisper模型: {self.whisper_model}")
        print(f"代理设置: {self.proxy_url or '未启用'}")
    
    def fetch_all_videos(self) -> list:
        """
        获取用户的所有视频信息
        
        Returns:
            视频信息列表
        """
        print(f"\n开始获取用户 {self.uid} 的所有视频...")
        
        try:
            video_infos = self.downloader.get_user_videos_sync(self.uid)
            
            if not video_infos:
                print("没有找到任何视频")
                return []
            
            print(f"获取到 {len(video_infos)} 个视频")
            
            # 保存视频信息到管理器
            for video_info in video_infos:
                self.video_info_manager.add_video_info(
                    bvid=video_info["bvid"],
                    title=video_info["title"],
                    desc=video_info["desc"],
                    extra_info={"url": video_info["url"]}
                )
            
            # 生成视频列表表格
            self.md_generator.create_video_info_table(
                video_infos, f"infinityacademy_video_list"
            )
            
            return video_infos
            
        except Exception as e:
            print(f"获取视频信息失败: {e}")
            return []
    
    def download_all_audios(self, video_infos: list = None) -> dict:
        """
        下载所有视频的音频
        
        Args:
            video_infos: 视频信息列表，None表示从文件加载
            
        Returns:
            下载结果字典
        """
        if video_infos is None:
            # 从视频信息管理器加载
            all_video_info = self.video_info_manager.get_all_video_info()
            video_infos = [
                {
                    "bvid": info["bvid"],
                    "title": info["title"],
                    "desc": info["desc"],
                    "url": info.get("url", f"https://www.bilibili.com/video/{info['bvid']}")
                }
                for info in all_video_info.values()
            ]
        
        if not video_infos:
            print("没有视频信息可供下载")
            return {}
        
        print(f"\n开始下载 {len(video_infos)} 个视频的音频...")
        
        download_results = {}
        downloaded_count = 0
        
        for i, video_info in enumerate(video_infos, 1):
            bvid = video_info["bvid"]
            title = video_info["title"]
            desc = video_info["desc"]
            url = video_info["url"]
            
            print(f"\n下载进度: {i}/{len(video_infos)}")
            print(f"视频ID: {bvid}")
            print(f"标题: {title}")
            
            # 检查是否已下载
            if self.downloaded_tracker.is_processed(bvid):
                print(f"视频 {bvid} 已下载，跳过")
                download_results[bvid] = {"success": True, "skipped": True}
                continue
            
            try:
                # 清理临时目录
                self.file_manager.clean_directory(self.file_manager.temp_dir)
                
                # 下载音频
                success = self.downloader.download_video_audio_sync(
                    url, 
                    self.file_manager.temp_dir, 
                    only_audio=True
                )
                
                if success:
                    # 移动音频文件
                    moved_files = self.file_manager.move_files(
                        self.file_manager.temp_dir,
                        self.file_manager.audio_dir,
                        file_prefix=bvid
                    )
                    
                    if moved_files:
                        audio_filename = os.path.basename(moved_files[0])
                        
                        # 更新视频信息，添加音频文件名
                        self.video_info_manager.add_video_info(
                            bvid=bvid,
                            title=title,
                            desc=desc,
                            audio_filename=audio_filename,
                            extra_info={"url": url}
                        )
                        
                        # 记录下载状态
                        self.downloaded_tracker.add_processed(bvid)
                        downloaded_count += 1
                        
                        download_results[bvid] = {
                            "success": True,
                            "audio_file": audio_filename,
                            "title": title
                        }
                        
                        print(f"下载成功: {audio_filename}")
                    else:
                        download_results[bvid] = {
                            "success": False,
                            "error": "文件移动失败"
                        }
                else:
                    download_results[bvid] = {
                        "success": False,
                        "error": "下载失败"
                    }
                    
            except Exception as e:
                print(f"下载视频 {bvid} 时出错: {e}")
                download_results[bvid] = {"success": False, "error": str(e)}
        
        print(f"\n下载完成！成功下载 {downloaded_count} 个新视频的音频文件")
        return download_results
    
    def transcribe_all_audios(self) -> dict:
        """
        转录所有音频文件
        
        Returns:
            转录结果字典
        """
        audio_files = self.file_manager.get_audio_files()
        
        if not audio_files:
            print("没有找到音频文件")
            return {}
        
        print(f"\n开始转录 {len(audio_files)} 个音频文件...")
        
        transcribe_results = {}
        transcribed_count = 0
        
        for i, audio_filename in enumerate(audio_files, 1):
            print(f"\n转录进度: {i}/{len(audio_files)}")
            print(f"音频文件: {audio_filename}")
            
            # 检查是否已转录
            if self.transcribed_tracker.is_processed(audio_filename):
                print(f"音频 {audio_filename} 已转录，跳过")
                transcribe_results[audio_filename] = {"success": True, "skipped": True}
                continue
            
            # 获取视频信息
            video_info = self.video_info_manager.get_info_by_audio_filename(audio_filename)
            
            if not video_info:
                print(f"音频文件 {audio_filename} 没有对应的视频信息，跳过")
                transcribe_results[audio_filename] = {
                    "success": False,
                    "error": "缺少视频信息"
                }
                continue
            
            bvid = video_info["bvid"]
            title = video_info["title"]
            desc = video_info["desc"]
            
            print(f"视频ID: {bvid}")
            print(f"标题: {title}")
            
            try:
                # 执行转录
                audio_path = os.path.join(self.file_manager.audio_dir, audio_filename)
                result = self.transcriber.transcribe_audio(audio_path)
                
                # 生成Markdown文件
                md_path = self.md_generator.create_video_markdown(
                    bvid=bvid,
                    title=title,
                    desc=desc,
                    transcribed_text=result["text"],
                    audio_filename=audio_filename,
                    custom_tags=["InfinityAcademy", "转录"]
                )
                
                # 记录转录状态
                self.transcribed_tracker.add_processed(audio_filename)
                transcribed_count += 1
                
                transcribe_results[audio_filename] = {
                    "success": True,
                    "text": result["text"],
                    "duration": result["duration"],
                    "markdown_file": md_path,
                    "bvid": bvid,
                    "title": title
                }
                
                print(f"转录成功: {md_path}")
                
            except Exception as e:
                print(f"转录音频 {audio_filename} 时出错: {e}")
                transcribe_results[audio_filename] = {"success": False, "error": str(e)}
        
        print(f"\n转录完成！成功转录 {transcribed_count} 个新音频文件")
        return transcribe_results
    
    def run_download_only_workflow(self) -> dict:
        """
        仅运行下载工作流
        
        Returns:
            下载结果
        """
        print("=== 开始 InfinityAcademy 下载工作流 ===")
        
        # 设置环境
        self.setup_environment()
        
        # 获取视频信息
        video_infos = self.fetch_all_videos()
        
        if not video_infos:
            return {"error": "没有获取到视频信息"}
        
        # 下载音频
        download_results = self.download_all_audios(video_infos)
        
        return {
            "video_count": len(video_infos),
            "download_results": download_results,
            "stats": {
                "total_videos": len(video_infos),
                "successful_downloads": sum(1 for r in download_results.values() if r.get("success"))
            }
        }
    
    def run_transcribe_only_workflow(self) -> dict:
        """
        仅运行转录工作流
        
        Returns:
            转录结果
        """
        print("=== 开始 InfinityAcademy 转录工作流 ===")
        
        # 设置环境
        self.setup_environment()
        
        # 转录音频
        transcribe_results = self.transcribe_all_audios()
        
        return {
            "transcribe_results": transcribe_results,
            "stats": {
                "successful_transcriptions": sum(1 for r in transcribe_results.values() if r.get("success"))
            }
        }
    
    def run_full_workflow(self) -> dict:
        """
        运行完整的获取+下载+转录工作流
        
        Returns:
            完整的处理结果
        """
        print("=== 开始完整的 InfinityAcademy 工作流 ===")
        
        # 设置环境
        self.setup_environment()
        
        # 获取视频信息
        video_infos = self.fetch_all_videos()
        
        if not video_infos:
            return {"error": "没有获取到视频信息"}
        
        # 下载音频
        download_results = self.download_all_audios(video_infos)
        
        # 转录音频
        transcribe_results = self.transcribe_all_audios()
        
        # 生成结果摘要
        summary_results = {
            "video_infos": video_infos,
            "download_results": download_results,
            "transcribe_results": transcribe_results,
            "stats": {
                "total_videos": len(video_infos),
                "successful_downloads": sum(1 for r in download_results.values() if r.get("success")),
                "successful_transcriptions": sum(1 for r in transcribe_results.values() if r.get("success"))
            }
        }
        
        # 生成摘要文件
        summary_md = self.md_generator.create_batch_summary(
            summary_results, "infinityacademy_workflow_summary"
        )
        
        print(f"\n=== InfinityAcademy 工作流完成 ===")
        print(f"获取视频: {summary_results['stats']['total_videos']}")
        print(f"下载成功: {summary_results['stats']['successful_downloads']}")
        print(f"转录成功: {summary_results['stats']['successful_transcriptions']}")
        print(f"摘要文件: {summary_md}")
        
        return summary_results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="InfinityAcademy 专用工作流")
    parser.add_argument("--mode", choices=["full", "download", "transcribe"], 
                       default="full", help="运行模式")
    parser.add_argument("--model", default="medium", 
                       help="Whisper模型 (tiny/base/small/medium/large/large-v3)")
    parser.add_argument("--proxy", help="代理URL，如 http://127.0.0.1:7890")
    parser.add_argument("--uid", type=int, default=10642220, 
                       help="B站用户UID")
    
    args = parser.parse_args()
    
    # 创建工作流实例
    workflow = InfinityAcademyWorkflow(
        base_dir=".",
        whisper_model=args.model,
        proxy_url=args.proxy,
        uid=args.uid
    )
    
    try:
        if args.mode == "full":
            results = workflow.run_full_workflow()
        elif args.mode == "download":
            results = workflow.run_download_only_workflow()
        elif args.mode == "transcribe":
            results = workflow.run_transcribe_only_workflow()
        
        if "error" in results:
            print(f"工作流失败: {results['error']}")
        else:
            print("\n=== 处理结果 ===")
            if "stats" in results:
                stats = results["stats"]
                if "total_videos" in stats:
                    print(f"总视频数: {stats['total_videos']}")
                if "successful_downloads" in stats:
                    print(f"下载成功: {stats['successful_downloads']}")
                if "successful_transcriptions" in stats:
                    print(f"转录成功: {stats['successful_transcriptions']}")
        
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n工作流执行失败: {e}")


if __name__ == "__main__":
    main()