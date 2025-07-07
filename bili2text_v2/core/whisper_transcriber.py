#!/usr/bin/env python3
"""
Whisper转录核心模块
统一所有音频转录功能
"""

import os
import re
from datetime import datetime
from typing import Optional, Dict, Any

import torch
import whisper


class WhisperTranscriber:
    """Whisper转录器类"""
    
    def __init__(self, 
                 model_name: str = "medium",
                 device: Optional[str] = None,
                 cache_dir: str = "./.cache/whisper"):
        """
        初始化Whisper转录器
        
        Args:
            model_name: 模型名称 (tiny, base, small, medium, large, large-v3)
            device: 设备 (cpu, cuda)，None为自动选择
            cache_dir: 模型缓存目录
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载Whisper模型"""
        print(f"使用Whisper模型: {self.model_name}")
        print(f"使用设备: {self.device}")
        print("正在加载模型......")
        
        start_time = datetime.now()
        
        try:
            self.model = whisper.load_model(
                name=self.model_name,
                device=self.device,
                download_root=self.cache_dir,
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).seconds
            print(f"模型加载完成，耗时 {duration} 秒")
            
        except Exception as e:
            print(f"模型加载失败: {e}")
            raise
    
    def transcribe_audio(self, 
                        audio_path: str,
                        initial_prompt: str = '简体中文,加上标点',
                        verbose: bool = True) -> Dict[str, Any]:
        """
        转录音频文件
        
        Args:
            audio_path: 音频文件路径
            initial_prompt: 转录提示文本
            verbose: 是否显示详细进度
            
        Returns:
            转录结果字典，包含原始结果和处理后的文本
        """
        if not self.model:
            raise RuntimeError("模型未加载，请先调用_load_model()")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        print(f"开始转录: {audio_path}")
        start_time = datetime.now()
        
        try:
            # 执行转录
            result = self.model.transcribe(
                audio_path,
                verbose=verbose,
                initial_prompt=initial_prompt,
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).seconds
            print(f"转录完成，耗时 {duration} 秒")
            
            # 处理转录文本
            processed_text = self._process_text(result["text"])
            
            return {
                "raw_result": result,
                "text": processed_text,
                "duration": duration,
                "audio_file": audio_path
            }
            
        except Exception as e:
            print(f"转录失败: {e}")
            raise
    
    def _process_text(self, text: str) -> str:
        """
        处理转录文本，标准化标点符号
        
        Args:
            text: 原始转录文本
            
        Returns:
            处理后的文本
        """
        if not text:
            return ""
        
        # 标点符号标准化（英文标点转中文标点）
        processed_text = text
        processed_text = re.sub(",", "，", processed_text)
        processed_text = re.sub(r"\?", "？", processed_text)
        processed_text = re.sub(r":", "：", processed_text)
        processed_text = re.sub(r";", "；", processed_text)
        
        return processed_text.strip()
    
    def transcribe_batch(self, 
                        audio_files: list,
                        audio_folder: str = "./audio",
                        initial_prompt: str = '简体中文,加上标点') -> Dict[str, Dict]:
        """
        批量转录音频文件
        
        Args:
            audio_files: 音频文件名列表
            audio_folder: 音频文件夹路径
            initial_prompt: 转录提示文本
            
        Returns:
            转录结果字典，文件名为键
        """
        results = {}
        total_files = len(audio_files)
        
        for i, audio_file in enumerate(audio_files, 1):
            print(f"\n批量转录进度: {i}/{total_files}")
            
            audio_path = os.path.join(audio_folder, audio_file)
            
            try:
                result = self.transcribe_audio(
                    audio_path=audio_path,
                    initial_prompt=initial_prompt,
                    verbose=False  # 批量处理时减少输出
                )
                results[audio_file] = result
                
            except Exception as e:
                print(f"转录文件 {audio_file} 时出错: {e}")
                results[audio_file] = {"error": str(e)}
                continue
        
        print(f"\n批量转录完成！成功转录 {len([r for r in results.values() if 'error' not in r])} 个文件")
        return results
    
    def get_available_models(self) -> list:
        """获取可用的模型列表"""
        return ["tiny", "base", "small", "medium", "large", "large-v3"]
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取当前模型信息"""
        return {
            "model_name": self.model_name,
            "device": str(self.device),
            "cache_dir": self.cache_dir,
            "loaded": self.model is not None
        }


# 便捷函数
def transcribe_single_file(audio_path: str, 
                         model_name: str = "medium",
                         initial_prompt: str = '简体中文,加上标点') -> str:
    """
    转录单个音频文件的便捷函数
    
    Args:
        audio_path: 音频文件路径
        model_name: 模型名称
        initial_prompt: 转录提示
        
    Returns:
        转录文本
    """
    transcriber = WhisperTranscriber(model_name=model_name)
    result = transcriber.transcribe_audio(audio_path, initial_prompt)
    return result["text"]


if __name__ == "__main__":
    # 测试代码
    print("=== Whisper转录器测试 ===")
    
    # 检查音频文件
    audio_folder = "./audio"
    if os.path.exists(audio_folder):
        audio_files = [f for f in os.listdir(audio_folder) 
                      if f.lower().endswith(('.mp3', '.wav', '.m4a', '.aac', '.flac'))]
        
        if audio_files:
            print(f"找到 {len(audio_files)} 个音频文件")
            
            # 测试转录第一个文件
            transcriber = WhisperTranscriber(model_name="tiny")  # 使用最小模型测试
            audio_path = os.path.join(audio_folder, audio_files[0])
            
            try:
                result = transcriber.transcribe_audio(audio_path)
                print("转录测试成功！")
                print("结果预览:")
                print("-" * 50)
                preview = result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"]
                print(preview)
                print("-" * 50)
                
            except Exception as e:
                print(f"转录测试失败: {e}")
        else:
            print("audio目录中没有找到音频文件")
    else:
        print("audio目录不存在")