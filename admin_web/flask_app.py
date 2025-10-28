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
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_session import Session
import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

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
    print(f"✅ 数据库已加载，当前有 {len(users)} 个用户")
except Exception as e:
    print(f"❌ 数据库加载失败: {e}")
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
        print(f"加载会话失败: {e}")
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
        print(f"保存会话失败: {e}")

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
        print(f"发送消息失败: {e}")
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
    
    # 详细统计
    stats = {
        'total_users': total_users,
        'new_users_today': total_users,  # 暂时等于总数
        'pending_messages': sum(1 for u in sessions.values() if u.get('state') == 'waiting_customer_service'),
        'active_sessions': total_users,
        'waiting_service': sum(1 for u in sessions.values() if u.get('state') == 'waiting_customer_service'),
        'bound': sum(1 for u in sessions.values() if u.get('state') == 'bound_and_ready'),
        'wallet_checked': sum(1 for u in sessions.values() if u.get('state') == 'wallet_checking'),
        'wallet_verified': sum(1 for u in sessions.values() if u.get('state') == 'wallet_verified')
    }
    
    # 获取最近10个用户
    recent_users = []
    for user_id, user_data in list(sessions.items())[:10]:
        recent_users.append({
            'user_id': user_id,
            'username': user_data.get('username', 'N/A'),
            'language': user_data.get('language', 'zh'),
            'state': user_data.get('state', 'idle'),
            'created_at': None  # 暂时不显示
        })
    
    # 转化漏斗数据
    funnel = {
        'step1_registered': stats['total_users'],
        'step2_wallet_created': stats['wallet_verified'] + stats['bound'],
        'step3_waiting_service': stats['waiting_service'],
        'step4_bound': stats['bound'],
        'step5_transfer_completed': sum(1 for u in sessions.values() if u.get('transfer_completed', False))
    }
    
    # 使用 Tailwind 模板
    return render_template('dashboard_tailwind.html', 
                         stats=stats, 
                         recent_users=recent_users, 
                         funnel=funnel,
                         users=load_sessions(),
                         active_users=stats['active_sessions'],
                         today_users=stats['new_users_today'],
                         completed_count=sum(1 for u in sessions.values() if u.get('transfer_completed', False)))

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
        conversion_rates = {
            'to_wallet': (sum(1 for u in sessions.values() if u.get('wallet')) / total * 100) if total else 0,
            'to_service': (sum(1 for u in sessions.values() if u.get('state') == 'waiting_customer_service') / total * 100) if total else 0,
            'to_bound': (sum(1 for u in sessions.values() if u.get('state') == 'bound_and_ready') / total * 100) if total else 0,
            'to_transfer': (sum(1 for u in sessions.values() if u.get('transfer_completed', False)) / total * 100) if total else 0
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
    
    for user_id, data in sessions.items():
        user_state = data.get('state', 'unknown')
        
        # 如果指定了状态筛选，只显示匹配的用户
        if filter_state and user_state != filter_state:
            continue
            
        users_list.append({
            'user_id': user_id,
            'username': data.get('username', 'N/A'),
            'wallet': data.get('wallet', ''),
            'note': data.get('note', ''),
            'state': user_state,
            'language': data.get('language', 'zh'),
            'transfer_completed': data.get('transfer_completed', False),
            'avatar_url': data.get('avatar_url'),
            'ip_info': data.get('ip_info')
        })
    
    return render_template('users_tailwind.html', users=users_list, filter_state=filter_state)

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
        print(f"删除用户失败: {e}")
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
        print(f"获取对话历史失败: {e}")
        user_data['history'] = []
    
    # 获取钱包信息
    try:
        wallet_info = db.get_wallet_info(user_id)
        if wallet_info:
            user_data['wallet_info'] = wallet_info
    except Exception as e:
        print(f"获取钱包信息失败: {e}")
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

@app.route('/push', methods=['GET', 'POST'])
def push():
    """消息推送"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    sessions = load_sessions()
    
    if request.method == 'POST':
        message = request.form.get('message')
        target_type = request.form.get('target_type', 'all')
        target_users = request.form.get('target_users', '')  # 指定用户ID
        
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
            # 全部用户
            user_list = list(sessions.keys())
        elif target_type == 'waiting':
            # 等待客服的用户
            for user_id, data in sessions.items():
                if data.get('state') == 'waiting_customer_service':
                    user_list.append(user_id)
        elif target_type == 'bound':
            # 已绑定的用户
            for user_id, data in sessions.items():
                if data.get('state') == 'bound_and_ready':
                    user_list.append(user_id)
        
        # 发送消息
        results = []
        for user_id in user_list:
            user_data = sessions.get(user_id, {})
            
            # 替换变量
            personalized_msg = message
            personalized_msg = personalized_msg.replace('{username}', user_data.get('username', '用户'))
            personalized_msg = personalized_msg.replace('{wallet}', user_data.get('wallet', 'N/A'))
            personalized_msg = personalized_msg.replace('{user_id}', str(user_id))
            
            if send_telegram_message(user_id, personalized_msg):
                sent_count += 1
                results.append({'user_id': user_id, 'status': 'success'})
            else:
                failed_count += 1
                results.append({'user_id': user_id, 'status': 'failed'})
        
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
            with open('push_history.json', 'a', encoding='utf-8') as f:
                f.write(json.dumps(push_record, ensure_ascii=False) + '\n')
        except:
            pass
        
        return render_template('push_result.html', 
                             count=sent_count, 
                             failed=failed_count,
                             total=len(user_list),
                             results=results)
    
    # GET请求：渲染推送页面
    # 获取各个状态的用户数量
    stats = {
        'all': len(sessions),
        'waiting': sum(1 for u in sessions.values() if u.get('state') == 'waiting_customer_service'),
        'bound': sum(1 for u in sessions.values() if u.get('state') == 'bound_and_ready'),
        'transfer_completed': sum(1 for u in sessions.values() if u.get('transfer_completed', False))
    }
    
    return render_template('push_tailwind.html', stats=stats, users=sessions)

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

if __name__ == '__main__':
    # 支持Railway和命令行两种启动方式
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

