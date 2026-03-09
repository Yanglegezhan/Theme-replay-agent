# -*- coding: utf-8 -*-
"""
CapacityProfiler使用示例

演示如何使用CapacityProfiler分析板块容量和结构健康度
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analysis import CapacityProfiler
from src.models import TurnoverData


def example_large_cap_sector():
    """示例1：大容量主线板块分析"""
    print("=" * 60)
    print("示例1：大容量主线板块分析")
    print("=" * 60)
    
    # 初始化分析器
    profiler = CapacityProfiler()
    
    # 准备成交额数据（大容量板块）
    turnover_data = TurnoverData(
        sector_turnover=180.0,  # 板块总成交额180亿
        top5_stocks=[
            {"stock_code": "000001", "stock_name": "平安银行", "turnover": 45.0},
            {"stock_code": "600036", "stock_name": "招商银行", "turnover": 38.0},
            {"stock_code": "601318", "stock_name": "中国平安", "turnover": 32.0},
            {"stock_code": "600016", "stock_name": "民生银行", "turnover": 28.0},
            {"stock_code": "601166", "stock_name": "兴业银行", "turnover": 25.0},
        ],
        stock_market_caps={
            "000001": 280.0,  # 280亿流通市值
            "600036": 520.0,
            "601318": 1200.0,
            "600016": 180.0,
            "601166": 220.0,
        }
    )
    
    # 准备连板数据（完整梯队）
    consecutive_boards = {
        5: ["000001"],  # 5连板龙头
        4: ["600036"],  # 4连板
        3: ["601318", "600016"],  # 3连板
        2: ["601166", "600000"],  # 2连板
        1: ["601988", "601398", "601939", "601288"],  # 首板
    }
    
    # 执行分析
    profile = profiler.profile_capacity(
        sector_name="银行板块",
        turnover_data=turnover_data,
        consecutive_boards=consecutive_boards
    )
    
    # 输出结果
    print(f"\n板块名称: 银行板块")
    print(f"容量类型: {profile.capacity_type}")
    print(f"板块总成交额: {profile.sector_turnover:.2f}亿元")
    print(f"核心中军成交额: {profile.leading_stock_turnover:.2f}亿元")
    print(f"\n金字塔结构:")
    print(f"  5板及以上: {profile.pyramid_structure.board_5_plus}只")
    print(f"  3-4板: {profile.pyramid_structure.board_3_to_4}只")
    print(f"  1-2板: {profile.pyramid_structure.board_1_to_2}只")
    print(f"  总个股数: {profile.pyramid_structure.total_stocks}只")
    print(f"  断层: {profile.pyramid_structure.gaps if profile.pyramid_structure.gaps else '无'}")
    print(f"\n结构健康度: {profile.structure_health:.2f}")
    print(f"持续性评分: {profile.sustainability_score:.2f}/100")
    print()


def example_small_cap_sector():
    """示例2：小众投机题材分析"""
    print("=" * 60)
    print("示例2：小众投机题材分析")
    print("=" * 60)
    
    # 初始化分析器
    profiler = CapacityProfiler()
    
    # 准备成交额数据（小容量板块）
    turnover_data = TurnoverData(
        sector_turnover=45.0,  # 板块总成交额45亿
        top5_stocks=[
            {"stock_code": "300001", "stock_name": "小盘龙头", "turnover": 18.0},
            {"stock_code": "300002", "stock_name": "跟风股1", "turnover": 12.0},
            {"stock_code": "300003", "stock_name": "跟风股2", "turnover": 8.0},
        ],
        stock_market_caps={
            "300001": 35.0,  # 35亿流通市值（小市值）
            "300002": 28.0,
            "300003": 22.0,
        }
    )
    
    # 准备连板数据（有断层）
    consecutive_boards = {
        5: ["300001"],  # 5连板龙头
        3: ["300002"],  # 3连板（缺少4板）
        1: ["300003", "300004", "300005"],  # 首板（缺少2板）
    }
    
    # 执行分析
    profile = profiler.profile_capacity(
        sector_name="低空经济",
        turnover_data=turnover_data,
        consecutive_boards=consecutive_boards
    )
    
    # 输出结果
    print(f"\n板块名称: 低空经济")
    print(f"容量类型: {profile.capacity_type}")
    print(f"板块总成交额: {profile.sector_turnover:.2f}亿元")
    print(f"核心中军成交额: {profile.leading_stock_turnover:.2f}亿元")
    print(f"\n金字塔结构:")
    print(f"  5板及以上: {profile.pyramid_structure.board_5_plus}只")
    print(f"  3-4板: {profile.pyramid_structure.board_3_to_4}只")
    print(f"  1-2板: {profile.pyramid_structure.board_1_to_2}只")
    print(f"  总个股数: {profile.pyramid_structure.total_stocks}只")
    print(f"  断层: {profile.pyramid_structure.gaps if profile.pyramid_structure.gaps else '无'}")
    print(f"\n结构健康度: {profile.structure_health:.2f}")
    print(f"持续性评分: {profile.sustainability_score:.2f}/100")
    print()


def example_unhealthy_sector():
    """示例3：结构不健康的板块分析"""
    print("=" * 60)
    print("示例3：结构不健康的板块分析")
    print("=" * 60)
    
    # 初始化分析器
    profiler = CapacityProfiler()
    
    # 准备成交额数据
    turnover_data = TurnoverData(
        sector_turnover=60.0,
        top5_stocks=[
            {"stock_code": "600001", "stock_name": "龙头股", "turnover": 25.0},
        ],
        stock_market_caps={
            "600001": 80.0,
        }
    )
    
    # 准备连板数据（严重断层）
    consecutive_boards = {
        7: ["600001"],  # 7连板龙头（孤立）
        2: ["600002"],  # 2连板（缺少3-6板）
        1: ["600003"],  # 首板（严重断层）
    }
    
    # 执行分析
    profile = profiler.profile_capacity(
        sector_name="问题板块",
        turnover_data=turnover_data,
        consecutive_boards=consecutive_boards
    )
    
    # 输出结果
    print(f"\n板块名称: 问题板块")
    print(f"容量类型: {profile.capacity_type}")
    print(f"板块总成交额: {profile.sector_turnover:.2f}亿元")
    print(f"核心中军成交额: {profile.leading_stock_turnover:.2f}亿元")
    print(f"\n金字塔结构:")
    print(f"  5板及以上: {profile.pyramid_structure.board_5_plus}只")
    print(f"  3-4板: {profile.pyramid_structure.board_3_to_4}只")
    print(f"  1-2板: {profile.pyramid_structure.board_1_to_2}只")
    print(f"  总个股数: {profile.pyramid_structure.total_stocks}只")
    print(f"  断层: {profile.pyramid_structure.gaps}")
    print(f"\n结构健康度: {profile.structure_health:.2f} ⚠️ 不健康")
    print(f"持续性评分: {profile.sustainability_score:.2f}/100")
    print(f"\n⚠️ 警告：该板块存在严重断层，梯队不完整，持续性较差！")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CapacityProfiler 使用示例")
    print("=" * 60 + "\n")
    
    # 运行示例
    example_large_cap_sector()
    example_small_cap_sector()
    example_unhealthy_sector()
    
    print("=" * 60)
    print("示例运行完成！")
    print("=" * 60)
