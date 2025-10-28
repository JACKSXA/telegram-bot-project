"""测试营销旅程"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_manager import DatabaseManager


@pytest.fixture(scope='function')
def db():
    db = DatabaseManager(':memory:')
    yield db


class TestJourney:
    """测试营销旅程"""
    
    def test_create_journey_node(self, db):
        """测试创建旅程节点"""
        config = {'action': 'send_welcome', 'template_id': 1}
        result = db.create_journey_node('state_idle', 'welcome', config)
        assert result is True
    
    def test_get_journey_nodes(self, db):
        """测试获取旅程节点"""
        config1 = {'action': 'send_welcome'}
        config2 = {'action': 'send_reminder'}
        
        db.create_journey_node('state_idle', 'welcome', config1)
        db.create_journey_node('state_idle', 'reminder', config2)
        
        nodes = db.get_journey_nodes('state_idle')
        assert len(nodes) == 2
    
    def test_check_journey_trigger(self, db):
        """测试检查旅程触发"""
        config = {'action': 'send_message', 'template': 'welcome_msg'}
        db.create_journey_node('state_wallet_verified', 'message', config)
        
        trigger_config = db.check_journey_trigger(123, 'wallet_verified')
        assert trigger_config is not None
        assert trigger_config['action'] == 'send_message'
