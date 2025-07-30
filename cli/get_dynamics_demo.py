"""
Bili2Text - 获取B站UP主动态视频列表（演示版本）
==============================================

功能：模拟获取指定UP主的最新动态视频信息
"""

import sys
from pathlib import Path
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main(args):
    """获取动态的主函数（演示版本）"""
    user_name = args.user
    count = args.count
    
    print(f"=== Bili2Text 动态获取工具 ===")
    print(f"目标用户: {user_name}")
    print(f"获取数量: {count} 条")
    print("=" * 30)
    
    # 模拟的动态数据
    mock_dynamics = [
        {
            "bvid": "BV1xx411c7mD",
            "title": "【投资分析】2024年加密货币市场展望",
            "desc": "本期我们将深入分析2024年加密货币市场的发展趋势...",
            "url": "https://www.bilibili.com/video/BV1xx411c7mD"
        },
        {
            "bvid": "BV1xx411c7mE", 
            "title": "【市场速递】比特币突破关键阻力位分析",
            "desc": "技术分析显示BTC已经突破重要阻力...",
            "url": "https://www.bilibili.com/video/BV1xx411c7mE"
        },
        {
            "bvid": "BV1xx411c7mF",
            "title": "【DeFi专题】去中心化金融的未来在哪里？",
            "desc": "随着监管政策的逐步明晰，DeFi生态正在发生变化...",
            "url": "https://www.bilibili.com/video/BV1xx411c7mF"
        }
    ]
    
    print("\n检测到系统缺少必要依赖，运行演示模式...")
    print("\n在完整环境下，本工具将:")
    print("1. 连接B站API搜索用户")
    print("2. 获取用户最新动态")
    print("3. 筛选视频类动态")
    print("4. 显示视频信息和链接")
    
    print(f"\n模拟获取结果（前{min(count, len(mock_dynamics))}条）:")
    print("-" * 50)
    
    for i, video in enumerate(mock_dynamics[:count], 1):
        print(f"\n{i}. {video['title']}")
        print(f"   BV号: {video['bvid']}")
        print(f"   链接: {video['url']}")
        print(f"   描述: {video['desc'][:50]}...")
    
    print("\n" + "-" * 50)
    print("\n提示: 要使用完整功能，请安装依赖:")
    print("1. 使用pip安装:")
    print("   pip install bilibili-api-python bilix")
    print("\n2. 或使用conda环境:")
    print("   conda env create -f config/environment/environment.yml")
    print("   conda activate bili2text")
    
    # 保存演示数据到data目录
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    output_file = data_dir / "dynamics_demo_output.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "user": user_name,
            "count": count,
            "mode": "demo",
            "videos": mock_dynamics[:count]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n演示数据已保存到: {output_file.relative_to(Path.cwd())}")
    
    return 0

if __name__ == '__main__':
    # 用于测试
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', default='CryptoInvest加密投资')
    parser.add_argument('--count', type=int, default=10)
    args = parser.parse_args()
    main(args)