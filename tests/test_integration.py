"""
集成测试：测试Bot和Web后台的协同工作
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_manager import get_database


class TestIntegration:
    """集成测试类"""
    
    @pytest.fixture(scope='function')
    def db(self):
        """数据库fixture"""
        from database_manager import DatabaseManager
        db = DatabaseManager(':memory:')
        yield db
    
    def test_user_lifecycle(self, db):
        """测试完整的用户生命周期"""
        # 1. 注册用户
        user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'language': 'zh',
            'state': 'idle'
        }
        db.save_user(123, user_data)
        
        # 2. 绑定钱包
        user_data['wallet'] = 'test_wallet_address'
        user_data['state'] = 'wallet_verified'
        db.save_user(123, user_data)
        
        # 3. 保存对话
        db.save_conversation(123, 'user', 'Hello')
        db.save_conversation(123, 'assistant', 'Hi there')
        
        # 4. 验证数据
        user = db.get_user(123)
        assert user['wallet'] == 'test_wallet_address'
        assert user['state'] == 'wallet_verified'
        
        conversations = db.get_conversations(123)
        assert len(conversations) == 2
    
    def test_analytics_calculation(self, db):
        """测试分析统计计算"""
        # 创建测试用户
        for i in range(5):
            user_data = {
                'username': f'user{i}',
                'language': 'zh',
                'state': 'idle'
            }
            db.save_user(i, user_data)
        
        # 统计
        snapshot = db.get_analytics_snapshot()
        assert snapshot['total_users'] == 5
        assert snapshot['conversion_rates']['to_wallet'] == 0
    
    def test_conversation_history(self, db):
        """测试对话历史排序"""
        # 保存对话
        db.save_conversation(100, 'user', 'First')
        db.save_conversation(100, 'assistant', 'Second')
        db.save_conversation(100, 'user', 'Third')
        
        # 获取对话历史
        history = db.get_conversations(100)
        
        # 验证顺序
        assert len(history) == 3
        assert history[0]['role'] == 'user'
        assert history[1]['role'] == 'assistant'
