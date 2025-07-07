#!/usr/bin/env python3
"""
Markdown生成核心模块
统一所有Markdown文件生成功能
"""

import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class MarkdownGenerator:
    """Markdown生成器类"""
    
    def __init__(self, output_dir: str = "./result"):
        """
        初始化Markdown生成器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_video_markdown(self, 
                            bvid: str,
                            title: str,
                            desc: str,
                            transcribed_text: str,
                            audio_filename: Optional[str] = None,
                            youtube_id: Optional[str] = None,
                            custom_tags: Optional[list] = None) -> str:
        """
        创建视频转录Markdown文件
        
        Args:
            bvid: B站视频ID
            title: 视频标题
            desc: 视频描述
            transcribed_text: 转录文本
            audio_filename: 音频文件名（可选）
            youtube_id: YouTube视频ID（可选）
            custom_tags: 自定义标签（可选）
            
        Returns:
            生成的Markdown文件路径
        """
        # 生成文件名
        if audio_filename:
            # 使用音频文件名作为基础
            base_name = os.path.splitext(audio_filename)[0]
        else:
            # 使用BVID作为基础
            base_name = bvid
        
        md_filename = f"{base_name}.md"
        md_path = os.path.join(self.output_dir, md_filename)
        
        # 生成YAML前置信息
        yaml_front_matter = self._generate_yaml_front_matter(
            title, desc, custom_tags
        )
        
        # 生成视频嵌入部分
        video_embed = self._generate_video_embed(bvid, youtube_id)
        
        # 生成警告信息
        warning_text = self._generate_warning_text()
        
        # 写入文件
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(yaml_front_matter)
            f.write(video_embed)
            f.write(warning_text)
            f.write(transcribed_text)
        
        print(f"Markdown文件已生成: {md_path}")
        return md_path
    
    def _generate_yaml_front_matter(self, 
                                   title: str, 
                                   desc: str,
                                   custom_tags: Optional[list] = None) -> str:
        """
        生成YAML前置信息
        
        Args:
            title: 标题
            desc: 描述
            custom_tags: 自定义标签
            
        Returns:
            YAML前置信息字符串
        """
        # 生成时间戳
        timestr = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + ".000Z"
        
        # 处理标签
        tags_str = ""
        if custom_tags:
            tags_str = "\n".join([f"  - {tag}" for tag in custom_tags])
        
        yaml_content = f"""---
title: {title}
description: {desc}
published: true
date: {timestr}
tags:
{tags_str}
editor: markdown
dateCreated: {timestr}
---

"""
        return yaml_content
    
    def _generate_video_embed(self, 
                             bvid: str, 
                             youtube_id: Optional[str] = None) -> str:
        """
        生成视频嵌入代码
        
        Args:
            bvid: B站视频ID
            youtube_id: YouTube视频ID
            
        Returns:
            视频嵌入HTML代码
        """
        # B站嵌入代码
        bilibili_embed = f"""## Tabs {{.tabset}}
### B站
<div style="position: relative; padding: 30% 45%;">
<iframe style="position: absolute; width: 100%; height: 100%; left: 0; top: 0;" src="//player.bilibili.com/player.html?&bvid={bvid}&page=1&as_wide=1&high_quality=1&danmaku=1&autoplay=0" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe>
</div>

"""
        
        # YouTube嵌入代码
        if youtube_id:
            youtube_embed = f"""### YouTube
<div style="position: relative; padding: 30% 45%;">
<iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" src="https://www.youtube-nocookie.com/embed/{youtube_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

"""
        else:
            youtube_embed = """### YouTube
<div style="position: relative; padding: 30% 45%;">
<iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" src="https://www.youtube-nocookie.com/embed/YouTubeVID" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

"""
        
        return bilibili_embed + youtube_embed + "##\n\n"
    
    def _generate_warning_text(self) -> str:
        """
        生成转录警告文本
        
        Returns:
            警告文本
        """
        return """> 以下文本为音频转录结果，存在一定错误，校对正在进行中。
{.is-warning}

