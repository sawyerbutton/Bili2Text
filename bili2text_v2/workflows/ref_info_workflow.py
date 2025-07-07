#!/usr/bin/env python3
"""
参考信息系列工作流
替代原来的get_ref_from_dynamics.py，专门处理"参考信息"系列视频
"""

import sys
import os
import re

# 添加core模块到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.whisper_transcriber import WhisperTranscriber
from core.bilibili_downloader import BilibiliDownloader
from core.markdown_generator import MarkdownGenerator
from core.file_manager import FileManager, StatusTracker, VideoInfoManager


class RefInfoWorkflow:
    """参考信息系列工作流类"""
    
    def __init__(self, 
                 base_dir: str = ".",
                 whisper_model: str = "medium",
                 proxy_url: str = None,
                 uid: int = 1556651916):  # 小黛晨读的UID
        """
        初始化参考信息工作流
        
        Args:
            base_dir: 工作目录
            whisper_model: Whisper模型名称
            proxy_url: 代理URL
            uid: 小黛晨读的B站UID
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
        self.processed_tracker = StatusTracker(
            os.path.join(base_dir, "processed_ref_info.txt")
        )
        
        # 视频信息管理器
        self.video_info_manager = VideoInfoManager(
            os.path.join(base_dir, "video_info_ref_info.json")
        )
    
    def setup_environment(self):
        """设置工作环境"""
        print("=== 参考信息系列工作流 ===")
        print(f"目标用户UID: {self.uid} (小黛晨读)")
        print("设置工作环境...")
        self.file_manager.setup_directories()
        
        print(f"工作目录: {os.path.abspath(self.base_dir)}")
        print(f"Whisper模型: {self.whisper_model}")
        print(f"代理设置: {self.proxy_url or '未启用'}")
    
    async def get_latest_ref_info_video(self):
        """
        获取最新的参考信息系列视频
        
        Returns:
            视频信息字典或None
        """
        try:
            # 获取用户最新动态
            video_infos = await self.downloader.get_user_dynamics_videos(self.uid)
            
            # 筛选参考信息系列视频
            for video_info in video_infos:
                title = video_info.get("title", "")
                if "参考信息" in title:
                    return video_info
            
            print("在最新动态中没有找到参考信息系列视频")
            return None
            
        except Exception as e:
            print(f"获取最新视频信息失败: {e}")
            return None
    
    def get_latest_ref_info_video_sync(self):
        """同步版本的获取最新参考信息视频"""
        import asyncio
        return asyncio.run(self.get_latest_ref_info_video())
    
    def normalize_ref_info_title(self, title: str) -> str:
        """
        标准化参考信息系列标题格式
        
        Args:
            title: 原始标题
            
        Returns:
            标准化后的标题
        """
        # 【参考信息第X期】-> 【参考信息X】
        normalized_title = re.sub(r"【参考信息第(.*?)期】(.*?)", r"【参考信息\1】\2", title)
        return normalized_title
    
    def process_latest_ref_info(self) -> dict:
        """
        处理最新的参考信息视频
        
        Returns:
            处理结果字典
        """
        print("\n开始处理最新的参考信息视频...")
        
        # 获取最新视频信息
        video_info = self.get_latest_ref_info_video_sync()
        
        if not video_info:
            return {"error": "没有找到参考信息系列视频"}
        
        bvid = video_info["bvid"]
        title_ori = video_info["title"]
        desc = video_info["desc"]
        url = video_info["url"]
        
        print(f"找到视频: {bvid}")
        print(f"原始标题: {title_ori}")
        
        # 检查是否为参考信息系列
        if "参考信息" not in title_ori:
            return {
                "error": "当前视频不是参考信息系列",
                "title": title_ori,
                "bvid": bvid
            }
        
        # 标准化标题
        title = self.normalize_ref_info_title(title_ori)
        print(f"标准化标题: {title}")
        
        # 检查是否已处理过
        if self.processed_tracker.is_processed(bvid):
            return {
                "error": "视频已经处理过",
                "bvid": bvid,
                "title": title,
                "already_processed": True
            }
        
        try:
            # 下载音频
            print(f"开始下载音频: {url}")
            
            # 清理临时目录
            self.file_manager.clean_directory(self.file_manager.temp_dir)
            
            # 下载音频
            success = self.downloader.download_video_audio_sync(
                url, 
                self.file_manager.temp_dir, 
                only_audio=True
            )
            
            if not success:
                return {
                    "error": "音频下载失败",
                    "bvid": bvid,
                    "title": title
                }
            
            print("音频下载完成")
            
            # 移动音频文件
            moved_files = self.file_manager.move_files(
                self.file_manager.temp_dir,
                self.file_manager.audio_dir
            )
            
            if not moved_files:
                return {
                    "error": "音频文件移动失败",
                    "bvid": bvid,
                    "title": title
                }
            
            audio_filename = os.path.basename(moved_files[0])
            audio_path = moved_files[0]
            
            print(f"音频文件保存为: {audio_filename}")
            
            # 保存视频信息
            self.video_info_manager.add_video_info(
                bvid=bvid,
                title=title,
                desc=desc,
                audio_filename=audio_filename,
                extra_info={
                    "url": url,
                    "original_title": title_ori,
                    "series": "参考信息"
                }
            )
            
            # 执行转录
            print("开始转录...")
            result = self.transcriber.transcribe_audio(
                audio_path,
                initial_prompt='"生于忧患，死于安乐。岂不快哉？"简体中文,加上标点。'
            )
            
            print(f"转录完成，耗时 {result['duration']} 秒")
            
            # 生成Markdown文件
            md_path = self.md_generator.create_video_markdown(
                bvid=bvid,
                title=title,
                desc=desc,
                transcribed_text=result["text"],
                audio_filename=audio_filename,
                custom_tags=["参考信息", "小黛晨读", "转录"]
            )
            
            # 记录已处理状态
            self.processed_tracker.add_processed(bvid)
            
            print(f"处理完成！结果保存到: {md_path}")
            
            return {
                "success": True,
                "bvid": bvid,
                "title": title,
                "desc": desc,
                "audio_file": audio_filename,
                "markdown_file": md_path,
                "transcription_text": result["text"],
                "transcription_duration": result["duration"]
            }
            
        except Exception as e:
            print(f"处理视频时出错: {e}")
            return {
                "error": f"处理失败: {str(e)}",
                "bvid": bvid,
                "title": title
            }
    
    def process_specific_ref_info(self, bvid_or_url: str) -> dict:
        """
        处理指定的参考信息视频
        
        Args:
            bvid_or_url: 视频BVID或URL
            
        Returns:
            处理结果字典
        """
        print(f"\n开始处理指定的参考信息视频: {bvid_or_url}")
        
        # 提取BVID
        if bvid_or_url.startswith("http"):
            # 从URL提取BVID
            if "bilibili.com/video/" in bvid_or_url:
                bvid = bvid_or_url.split("/video/")[1].split("?")[0].split("/")[0]
                url = bvid_or_url
            else:
                return {"error": "无效的B站视频URL"}
        else:
            # 直接是BVID
            bvid = bvid_or_url
            url = f"https://www.bilibili.com/video/{bvid}"
        
        print(f"视频BVID: {bvid}")
        print(f"视频URL: {url}")
        
        # 检查是否已处理过
        if self.processed_tracker.is_processed(bvid):
            return {
                "error": "视频已经处理过",
                "bvid": bvid,
                "already_processed": True
            }
        
        try:
            # 下载音频
            print(f"开始下载音频...")
            
            # 清理临时目录
            self.file_manager.clean_directory(self.file_manager.temp_dir)
            
            # 下载音频
            success = self.downloader.download_video_audio_sync(
                url, 
                self.file_manager.temp_dir, 
                only_audio=True
            )
            
            if not success:
                return {
                    "error": "音频下载失败",
                    "bvid": bvid
                }
            
            print("音频下载完成")
            
            # 移动音频文件
            moved_files = self.file_manager.move_files(
                self.file_manager.temp_dir,
                self.file_manager.audio_dir
            )
            
            if not moved_files:
                return {
                    "error": "音频文件移动失败",
                    "bvid": bvid
                }
            
            audio_filename = os.path.basename(moved_files[0])
            audio_path = moved_files[0]
            
            print(f"音频文件保存为: {audio_filename}")
            
            # 使用默认信息（因为没有从API获取详细信息）
            title = f"参考信息_{bvid}"
            desc = "手动指定的参考信息视频"
            
            # 保存视频信息
            self.video_info_manager.add_video_info(
                bvid=bvid,
                title=title,
                desc=desc,
                audio_filename=audio_filename,
                extra_info={
                    "url": url,
                    "series": "参考信息",
                    "manual_input": True
                }
            )
            
            # 执行转录
            print("开始转录...")
            result = self.transcriber.transcribe_audio(
                audio_path,
                initial_prompt='"生于忧患，死于安乐。岂不快哉？"简体中文,加上标点。'
            )
            
            print(f"转录完成，耗时 {result['duration']} 秒")
            
            # 生成Markdown文件
            md_path = self.md_generator.create_video_markdown(
                bvid=bvid,
                title=title,
                desc=desc,
                transcribed_text=result["text"],
                audio_filename=audio_filename,
                custom_tags=["参考信息", "转录", "手动指定"]
            )
            
            # 记录已处理状态
            self.processed_tracker.add_processed(bvid)
            
            print(f"处理完成！结果保存到: {md_path}")
            
            return {
                "success": True,
                "bvid": bvid,
                "title": title,
                "desc": desc,
                "audio_file": audio_filename,
                "markdown_file": md_path,
                "transcription_text": result["text"],
                "transcription_duration": result["duration"]
            }
            
        except Exception as e:
            print(f"处理视频时出错: {e}")
            return {
                "error": f"处理失败: {str(e)}",
                "bvid": bvid
            }
    
    def run_workflow(self, target: str = "latest") -> dict:
        """
        运行参考信息工作流
        
        Args:
            target: 目标，"latest"表示最新视频，或者指定BVID/URL
            
        Returns:
            处理结果
        """
        print("=== 开始参考信息系列工作流 ===")
        
        # 设置环境
        self.setup_environment()
        
        if target == "latest":
            # 处理最新的参考信息视频
            result = self.process_latest_ref_info()
        else:
            # 处理指定的视频
            result = self.process_specific_ref_info(target)
        
        # 输出结果
        if result.get("success"):
            print(f"\n=== 处理成功 ===")
            print(f"视频ID: {result['bvid']}")
            print(f"标题: {result['title']}")
            print(f"音频文件: {result['audio_file']}")
            print(f"Markdown文件: {result['markdown_file']}")
            print(f"转录时长: {result['transcription_duration']} 秒")
        elif result.get("already_processed"):
            print(f"\n视频 {result['bvid']} 已经处理过，跳过")
        else:
            print(f"\n处理失败: {result.get('error', '未知错误')}")
        
        return result


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="参考信息系列工作流")
    parser.add_argument("--target", default="latest", 
                       help="目标视频：'latest' 表示最新，或指定 BVID/URL")
    parser.add_argument("--model", default="medium", 
                       help="Whisper模型 (tiny/base/small/medium/large/large-v3)")
    parser.add_argument("--proxy", help="代理URL，如 http://127.0.0.1:7890")
    parser.add_argument("--uid", type=int, default=1556651916, 
                       help="B站用户UID（默认：小黛晨读）")
    
    args = parser.parse_args()
    
    # 创建工作流实例
    workflow = RefInfoWorkflow(
        base_dir=".",
        whisper_model=args.model,
        proxy_url=args.proxy,
        uid=args.uid
    )
    
    try:
        result = workflow.run_workflow(args.target)
        
        if result.get("success"):
            print("\n工作流执行成功！")
        else:
            print(f"\n工作流执行失败: {result.get('error', '未知错误')}")
            
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n工作流执行失败: {e}")


if __name__ == "__main__":
    main()