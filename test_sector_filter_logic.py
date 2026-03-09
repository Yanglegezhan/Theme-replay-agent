# -*- coding: utf-8 -*-
"""
测试板块筛选逻辑

验证新的筛选规则：
1. 如果中等以上强度板块不足7个，则取所有中等以上强度的板块
2. 如果没有中等以上强度的板块，则返回空列表
"""

import sys
import os
from pathlib import Path

# 设置Windows控制台UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import pandas as pd
from src.analysis.sector_filter import SectorFilter
from src.data import HistoryTracker


def test_case_1():
    """测试用例1: 中等以上强度板块不足7个"""
    print("\n" + "=" * 80)
    print("测试用例1: 中等以上强度板块不足7个（只有5个）")
    print("=" * 80)
    
    # 创建测试数据：5个中等以上强度的板块
    test_data = pd.DataFrame({
        '日期': ['2026-01-21'] * 5,
        '板块代码': ['BK001', 'BK002', 'BK003', 'BK004', 'BK005'],
        '板块名称': ['板块A', '板块B', '板块C', '板块D', '板块E'],
        '涨停数': [10000, 5000, 3000, 2500, 2000],  # 都 >= 2000
        '涨停股票': [['股票1'], ['股票2'], ['股票3'], ['股票4'], ['股票5']]
    })
    
    # 初始化筛选器
    history_tracker = HistoryTracker(storage_path='data/history/test_rankings.csv')
    sector_filter = SectorFilter(history_tracker)
    
    # 执行筛选
    result = sector_filter.filter_sectors(
        ndays_data=test_data,
        current_date='2026-01-21',
        high_threshold=8000,
        medium_threshold=2000,
        target_count=7
    )
    
    # 验证结果
    print(f"\n结果: 筛选出 {len(result.target_sectors)} 个板块")
    for sector in result.target_sectors:
        print(f"  - {sector.sector_name}: 强度={sector.strength_score}")
    
    # 断言
    assert len(result.target_sectors) == 5, f"期望5个板块，实际{len(result.target_sectors)}个"
    print("\n✓ 测试通过: 返回了所有5个中等以上强度的板块")


def test_case_2():
    """测试用例2: 没有中等以上强度的板块"""
    print("\n" + "=" * 80)
    print("测试用例2: 没有中等以上强度的板块（所有板块强度 < 2000）")
    print("=" * 80)
    
    # 创建测试数据：所有板块强度都低于中等阈值
    test_data = pd.DataFrame({
        '日期': ['2026-01-21'] * 3,
        '板块代码': ['BK001', 'BK002', 'BK003'],
        '板块名称': ['板块A', '板块B', '板块C'],
        '涨停数': [1500, 1000, 500],  # 都 < 2000
        '涨停股票': [['股票1'], ['股票2'], ['股票3']]
    })
    
    # 初始化筛选器
    history_tracker = HistoryTracker(storage_path='data/history/test_rankings.csv')
    sector_filter = SectorFilter(history_tracker)
    
    # 执行筛选
    result = sector_filter.filter_sectors(
        ndays_data=test_data,
        current_date='2026-01-21',
        high_threshold=8000,
        medium_threshold=2000,
        target_count=7
    )
    
    # 验证结果
    print(f"\n结果: 筛选出 {len(result.target_sectors)} 个板块")
    
    # 断言
    assert len(result.target_sectors) == 0, f"期望0个板块，实际{len(result.target_sectors)}个"
    print("\n✓ 测试通过: 返回了空列表")


def test_case_3():
    """测试用例3: 中等以上强度板块超过7个"""
    print("\n" + "=" * 80)
    print("测试用例3: 中等以上强度板块超过7个（有10个）")
    print("=" * 80)
    
    # 创建测试数据：10个中等以上强度的板块
    test_data = pd.DataFrame({
        '日期': ['2026-01-21'] * 10,
        '板块代码': [f'BK{i:03d}' for i in range(1, 11)],
        '板块名称': [f'板块{chr(65+i)}' for i in range(10)],
        '涨停数': [10000, 9000, 8500, 7000, 5000, 4000, 3000, 2500, 2200, 2000],
        '涨停股票': [[f'股票{i}'] for i in range(1, 11)]
    })
    
    # 初始化筛选器
    history_tracker = HistoryTracker(storage_path='data/history/test_rankings.csv')
    sector_filter = SectorFilter(history_tracker)
    
    # 执行筛选
    result = sector_filter.filter_sectors(
        ndays_data=test_data,
        current_date='2026-01-21',
        high_threshold=8000,
        medium_threshold=2000,
        target_count=7
    )
    
    # 验证结果
    print(f"\n结果: 筛选出 {len(result.target_sectors)} 个板块")
    for sector in result.target_sectors:
        print(f"  - {sector.sector_name}: 强度={sector.strength_score}")
    
    # 断言
    assert len(result.target_sectors) == 7, f"期望7个板块，实际{len(result.target_sectors)}个"
    
    # 验证选择的是强度最高的7个
    expected_scores = [10000, 9000, 8500, 7000, 5000, 4000, 3000]
    actual_scores = [s.strength_score for s in result.target_sectors]
    assert actual_scores == expected_scores, f"期望{expected_scores}，实际{actual_scores}"
    
    print("\n✓ 测试通过: 返回了强度最高的7个板块")


def test_case_4():
    """测试用例4: 边界情况 - 恰好7个中等以上强度的板块"""
    print("\n" + "=" * 80)
    print("测试用例4: 恰好7个中等以上强度的板块")
    print("=" * 80)
    
    # 创建测试数据：恰好7个中等以上强度的板块
    test_data = pd.DataFrame({
        '日期': ['2026-01-21'] * 7,
        '板块代码': [f'BK{i:03d}' for i in range(1, 8)],
        '板块名称': [f'板块{chr(65+i)}' for i in range(7)],
        '涨停数': [10000, 8500, 6000, 4000, 3000, 2500, 2000],
        '涨停股票': [[f'股票{i}'] for i in range(1, 8)]
    })
    
    # 初始化筛选器
    history_tracker = HistoryTracker(storage_path='data/history/test_rankings.csv')
    sector_filter = SectorFilter(history_tracker)
    
    # 执行筛选
    result = sector_filter.filter_sectors(
        ndays_data=test_data,
        current_date='2026-01-21',
        high_threshold=8000,
        medium_threshold=2000,
        target_count=7
    )
    
    # 验证结果
    print(f"\n结果: 筛选出 {len(result.target_sectors)} 个板块")
    for sector in result.target_sectors:
        print(f"  - {sector.sector_name}: 强度={sector.strength_score}")
    
    # 断言
    assert len(result.target_sectors) == 7, f"期望7个板块，实际{len(result.target_sectors)}个"
    print("\n✓ 测试通过: 返回了所有7个板块")


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("板块筛选逻辑测试")
    print("=" * 80)
    
    try:
        test_case_1()
        test_case_2()
        test_case_3()
        test_case_4()
        
        print("\n" + "=" * 80)
        print("所有测试通过！")
        print("=" * 80)
        print("\n新的筛选规则验证成功：")
        print("1. ✓ 中等以上强度板块不足7个时，返回所有中等以上强度的板块")
        print("2. ✓ 没有中等以上强度的板块时，返回空列表")
        print("3. ✓ 中等以上强度板块超过7个时，返回强度最高的7个")
        print("4. ✓ 恰好7个中等以上强度板块时，返回所有7个")
        
        return 0
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
