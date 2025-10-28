#!/usr/bin/env python3
"""检查部署状态"""
import requests

print("=" * 60)
print("检查部署状态")
print("=" * 60)

# 1. 检查Web服务
print("\n【1】检查Web服务...")
try:
    url = "https://telegram-bot-project-otyc.onrender.com/"
    response = requests.get(url, timeout=10)
    print(f"✅ Web服务响应: {response.status_code}")
    if response.status_code == 302:
        print("   → 正常重定向")
    else:
        print(f"   → 内容长度: {len(response.text)} bytes")
except Exception as e:
    print(f"❌ Web服务访问失败: {e}")

# 2. 检查PostgreSQL连接
print("\n【2】测试PostgreSQL连接...")
import os
postgres_url = "postgresql://botuser:bGgYc1D6iUCcjIALANMqhT5y7bJPQkhh@dpg-d400jlbe5dus7380t9mg-a/railway_i14o"
os.environ['DATABASE_URL'] = postgres_url

try:
    from database_manager import get_database
    db = get_database()
    users = db.get_all_users()
    print(f"✅ PostgreSQL连接成功")
    print(f"📊 当前用户数量: {len(users)}")
    
    if len(users) > 0:
        print("\n   最新用户:")
        for u in users[-3:]:
            print(f"   - ID: {u.get('user_id')}, 用户名: {u.get('username')}")
    else:
        print("   ⚠️ 数据库中没有用户（需要等待Bot运行）")
        
except Exception as e:
    print(f"❌ PostgreSQL连接失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)
