"""测试A/B测试引擎"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_manager import DatabaseManager


@pytest.fixture(scope='function')
def db():
    db = DatabaseManager(':memory:')
    yield db


class TestABExperiment:
    """测试A/B测试引擎"""
    
    def test_create_experiment(self, db):
        """测试创建实验"""
        result = db.create_experiment('welcome_msg', 'variant_a', 50)
        assert result is True
    
    def test_get_variant(self, db):
        """测试获取实验变体"""
        # 创建两个变体
        db.create_experiment('welcome_msg', 'control', 50)
        db.create_experiment('welcome_msg', 'treatment', 50)
        
        variant = db.get_experiment_variant('welcome_msg')
        assert variant in ['control', 'treatment']
    
    def test_variant_weight_distribution(self, db):
        """测试权重分配"""
        db.create_experiment('test', 'A', 10)  # 10%权重
        db.create_experiment('test', 'B', 90)  # 90%权重
        
        # 多次获取看分布
        variants = [db.get_experiment_variant('test') for _ in range(100)]
        # B应该占主导
        b_count = variants.count('B')
        assert b_count > 50  # 应该有超过50%是B
    
    def test_record_event(self, db):
        """测试记录用户事件"""
        result = db.record_user_event(123, 'wallet_bound', {'wallet': 'test123'})
        assert result is True
