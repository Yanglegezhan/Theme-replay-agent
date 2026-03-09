# -*- coding: utf-8 -*-
"""
数据层基础测试

验证数据层组件的基本功能
"""

import os
import sys
import tempfile
import pytest
from datetime import datetime

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data import (
    KaipanlaDataSource,
    AkshareDataSource,
    DataSourceFallback,
    HistoryTracker
)
from src.models import SectorStrength


class TestHistoryTracker:
    """测试HistoryTracker"""
    
    def test_init_creates_storage_file(self):
        """测试初始化创建存储文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'test_history.csv')
            tracker = HistoryTracker(storage_path)
            
            assert os.path.exists(storage_path)
    
    def test_save_and_get_history(self):
        """测试保存和查询历史数据"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'test_history.csv')
            tracker = HistoryTracker(storage_path)
            
            # 保存数据
            rankings = [
                SectorStrength(
                    sector_name='低空经济',
                    sector_code='BK0001',
                    strength_score=12500,
                    ndays_limit_up=8,
                    rank=1
                ),
                SectorStrength(
                    sector_name='固态电池',
                    sector_code='BK0002',
                    strength_score=10800,
                    ndays_limit_up=6,
                    rank=2
                )
            ]
            
            tracker.save_daily_ranking('2026-01-20', rankings)
            
            # 查询历史
            history = tracker.get_history('低空经济', days=7)
            
            assert len(history) > 0
            assert history[0].date == '2026-01-20'
            assert history[0].rank == 1
            assert history[0].strength_score == 12500
    
    def test_is_new_face_with_empty_history(self):
        """测试空历史时判断新面孔"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'test_history.csv')
            tracker = HistoryTracker(storage_path)
            
            # 空历史应该返回True（新面孔）
            is_new = tracker.is_new_face('低空经济', '2026-01-20')
            
            assert is_new is True
    
    def test_get_consecutive_days_with_empty_history(self):
        """测试空历史时统计连续天数"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'test_history.csv')
            tracker = HistoryTracker(storage_path)
            
            # 空历史应该返回1天
            days = tracker.get_consecutive_days('低空经济', '2026-01-20')
            
            assert days == 1


class TestDataSourceFallback:
    """测试DataSourceFallback"""
    
    def test_init(self):
        """测试初始化"""
        fallback = DataSourceFallback()
        
        assert fallback.primary_source is not None
        assert fallback.fallback_source is not None
        assert isinstance(fallback.usage_log, list)
    
    def test_get_usage_statistics_empty(self):
        """测试空使用统计"""
        fallback = DataSourceFallback()
        
        stats = fallback.get_usage_statistics()
        
        assert stats['total_requests'] == 0
        assert stats['primary_success'] == 0
        assert stats['primary_failure'] == 0


def test_imports():
    """测试所有导入是否正常"""
    from src.data import (
        KaipanlaDataSource,
        AkshareDataSource,
        DataSourceFallback,
        HistoryTracker
    )
    from src.models import (
        IntradayData,
        LimitUpData,
        TurnoverData,
        SectorStrength,
        HistoryRecord
    )
    
    # 如果能导入就说明模块结构正确
    assert True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
