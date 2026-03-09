# -*- coding: utf-8 -*-
"""
CapacityProfiler基础功能测试
"""

import pytest
from src.analysis import CapacityProfiler
from src.models import TurnoverData, PyramidStructure, CapacityProfile


class TestCapacityProfiler:
    """CapacityProfiler基础功能测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.profiler = CapacityProfiler(
            large_cap_turnover_threshold=30.0,
            health_score_gap_penalty=0.2
        )
    
    def test_classify_capacity_large_cap(self):
        """测试大容量分类"""
        turnover_data = TurnoverData(
            sector_turnover=150.0,
            top5_stocks=[
                {"stock_code": "000001", "stock_name": "平安银行", "turnover": 35.0},
                {"stock_code": "000002", "stock_name": "万科A", "turnover": 25.0},
            ],
            stock_market_caps={
                "000001": 120.0,  # 120亿流通市值
                "000002": 150.0,
            }
        )
        
        capacity_type = self.profiler._classify_capacity(turnover_data)
        assert capacity_type == "LARGE_CAP"
    
    def test_classify_capacity_small_cap(self):
        """测试小容量分类"""
        turnover_data = TurnoverData(
            sector_turnover=50.0,
            top5_stocks=[
                {"stock_code": "300001", "stock_name": "小盘股", "turnover": 15.0},
            ],
            stock_market_caps={
                "300001": 30.0,  # 30亿流通市值（小于100亿）
            }
        )
        
        capacity_type = self.profiler._classify_capacity(turnover_data)
        assert capacity_type == "SMALL_CAP"
    
    def test_build_pyramid_complete(self):
        """测试构建完整金字塔（无断层）"""
        consecutive_boards = {
            5: ["stock1", "stock2"],
            4: ["stock3"],
            3: ["stock4", "stock5"],
            2: ["stock6"],
            1: ["stock7", "stock8", "stock9"],
        }
        
        pyramid = self.profiler._build_pyramid(consecutive_boards)
        
        assert pyramid.board_5_plus == 2  # 5板：2只
        assert pyramid.board_3_to_4 == 3  # 3-4板：3只
        assert pyramid.board_1_to_2 == 4  # 1-2板：4只
        assert pyramid.total_stocks == 9
        assert pyramid.gaps == []  # 无断层
    
    def test_build_pyramid_with_gaps(self):
        """测试构建有断层的金字塔"""
        consecutive_boards = {
            5: ["stock1"],
            3: ["stock2", "stock3"],
            1: ["stock4", "stock5"],
            # 缺少4板和2板
        }
        
        pyramid = self.profiler._build_pyramid(consecutive_boards)
        
        assert pyramid.board_5_plus == 1
        assert pyramid.board_3_to_4 == 2
        assert pyramid.board_1_to_2 == 2
        assert pyramid.total_stocks == 5
        assert pyramid.gaps == [4, 2]  # 断层：4板和2板
    
    def test_build_pyramid_empty(self):
        """测试空连板数据"""
        consecutive_boards = {}
        
        pyramid = self.profiler._build_pyramid(consecutive_boards)
        
        assert pyramid.board_5_plus == 0
        assert pyramid.board_3_to_4 == 0
        assert pyramid.board_1_to_2 == 0
        assert pyramid.total_stocks == 0
        assert pyramid.gaps == []
    
    def test_calculate_health_score_perfect(self):
        """测试完美健康度（无断层，梯队完整）"""
        pyramid = PyramidStructure(
            board_5_plus=2,
            board_3_to_4=3,
            board_1_to_2=5,
            gaps=[],
            total_stocks=10
        )
        
        health_score = self.profiler._calculate_health_score(pyramid)
        
        assert health_score == 1.0  # 满分
    
    def test_calculate_health_score_with_gaps(self):
        """测试有断层的健康度"""
        pyramid = PyramidStructure(
            board_5_plus=1,
            board_3_to_4=2,
            board_1_to_2=3,
            gaps=[4, 2],  # 2个断层
            total_stocks=6
        )
        
        health_score = self.profiler._calculate_health_score(pyramid)
        
        # 基础分1.0 - 2个断层 * 0.2 = 0.6
        assert health_score == 0.6
    
    def test_calculate_health_score_missing_layers(self):
        """测试缺少某些层级的健康度"""
        pyramid = PyramidStructure(
            board_5_plus=0,  # 缺少高度板
            board_3_to_4=2,
            board_1_to_2=3,
            gaps=[],
            total_stocks=5
        )
        
        health_score = self.profiler._calculate_health_score(pyramid)
        
        # 基础分1.0 - 缺少高度板0.1 = 0.9
        assert health_score == 0.9
    
    def test_calculate_sustainability_score_large_cap(self):
        """测试大容量题材的持续性评分"""
        turnover_data = TurnoverData(
            sector_turnover=120.0,  # 120亿成交额
            top5_stocks=[],
            stock_market_caps={}
        )
        
        score = self.profiler._calculate_sustainability_score(
            capacity_type="LARGE_CAP",
            structure_health=1.0,  # 完美健康度
            turnover_data=turnover_data
        )
        
        # 大容量基础分60 + 健康度30 + 成交额10 = 100
        assert score == 100.0
    
    def test_calculate_sustainability_score_small_cap(self):
        """测试小容量题材的持续性评分"""
        turnover_data = TurnoverData(
            sector_turnover=30.0,  # 30亿成交额
            top5_stocks=[],
            stock_market_caps={}
        )
        
        score = self.profiler._calculate_sustainability_score(
            capacity_type="SMALL_CAP",
            structure_health=0.5,  # 中等健康度
            turnover_data=turnover_data
        )
        
        # 小容量基础分40 + 健康度15 + 成交额3 = 58
        assert 57.0 <= score <= 59.0  # 允许小误差
    
    def test_profile_capacity_complete(self):
        """测试完整的容量分析流程"""
        turnover_data = TurnoverData(
            sector_turnover=150.0,
            top5_stocks=[
                {"stock_code": "000001", "stock_name": "龙头股", "turnover": 40.0},
                {"stock_code": "000002", "stock_name": "二线股", "turnover": 30.0},
            ],
            stock_market_caps={
                "000001": 150.0,
                "000002": 120.0,
            }
        )
        
        consecutive_boards = {
            5: ["000001"],
            4: ["000002"],
            3: ["000003", "000004"],
            2: ["000005"],
            1: ["000006", "000007", "000008"],
        }
        
        profile = self.profiler.profile_capacity(
            sector_name="测试板块",
            turnover_data=turnover_data,
            consecutive_boards=consecutive_boards
        )
        
        # 验证结果
        assert isinstance(profile, CapacityProfile)
        assert profile.capacity_type == "LARGE_CAP"
        assert profile.sector_turnover == 150.0
        assert profile.leading_stock_turnover == 40.0
        assert profile.pyramid_structure.total_stocks == 8
        assert profile.pyramid_structure.gaps == []  # 无断层
        assert profile.structure_health == 1.0  # 完美健康度
        assert profile.sustainability_score == 100.0  # 满分
    
    def test_profile_capacity_with_issues(self):
        """测试有问题的板块容量分析"""
        turnover_data = TurnoverData(
            sector_turnover=40.0,
            top5_stocks=[
                {"stock_code": "300001", "stock_name": "小盘股", "turnover": 12.0},
            ],
            stock_market_caps={
                "300001": 25.0,  # 小市值
            }
        )
        
        consecutive_boards = {
            5: ["300001"],
            3: ["300002"],
            1: ["300003"],
            # 缺少4板和2板
        }
        
        profile = self.profiler.profile_capacity(
            sector_name="问题板块",
            turnover_data=turnover_data,
            consecutive_boards=consecutive_boards
        )
        
        # 验证结果
        assert profile.capacity_type == "SMALL_CAP"
        assert profile.pyramid_structure.gaps == [4, 2]  # 有断层
        assert profile.structure_health < 1.0  # 健康度不满分
        assert profile.sustainability_score < 100.0  # 持续性评分不满分


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
