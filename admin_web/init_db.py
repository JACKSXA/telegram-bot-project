#!/usr/bin/env python3
"""初始化数据库脚本"""
import os
import sys

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_manager import get_database

def init_database():
    """初始化数据库"""
    try:
        db = get_database()
        
        # 检查是否已有用户
        users = db.get_all_users()
        print(f"📊 当前数据库有 {len(users)} 个用户")
        
        if len(users) == 0:
            print("💡 数据库为空，等待用户访问Bot...")
            print("   当用户发送/start后，数据会自动保存")
        else:
            print("\n✅ 数据库已初始化")
            print("用户列表:")
            for u in users:
                print(f"  - ID: {u.get('user_id')}, 用户名: {u.get('username')}, 语言: {u.get('language')}")
        
        return True
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    init_database()
