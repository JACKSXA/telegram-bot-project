#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot Webhook 端点
用于接收Telegram消息并获取用户真实IP
"""

import os
import json
import logging
import requests
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def get_ip_details(ip_address: str) -> Dict:
    """查询IP详细信息"""
    try:
        response = requests.get(
            f'http://ip-api.com/json/{ip_address}',
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return {
                'ip': ip_address,
                'country': data.get('country', '未知'),
                'region': data.get('regionName', '未知'),
                'city': data.get('city', '未知'),
                'isp': data.get('isp', '未知'),
                'proxy': data.get('proxy', False),
                'mobile': data.get('mobile', False),
                'timezone': data.get('timezone', '未知'),
                'lat': data.get('lat', 0),
                'lon': data.get('lon', 0),
                'success': data.get('status') == 'success'
            }
    except Exception as e:
        logger.error(f"查询IP信息失败: {e}")
    
    return {
        'ip': ip_address,
        'country': '未知',
        'region': '未知',
        'city': '未知',
        'isp': '未知',
        'success': False
    }

def save_user_ip(user_id: int, ip_info: Dict):
    """保存用户IP信息到数据库"""
    try:
        # 添加到SQLite数据库
        import sqlite3
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        
        # 更新用户的IP信息
        cursor.execute("""
            UPDATE users 
            SET ip_info = ?
            WHERE user_id = ?
        """, (json.dumps(ip_info), user_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ 已保存用户{user_id}的IP信息: {ip_info.get('ip')}")
    except Exception as e:
        logger.error(f"保存IP信息失败: {e}")

def handle_update(update_data: dict, user_ip: str):
    """处理Telegram更新"""
    try:
        # 提取用户信息
        message = update_data.get('message', {})
        user = message.get('from', {})
        user_id = user.get('id')
        
        if not user_id:
            return
        
        logger.info(f"📥 收到用户{user_id}的消息，IP: {user_ip}")
        
        # 查询IP详细信息
        ip_info = get_ip_details(user_ip)
        
        # 保存IP信息
        save_user_ip(user_id, ip_info)
        
        # 这里可以继续处理消息
        # ...
        
        return ip_info
    except Exception as e:
        logger.error(f"处理更新失败: {e}")
        return None

