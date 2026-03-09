# -*- coding: utf-8 -*-
"""
数据层使用示例

演示如何使用数据层组件获取和管理市场数据
"""

import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data import (
    KaipanlaDataSource,
    DataSourceFallback,
    HistoryTracker
)
from src.models import SectorStrength


def example_kaipanla_source():
    """示例1: 使用KaipanlaDataSource"""
    print("=" * 60)
    print("示例1: 使用KaipanlaDataSource获取数据")
    print("=" * 60)
    
    # 初始化数据源
    source = KaipanlaDataSource()
    
    # 获取板块强度数据
    print("\n1. 获取7日板块强度数据...")
    try:
        strength_data = source.get_sector_strength_ndays(
            end_date='2026-01-20',
            num_days=7
        )
        print(f"   获取到 {len(strength_data)} 条板块数据")
        if not strength_data.empty:
            print(f"   前3个板块:")
            print(strength_data.head(3))
    except Exception as e:
        print(f"   获取失败: {e}")
    
    # 获取分时数据
    print("\n2. 获取上证指数分时数据...")
    try:
        intraday = source.get_intraday_data(
            target='SH000001',
            date='2026-01-20'
        )
        print(f"   获取到 {len(intraday.timestamps)} 个数据点")
        if intraday.timestamps:
            print(f"   开盘时间: {intraday.timestamps[0]}")
            print(f"   收盘时间: {intraday.timestamps[-1]}")
    except Exception as e:
        print(f"   获取失败: {e}")
    
    # 获取涨停数据
    print("\n3. 获取涨停数据...")
    try:
        limit_up = source.get_limit_up_data(date='2026-01-20')
        print(f"   涨停数: {limit_up.limit_up_count}")
        print(f"   跌停数: {limit_up.limit_down_count}")
        print(f"   炸板率: {limit_up.blown_limit_up_rate}%")
    except Exception as e:
        print(f"   获取失败: {e}")


def example_data_source_fallback():
    """示例2: 使用DataSourceFallback（推荐）"""
    print("\n" + "=" * 60)
    print("示例2: 使用DataSourceFallback（带自动降级）")
    print("=" * 60)
    
    # 初始化降级管理器
    fallback = DataSourceFallback()
    
    # 获取分时数据（自动降级）
    print("\n1. 获取分时数据（自动降级）...")
    try:
        intraday = fallback.get_intraday_data(
            target='SH000001',
            date='2026-01-20'
        )
        print(f"   获取到 {len(intraday.timestamps)} 个数据点")
    except Exception as e:
        print(f"   获取失败: {e}")
    
    # 查看使用统计
    print("\n2. 数据源使用统计:")
    stats = fallback.get_usage_statistics()
    print(f"   总请求数: {stats['total_requests']}")
    print(f"   主数据源成功: {stats['primary_success']}")
    print(f"   主数据源失败: {stats['primary_failure']}")
    print(f"   备用数据源成功: {stats['fallback_success']}")
    print(f"   备用数据源失败: {stats['fallback_failure']}")
    if stats['total_requests'] > 0:
        print(f"   主数据源成功率: {stats['primary_success_rate']:.2%}")


def example_history_tracker():
    """示例3: 使用HistoryTracker"""
    print("\n" + "=" * 60)
    print("示例3: 使用HistoryTracker管理历史数据")
    print("=" * 60)
    
    # 初始化追踪器
    storage_path = 'data/history/example_sector_rankings.csv'
    tracker = HistoryTracker(storage_path)
    
    # 保存当日排名
    print("\n1. 保存当日排名...")
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
        ),
        SectorStrength(
            sector_name='AI芯片',
            sector_code='BK0003',
            strength_score=9500,
            ndays_limit_up=5,
            rank=3
        )
    ]
    
    tracker.save_daily_ranking('2026-01-20', rankings)
    print(f"   已保存 {len(rankings)} 个板块的排名")
    
    # 查询历史
    print("\n2. 查询板块历史...")
    history = tracker.get_history('低空经济', days=7)
    print(f"   查询到 {len(history)} 条历史记录")
    for record in history:
        print(f"   {record.date}: 排名{record.rank}, 强度{record.strength_score}")
    
    # 判断新旧面孔
    print("\n3. 判断新旧面孔...")
    for sector in ['低空经济', '固态电池', 'AI芯片']:
        is_new = tracker.is_new_face(sector, '2026-01-20')
        status = "新面孔" if is_new else "老面孔"
        print(f"   {sector}: {status}")
    
    # 统计连续天数
    print("\n4. 统计连续天数...")
    for sector in ['低空经济', '固态电池', 'AI芯片']:
        days = tracker.get_consecutive_days(sector, '2026-01-20')
        print(f"   {sector}: 连续 {days} 天进入前7")
    
    # 获取所有板块
    print("\n5. 获取所有板块...")
    all_sectors = tracker.get_all_sectors()
    print(f"   共有 {len(all_sectors)} 个板块")
    print(f"   板块列表: {', '.join(all_sectors)}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("数据层使用示例")
    print("=" * 60)
    
    # 示例1: KaipanlaDataSource
    example_kaipanla_source()
    
    # 示例2: DataSourceFallback
    example_data_source_fallback()
    
    # 示例3: HistoryTracker
    example_history_tracker()
    
    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
