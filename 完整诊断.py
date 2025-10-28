#!/usr/bin/env python3
"""完整诊断系统"""
import os
import sys

print("=" * 60)
print("完整系统诊断")
print("=" * 60)

# 1. 检查环境变量
print("\n1. 检查环境变量:")
print(f"   DATABASE_URL: {os.getenv('DATABASE_URL', '未设置')}")
print(f"   TELEGRAM_BOT_TOKEN: {'已设置' if os.getenv('TELEGRAM_BOT_TOKEN') else '未设置'}")

# 2. 检查数据库文件
print("\n2. 检查数据库文件:")
files = [
    'user_data.db',
    'admin_web/user_data.db',
    '../user_data.db'
]

for f in files:
    if os.path.exists(f):
        size = os.path.getsize(f)
        print(f"   ✅ {f} - {size} bytes")
    else:
        print(f"   ❌ {f} - 不存在")

# 3. 检查database_manager
print("\n3. 检查database_manager:")
try:
    sys.path.insert(0, '.')
    import database_manager
    print(f"   ✅ 模块导入成功")
    print(f"   USE_POSTGRES: {database_manager.USE_POSTGRES}")
    print(f"   DATABASE_URL: {database_manager.DATABASE_URL}")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")

# 4. 测试数据库连接
print("\n4. 测试数据库连接:")
try:
    from database_manager import get_database
    db = get_database()
    print(f"   ✅ 数据库管理器创建成功")
    print(f"   数据库路径: {db.db_path if hasattr(db, 'db_path') else 'PostgreSQL'}")
    
    users = db.get_all_users()
    print(f"   📊 用户数量: {len(users)}")
    
    if users:
        print("   \n   用户列表:")
        for u in users:
            print(f"   - ID: {u.get('user_id')}, 用户名: {u.get('username')}, 语言: {u.get('language')}")
    else:
        print("   ⚠️ 没有用户数据")
        
except Exception as e:
    print(f"   ❌ 数据库连接失败: {e}")
    import traceback
    traceback.print_exc()

# 5. 检查Flask导入
print("\n5. 检查Flask导入:")
try:
    import admin_web.flask_app
    print("   ✅ Flask应用导入成功")
except Exception as e:
    print(f"   ❌ Flask导入失败: {e}")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
