"""
数据库管理器 V2 - 支持PostgreSQL和SQLite
自动检测环境变量选择数据库类型
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import threading

# 检测使用哪个数据库
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    # 使用PostgreSQL
    import psycopg2
    from psycopg2.extras import RealDictCursor
    USE_POSTGRES = True
else:
    import sqlite3
    USE_POSTGRES = False

class DatabaseManager:
    """数据库管理器 - 自动选择PostgreSQL或SQLite"""
    
    def __init__(self, db_path: str = None):
        self.lock = threading.Lock()
        # 保存数据库路径
        self.db_path = db_path or 'user_data.db'
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """连接到数据库"""
        if USE_POSTGRES:
            try:
                print(f"🔗 尝试连接到PostgreSQL...")
                self.conn = psycopg2.connect(DATABASE_URL)
                self.cursor = self.conn.cursor()
                print(f"✅ PostgreSQL连接成功")
            except Exception as e:
                print(f"❌ PostgreSQL连接失败: {e}")
                print(f"DATABASE_URL: {DATABASE_URL}")
                raise
        else:
            # 使用传入的路径或默认路径
            if not hasattr(self, 'db_path'):
                self.db_path = 'user_data.db'
            print(f"📁 使用SQLite数据库: {self.db_path}")
    
    def _get_cursor(self):
        """获取游标"""
        if USE_POSTGRES:
            return self.conn.cursor(cursor_factory=RealDictCursor)
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn, conn.cursor()
    
    def _execute(self, query, params=None):
        """执行SQL"""
        if USE_POSTGRES:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.conn.commit()
            return cursor
        else:
            conn, cursor = self._get_cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            conn.close()
            return cursor
    
    def _fetchall(self, cursor):
        """获取所有结果"""
        if USE_POSTGRES:
            return [dict(row) for row in cursor.fetchall()]
        else:
            return [dict(row) for row in cursor.fetchall()]
    
    def _create_tables(self):
        """创建数据库表结构"""
        # SQL定义（SQLite和PostgreSQL都支持）
        users_table = """
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
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
        """
        
        # 对于SQLite，需要调整语法
        if USE_POSTGRES:
            conversations_table = """
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """
            
            wallet_info_table = """
                CREATE TABLE IF NOT EXISTS wallet_info (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    wallet_address TEXT,
                    balance DOUBLE PRECISION DEFAULT 0,
                    previous_balance DOUBLE PRECISION DEFAULT 0,
                    status TEXT,
                    is_active INTEGER DEFAULT 1,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    UNIQUE(user_id)
                )
            """
        else:
            conversations_table = """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            
            wallet_info_table = """
                CREATE TABLE IF NOT EXISTS wallet_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    wallet_address TEXT,
                    balance REAL DEFAULT 0,
                    previous_balance REAL DEFAULT 0,
                    status TEXT,
                    is_active INTEGER DEFAULT 1,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            
            users_table = users_table.replace('BIGINT', 'INTEGER')
        
        try:
            self._execute(users_table)
            print(f"✅ users表已创建/已存在")
            self._execute(conversations_table)
            print(f"✅ conversations表已创建/已存在")
            self._execute(wallet_info_table)
            print(f"✅ wallet_info表已创建/已存在")
        except Exception as e:
            print(f"❌ 创建表失败: {e}")
            import traceback
            traceback.print_exc()
    
    def save_user(self, user_id: int, data: Dict[str, Any]):
        """保存或更新用户数据"""
        with self.lock:
            try:
                user_info = {
                    'username': data.get('username'),
                    'first_name': data.get('first_name'),
                    'last_name': data.get('last_name'),
                    'language': data.get('language', 'zh'),
                    'state': data.get('state', 'idle'),
                    'wallet': data.get('wallet'),
                    'note': data.get('note'),
                    'transfer_completed': 1 if data.get('transfer_completed', False) else 0,
                    'avatar_url': data.get('avatar_url'),
                    'ip_info': data.get('ip_info'),
                    'updated_at': datetime.now().isoformat()
                }
                
                # UPSERT操作
                if USE_POSTGRES:
                    query = """
                        INSERT INTO users (user_id, username, first_name, last_name, language, state, 
                                          wallet, note, transfer_completed, avatar_url, ip_info, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (user_id) 
                        DO UPDATE SET username=%s, first_name=%s, last_name=%s, language=%s, state=%s,
                                      wallet=%s, note=%s, transfer_completed=%s, avatar_url=%s, 
                                      ip_info=%s, updated_at=%s
                    """
                    cursor = self._execute(query, (
                        user_id, user_info['username'], user_info['first_name'], user_info['last_name'],
                        user_info['language'], user_info['state'], user_info['wallet'], user_info['note'],
                        user_info['transfer_completed'], user_info['avatar_url'], user_info['ip_info'], user_info['updated_at'],
                        user_info['username'], user_info['first_name'], user_info['last_name'],
                        user_info['language'], user_info['state'], user_info['wallet'], user_info['note'],
                        user_info['transfer_completed'], user_info['avatar_url'], user_info['ip_info'], user_info['updated_at']
                    ))
                    cursor.close()
                else:
                    # SQLite逻辑
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                    exists = cursor.fetchone()
                    
                    if exists:
                        cursor.execute("""
                            UPDATE users SET username=?, first_name=?, last_name=?, language=?, state=?,
                                wallet=?, note=?, transfer_completed=?, avatar_url=?, ip_info=?, updated_at=?
                            WHERE user_id=?
                        """, (
                            user_info['username'], user_info['first_name'], user_info['last_name'],
                            user_info['language'], user_info['state'], user_info['wallet'], user_info['note'],
                            user_info['transfer_completed'], user_info['avatar_url'], user_info['ip_info'],
                            user_info['updated_at'], user_id
                        ))
                    else:
                        cursor.execute("""
                            INSERT INTO users (user_id, username, first_name, last_name, language, state,
                                wallet, note, transfer_completed, avatar_url, ip_info, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            user_id, user_info['username'], user_info['first_name'], user_info['last_name'],
                            user_info['language'], user_info['state'], user_info['wallet'], user_info['note'],
                            user_info['transfer_completed'], user_info['avatar_url'], user_info['ip_info'],
                            user_info['updated_at']
                        ))
                    conn.commit()
                    conn.close()
                    
            except Exception as e:
                print(f"保存用户失败: {e}")
    
    def get_all_users(self) -> list:
        """获取所有用户"""
        try:
            if USE_POSTGRES:
                cursor = self._get_cursor()
                cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
                return [dict(row) for row in cursor.fetchall()]
            else:
                conn, cursor = self._get_cursor()
                cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"获取用户列表失败: {e}")
            return []
    
    def save_conversation(self, user_id: int, role: str, content: str):
        """保存对话记录"""
        try:
            query = "INSERT INTO conversations (user_id, role, content) VALUES (%s, %s, %s)"
            if USE_POSTGRES:
                cursor = self.conn.cursor()
                cursor.execute(query, (user_id, role, content))
                self.conn.commit()
            else:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO conversations (user_id, role, content) VALUES (?, ?, ?)",
                             (user_id, role, content))
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"保存对话失败: {e}")
    
    def get_conversations(self, user_id: int, limit: int = 100) -> list:
        """获取用户对话历史"""
        try:
            query = "SELECT role, content, timestamp FROM conversations WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s"
            if USE_POSTGRES:
                cursor = self._get_cursor()
                cursor.execute(query, (user_id, limit))
                return [dict(row) for row in cursor.fetchall()]
            else:
                conn, cursor = self._get_cursor()
                cursor.execute("SELECT role, content, timestamp FROM conversations WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                             (user_id, limit))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"获取对话历史失败: {e}")
            return []
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户数据"""
        query = "SELECT * FROM users WHERE user_id = %s"
        try:
            if USE_POSTGRES:
                cursor = self._get_cursor()
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
            else:
                conn, cursor = self._get_cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"获取用户失败: {e}")
            return None

# 全局数据库管理器实例
_db_manager = None

def get_database(db_path: str = None) -> DatabaseManager:
    """获取数据库管理器实例（单例模式）"""
    global _db_manager
    
    # 检查PostgreSQL环境变量
    postgres_url = os.getenv('DATABASE_URL')
    if postgres_url and postgres_url.startswith('postgresql://'):
        # 使用PostgreSQL
        print("✅ 检测到PostgreSQL，使用云数据库")
        if _db_manager is None:
            _db_manager = DatabaseManager()
        return _db_manager
    
    # 使用SQLite（默认）
    print("📁 使用SQLite数据库")
    if _db_manager is None:
        # 统一使用项目根目录的 user_data.db，避免进程工作目录不同导致读写不同数据库
        project_root = os.path.dirname(os.path.abspath(__file__))
        sqlite_path = db_path or os.path.join(project_root, 'user_data.db')
        _db_manager = DatabaseManager(sqlite_path)
    return _db_manager
