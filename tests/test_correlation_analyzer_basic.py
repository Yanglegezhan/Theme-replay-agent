# -*- coding: utf-8 -*-
"""
CorrelationAnalyzer基础功能测试

验证CorrelationAnalyzer的核心功能是否正常工作
"""

import pytest
from datetime import datetime, timedelta
import numpy as np

from src.analysis import CorrelationAnalyzer
from src.models import IntradayData, ResonancePoint


def create_test_intraday_data(
    target: str,
    date: str,
    num_points: int = 240,
    pattern: str = "flat"
) -> IntradayData:
    """创建测试用的分时数据
    
    Args:
        target: 目标代码
        date: 日期
        num_points: 数据点数（默认240，对应4小时交易）
        pattern: 数据模式（flat/dip/v_reversal/breakthrough）
    """
    start_time = datetime.strptime(f"{date} 09:30:00", "%Y-%m-%d %H:%M:%S")
    timestamps = [start_time + timedelta(minutes=i) for i in range(num_points)]
    
    if pattern == "flat":
        # 平稳走势
        pct_changes = [0.1 * i / num_points for i in range(num_points)]
        prices = [100 + 100 * pct / 100 for pct in pct_changes]
    
    elif pattern == "dip":
        # 急跌模式：前半段下跌，后半段平稳
        pct_changes = []
        for i in range(num_points):
            if i < num_points // 2:
                pct_changes.append(-2.0 * i / (num_points // 2))
            else:
                pct_changes.append(-2.0)
        prices = [100 + 100 * pct / 100 for pct in pct_changes]
    
    elif pattern == "v_reversal":
        # V型反转：先跌后涨
        pct_changes = []
        for i in range(num_points):
            if i < num_points // 2:
                pct_changes.append(-2.0 * i / (num_points // 2))
            else:
                pct_changes.append(-2.0 + 3.0 * (i - num_points // 2) / (num_points // 2))
        prices = [100 + 100 * pct / 100 for pct in pct_changes]
    
    elif pattern == "breakthrough":
        # 突破模式：逐步上涨并突破
        pct_changes = []
        for i in range(num_points):
            if i < num_points * 0.7:
                pct_changes.append(0.5 * i / (num_points * 0.7))
            else:
                pct_changes.append(0.5 + 1.5 * (i - num_points * 0.7) / (num_points * 0.3))
        prices = [100 + 100 * pct / 100 for pct in pct_changes]
    
    else:
        raise ValueError(f"Unknown pattern: {pattern}")
    
    return IntradayData(
        target=target,
        date=date,
        timestamps=timestamps,
        prices=prices,
        pct_changes=pct_changes
    )


class TestCorrelationAnalyzer:
    """CorrelationAnalyzer测试类"""
    
    def test_initialization(self):
        """测试初始化"""
        analyzer = CorrelationAnalyzer()
        assert analyzer.leading_time_lag_min == 5
        assert analyzer.leading_time_lag_max == 10
        assert analyzer.resonance_elasticity_threshold == 3.0
        assert analyzer.divergence_threshold == 0.5
    
    def test_find_resonance_points_dip(self):
        """测试识别急跌低点"""
        analyzer = CorrelationAnalyzer()
        market_data = create_test_intraday_data("SH000001", "2026-01-20", pattern="dip")
        
        resonance_points = analyzer._find_resonance_points(market_data)
        
        # 应该识别到至少一个DIP类型的共振点
        dip_points = [p for p in resonance_points if p.point_type == "DIP"]
        assert len(dip_points) > 0, "应该识别到急跌低点"
        
        # 验证共振点的属性
        for point in dip_points:
            assert isinstance(point, ResonancePoint)
            assert point.point_type == "DIP"
            assert point.price_change < 0, "急跌低点的价格变化应该为负"
    
    def test_find_resonance_points_v_reversal(self):
        """测试识别V型反转"""
        analyzer = CorrelationAnalyzer()
        market_data = create_test_intraday_data("SH000001", "2026-01-20", pattern="v_reversal")
        
        resonance_points = analyzer._find_resonance_points(market_data)
        
        # 应该识别到V型反转
        v_reversal_points = [p for p in resonance_points if p.point_type == "V_REVERSAL"]
        assert len(v_reversal_points) > 0, "应该识别到V型反转"
    
    def test_find_resonance_points_breakthrough(self):
        """测试识别突破点"""
        analyzer = CorrelationAnalyzer()
        market_data = create_test_intraday_data("SH000001", "2026-01-20", pattern="breakthrough")
        
        resonance_points = analyzer._find_resonance_points(market_data)
        
        # 应该识别到突破点
        breakthrough_points = [p for p in resonance_points if p.point_type == "BREAKTHROUGH"]
        assert len(breakthrough_points) > 0, "应该识别到突破点"
        
        # 验证突破点的价格变化为正
        for point in breakthrough_points:
            assert point.price_change > 0, "突破点的价格变化应该为正"
    
    def test_calculate_elasticity(self):
        """测试弹性系数计算"""
        analyzer = CorrelationAnalyzer()
        
        # 测试正常情况
        elasticity = analyzer._calculate_elasticity(1.0, 3.0)
        assert elasticity == 3.0
        
        # 测试大盘涨幅为0的情况
        elasticity = analyzer._calculate_elasticity(0.0, 3.0)
        assert elasticity == 0.0
        
        # 测试负弹性
        elasticity = analyzer._calculate_elasticity(1.0, -1.0)
        assert elasticity == -1.0
    
    def test_calculate_time_lag(self):
        """测试时差计算"""
        analyzer = CorrelationAnalyzer()
        
        # 创建大盘数据（急跌）
        market_data = create_test_intraday_data("SH000001", "2026-01-20", pattern="dip")
        
        # 创建板块数据（也是急跌，但时间稍早）
        sector_data = create_test_intraday_data("BK0001", "2026-01-20", pattern="dip")
        
        # 创建一个共振点
        resonance_point = ResonancePoint(
            timestamp=market_data.timestamps[120],  # 中间时间点
            point_type="DIP",
            price_change=-2.0,
            index=120
        )
        
        # 计算时差
        time_lag = analyzer._calculate_time_lag(resonance_point, sector_data)
        
        # 应该返回一个时差值
        assert time_lag is not None or time_lag == 0, "应该计算出时差"
    
    def test_analyze_correlation_basic(self):
        """测试完整的联动分析流程"""
        analyzer = CorrelationAnalyzer()
        
        # 创建大盘数据
        market_data = create_test_intraday_data("SH000001", "2026-01-20", pattern="v_reversal")
        
        # 创建板块数据列表
        sector_data_list = [
            ("低空经济", create_test_intraday_data("BK0001", "2026-01-20", pattern="v_reversal")),
            ("固态电池", create_test_intraday_data("BK0002", "2026-01-20", pattern="breakthrough")),
        ]
        
        # 执行分析
        result = analyzer.analyze_correlation(market_data, sector_data_list)
        
        # 验证结果结构
        assert result is not None
        assert isinstance(result.resonance_points, list)
        assert isinstance(result.leading_sectors, list)
        assert isinstance(result.resonance_sectors, list)
        assert isinstance(result.divergence_sectors, list)
        assert isinstance(result.seesaw_effects, list)
        
        # 应该识别到共振点
        assert len(result.resonance_points) > 0, "应该识别到共振点"
    
    def test_analyze_correlation_empty_sectors(self):
        """测试空板块列表的情况"""
        analyzer = CorrelationAnalyzer()
        
        market_data = create_test_intraday_data("SH000001", "2026-01-20", pattern="flat")
        sector_data_list = []
        
        result = analyzer.analyze_correlation(market_data, sector_data_list)
        
        # 应该正常返回结果，但板块相关的列表为空
        assert result is not None
        assert len(result.leading_sectors) == 0
        assert len(result.resonance_sectors) == 0
        assert len(result.divergence_sectors) == 0
        assert len(result.seesaw_effects) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