"""
    
    def create_simple_markdown(self, 
                              filename: str,
                              title: str,
                              content: str,
                              metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        创建简单的Markdown文件
        
        Args:
            filename: 文件名（不含扩展名）
            title: 标题
            content: 内容
            metadata: 元数据字典
            
        Returns:
            生成的Markdown文件路径
        """
        md_filename = f"{filename}.md"
        md_path = os.path.join(self.output_dir, md_filename)
        
        with open(md_path, "w", encoding="utf-8") as f:
            # 写入简单的标题
            f.write(f"# {title}\n\n")
            
            # 写入元数据（如果有）
            if metadata:
                f.write("## 信息\n\n")
                for key, value in metadata.items():
                    f.write(f"- **{key}**: {value}\n")
                f.write("\n")
            
            # 写入内容
            f.write("## 内容\n\n")
            f.write(content)
        
        print(f"简单Markdown文件已生成: {md_path}")
        return md_path
    
    def append_to_markdown(self, md_path: str, content: str):
        """
        向已存在的Markdown文件追加内容
        
        Args:
            md_path: Markdown文件路径
            content: 要追加的内容
        """
        with open(md_path, "a", encoding="utf-8") as f:
            f.write(content)
        
        print(f"内容已追加到: {md_path}")
    
    def create_batch_summary(self, 
                           results: Dict[str, Any],
                           summary_filename: str = "batch_summary") -> str:
        """
        创建批量处理结果摘要
        
        Args:
            results: 处理结果字典
            summary_filename: 摘要文件名
            
        Returns:
            摘要文件路径
        """
        md_path = os.path.join(self.output_dir, f"{summary_filename}.md")
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# 批量处理结果摘要\n\n")
            
            # 统计信息
            total_count = len(results)
            success_count = sum(1 for r in results.values() if isinstance(r, dict) and "error" not in r)
            error_count = total_count - success_count
            
            f.write(f"## 统计信息\n\n")
            f.write(f"- **总计**: {total_count} 个文件\n")
            f.write(f"- **成功**: {success_count} 个文件\n")
            f.write(f"- **失败**: {error_count} 个文件\n")
            f.write(f"- **成功率**: {success_count/total_count*100:.1f}%\n\n")
            
            # 成功列表
            if success_count > 0:
                f.write("## 成功处理的文件\n\n")
                for filename, result in results.items():
                    if isinstance(result, dict) and "error" not in result:
                        f.write(f"- `{filename}`\n")
                f.write("\n")
            
            # 失败列表
            if error_count > 0:
                f.write("## 失败的文件\n\n")
                for filename, result in results.items():
                    if isinstance(result, dict) and "error" in result:
                        f.write(f"- `{filename}`: {result['error']}\n")
                f.write("\n")
            
            # 时间戳
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"*生成时间: {timestamp}*\n")
        
        print(f"批量处理摘要已生成: {md_path}")
        return md_path
    
    def create_video_info_table(self, 
                               video_infos: list,
                               table_filename: str = "video_list") -> str:
        """
        创建视频信息表格
        
        Args:
            video_infos: 视频信息列表
            table_filename: 表格文件名
            
        Returns:
            表格文件路径
        """
        md_path = os.path.join(self.output_dir, f"{table_filename}.md")
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# 视频信息列表\n\n")
            
            if not video_infos:
                f.write("暂无视频信息。\n")
                return md_path
            
            # 创建表格
            f.write("| 序号 | 视频ID | 标题 | 描述 |\n")
            f.write("|------|--------|------|------|\n")
            
            for i, video_info in enumerate(video_infos, 1):
                bvid = video_info.get("bvid", "未知")
                title = video_info.get("title", "无标题")
                desc = video_info.get("desc", "无描述")
                
                # 限制描述长度
                if len(desc) > 50:
                    desc = desc[:50] + "..."
                
                # 转义Markdown特殊字符
                title = title.replace("|", "\\|")
                desc = desc.replace("|", "\\|")
                
                f.write(f"| {i} | `{bvid}` | {title} | {desc} |\n")
            
            f.write(f"\n*共 {len(video_infos)} 个视频*\n")
        
        print(f"视频信息表格已生成: {md_path}")
        return md_path


# 便捷函数
def create_video_markdown_simple(bvid: str, 
                                title: str, 
                                desc: str,
                                transcribed_text: str,
                                output_dir: str = "./result") -> str:
    """
    创建视频Markdown文件的便捷函数
    
    Args:
        bvid: B站视频ID
        title: 视频标题
        desc: 视频描述
        transcribed_text: 转录文本
        output_dir: 输出目录
        
    Returns:
        生成的Markdown文件路径
    """
    generator = MarkdownGenerator(output_dir)
    return generator.create_video_markdown(bvid, title, desc, transcribed_text)


def create_text_file(filename: str, 
                    content: str,
                    output_dir: str = "./result") -> str:
    """
    创建纯文本文件的便捷函数
    
    Args:
        filename: 文件名（含扩展名）
        content: 文件内容
        output_dir: 输出目录
        
    Returns:
        生成的文件路径
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"文本文件已生成: {file_path}")
    return file_path


if __name__ == "__main__":
    # 测试代码
    print("=== Markdown生成器测试 ===")
    
    generator = MarkdownGenerator("./test_result")
    
    # 测试视频Markdown生成
    test_md = generator.create_video_markdown(
        bvid="BV1234567890",
        title="测试视频标题",
        desc="这是一个测试视频的描述",
        transcribed_text="这是转录的测试文本内容。\n\n包含多行文本。",
        custom_tags=["测试", "转录", "B站"]
    )
    
    print(f"测试文件生成: {test_md}")
    
    # 测试简单Markdown生成
    simple_md = generator.create_simple_markdown(
        filename="test_simple",
        title="简单测试",
        content="这是简单的测试内容",
        metadata={"类型": "测试", "时间": "2024"}
    )
    
    print(f"简单文件生成: {simple_md}")
    
    print("Markdown生成器测试完成！")