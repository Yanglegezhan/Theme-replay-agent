# -*- coding: utf-8 -*-
"""
验证复盘报告数据的脚本
使用akshare获取实际数据进行对比
"""

import sys
sys.path.insert(0, r'D:\pythonProject2\量化交易1\Ashare复盘multi-agents\Theme_repay_agent')

import akshare as ak
from datetime import datetime, timedelta

print("="*70)
print("验证复盘报告数据 - 2026-03-06")
print("="*70)

# 注意：2026-03-06是未来的日期，akshare可能无法获取数据
# 所以我们检查最近一个交易日的数据

try:
    # 获取最近一个交易日
    print("\n1. 获取A股最近交易日...")
    trade_dates = ak.tool_trade_date_hist_sina()
    today = datetime.now().strftime('%Y-%m-%d')

    # 找到最近的交易日
    trade_dates['trade_date'] = pd.to_datetime(trade_dates['trade_date'])
    latest_trade_date = trade_dates[trade_dates['trade_date'] <= today]['trade_date'].max()
    print(f"   最近交易日: {latest_trade_date.strftime('%Y-%m-%d')}")

except Exception as e:
    print(f"   获取交易日失败: {e}")

# 尝试获取个股数据验证
print("\n2. 验证个股数据...")

# 验证美利云(000815)
try:
    print("\n   美利云 (000815):")
    stock_data = ak.stock_zh_a_hist(symbol="000815", period="daily",
                                    start_date="20250301", end_date="20250307",
                                    adjust="qfq")
    if not stock_data.empty:
        print(f"   最近5日数据:")
        print(stock_data[['日期', '开盘', '收盘', '涨跌幅', '成交量']].tail())
    else:
        print("   无数据（可能是未来日期）")
except Exception as e:
    print(f"   获取失败: {e}")

# 验证卫星化学(002648)
try:
    print("\n   卫星化学 (002648):")
    stock_data = ak.stock_zh_a_hist(symbol="002648", period="daily",
                                    start_date="20250301", end_date="20250307",
                                    adjust="qfq")
    if not stock_data.empty:
        print(f"   最近5日数据:")
        print(stock_data[['日期', '开盘', '收盘', '涨跌幅', '成交量']].tail())
    else:
        print("   无数据（可能是未来日期）")
except Exception as e:
    print(f"   获取失败: {e}")

# 获取板块数据
print("\n3. 获取板块概念数据...")

try:
    # 获取概念板块列表
    concept_list = ak.stock_board_concept_name_em()
    print(f"\n   概念板块总数: {len(concept_list)}")

    # 查找算力相关板块
    compute_power = concept_list[concept_list['板块名称'].str.contains('算力|计算', na=False)]
    print(f"\n   算力相关板块:")
    print(compute_power[['板块名称', '板块代码']].head())

    # 查找化工板块
    chemical = concept_list[concept_list['板块名称'].str.contains('化工|化学', na=False)]
    print(f"\n   化工相关板块:")
    print(chemical[['板块名称', '板块代码']].head())

except Exception as e:
    print(f"   获取板块数据失败: {e}")

print("\n" + "="*70)
print("验证完成")
print("注意: 由于2026-03-06是未来日期，无法获取实际交易数据进行对比")
print("="*70)
