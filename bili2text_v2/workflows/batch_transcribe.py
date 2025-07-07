#!/usr/bin/env python3
"""
批量转录工作流
替代原来的main.py，提供批量视频下载和转录功能
"""

import sys
import os

# 添加core模块到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.whisper_transcriber import WhisperTranscriber
from core.bilibili_downloader import BilibiliDownloader
from core.markdown_generator import MarkdownGenerator
from core.file_manager import FileManager, StatusTracker, VideoInfoManager


class BatchTranscribeWorkflow:
    """批量转录工作流类"""
    
    def __init__(self, 
                 base_dir: str = ".",
                 whisper_model: str = "medium",
                 proxy_url: str = None):
        """
        初始化批量转录工作流
        
        Args:
            base_dir: 工作目录
            whisper_model: Whisper模型名称
            proxy_url: 代理URL
        """
        self.base_dir = base_dir
        self.whisper_model = whisper_model
        self.proxy_url = proxy_url
        
        # 初始化各个组件
        self.file_manager = FileManager(base_dir)
        self.downloader = BilibiliDownloader(proxy_url=proxy_url)
        self.transcriber = WhisperTranscriber(model_name=whisper_model)
        self.md_generator = MarkdownGenerator(
            output_dir=os.path.join(base_dir, "result")
        )
        
        # 状态跟踪器
        self.downloaded_tracker = StatusTracker(
            os.path.join(base_dir, "downloaded_videos.txt")
        )
        self.transcribed_tracker = StatusTracker(
            os.path.join(base_dir, "transcribed_audios.txt")
        )
        
        # 视频信息管理器
        self.video_info_manager = VideoInfoManager(
            os.path.join(base_dir, "video_info.json")
        )
    
    def setup_environment(self):
        """设置工作环境"""
        print("=== 批量转录工作流 ===")
        print("设置工作环境...")
        self.file_manager.setup_directories()
        
        print(f"工作目录: {os.path.abspath(self.base_dir)}")
        print(f"Whisper模型: {self.whisper_model}")
        print(f"代理设置: {self.proxy_url or '未启用'}")
    
    def download_videos(self, video_urls: list) -> dict:
        """
        下载视频列表
        
        Args:
            video_urls: 视频URL列表
            
        Returns:
            下载结果字典
        """
        print(f"\n开始下载 {len(video_urls)} 个视频...")
        
        download_results = {}
        
        for i, video_url in enumerate(video_urls, 1):
            print(f"\n下载进度: {i}/{len(video_urls)}")
            print(f"视频URL: {video_url}")
            
            # 提取BVID
            bvid = self._extract_bvid(video_url)
            if not bvid:
                print(f"无法提取BVID: {video_url}")
                download_results[video_url] = {"success": False, "error": "无效URL"}
                continue
            
            # 检查是否已下载
            if self.downloaded_tracker.is_processed(bvid):
                print(f"视频 {bvid} 已下载，跳过")
                download_results[video_url] = {"success": True, "bvid": bvid, "skipped": True}
                continue
            
            try:
                # 清理临时目录
                self.file_manager.clean_directory(self.file_manager.temp_dir)
                
                # 下载音频
                success = self.downloader.download_video_audio_sync(
                    video_url, 
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
                        
                        # 记录下载状态
                        self.downloaded_tracker.add_processed(bvid)
                        
                        # 记录视频信息（简化版，没有详细信息）
                        self.video_info_manager.add_video_info(
                            bvid=bvid,
                            title=f"视频_{bvid}",
                            desc="批量下载的视频",
                            audio_filename=audio_filename
                        )
                        
                        download_results[video_url] = {
                            "success": True, 
                            "bvid": bvid,
                            "audio_file": audio_filename
                        }
                        print(f"下载成功: {bvid}")
                    else:
                        download_results[video_url] = {
                            "success": False, 
                            "error": "文件移动失败"
                        }
                else:
                    download_results[video_url] = {
                        "success": False, 
                        "error": "下载失败"
                    }
                    
            except Exception as e:
                print(f"下载视频 {video_url} 时出错: {e}")
                download_results[video_url] = {"success": False, "error": str(e)}
        
        success_count = sum(1 for r in download_results.values() if r.get("success"))
        print(f"\n下载完成！成功: {success_count}/{len(video_urls)}")
        
        return download_results
    
    def transcribe_audios(self, audio_files: list = None) -> dict:
        """
        转录音频文件
        
        Args:
            audio_files: 音频文件列表，None表示转录所有音频
            
        Returns:
            转录结果字典
        """
        if audio_files is None:
            audio_files = self.file_manager.get_audio_files()
        
        if not audio_files:
            print("没有找到音频文件")
            return {}
        
        print(f"\n开始转录 {len(audio_files)} 个音频文件...")
        
        transcribe_results = {}
        
        for i, audio_filename in enumerate(audio_files, 1):
            print(f"\n转录进度: {i}/{len(audio_files)}")
            print(f"音频文件: {audio_filename}")
            
            # 检查是否已转录
            if self.transcribed_tracker.is_processed(audio_filename):
                print(f"音频 {audio_filename} 已转录，跳过")
                transcribe_results[audio_filename] = {"success": True, "skipped": True}
                continue
            
            try:
                # 执行转录
                audio_path = os.path.join(self.file_manager.audio_dir, audio_filename)
                result = self.transcriber.transcribe_audio(audio_path)
                
                # 获取视频信息
                video_info = self.video_info_manager.get_info_by_audio_filename(audio_filename)
                
                if video_info:
                    bvid = video_info["bvid"]
                    title = video_info["title"]
                    desc = video_info["desc"]
                else:
                    # 如果没有视频信息，使用默认信息
                    bvid = audio_filename.split("_")[0] if "_" in audio_filename else "unknown"
                    title = f"音频转录_{os.path.splitext(audio_filename)[0]}"
                    desc = "批量转录的音频文件"
                
                # 生成Markdown文件
                md_path = self.md_generator.create_video_markdown(
                    bvid=bvid,
                    title=title,
                    desc=desc,
                    transcribed_text=result["text"],
                    audio_filename=audio_filename
                )
                
                # 记录转录状态
                self.transcribed_tracker.add_processed(audio_filename)
                
                transcribe_results[audio_filename] = {
                    "success": True,
                    "text": result["text"],
                    "duration": result["duration"],
                    "markdown_file": md_path
                }
                
                print(f"转录成功: {audio_filename}")
                
            except Exception as e:
                print(f"转录音频 {audio_filename} 时出错: {e}")
                transcribe_results[audio_filename] = {"success": False, "error": str(e)}
        
        success_count = sum(1 for r in transcribe_results.values() if r.get("success"))
        print(f"\n转录完成！成功: {success_count}/{len(audio_files)}")
        
        return transcribe_results
    
    def run_full_workflow(self, video_urls: list) -> dict:
        """
        运行完整的下载+转录工作流
        
        Args:
            video_urls: 视频URL列表
            
        Returns:
            完整的处理结果
        """
        print("=== 开始完整的批量转录工作流 ===")
        
        # 设置环境
        self.setup_environment()
        
        # 下载视频
        download_results = self.download_videos(video_urls)
        
        # 转录音频
        transcribe_results = self.transcribe_audios()
        
        # 生成结果摘要
        summary_results = {
            "download_results": download_results,
            "transcribe_results": transcribe_results,
            "stats": {
                "total_videos": len(video_urls),
                "successful_downloads": sum(1 for r in download_results.values() if r.get("success")),
                "successful_transcriptions": sum(1 for r in transcribe_results.values() if r.get("success"))
            }
        }
        
        # 生成摘要文件
        summary_md = self.md_generator.create_batch_summary(
            summary_results, "batch_workflow_summary"
        )
        
        print(f"\n=== 工作流完成 ===")
        print(f"下载成功: {summary_results['stats']['successful_downloads']}/{summary_results['stats']['total_videos']}")
        print(f"转录成功: {summary_results['stats']['successful_transcriptions']}")
        print(f"摘要文件: {summary_md}")
        
        return summary_results
    
    def _extract_bvid(self, url: str) -> str:
        """从URL中提取BVID"""
        if "bilibili.com/video/" in url:
            # 提取BV号
            parts = url.split("/video/")
            if len(parts) > 1:
                bvid_part = parts[1].split("?")[0].split("/")[0]
                return bvid_part
        elif url.startswith("BV"):
            # 直接是BV号
            return url.split("?")[0]
        return None


def main():
    """主函数"""
    # 配置要处理的视频URL列表
    video_urls = [
        "https://www.bilibili.com/video/BV1LCM3zwEH9/?spm_id_from=333.1391.0.0",
        # 可以在这里添加更多视频URL
    ]
    
    # 创建工作流实例
    workflow = BatchTranscribeWorkflow(
        base_dir=".",
        whisper_model="medium",  # 可以改为 "tiny", "base", "large-v3" 等
        proxy_url=None  # 如需要代理，设置为 "http://127.0.0.1:7890"
    )
    
    try:
        # 运行完整工作流
        results = workflow.run_full_workflow(video_urls)
        
        print("\n=== 处理结果 ===")
        print(f"总视频数: {results['stats']['total_videos']}")
        print(f"下载成功: {results['stats']['successful_downloads']}")
        print(f"转录成功: {results['stats']['successful_transcriptions']}")
        
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n工作流执行失败: {e}")


if __name__ == "__main__":
    main()