#!/usr/bin/env python3
"""诊断数据库问题"""
import os
import sys

print("=" * 50)
print("数据库问题诊断")
print("=" * 50)

# 检查数据库文件
print("\n1. 检查本地数据库文件:")
local_db = 'user_data.db'
if os.path.exists(local_db):
    size = os.path.getsize(local_db)
    print(f"   ✅ {local_db} 存在 ({size} bytes)")
else:
    print(f"   ❌ {local_db} 不存在")

# 检查admin_web目录中的数据库
admin_db = 'admin_web/user_data.db'
if os.path.exists(admin_db):
    size = os.path.getsize(admin_db)
    print(f"   ✅ {admin_db} 存在 ({size} bytes)")
else:
    print(f"   ❌ {admin_db} 不存在")

# 检查环境变量
print("\n2. 检查环境变量:")
print(f"   DATABASE_URL: {os.getenv('DATABASE_URL', '未设置')}")

# 测试数据库连接
print("\n3. 测试数据库连接:")
try:
    sys.path.insert(0, '.')
    from database_manager import get_database
    db = get_database()
    print("   ✅ 数据库管理器导入成功")
    
    users = db.get_all_users()
    print(f"   📊 当前有 {len(users)} 个用户")
    
    if users:
        print("\n   用户列表:")
        for u in users[:5]:
            print(f"   - ID: {u.get('user_id')}, 用户名: {u.get('username')}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print("\n" + "=" * 50)
