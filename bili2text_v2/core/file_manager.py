#!/usr/bin/env python3
"""
文件管理核心模块
统一所有文件操作、目录管理和状态跟踪功能
"""

import os
import shutil
import json
from datetime import datetime
from typing import Set, List, Dict, Any, Optional


class FileManager:
    """文件管理器类"""
    
    def __init__(self, base_dir: str = "."):
        """
        初始化文件管理器
        
        Args:
            base_dir: 基础工作目录
        """
        self.base_dir = base_dir
        self.audio_dir = os.path.join(base_dir, "audio")
        self.video_dir = os.path.join(base_dir, "video")
        self.temp_dir = os.path.join(base_dir, "temp")
        self.result_dir = os.path.join(base_dir, "result")
        self.cache_dir = os.path.join(base_dir, ".cache")
        
        # 状态文件路径
        self.downloaded_file = os.path.join(base_dir, "downloaded_videos.txt")
        self.transcribed_file = os.path.join(base_dir, "transcribed_audios.txt")
        self.processed_file = os.path.join(base_dir, "processed_videos.txt")
        self.video_info_file = os.path.join(base_dir, "video_info.json")
    
    def setup_directories(self):
        """创建所有必要的目录"""
        directories = [
            self.audio_dir,
            self.video_dir,
            self.temp_dir,
            self.result_dir,
            self.cache_dir,
            os.path.join(self.cache_dir, "whisper")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"目录已创建/确认存在: {directory}")
    
    def clean_directory(self, directory: str, keep_files: Optional[List[str]] = None):
        """
        清理目录
        
        Args:
            directory: 要清理的目录
            keep_files: 要保留的文件列表（可选）
        """
        if not os.path.exists(directory):
            return
        
        keep_files = keep_files or []
        
        for file in os.listdir(directory):
            if file not in keep_files:
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"已删除文件: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"已删除目录: {file_path}")
    
    def move_files(self, 
                   source_dir: str, 
                   target_dir: str,
                   file_pattern: Optional[str] = None,
                   file_prefix: Optional[str] = None) -> List[str]:
        """
        移动文件到目标目录
        
        Args:
            source_dir: 源目录
            target_dir: 目标目录
            file_pattern: 文件模式（如 "*.mp3"）
            file_prefix: 添加到文件名的前缀
            
        Returns:
            移动的文件路径列表
        """
        os.makedirs(target_dir, exist_ok=True)
        
        if not os.path.exists(source_dir):
            print(f"源目录不存在: {source_dir}")
            return []
        
        moved_files = []
        
        for file_name in os.listdir(source_dir):
            source_file_path = os.path.join(source_dir, file_name)
            
            # 跳过目录
            if not os.path.isfile(source_file_path):
                continue
            
            # 检查文件模式
            if file_pattern and not file_name.endswith(file_pattern.replace("*", "")):
                continue
            
            # 生成目标文件名
            if file_prefix:
                name, ext = os.path.splitext(file_name)
                target_file_name = f"{file_prefix}_{file_name}"
            else:
                target_file_name = file_name
            
            target_file_path = os.path.join(target_dir, target_file_name)
            
            # 处理重名文件
            if os.path.exists(target_file_path):
                name, ext = os.path.splitext(target_file_name)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                target_file_path = os.path.join(target_dir, f"{name}_{timestamp}{ext}")
            
            # 移动文件
            shutil.move(source_file_path, target_file_path)
            moved_files.append(target_file_path)
            print(f"文件已移动: {source_file_path} -> {target_file_path}")
        
        return moved_files
    
    def get_audio_files(self, audio_extensions: Optional[List[str]] = None) -> List[str]:
        """
        获取音频目录中的所有音频文件
        
        Args:
            audio_extensions: 音频文件扩展名列表
            
        Returns:
            音频文件名列表
        """
        if audio_extensions is None:
            audio_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.wma']
        
        audio_files = []
        
        if not os.path.exists(self.audio_dir):
            print(f"音频目录不存在: {self.audio_dir}")
            return audio_files
        
        for file in os.listdir(self.audio_dir):
            if any(file.lower().endswith(ext) for ext in audio_extensions):
                audio_files.append(file)
        
        audio_files.sort()  # 排序
        return audio_files
    
    def get_video_files(self, video_extensions: Optional[List[str]] = None) -> List[str]:
        """
        获取视频目录中的所有视频文件
        
        Args:
            video_extensions: 视频文件扩展名列表
            
        Returns:
            视频文件名列表
        """
        if video_extensions is None:
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        
        video_files = []
        
        if not os.path.exists(self.video_dir):
            print(f"视频目录不存在: {self.video_dir}")
            return video_files
        
        for file in os.listdir(self.video_dir):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(file)
        
        video_files.sort()  # 排序
        return video_files


class StatusTracker:
    """状态跟踪器类，管理已下载、已转录等状态"""
    
    def __init__(self, status_file: str):
        """
        初始化状态跟踪器
        
        Args:
            status_file: 状态文件路径
        """
        self.status_file = status_file
        self.status_set = self._load_status()
    
    def _load_status(self) -> Set[str]:
        """加载状态文件"""
        try:
            with open(self.status_file, "r", encoding="utf-8") as f:
                return set(line.strip() for line in f.readlines() if line.strip())
        except FileNotFoundError:
            return set()
    
    def _save_status(self):
        """保存状态文件"""
        with open(self.status_file, "w", encoding="utf-8") as f:
            for item in sorted(self.status_set):
                f.write(item + "\n")
    
    def is_processed(self, item: str) -> bool:
        """检查项目是否已处理"""
        return item in self.status_set
    
    def add_processed(self, item: str):
        """添加已处理的项目"""
        self.status_set.add(item)
        self._save_status()
        print(f"已记录处理状态: {item}")
    
    def remove_processed(self, item: str):
        """移除已处理的项目"""
        if item in self.status_set:
            self.status_set.remove(item)
            self._save_status()
            print(f"已移除处理状态: {item}")
    
    def get_all_processed(self) -> Set[str]:
        """获取所有已处理的项目"""
        return self.status_set.copy()
    
    def get_unprocessed(self, all_items: List[str]) -> List[str]:
        """获取未处理的项目列表"""
        return [item for item in all_items if item not in self.status_set]
    
    def clear_all(self):
        """清空所有状态"""
        self.status_set.clear()
        self._save_status()
        print("已清空所有处理状态")
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            "total_processed": len(self.status_set),
            "status_file": self.status_file
        }


