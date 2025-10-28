import os
import sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'admin_web'))
from flask_app import app

def test_users_route_redirect_when_not_logged_in():
    client = app.test_client()
    resp = client.get('/users')
    # 未登录应重定向到登录
    assert resp.status_code in (301, 302)

