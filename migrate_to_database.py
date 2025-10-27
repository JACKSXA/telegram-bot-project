#!/usr/bin/env python3
"""
数据迁移脚本 - 将JSON数据迁移到SQLite数据库
所有数据仅存储在本地，不对外传输
"""

import os
import sys
from database_manager import DatabaseManager

def main():
    print("=" * 60)
    print("📊 数据迁移工具 - JSON → SQLite")
    print("=" * 60)
    print()
    
    # 检查JSON文件是否存在
    json_path = 'user_sessions.json'
    if not os.path.exists(json_path):
        print(f"❌ 文件不存在: {json_path}")
        print("   请确保 user_sessions.json 文件存在于当前目录")
        return
    
    # 创建数据库管理器
    db = DatabaseManager(db_path='user_data.db')
    
    print(f"📁 JSON文件: {json_path}")
    print(f"💾 数据库文件: user_data.db")
    print()
    
    # 检查是否要备份现有数据库
    if os.path.exists('user_data.db'):
        print("⚠️  数据库已存在，自动备份...")
        backup_path = db.backup_database()
        print(f"✅ 已备份到: {backup_path}")
        print()
    
    # 执行迁移
    print("🚀 开始迁移数据...")
    print()
    
    try:
        db.migrate_from_json(json_path)
        
        print()
        print("=" * 60)
        print("✅ 迁移完成！")
        print("=" * 60)
        print()
        
        # 验证迁移结果
        users = db.get_all_users()
        print(f"📊 验证结果:")
        print(f"   - 迁移用户数: {len(users)}")
        
        # 显示前5个用户
        print()
        print("📋 前5个用户:")
        for user in users[:5]:
            print(f"   - 用户ID: {user['user_id']}, "
                  f"状态: {user['state']}, "
                  f"语言: {user['language']}")
        
        print()
        print("💡 下一步:")
        print("   1. 数据已迁移到 user_data.db")
        print("   2. 请修改 Bot 代码使用新的数据库")
        print("   3. 建议保留 user_sessions.json 作为备份")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ 迁移失败: {e}")
        print("=" * 60)
        return
    
    print("✨ 迁移成功！")

if __name__ == '__main__':
    main()

