#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动备份脚本 - 定期备份数据库
功能：
1. 每日自动备份
2. 备份保留策略（保留最近7天的备份）
3. 自动清理旧备份
"""

import os
import sys
import shutil
from datetime import datetime, timedelta
from database_manager import get_database

# 配置
BACKUP_DIR = 'backups'
DB_FILE = 'user_data.db'
KEEP_DAYS = 7  # 保留最近7天的备份

def create_backup():
    """创建数据库备份"""
    try:
        # 确保备份目录存在
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        # 生成备份文件名（带时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'user_data_backup_{timestamp}.db'
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        # 复制数据库文件
        if os.path.exists(DB_FILE):
            shutil.copy2(DB_FILE, backup_path)
            print(f"✅ 备份成功: {backup_path}")
            
            # 返回备份文件路径
            return backup_path
        else:
            print(f"❌ 数据库文件不存在: {DB_FILE}")
            return None
            
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None

def clean_old_backups():
    """清理旧的备份文件"""
    try:
        if not os.path.exists(BACKUP_DIR):
            return
        
        # 获取所有备份文件
        backup_files = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith('user_data_backup_') and filename.endswith('.db'):
                filepath = os.path.join(BACKUP_DIR, filename)
                mtime = os.path.getmtime(filepath)
                backup_files.append((filepath, mtime))
        
        # 计算过期时间
        expire_time = (datetime.now() - timedelta(days=KEEP_DAYS)).timestamp()
        
        # 删除过期备份
        deleted_count = 0
        for filepath, mtime in backup_files:
            if mtime < expire_time:
                os.remove(filepath)
                deleted_count += 1
                print(f"🗑️  删除旧备份: {filepath}")
        
        if deleted_count > 0:
            print(f"✅ 已清理 {deleted_count} 个旧备份")
        else:
            print("✅ 无需清理旧备份")
            
    except Exception as e:
        print(f"❌ 清理失败: {e}")

def list_backups():
    """列出所有备份文件"""
    try:
        if not os.path.exists(BACKUP_DIR):
            print("📁 备份目录不存在")
            return []
        
        backups = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith('user_data_backup_') and filename.endswith('.db'):
                filepath = os.path.join(BACKUP_DIR, filename)
                size = os.path.getsize(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'size': size,
                    'date': mtime
                })
        
        # 按时间排序
        backups.sort(key=lambda x: x['date'], reverse=True)
        return backups
        
    except Exception as e:
        print(f"❌ 列出备份失败: {e}")
        return []

def restore_backup(backup_filename):
    """恢复备份"""
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        if not os.path.exists(backup_path):
            print(f"❌ 备份文件不存在: {backup_path}")
            return False
        
        # 备份当前数据库
        if os.path.exists(DB_FILE):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            current_backup = f'{DB_FILE}.{timestamp}.bak'
            shutil.copy2(DB_FILE, current_backup)
            print(f"📦 已备份当前数据库: {current_backup}")
        
        # 恢复备份
        shutil.copy2(backup_path, DB_FILE)
        print(f"✅ 已恢复备份: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("💾 自动备份工具")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'backup':
            print("🔄 开始备份...")
            create_backup()
            clean_old_backups()
            
        elif command == 'list':
            print("📋 备份列表:")
            backups = list_backups()
            for i, backup in enumerate(backups, 1):
                size_mb = backup['size'] / 1024 / 1024
                print(f"{i}. {backup['filename']}")
                print(f"   时间: {backup['date'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   大小: {size_mb:.2f} MB")
                print()
        
        elif command == 'restore':
            if len(sys.argv) < 3:
                print("❌ 请指定要恢复的备份文件名")
                print("   用法: python auto_backup.py restore <backup_filename>")
                return
            
            backup_filename = sys.argv[2]
            print(f"🔄 开始恢复备份: {backup_filename}")
            restore_backup(backup_filename)
        
        elif command == 'clean':
            print("🗑️  清理旧备份...")
            clean_old_backups()
        
        else:
            print(f"❌ 未知命令: {command}")
            print()
            print("可用命令:")
            print("  backup  - 创建备份并清理旧备份")
            print("  list    - 列出所有备份")
            print("  restore <filename> - 恢复指定备份")
            print("  clean   - 清理旧备份")
    else:
        # 默认行为：创建备份
        print("🔄 开始备份...")
        create_backup()
        clean_old_backups()
    
    print()
    print("=" * 60)
    print("✅ 完成")
    print("=" * 60)

if __name__ == '__main__':
    main()

