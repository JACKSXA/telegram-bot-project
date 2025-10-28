#!/usr/bin/env python3
"""完整排查数据流程"""
import os
import sys
import sqlite3

print("=" * 70)
print("完整数据流程排查")
print("=" * 70)

# 1. 检查Bot的数据库
print("\n【1】检查Bot数据库 (根目录)")
bot_db = 'user_data.db'
if os.path.exists(bot_db):
    print(f"✅ {bot_db} 存在 ({os.path.getsize(bot_db)} bytes)")
    conn = sqlite3.connect(bot_db)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, first_name, language FROM users")
    users = cursor.fetchall()
    print(f"📊 用户数量: {len(users)}")
    for u in users:
        print(f"   - ID: {u[0]}, 用户名: {u[1]}, 姓名: {u[2]}, 语言: {u[3]}")
    conn.close()
else:
    print(f"❌ {bot_db} 不存在")

# 2. 检查Web的数据库
print("\n【2】检查Web数据库 (admin_web/)")
web_db = 'admin_web/user_data.db'
if os.path.exists(web_db):
    print(f"✅ {web_db} 存在 ({os.path.getsize(web_db)} bytes)")
    conn = sqlite3.connect(web_db)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, first_name, language FROM users")
    users = cursor.fetchall()
    print(f"📊 用户数量: {len(users)}")
    for u in users:
        print(f"   - ID: {u[0]}, 用户名: {u[1]}, 姓名: {u[2]}, 语言: {u[3]}")
    conn.close()
else:
    print(f"❌ {web_db} 不存在")

# 3. 测试Flask导入
print("\n【3】测试Flask数据库连接")
sys.path.insert(0, '.')
try:
    # 模拟Flask环境
    os.chdir('admin_web')
    sys.path.insert(0, '..')
    
    from database_manager import get_database
    db = get_database()
    users = db.get_all_users()
    
    print(f"✅ Flask读取成功")
    print(f"📊 读取到 {len(users)} 个用户")
    if db.db_path:
        print(f"📁 数据库路径: {db.db_path}")
        print(f"📁 绝对路径: {os.path.abspath(db.db_path)}")
    
    for u in users[:3]:
        print(f"   - ID: {u.get('user_id')}, 用户名: {u.get('username')}")
        
except Exception as e:
    print(f"❌ Flask连接失败: {e}")
    import traceback
    traceback.print_exc()

os.chdir('..')

# 4. 检查gitignore
print("\n【4】检查.gitignore")
if os.path.exists('.gitignore'):
    with open('.gitignore', 'r') as f:
        content = f.read()
        if '*.db' in content or 'user_data.db' in content:
            print("⚠️ 数据库文件被gitignore忽略")
            print("   这意味着Render不会获得数据库文件！")
        else:
            print("✅ 数据库文件没有被忽略")

# 5. 问题总结
print("\n" + "=" * 70)
print("【问题总结】")
print("=" * 70)
print("""
关键问题：数据库文件被.gitignore忽略，无法推送到GitHub
结果：Render部署时数据库是空的

解决方案：
1. 从.gitignore中移除*.db
2. 或者让Bot和Web使用同一个数据库（PostgreSQL或同一服务器）
3. 或者创建数据同步API
""")
