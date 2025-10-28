"""
数据库管理器 - 本地SQLite数据库
数据仅存储在本地，不对外传输
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import threading


class DatabaseManager:
    """数据库管理器 - 本地SQLite存储"""
    
    def __init__(self, db_path: str = 'user_data.db'):
        """
        初始化数据库管理器
        
        参数:
            db_path: 数据库文件路径（本地存储）
        """
        self.db_path = db_path
        self.lock = threading.Lock()
        
        # 创建数据库和表
        self._create_tables()
        
    def _create_tables(self):
        """创建数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute("""
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
            
            # 对话历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # 钱包信息表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wallet_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    wallet_address TEXT,
                    balance REAL DEFAULT 0,
                    previous_balance REAL DEFAULT 0,
                    status TEXT,
                    is_active INTEGER DEFAULT 1,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    UNIQUE(user_id)
                )
            """)
            
            # 推送记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS push_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'sent',
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # 操作日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS operation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    operation_type TEXT NOT NULL,
                    details TEXT,
                    operator TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            conn.commit()
    
    def save_user(self, user_id: int, data: Dict[str, Any]):
        """
        保存或更新用户数据
        
        参数:
            user_id: 用户ID
            data: 用户数据字典
        """
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 检查用户是否存在
                cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                exists = cursor.fetchone()
                
                if exists:
                    # 更新用户信息
                    cursor.execute("""
                        UPDATE users 
                        SET username = ?, first_name = ?, last_name = ?,
                            language = ?, state = ?, wallet = ?, note = ?,
                            transfer_completed = ?, avatar_url = ?, ip_info = ?,
                            updated_at = ?
                        WHERE user_id = ?
                    """, (
                        data.get('username'),
                        data.get('first_name'),
                        data.get('last_name'),
                        data.get('language', 'zh'),
                        data.get('state', 'idle'),
                        data.get('wallet'),
                        data.get('note'),
                        1 if data.get('transfer_completed', False) else 0,
                        data.get('avatar_url'),
                        data.get('ip_info'),
                        datetime.now().isoformat(),
                        user_id
                    ))
                else:
                    # 插入新用户
                    cursor.execute("""
                        INSERT INTO users (user_id, username, first_name, last_name,
                                          language, state, wallet, note, transfer_completed,
                                          avatar_url, ip_info)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        data.get('username'),
                        data.get('first_name'),
                        data.get('last_name'),
                        data.get('language', 'zh'),
                        data.get('state', 'idle'),
                        data.get('wallet'),
                        data.get('note'),
                        1 if data.get('transfer_completed', False) else 0,
                        data.get('avatar_url'),
                        data.get('ip_info')
                    ))
                
                conn.commit()
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        获取用户数据
        
        参数:
            user_id: 用户ID
            
        返回:
            用户数据字典
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_all_users(self) -> list:
        """
        获取所有用户
        
        返回:
            用户列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def save_conversation(self, user_id: int, role: str, content: str):
        """
        保存对话记录
        
        参数:
            user_id: 用户ID
            role: 角色（user/assistant）
            content: 对话内容
        """
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversations (user_id, role, content)
                    VALUES (?, ?, ?)
                """, (user_id, role, content))
                conn.commit()
    
    def get_conversations(self, user_id: int, limit: int = 100) -> list:
        """
        获取用户对话历史
        
        参数:
            user_id: 用户ID
            limit: 返回记录数限制
            
        返回:
            对话历史列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT role, content, timestamp 
                FROM conversations 
                WHERE user_id = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (user_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_wallet_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        获取用户钱包信息
        
        参数:
            user_id: 用户ID
            
        返回:
            钱包信息字典
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM wallet_info WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def save_wallet_info(self, user_id: int, wallet_info: Dict[str, Any]):
        """
        保存钱包信息
        
        参数:
            user_id: 用户ID
            wallet_info: 钱包信息字典
        """
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 检查钱包信息是否存在
                cursor.execute("SELECT user_id FROM wallet_info WHERE user_id = ?", (user_id,))
                exists = cursor.fetchone()
                
                if exists:
                    cursor.execute("""
                        UPDATE wallet_info
                        SET wallet_address = ?, balance = ?, previous_balance = ?,
                            status = ?, is_active = ?, updated_at = ?
                        WHERE user_id = ?
                    """, (
                        wallet_info.get('wallet_address'),
                        wallet_info.get('balance', 0),
                        wallet_info.get('previous_balance', 0),
                        wallet_info.get('status'),
                        1 if wallet_info.get('is_active', False) else 0,
                        datetime.now().isoformat(),
                        user_id
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO wallet_info (user_id, wallet_address, balance, 
                                                previous_balance, status, is_active)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        wallet_info.get('wallet_address'),
                        wallet_info.get('balance', 0),
                        wallet_info.get('previous_balance', 0),
                        wallet_info.get('status'),
                        1 if wallet_info.get('is_active', False) else 0
                    ))
                
                conn.commit()
    
    def add_operation_log(self, user_id: int, operation_type: str, details: str, operator: str = 'system'):
        """
        记录操作日志
        
        参数:
            user_id: 用户ID
            operation_type: 操作类型
            details: 操作详情
            operator: 操作者
        """
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO operation_logs (user_id, operation_type, details, operator)
                    VALUES (?, ?, ?, ?)
                """, (user_id, operation_type, details, operator))
                conn.commit()
    
    def backup_database(self, backup_path: str = None):
        """
        备份数据库（本地备份）
        
        参数:
            backup_path: 备份文件路径（默认为当前目录）
        """
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'backup_{timestamp}.db'
        
        # 复制数据库文件
        with open(self.db_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        
        return backup_path
    
    def migrate_from_json(self, json_path: str):
        """
        从JSON文件迁移数据到数据库
        
        参数:
            json_path: JSON文件路径
        """
        if not os.path.exists(json_path):
            print(f"文件不存在: {json_path}")
            return
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            conn.execute('BEGIN TRANSACTION')
            
            try:
                for user_id_str, user_data in data.items():
                    user_id = int(user_id_str)
                    
                    # 保存用户基本信息
                    user_info = {
                        'username': user_data.get('username'),
                        'first_name': user_data.get('first_name'),
                        'last_name': user_data.get('last_name'),
                        'language': user_data.get('language', 'zh'),
                        'state': user_data.get('state', 'idle'),
                        'wallet': user_data.get('wallet'),
                        'note': user_data.get('note'),
                        'transfer_completed': user_data.get('transfer_completed', False)
                    }
                    
                    # 保存用户
                    cursor.execute("""
                        INSERT OR REPLACE INTO users 
                        (user_id, username, first_name, last_name, language, state, 
                         wallet, note, transfer_completed, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        user_info['username'],
                        user_info['first_name'],
                        user_info['last_name'],
                        user_info['language'],
                        user_info['state'],
                        user_info['wallet'],
                        user_info['note'],
                        1 if user_info['transfer_completed'] else 0,
                        datetime.now().isoformat()
                    ))
                    
                    # 保存对话历史
                    if 'history' in user_data:
                        for msg in user_data['history']:
                            cursor.execute("""
                                INSERT INTO conversations (user_id, role, content)
                                VALUES (?, ?, ?)
                            """, (user_id, msg['role'], msg['content']))
                    
                    # 保存钱包信息
                    if 'wallet_info' in user_data:
                        wallet_info = user_data['wallet_info']
                        cursor.execute("""
                            INSERT OR REPLACE INTO wallet_info 
                            (user_id, wallet_address, balance, previous_balance, status, is_active)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            user_id,
                            wallet_info.get('wallet_address'),
                            wallet_info.get('balance', 0),
                            wallet_info.get('previous_balance', 0),
                            wallet_info.get('status'),
                            1 if wallet_info.get('is_active', False) else 0
                        ))
                
                conn.commit()
                print(f"✅ 成功迁移 {len(data)} 个用户数据")
                
            except Exception as e:
                conn.rollback()
                print(f"❌ 迁移失败: {e}")


# 全局数据库管理器实例
_db_manager = None

def get_database() -> DatabaseManager:
    """获取数据库管理器实例（单例模式）"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

