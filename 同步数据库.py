#!/usr/bin/env python3
"""同步数据库到Render"""
import sqlite3
import json
import os

# 读取Railway的数据库
railway_db = 'user_data.db'
render_db = 'admin_web/user_data.db'

print("=" * 50)
print("同步数据库到Render")
print("=" * 50)

# 检查文件
if not os.path.exists(railway_db):
    print(f"❌ {railway_db} 不存在")
    exit(1)

if not os.path.exists(render_db):
    print(f"❌ {render_db} 不存在，创建它")
    os.makedirs('admin_web', exist_ok=True)

# 读取Railway数据
print(f"\n📖 读取 {railway_db}...")
conn_r = sqlite3.connect(railway_db)
conn_r.row_factory = sqlite3.Row
cursor_r = conn_r.cursor()

cursor_r.execute("SELECT * FROM users")
users = cursor_r.fetchall()
print(f"找到 {len(users)} 个用户")

# 写入Render数据
print(f"\n💾 写入 {render_db}...")
conn_w = sqlite3.connect(render_db)
cursor_w = conn_w.cursor()

# 确保表结构
cursor_w.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        language TEXT DEFAULT 'zh',
        state TEXT DEFAULT 'idle',
        wallet TEXT,
        note TEXT,
        transfer_completed INTEGER DEFAULT 0,
        avatar_url TEXT,
        ip_info TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# 同步数据
cursor_w.execute("DELETE FROM users")
print(f"✅ 清空旧数据")

for user in users:
    user_dict = dict(user)
    cursor_w.execute("""
        INSERT INTO users (user_id, username, first_name, last_name, language, state,
                          wallet, note, transfer_completed, avatar_url, ip_info,
                          created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_dict['user_id'],
        user_dict.get('username'),
        user_dict.get('first_name'),
        user_dict.get('last_name'),
        user_dict.get('language', 'zh'),
        user_dict.get('state', 'idle'),
        user_dict.get('wallet'),
        user_dict.get('note'),
        user_dict.get('transfer_completed', 0),
        user_dict.get('avatar_url'),
        user_dict.get('ip_info'),
        user_dict.get('created_at'),
        user_dict.get('updated_at')
    ))
    print(f"  ✅ 同步用户 {user_dict['user_id']}")

conn_w.commit()
conn_w.close()
conn_r.close()

print(f"\n✅ 同步完成！")
print(f"Render数据库：{render_db}")
print(f"大小：{os.path.getsize(render_db)} bytes")