class VideoInfoManager:
    """视频信息管理器"""
    
    def __init__(self, info_file: str):
        """
        初始化视频信息管理器
        
        Args:
            info_file: 信息文件路径
        """
        self.info_file = info_file
        self.video_info = self._load_video_info()
    
    def _load_video_info(self) -> Dict[str, Dict[str, Any]]:
        """加载视频信息文件"""
        try:
            with open(self.info_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_video_info(self):
        """保存视频信息文件"""
        with open(self.info_file, "w", encoding="utf-8") as f:
            json.dump(self.video_info, f, ensure_ascii=False, indent=2)
    
    def add_video_info(self, 
                      bvid: str, 
                      title: str, 
                      desc: str,
                      audio_filename: Optional[str] = None,
                      extra_info: Optional[Dict[str, Any]] = None):
        """
        添加视频信息
        
        Args:
            bvid: 视频ID
            title: 视频标题
            desc: 视频描述
            audio_filename: 音频文件名
            extra_info: 额外信息
        """
        info = {
            "bvid": bvid,
            "title": title,
            "desc": desc,
            "audio_filename": audio_filename,
            "added_time": datetime.now().isoformat()
        }
        
        if extra_info:
            info.update(extra_info)
        
        self.video_info[bvid] = info
        self._save_video_info()
        print(f"已添加视频信息: {bvid} - {title}")
    
    def get_video_info(self, bvid: str) -> Optional[Dict[str, Any]]:
        """获取视频信息"""
        return self.video_info.get(bvid)
    
    def get_info_by_audio_filename(self, audio_filename: str) -> Optional[Dict[str, Any]]:
        """根据音频文件名获取视频信息"""
        for info in self.video_info.values():
            if info.get("audio_filename") == audio_filename:
                return info
        return None
    
    def get_all_video_info(self) -> Dict[str, Dict[str, Any]]:
        """获取所有视频信息"""
        return self.video_info.copy()
    
    def remove_video_info(self, bvid: str):
        """删除视频信息"""
        if bvid in self.video_info:
            del self.video_info[bvid]
            self._save_video_info()
            print(f"已删除视频信息: {bvid}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_videos = len(self.video_info)
        with_audio = sum(1 for info in self.video_info.values() 
                        if info.get("audio_filename"))
        
        return {
            "total_videos": total_videos,
            "videos_with_audio": with_audio,
            "info_file": self.info_file
        }


# 便捷函数
def setup_project_directories(base_dir: str = "."):
    """
    设置项目目录结构的便捷函数
    
    Args:
        base_dir: 基础目录
    """
    file_manager = FileManager(base_dir)
    file_manager.setup_directories()
    return file_manager


def create_status_tracker(status_type: str, base_dir: str = ".") -> StatusTracker:
    """
    创建状态跟踪器的便捷函数
    
    Args:
        status_type: 状态类型 ("downloaded", "transcribed", "processed")
        base_dir: 基础目录
        
    Returns:
        状态跟踪器实例
    """
    status_file = os.path.join(base_dir, f"{status_type}_videos.txt")
    return StatusTracker(status_file)


def create_video_info_manager(base_dir: str = ".") -> VideoInfoManager:
    """
    创建视频信息管理器的便捷函数
    
    Args:
        base_dir: 基础目录
        
    Returns:
        视频信息管理器实例
    """
    info_file = os.path.join(base_dir, "video_info.json")
    return VideoInfoManager(info_file)


if __name__ == "__main__":
    # 测试代码
    print("=== 文件管理器测试 ===")
    
    # 测试目录设置
    file_manager = setup_project_directories("./test_project")
    
    # 测试状态跟踪
    downloaded_tracker = create_status_tracker("downloaded", "./test_project")
    downloaded_tracker.add_processed("BV1234567890")
    downloaded_tracker.add_processed("BV0987654321")
    
    print(f"已下载: {downloaded_tracker.get_all_processed()}")
    print(f"统计: {downloaded_tracker.get_stats()}")
    
    # 测试视频信息管理
    video_info_manager = create_video_info_manager("./test_project")
    video_info_manager.add_video_info(
        bvid="BV1234567890",
        title="测试视频",
        desc="这是一个测试视频",
        audio_filename="test_audio.aac"
    )
    
    info = video_info_manager.get_video_info("BV1234567890")
    print(f"视频信息: {info}")
    print(f"统计: {video_info_manager.get_stats()}")
    
    # 测试文件移动
    os.makedirs("./test_project/temp", exist_ok=True)
    with open("./test_project/temp/test_file.txt", "w") as f:
        f.write("测试文件内容")
    
    moved_files = file_manager.move_files(
        "./test_project/temp",
        "./test_project/result",
        file_prefix="moved"
    )
    print(f"移动的文件: {moved_files}")
    
    print("文件管理器测试完成！")