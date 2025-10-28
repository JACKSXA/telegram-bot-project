"""测试RFM模型"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_manager import DatabaseManager
from datetime import datetime, timedelta


@pytest.fixture(scope='function')
def db():
    db = DatabaseManager(':memory:')
    yield db


class TestRFM:
    """测试RFM模型"""
    
    def test_calculate_rfm_no_events(self, db):
        """测试无事件的用户RFM"""
        db.save_user(1, {'username': 'test', 'wallet': None})
        rfm = db.calculate_user_rfm(1)
        
        assert rfm['recency'] == '1'
        assert rfm['frequency'] == '1'
        assert rfm['monetary'] == '1'
        assert rfm['rfm_total'] == '111'
    
    def test_calculate_rfm_with_wallet(self, db):
        """测试有钱包的用户RFM"""
        db.save_user(2, {'username': 'rich', 'wallet': 'wallet123'})
        rfm = db.calculate_user_rfm(2)
        
        assert rfm['monetary'] == '5'
    
    def test_calculate_rfm_recent_activity(self, db):
        """测试最近活动的用户RFM"""
        db.save_user(3, {'username': 'active'})
        # 记录最近30天内的活动
        now = datetime.now()
        db.record_user_event(3, 'test_event', {'timestamp': now.isoformat()})
        
        rfm = db.calculate_user_rfm(3)
        assert int(rfm['recency']) >= 4  # 应该是4或5
        
        # 记录多次活动
        for i in range(60):
            db.record_user_event(3, f'event_{i}', {})
        
        rfm2 = db.calculate_user_rfm(3)
        assert int(rfm2['frequency']) >= 4  # 应该是4或5
