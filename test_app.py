#!/usr/bin/env python3
"""
简单的应用测试脚本
用于验证Bili2Text Web应用是否能正常启动
"""

import sys
import os
import traceback

def test_imports():
    """测试关键模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        import flask
        try:
            version = flask.__version__
        except AttributeError:
            import importlib.metadata
            version = importlib.metadata.version("flask")
        print(f"✅ Flask {version}")
    except ImportError as e:
        print(f"❌ Flask导入失败: {e}")
        return False
    
    try:
        import flask_socketio
        try:
            version = flask_socketio.__version__
        except AttributeError:
            import importlib.metadata
            version = importlib.metadata.version("flask-socketio")
        print(f"✅ Flask-SocketIO {version}")
    except ImportError as e:
        print(f"❌ Flask-SocketIO导入失败: {e}")
        return False
    
    try:
        import psutil
        print(f"✅ psutil {psutil.__version__}")
    except ImportError as e:
        print(f"❌ psutil导入失败: {e}")
        return False
    
    # 测试可选依赖
    try:
        import whisper
        print(f"✅ openai-whisper 可用")
    except ImportError:
        print(f"⚠️ openai-whisper 未安装，将使用模拟模式")
    
    return True

def test_directories():
    """测试目录结构"""
    print("\n📁 测试目录结构...")
    
    required_dirs = [
        'webapp',
        'webapp/api',
        'webapp/core',
        'webapp/static',
        'webapp/static/templates',
        'webapp/static/css',
        'webapp/static/js',
        'storage',
        'storage/audio',
        'storage/results',
        'storage/temp',
        'webapp/logs'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} 不存在")
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"  📁 已创建目录: {dir_path}")
            except Exception as e:
                print(f"  ❌ 创建目录失败: {e}")
                return False
    
    return True

def test_app_creation():
    """测试应用创建"""
    print("\n🚀 测试应用创建...")
    
    try:
        # 初始化项目路径管理
        from src.utils import setup_project_paths
        setup_project_paths()
        
        from webapp.app import create_app
        app = create_app()
        
        print(f"✅ Flask应用创建成功")
        print(f"✅ 应用名称: {app.name}")
        print(f"✅ 调试模式: {app.debug}")
        print(f"✅ SocketIO实例: {'是' if hasattr(app, 'socketio') else '否'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 应用创建失败: {e}")
        print(f"详细错误信息:")
        traceback.print_exc()
        return False

def test_database():
    """测试数据库连接"""
    print("\n💾 测试数据库...")
    
    try:
        from webapp.app import create_app
        from webapp.core.database import db
        
        app = create_app()
        
        with app.app_context():
            # 测试数据库连接
            result = db.session.execute(db.text('SELECT 1')).scalar()
            
        print(f"✅ 数据库连接成功")
        print(f"✅ 数据库文件: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🧪 Bili2Text Web 应用测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("目录结构", test_directories),
        ("应用创建", test_app_creation),
        ("数据库连接", test_database)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n❌ {test_name} 测试失败")
        except Exception as e:
            print(f"\n❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！应用可以正常启动。")
        print("\n🚀 启动应用:")
        print("   python run.py --debug")
        return True
    else:
        print("⚠️ 部分测试失败，请检查错误信息。")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 