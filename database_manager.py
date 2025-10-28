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
        self.sqlite_conn = None  # SQLite连接缓存
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
            # 对于内存数据库，创建连接缓存
            if self.db_path == ':memory:':
                self.sqlite_conn = sqlite3.connect(':memory:')
                self.sqlite_conn.row_factory = sqlite3.Row
                print(f"✅ SQLite内存数据库连接已缓存")
    
    def _get_cursor(self):
        """获取游标"""
        if USE_POSTGRES:
            return self.conn.cursor(cursor_factory=RealDictCursor)
        else:
            # 对于内存数据库，复用缓存的连接
            if self.db_path == ':memory:' and self.sqlite_conn:
                return self.sqlite_conn, self.sqlite_conn.cursor()
            # 文件数据库，每次创建新连接
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
            # 内存数据库不关闭连接，文件数据库才关闭
            if self.db_path != ':memory:':
                if self.db_path != ":memory:":

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
                channel TEXT,
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
        
        # 业务扩展表：模板中心 / 实验 / 事件 / 旅程（与数据库类型无关）
        templates_table = """
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

        experiments_table = """
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exp_key TEXT NOT NULL,
                variant TEXT NOT NULL,
                weight INTEGER DEFAULT 50,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

        user_events_table = """
            CREATE TABLE IF NOT EXISTS user_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event TEXT NOT NULL,
                meta TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

        journeys_table = """
            CREATE TABLE IF NOT EXISTS journeys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                journey_key TEXT NOT NULL,
                node TEXT NOT NULL,
                config TEXT,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        try:
            self._execute(users_table)
            print(f"✅ users表已创建/已存在")
            self._execute(conversations_table)
            print(f"✅ conversations表已创建/已存在")
            self._execute(wallet_info_table)
            print(f"✅ wallet_info表已创建/已存在")
            # 扩展表
            try:
                self._execute(templates_table)
                print(f"✅ templates表已创建/已存在")
            except Exception as e:
                print(f"⚠️ templates表创建失败: {e}")
            try:
                self._execute(experiments_table)
                print(f"✅ experiments表已创建/已存在")
            except Exception as e:
                print(f"⚠️ experiments表创建失败: {e}")
            try:
                self._execute(user_events_table)
                print(f"✅ user_events表已创建/已存在")
            except Exception as e:
                print(f"⚠️ user_events表创建失败: {e}")
            try:
                self._execute(journeys_table)
                print(f"✅ journeys表已创建/已存在")
            except Exception as e:
                print(f"⚠️ journeys表创建失败: {e}")
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
                    if self.db_path == ':memory:' and self.sqlite_conn:
                        conn = self.sqlite_conn
                        cursor = conn.cursor()
                    else:
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
                    if self.db_path != ':memory:':
                        if self.db_path != ":memory:":

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
                             (int(user_id), str(role or ''), str(content or '')))
                conn.commit()
                if self.db_path != ":memory:":

                    conn.close()
        except Exception as e:
            print(f"保存对话失败: {e}")
            import traceback
            traceback.print_exc()
    
    def get_conversations(self, user_id: int, limit: int = 100) -> list:
        """获取用户对话历史"""
        try:
            # 取最新limit条，再按时间升序（旧->新），确保能看到最新消息
            query = (
                "SELECT role, content, timestamp FROM ("
                " SELECT role, content, timestamp FROM conversations"
                " WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s"
                ") t ORDER BY timestamp ASC"
            )
            if USE_POSTGRES:
                cursor = self._get_cursor()
                cursor.execute(query, (user_id, limit))
                return [dict(row) for row in cursor.fetchall()]
            else:
                conn, cursor = self._get_cursor()
                cursor.execute(
                    "SELECT role, content, timestamp FROM ("
                    " SELECT role, content, timestamp FROM conversations"
                    " WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?"
                    ") t ORDER BY timestamp ASC",
                    (user_id, limit)
                )
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

    # ====== A/B 测试引擎 ======
    def create_experiment(self, exp_key: str, variant: str, weight: int = 50) -> bool:
        """创建A/B测试实验"""
        try:
            if USE_POSTGRES:
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO experiments (exp_key, variant, weight, active) VALUES (%s, %s, %s, 1)", (exp_key, variant, weight))
                self.conn.commit()
                return True
            else:
                conn, cursor = self._get_cursor()
                cursor.execute("INSERT INTO experiments (exp_key, variant, weight, active) VALUES (?, ?, ?, 1)", (exp_key, variant, weight))
                conn.commit()
                if self.db_path != ":memory:":
                    conn.close()
                return True
        except Exception as e:
            print(f"创建实验失败: {e}")
            return False
    
    def get_experiment_variant(self, exp_key: str) -> Optional[str]:
        """获取用户应使用的实验变体"""
        try:
            if USE_POSTGRES:
                cursor = self._get_cursor()
                cursor.execute("SELECT variant, weight FROM experiments WHERE exp_key = %s AND active = 1", (exp_key,))
                rows = cursor.fetchall()
            else:
                conn, cursor = self._get_cursor()
                cursor.execute("SELECT variant, weight FROM experiments WHERE exp_key = ? AND active = 1", (exp_key,))
                rows = cursor.fetchall()
                if self.db_path != ":memory:":
                    conn.close()
            
            if not rows:
                return None
            
            # 按权重随机分配
            import random
            variants = [(r['variant'], r['weight']) for r in rows]
            total_weight = sum(w for _, w in variants)
            if total_weight == 0:
                return variants[0][0] if variants else None
            
            r = random.random() * total_weight
            cumsum = 0
            for variant, weight in variants:
                cumsum += weight
                if r < cumsum:
                    return variant
            return variants[-1][0] if variants else None
        except Exception as e:
            print(f"获取实验变体失败: {e}")
            return None
    
    def record_user_event(self, user_id: int, event: str, meta: Dict[str, Any] = None) -> bool:
        """记录用户事件（用于A/B测试和旅程）"""
        try:
            meta_json = json.dumps(meta) if meta else None
            if USE_POSTGRES:
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO user_events (user_id, event, meta) VALUES (%s, %s, %s)", (user_id, event, meta_json))
                self.conn.commit()
                return True
            else:
                conn, cursor = self._get_cursor()
                cursor.execute("INSERT INTO user_events (user_id, event, meta) VALUES (?, ?, ?)", (user_id, event, meta_json))
                conn.commit()
                if self.db_path != ":memory:":
                    conn.close()
                return True
        except Exception as e:
            print(f"记录事件失败: {e}")
            return False
    
    # ====== 营销旅程 ======
    def create_journey_node(self, journey_key: str, node: str, config: Dict[str, Any]) -> bool:
        """创建旅程节点（状态触发点）"""
        try:
            config_json = json.dumps(config) if config else None
            if USE_POSTGRES:
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO journeys (journey_key, node, config, active) VALUES (%s, %s, %s, 1)", (journey_key, node, config_json))
                self.conn.commit()
                return True
            else:
                conn, cursor = self._get_cursor()
                cursor.execute("INSERT INTO journeys (journey_key, node, config, active) VALUES (?, ?, ?, 1)", (journey_key, node, config_json))
                conn.commit()
                if self.db_path != ":memory:":
                    conn.close()
                return True
        except Exception as e:
            print(f"创建旅程节点失败: {e}")
            return False
    
    def get_journey_nodes(self, journey_key: str) -> list:
        """获取旅程的所有节点"""
        try:
            if USE_POSTGRES:
                cursor = self._get_cursor()
                cursor.execute("SELECT node, config, active FROM journeys WHERE journey_key = %s AND active = 1", (journey_key,))
                return [dict(row) for row in cursor.fetchall()]
            else:
                conn, cursor = self._get_cursor()
                cursor.execute("SELECT node, config, active FROM journeys WHERE journey_key = ? AND active = 1", (journey_key,))
                rows = [dict(row) for row in cursor.fetchall()]
                if self.db_path != ":memory:":
                    conn.close()
                return rows
        except Exception as e:
            print(f"获取旅程节点失败: {e}")
            return []
    
    def check_journey_trigger(self, user_id: int, trigger_state: str) -> Optional[Dict[str, Any]]:
        """检查是否应该触发旅程动作"""
        try:
            # 检查是否有针对该状态的旅程配置
            journey_key = f"state_{trigger_state}"
            nodes = self.get_journey_nodes(journey_key)
            
            if not nodes:
                return None
            
            # 返回第一个活跃节点的配置
            for node in nodes:
                if node.get('active', 1) == 1:
                    config = node.get('config')
                    if config:
                        try:
                            return json.loads(config) if isinstance(config, str) else config
                        except:
                            pass
            return None
        except Exception as e:
            print(f"检查旅程触发失败: {e}")
            return None
    
    # ====== 模板中心 ======
    def get_templates(self, active_only: bool = True) -> list:
        """获取消息模板列表"""
        try:
            if USE_POSTGRES:
                cursor = self._get_cursor()
                if active_only:
                    cursor.execute("SELECT id, name, type, content, active, created_at FROM templates WHERE active=1 ORDER BY id DESC")
                else:
                    cursor.execute("SELECT id, name, type, content, active, created_at FROM templates ORDER BY id DESC")
                return [dict(row) for row in cursor.fetchall()]
            else:
                conn, cursor = self._get_cursor()
                if active_only:
                    cursor.execute("SELECT id, name, type, content, active, created_at FROM templates WHERE active=1 ORDER BY id DESC")
                else:
                    cursor.execute("SELECT id, name, type, content, active, created_at FROM templates ORDER BY id DESC")
                rows = [dict(row) for row in cursor.fetchall()]
                if self.db_path != ":memory:":

                    conn.close()
                return rows
        except Exception as e:
            print(f"获取模板失败: {e}")
            return []

    def save_template(self, name: str, type_: str, content: str, active: int = 1) -> bool:
        """保存新模板"""
        try:
            if USE_POSTGRES:
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO templates (name, type, content, active) VALUES (%s, %s, %s, %s)", (name, type_, content, active))
                self.conn.commit()
                return True
            else:
                conn, cursor = self._get_cursor()
                cursor.execute("INSERT INTO templates (name, type, content, active) VALUES (?, ?, ?, ?)", (name, type_, content, active))
                conn.commit()
                if self.db_path != ":memory:":

                    conn.close()
                return True
        except Exception as e:
            print(f"保存模板失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ====== 渠道漏斗 ======
    def get_funnel_by_channel(self) -> list:
        """按渠道统计漏斗"""
        try:
            if USE_POSTGRES:
                cursor = self._get_cursor()
                cursor.execute(
                    """
                    SELECT COALESCE(channel,'unknown') AS channel,
                           COUNT(*) AS total,
                           SUM(CASE WHEN COALESCE(wallet,'') <> '' THEN 1 ELSE 0 END) AS wallet_bound,
                           SUM(CASE WHEN state IN ('waiting_customer_service','waiting') THEN 1 ELSE 0 END) AS waiting_cs,
                           SUM(CASE WHEN state IN ('bound_and_ready','bound','completed') THEN 1 ELSE 0 END) AS bound_ready,
                           SUM(CASE WHEN transfer_completed = TRUE OR transfer_completed = 1 THEN 1 ELSE 0 END) AS transfer_completed
                    FROM users
                    GROUP BY COALESCE(channel,'unknown')
                    ORDER BY total DESC
                    """
                )
                return [dict(row) for row in cursor.fetchall()]
            else:
                conn, cursor = self._get_cursor()
                cursor.execute(
                    """
                    SELECT IFNULL(channel,'unknown') AS channel,
                           COUNT(*) AS total,
                           SUM(CASE WHEN IFNULL(wallet,'') <> '' THEN 1 ELSE 0 END) AS wallet_bound,
                           SUM(CASE WHEN state IN ('waiting_customer_service','waiting') THEN 1 ELSE 0 END) AS waiting_cs,
                           SUM(CASE WHEN state IN ('bound_and_ready','bound','completed') THEN 1 ELSE 0 END) AS bound_ready,
                           SUM(CASE WHEN transfer_completed = 1 THEN 1 ELSE 0 END) AS transfer_completed
                    FROM users
                    GROUP BY IFNULL(channel,'unknown')
                    ORDER BY total DESC
                    """
                )
                rows = [dict(row) for row in cursor.fetchall()]
                if self.db_path != ":memory:":

                    conn.close()
                return rows
        except Exception as e:
            print(f"按渠道统计失败: {e}")
            return []

    # ====== 分析统计：直接数据库聚合，避免内存不同步 ======
    def get_analytics_snapshot(self) -> Dict[str, Any]:
        """返回分析页所需的快照数据（总数、状态分布、语言分布、转化漏斗）"""
        try:
            if USE_POSTGRES:
                cursor = self._get_cursor()
                # 总用户数
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]

                # 状态分布
                cursor.execute("SELECT state, COUNT(*) FROM users GROUP BY state")
                state_rows = cursor.fetchall()
                state_distribution = {row[0] or 'unknown': row[1] for row in state_rows}

                # 语言分布
                cursor.execute("SELECT language, COUNT(*) FROM users GROUP BY language")
                lang_rows = cursor.fetchall()
                language_distribution = {row[0] or 'unknown': row[1] for row in lang_rows}

                # 各环节统计
                cursor.execute("SELECT COUNT(*) FROM users WHERE COALESCE(wallet, '') <> ''")
                wallet_bound = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM users WHERE state IN ('waiting_customer_service','waiting')")
                waiting_cs = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM users WHERE state IN ('bound_and_ready','bound','completed')")
                bound_ready = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM users WHERE transfer_completed = TRUE OR transfer_completed = 1")
                transfer_completed = cursor.fetchone()[0]
            else:
                conn, cursor = self._get_cursor()
                # 总用户数
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]

                # 状态分布
                cursor.execute("SELECT state, COUNT(*) FROM users GROUP BY state")
                state_rows = cursor.fetchall()
                state_distribution = {row[0] or 'unknown': row[1] for row in state_rows}

                # 语言分布
                cursor.execute("SELECT language, COUNT(*) FROM users GROUP BY language")
                lang_rows = cursor.fetchall()
                language_distribution = {row[0] or 'unknown': row[1] for row in lang_rows}

                # 各环节统计
                cursor.execute("SELECT COUNT(*) FROM users WHERE IFNULL(wallet, '') <> ''")
                wallet_bound = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM users WHERE state IN ('waiting_customer_service','waiting')")
                waiting_cs = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM users WHERE state IN ('bound_and_ready','bound','completed')")
                bound_ready = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM users WHERE transfer_completed = 1")
                transfer_completed = cursor.fetchone()[0]
                if self.db_path != ":memory:":

                    conn.close()

            # 转化率
            if total_users > 0:
                conversion_rates = {
                    'to_wallet': wallet_bound / total_users * 100,
                    'to_service': waiting_cs / total_users * 100,
                    'to_bound': bound_ready / total_users * 100,
                    'to_transfer': transfer_completed / total_users * 100,
                }
            else:
                conversion_rates = {'to_wallet': 0, 'to_service': 0, 'to_bound': 0, 'to_transfer': 0}

            return {
                'total_users': total_users,
                'state_distribution': state_distribution,
                'language_distribution': language_distribution,
                'conversion_rates': conversion_rates,
                'wallet_bound': wallet_bound,
                'waiting_cs': waiting_cs,
                'bound_ready': bound_ready,
                'transfer_completed': transfer_completed,
            }
        except Exception as e:
            print(f"获取分析快照失败: {e}")
            return {
                'total_users': 0,
                'state_distribution': {},
                'language_distribution': {},
                'conversion_rates': {'to_wallet': 0, 'to_service': 0, 'to_bound': 0, 'to_transfer': 0},
                'wallet_bound': 0,
                'waiting_cs': 0,
                'bound_ready': 0,
                'transfer_completed': 0,
            }

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
