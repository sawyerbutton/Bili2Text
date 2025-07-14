#!/usr/bin/env python3
"""
日志系统迁移辅助脚本
帮助自动化部分迁移工作
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict
import argparse


class LoggingMigrator:
    """日志迁移工具"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.changes = []
    
    def analyze_file(self, file_path: Path) -> Dict[str, int]:
        """分析文件中需要迁移的内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        stats = {
            'print_statements': len(re.findall(r'\bprint\s*\(', content)),
            'generic_exceptions': len(re.findall(r'except\s+Exception', content)),
            'raise_exceptions': len(re.findall(r'raise\s+Exception', content)),
            'value_errors': len(re.findall(r'raise\s+ValueError', content)),
        }
        
        return stats
    
    def suggest_logger_import(self, content: str) -> str:
        """建议添加logger导入"""
        if 'from .logger import get_logger' in content:
            return content
        
        # 查找导入部分
        import_match = re.search(r'((?:from\s+\S+\s+import\s+\S+\s*\n|import\s+\S+\s*\n)+)', content)
        
        if import_match:
            insert_pos = import_match.end()
            new_import = '\nfrom .logger import get_logger\n'
            content = content[:insert_pos] + new_import + content[insert_pos:]
            self.changes.append("添加logger导入")
        
        return content
    
    def add_logger_init(self, content: str, class_name: str) -> str:
        """在类的__init__方法中添加logger初始化"""
        pattern = rf'class\s+{class_name}.*?:\s*\n(.*?)def\s+__init__\s*\([^)]*\)\s*:'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # 查找__init__方法的内容
            init_pattern = rf'(class\s+{class_name}.*?def\s+__init__\s*\([^)]*\)\s*:\s*\n)'
            init_match = re.search(init_pattern, content, re.DOTALL)
            
            if init_match and 'self.logger' not in content:
                # 在__init__方法开始处添加logger
                insert_pos = init_match.end()
                
                # 检查缩进
                next_line_match = re.search(r'\n(\s+)', content[insert_pos:])
                indent = next_line_match.group(1) if next_line_match else '        '
                
                logger_init = f'{indent}self.logger = get_logger(__name__)\n'
                content = content[:insert_pos] + logger_init + content[insert_pos:]
                self.changes.append(f"在{class_name}.__init__中添加logger")
        
        return content
    
    def replace_print_statements(self, content: str) -> str:
        """替换print语句为logger调用"""
        # 匹配各种print模式
        patterns = [
            # print(f"...")
            (r'print\s*\(\s*f["\']([^"\']+)["\']\s*\)', r'self.logger.info(f"\1")'),
            # print("...")
            (r'print\s*\(\s*["\']([^"\']+)["\']\s*\)', r'self.logger.info("\1")'),
            # print(f"Error: ...")  
            (r'print\s*\(\s*f["\']([Ee]rror|[Ff]ail|失败)[^"\']*["\']\s*\)', r'self.logger.error(f"\1")'),
            # print(f"Warning: ...")
            (r'print\s*\(\s*f["\']([Ww]arning|警告)[^"\']*["\']\s*\)', r'self.logger.warning(f"\1")'),
        ]
        
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                self.changes.append("替换print语句")
        
        return content
    
    def suggest_custom_exceptions(self, content: str) -> str:
        """建议使用自定义异常"""
        suggestions = []
        
        # 检查通用异常使用
        if 'raise Exception' in content:
            suggestions.append("建议: 将 'raise Exception' 替换为具体的自定义异常类")
        
        if 'raise ValueError' in content:
            suggestions.append("建议: 将 'raise ValueError' 替换为 'raise ValidationError'")
        
        if 'except Exception as e:' in content:
            suggestions.append("建议: 捕获更具体的异常类型而不是通用Exception")
        
        if suggestions:
            self.changes.extend(suggestions)
        
        return content
    
    def process_file(self, file_path: Path) -> bool:
        """处理单个文件"""
        print(f"\n处理文件: {file_path}")
        
        # 分析文件
        stats = self.analyze_file(file_path)
        print(f"  - Print语句: {stats['print_statements']}")
        print(f"  - 通用Exception: {stats['generic_exceptions']}")
        print(f"  - 抛出Exception: {stats['raise_exceptions']}")
        print(f"  - ValueError: {stats['value_errors']}")
        
        if sum(stats.values()) == 0:
            print("  ✓ 无需迁移")
            return False
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        self.changes = []
        
        # 应用迁移
        content = self.suggest_logger_import(content)
        
        # 查找类名
        class_matches = re.findall(r'class\s+(\w+)', content)
        for class_name in class_matches:
            content = self.add_logger_init(content, class_name)
        
        content = self.replace_print_statements(content)
        content = self.suggest_custom_exceptions(content)
        
        # 保存更改
        if content != original_content and not self.dry_run:
            # 备份原文件
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # 写入新内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✓ 文件已更新 (备份: {backup_path})")
        
        if self.changes:
            print("  应用的更改:")
            for change in self.changes:
                print(f"    - {change}")
        
        return True
    
    def process_directory(self, directory: Path, pattern: str = "*.py"):
        """处理目录中的所有Python文件"""
        py_files = list(directory.rglob(pattern))
        
        print(f"找到 {len(py_files)} 个Python文件")
        
        if self.dry_run:
            print("\n🔍 DRY RUN 模式 - 只分析不修改\n")
        
        updated_count = 0
        for py_file in py_files:
            # 跳过迁移脚本自己
            if py_file.name == "migrate_logging.py":
                continue
            
            # 跳过已迁移的v2版本
            if "_v2.py" in py_file.name:
                continue
                
            if self.process_file(py_file):
                updated_count += 1
        
        print(f"\n总结: {updated_count}/{len(py_files)} 个文件需要迁移")


def main():
    parser = argparse.ArgumentParser(description="日志系统迁移辅助工具")
    parser.add_argument(
        "path",
        type=Path,
        help="要处理的文件或目录路径"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="实际应用更改（默认为dry run）"
    )
    parser.add_argument(
        "--pattern",
        default="*.py",
        help="文件匹配模式（默认: *.py）"
    )
    
    args = parser.parse_args()
    
    migrator = LoggingMigrator(dry_run=not args.apply)
    
    if args.path.is_file():
        migrator.process_file(args.path)
    elif args.path.is_dir():
        migrator.process_directory(args.path, args.pattern)
    else:
        print(f"错误: {args.path} 不是有效的文件或目录")
        return 1
    
    if not args.apply:
        print("\n💡 提示: 使用 --apply 参数来实际应用更改")
    
    return 0


if __name__ == "__main__":
    exit(main())