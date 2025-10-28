#!/usr/bin/env python3
"""清空数据库"""
import os
import sys

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_manager import get_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_database():
    """清空所有数据"""
    try:
        db = get_database()
        
        # 清空所有表
        print("正在清空数据库...")
        
        # 删除所有数据
        if hasattr(db, 'conn') and db.conn:  # PostgreSQL
            cursor = db.conn.cursor()
            cursor.execute("TRUNCATE TABLE conversations CASCADE")
            cursor.execute("TRUNCATE TABLE wallet_info CASCADE")
            cursor.execute("TRUNCATE TABLE users CASCADE")
            db.conn.commit()
            print("✅ PostgreSQL数据库已清空")
        else:  # SQLite
            import sqlite3
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations")
            cursor.execute("DELETE FROM wallet_info")
            cursor.execute("DELETE FROM users")
            conn.commit()
            conn.close()
            print("✅ SQLite数据库已清空")
            
        print("✅ 数据库清空完成！")
        
    except Exception as e:
        print(f"❌ 清空数据库失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    clear_database()
