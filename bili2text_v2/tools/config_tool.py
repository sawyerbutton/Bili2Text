#!/usr/bin/env python3
"""
配置管理工具
提供配置查看、生成、验证等功能
"""

import sys
import os
import argparse
import json
import yaml
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from bili2text_v2.config import get_config, init_config, get_config_manager, AppConfig


def show_config(args):
    """显示当前配置"""
    config = get_config()
    config_dict = config.dict()
    
    if args.format == 'json':
        print(json.dumps(config_dict, indent=2, ensure_ascii=False))
    elif args.format == 'yaml':
        print(yaml.dump(config_dict, default_flow_style=False, allow_unicode=True))
    else:
        # 美化输出
        print("=== Bili2Text 配置 ===\n")
        _print_config_tree(config_dict)


def _print_config_tree(config, prefix="", is_last=True):
    """树形打印配置"""
    items = list(config.items())
    for i, (key, value) in enumerate(items):
        is_last_item = i == len(items) - 1
        
        # 打印树形符号
        if prefix:
            print(prefix + ("└── " if is_last_item else "├── "), end="")
        
        if isinstance(value, dict):
            print(f"{key}:")
            extension = "    " if is_last_item else "│   "
            _print_config_tree(value, prefix + extension, is_last_item)
        else:
            print(f"{key}: {value}")


def generate_config(args):
    """生成配置文件"""
    # 创建默认配置
    config = AppConfig()
    config_dict = config.dict()
    
    # 确定输出路径
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 根据文件扩展名决定格式
    if output_path.suffix == '.json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    else:
        # 默认使用YAML
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
    
    print(f"配置文件已生成: {output_path}")
    
    if args.env:
        # 同时生成环境变量示例
        env_path = output_path.parent / '.env.example'
        generate_env_example(config_dict, env_path)
        print(f"环境变量示例已生成: {env_path}")


def generate_env_example(config_dict, output_path):
    """生成环境变量示例文件"""
    lines = ["# Bili2Text 环境变量配置", "# 复制为 .env 并修改相应的值", ""]
    
    def flatten_config(obj, prefix="BILI2TEXT"):
        for key, value in obj.items():
            env_key = f"{prefix}__{key.upper()}"
            if isinstance(value, dict):
                flatten_config(value, env_key)
            else:
                if isinstance(value, bool):
                    value = str(value).lower()
                elif value is None:
                    value = ""
                lines.append(f"# {env_key}={value}")
    
    flatten_config(config_dict)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def validate_config(args):
    """验证配置文件"""
    config_path = Path(args.file)
    
    if not config_path.exists():
        print(f"错误: 配置文件不存在: {config_path}")
        return 1
    
    try:
        # 尝试加载配置
        manager = get_config_manager()
        config_data = manager.load_from_file(config_path)
        
        # 尝试创建配置对象
        config = AppConfig(**config_data)
        
        print(f"✅ 配置文件验证通过: {config_path}")
        
        if args.verbose:
            print("\n配置内容:")
            print(yaml.dump(config.dict(), default_flow_style=False, allow_unicode=True))
        
        return 0
        
    except Exception as e:
        print(f"❌ 配置文件验证失败: {e}")
        return 1


def diff_config(args):
    """比较配置差异"""
    # 加载默认配置
    default_config = AppConfig().dict()
    
    # 加载当前配置
    current_config = get_config().dict()
    
    # 找出差异
    differences = _find_differences(default_config, current_config)
    
    if not differences:
        print("当前配置与默认配置相同")
    else:
        print("=== 配置差异 ===\n")
        for path, (default, current) in differences.items():
            print(f"{path}:")
            print(f"  默认值: {default}")
            print(f"  当前值: {current}")
            print()


def _find_differences(default, current, path=""):
    """递归查找配置差异"""
    differences = {}
    
    for key in default:
        current_path = f"{path}.{key}" if path else key
        
        if key not in current:
            differences[current_path] = (default[key], "未设置")
        elif isinstance(default[key], dict) and isinstance(current[key], dict):
            sub_diff = _find_differences(default[key], current[key], current_path)
            differences.update(sub_diff)
        elif default[key] != current[key]:
            differences[current_path] = (default[key], current[key])
    
    return differences


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Bili2Text 配置管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # show 命令
    show_parser = subparsers.add_parser('show', help='显示当前配置')
    show_parser.add_argument(
        '-f', '--format',
        choices=['tree', 'json', 'yaml'],
        default='tree',
        help='输出格式'
    )
    show_parser.set_defaults(func=show_config)
    
    # generate 命令
    gen_parser = subparsers.add_parser('generate', help='生成配置文件')
    gen_parser.add_argument(
        '-o', '--output',
        default='config.yml',
        help='输出文件路径'
    )
    gen_parser.add_argument(
        '--env',
        action='store_true',
        help='同时生成环境变量示例'
    )
    gen_parser.set_defaults(func=generate_config)
    
    # validate 命令
    val_parser = subparsers.add_parser('validate', help='验证配置文件')
    val_parser.add_argument(
        'file',
        help='配置文件路径'
    )
    val_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细信息'
    )
    val_parser.set_defaults(func=validate_config)
    
    # diff 命令
    diff_parser = subparsers.add_parser('diff', help='比较配置差异')
    diff_parser.set_defaults(func=diff_config)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # 初始化配置
    init_config()
    
    # 执行命令
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())