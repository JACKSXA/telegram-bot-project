#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel Serverless函数入口
"""

from vercel import Request, Response

def handler(request: Request) -> Response:
    """主处理函数"""
    
    # 获取用户真实IP
    user_ip = request.headers.get('x-forwarded-for', '').split(',')[0].strip()
    if not user_ip:
        user_ip = request.remote_addr
    
    # 如果是Webhook请求
    if request.path == '/api/webhook':
        try:
            from api.webhook import handle_update
            
            update_data = request.json()
            result = handle_update(update_data, user_ip)
            
            return Response(
                {'status': 'ok', 'ip_info': result},
                status=200
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=500
            )
    
    return Response({'error': 'Not found'}, status=404)

