"""
Bili2Text - 获取B站UP主动态视频列表
====================================

功能：获取指定UP主的最新动态视频信息
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 检查依赖
try:
    import asyncio
    from bilibili_api import search, user
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False

def main(args):
    """获取动态的主函数"""
    user_name = args.user
    count = args.count
    
    print(f"准备获取 {user_name} 的最新 {count} 条动态")
    
    if not DEPS_AVAILABLE:
        # 使用演示模式
        from cli.get_dynamics_demo import main as demo_main
        return demo_main(args)
    
    try:
        
        async def get_user_dynamics(user_name, count):
            """异步获取用户动态"""
            # 搜索用户
            search_result = await search.search_by_type(
                keyword=user_name,
                search_type=search.SearchObjectType.USER,
                page=1
            )
            
            if not search_result or 'result' not in search_result:
                print(f"未找到用户: {user_name}")
                return
            
            # 获取第一个匹配的用户
            users = search_result['result']
            if not users:
                print(f"未找到用户: {user_name}")
                return
                
            target_user = users[0]
            uid = target_user['mid']
            print(f"找到用户: {target_user['uname']} (UID: {uid})")
            
            # 获取用户对象
            u = user.User(uid)
            
            # 获取动态
            dynamics = []
            try:
                # 使用新API
                result = await u.get_dynamics_new()
                if result and "items" in result:
                    dynamics = result["items"][:count]
                else:
                    print(f"未获取到动态数据")
                    return
            except Exception as e:
                print(f"获取动态时出错: {e}")
                # 尝试旧API
                try:
                    page = await u.get_dynamics(0)
                    if page and "cards" in page:
                        dynamics = page["cards"][:count]
                except Exception as e2:
                    print(f"旧API也失败: {e2}")
                    return
            
            print(f"\n获取到 {len(dynamics)} 条动态:")
            print("-" * 50)
            
            for i, dynamic in enumerate(dynamics, 1):
                try:
                    # 新API格式解析
                    if 'modules' in dynamic:
                        # 获取动态类型
                        dynamic_type = dynamic.get('type', '')
                        
                        # 获取主要内容模块
                        module_dynamic = dynamic.get('modules', {}).get('module_dynamic', {})
                        
                        if dynamic_type == 'DYNAMIC_TYPE_AV':
                            # 视频动态
                            major = module_dynamic.get('major', {})
                            archive = major.get('archive', {})
                            
                            title = archive.get('title', '无标题')
                            bvid = archive.get('bvid', '')
                            desc = archive.get('desc', '')
                            
                            print(f"\n{i}. {title}")
                            print(f"   BV号: {bvid}")
                            print(f"   链接: https://www.bilibili.com/video/{bvid}")
                            if desc:
                                print(f"   描述: {desc[:50]}...")
                        else:
                            # 其他类型动态
                            desc_text = module_dynamic.get('desc', {}).get('text', '')
                            if not desc_text:
                                # 尝试其他字段
                                desc_text = str(dynamic.get('orig', {}).get('modules', {}).get('module_dynamic', {}).get('desc', {}).get('text', '动态内容'))
                            
                            print(f"\n{i}. [动态] {desc_text[:50]}...")
                    else:
                        # 旧API格式
                        if 'desc' in dynamic and 'bvid' in dynamic['desc']:
                            bvid = dynamic['desc']['bvid']
                            card = dynamic.get('card', {})
                            title = card.get('title', '无标题')
                            desc = card.get('dynamic', '无描述')
                            
                            print(f"\n{i}. {title}")
                            print(f"   BV号: {bvid}")
                            print(f"   链接: https://www.bilibili.com/video/{bvid}")
                        else:
                            print(f"\n{i}. [动态] 未知格式")
                        
                except Exception as e:
                    print(f"\n{i}. 解析动态失败: {e}")
            
            print("\n" + "-" * 50)
            
        # 运行异步函数
        asyncio.run(get_user_dynamics(user_name, count))
        
    except ImportError as e:
        print(f"\n错误: 缺少必要的依赖库 - {e}")
        print("\n请先安装依赖:")
        print("  pip install bilibili-api-python")
        print("\n或使用conda环境:")
        print("  conda env create -f config/environment/environment.yml")
        print("  conda activate bili2text")
        sys.exit(1)
    except Exception as e:
        print(f"\n执行错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    # 用于测试
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', default='CryptoInvest加密投资')
    parser.add_argument('--count', type=int, default=10)
    args = parser.parse_args()
    main(args)