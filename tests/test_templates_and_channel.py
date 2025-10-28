"""
测试模板中心和渠道漏斗API
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_manager import DatabaseManager


@pytest.fixture(scope='function')
def db():
    """数据库fixture"""
    db = DatabaseManager(':memory:')
    yield db


class TestTemplates:
    """测试模板中心"""
    
    def test_save_template(self, db):
        """测试保存模板"""
        result = db.save_template('欢迎消息', 'text', '欢迎使用我们的服务！', 1)
        assert result is True
        
        templates = db.get_templates()
        assert len(templates) == 1
        assert templates[0]['name'] == '欢迎消息'
        assert templates[0]['type'] == 'text'
        assert templates[0]['content'] == '欢迎使用我们的服务！'
    
    def test_get_templates_active_only(self, db):
        """测试只获取活跃模板"""
        db.save_template('活跃模板', 'text', '内容', 1)
        db.save_template('非活跃模板', 'text', '内容', 0)
        
        templates = db.get_templates(active_only=True)
        assert len(templates) == 1
        assert templates[0]['name'] == '活跃模板'
        
        all_templates = db.get_templates(active_only=False)
        assert len(all_templates) == 2


class TestChannelFunnel:
    """测试渠道漏斗"""
    
    def test_funnel_by_channel(self, db):
        """测试按渠道统计漏斗"""
        # 创建测试用户
        users_data = [
            {'user_id': 1, 'username': 'user1', 'wallet': 'wallet1', 'state': 'wallet_verified', 'channel': 'weibo'},
            {'user_id': 2, 'username': 'user2', 'wallet': 'wallet2', 'state': 'waiting_customer_service', 'channel': 'weibo'},
            {'user_id': 3, 'username': 'user3', 'wallet': None, 'state': 'idle', 'channel': 'facebook'},
        ]
        
        for user in users_data:
            db.save_user(user['user_id'], user)
        
        # 统计
        channel_data = db.get_funnel_by_channel()
        
        # 验证统计结果
        assert len(channel_data) >= 2
        
        weibo_data = next((c for c in channel_data if c['channel'] == 'weibo'), None)
        assert weibo_data is not None
        assert weibo_data['total'] == 2
        assert weibo_data['wallet_bound'] == 2
        
        facebook_data = next((c for c in channel_data if c['channel'] == 'facebook'), None)
        assert facebook_data is not None
        assert facebook_data['total'] == 1
    
    def test_channel_unknown(self, db):
        """测试未知渠道统计"""
        db.save_user(100, {'user_id': 100, 'username': 'test', 'channel': None})
        
        channel_data = db.get_funnel_by_channel()
        unknown_data = next((c for c in channel_data if c['channel'] == 'unknown'), None)
        assert unknown_data is not None
