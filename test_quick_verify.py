# -*- coding: utf-8 -*-
"""
快速验证修复脚本 - 测试2026-03-06数据获取和报告生成
"""

import sys
sys.path.insert(0, r'D:\pythonProject2\量化交易1\Ashare复盘multi-agents\Theme_repay_agent')

from src.data.kaipanla_source import KaipanlaDataSource
from src.output.report_generator import ReportGenerator
import json
from datetime import datetime

print("="*70)
print("验证修复 - 2026-03-06 数据获取测试")
print("="*70)

source = KaipanlaDataSource()
generator = ReportGenerator()
date = "2026-03-06"

# 测试板块列表
test_sectors = [
    ("军工", "801807"),
    ("化工", "801235"),
]

for sector_name, sector_code in test_sectors:
    print(f"\n{'='*70}")
    print(f"测试板块: {sector_name} ({sector_code})")
    print(f"{'='*70}")

    try:
        # 获取板块详细数据
        detailed_data = source.get_sector_detailed_data(
            sector_code=sector_code,
            sector_name=sector_name,
            date=date
        )

        print(f"\n1. 基础数据:")
        print(f"   今日涨停数: {detailed_data.get('limit_up_count', 0)}")
        print(f"   连板梯队: {detailed_data.get('consecutive_boards', {})}")

        # 检查空间龙
        space_dragons = detailed_data.get('space_dragons', [])
        print(f"\n2. 空间龙 ({len(space_dragons)}只, 至少2板):")
        if space_dragons:
            for dragon in space_dragons[:4]:
                print(f"   - {dragon['name']} ({dragon['code']}): {dragon['consecutive_days']}")
        else:
            print("   无 (该板块没有2板以上的个股)")

        # 检查中军
        zhongjun_list = detailed_data.get('zhongjun_list', [])
        print(f"\n3. 中军 ({len(zhongjun_list)}只, 市值最大):")
        if zhongjun_list:
            for zj in zhongjun_list[:2]:
                print(f"   - {zj['name']} ({zj['code']}): 市值{zj['market_cap']:.2f}亿, 换手{zj.get('actual_turnover_rate', 0):.2f}%")
        else:
            print("   无")

        # 检查先锋龙
        pioneer_list = detailed_data.get('pioneer_list', [])
        print(f"\n4. 先锋龙 ({len(pioneer_list)}只, 最早封板):")
        if pioneer_list:
            for pioneer in pioneer_list[:2]:
                print(f"   - {pioneer['name']} ({pioneer['code']}): 首次封板{pioneer['first_seal_time']}, {pioneer['consecutive_days']}")
        else:
            print("   无")

        # 检查主龙头股
        leading = detailed_data.get('leading_stock')
        print(f"\n5. 主龙头股:")
        if leading:
            print(f"   - 名称: {leading['name']} ({leading['code']})")
            print(f"   - 连板: {leading['consecutive_days']}")
            print(f"   - 收盘封单: {leading.get('seal_amount', 0):.2f}亿")
            print(f"   - 大单净流入: {leading.get('big_order_net', 0):+.2f}亿")
            print(f"   - 流通市值: {leading.get('market_cap', 0):.2f}亿")
            print(f"   - 实际换手: {leading.get('actual_turnover_rate', 0):.2f}%")
            print(f"   - 首次涨停: {leading.get('first_seal_time', '-')}")
            print(f"   - 最终涨停: {leading.get('last_seal_time', '-')}")
            print(f"   - 开板次数: {leading.get('open_count', 0)}")
        else:
            print("   无")

        # 检查涨停股票列表
        limit_up_stocks = detailed_data.get('limit_up_stocks', [])
        print(f"\n6. 涨停股票列表 ({len(limit_up_stocks)}只):")

        # 使用报告生成器的格式化功能
        core_stocks = generator._format_core_stocks(detailed_data)
        formatted_stocks = core_stocks.get('all_limit_up_stocks', [])

        print(f"   格式化后: {len(formatted_stocks)}只")
        print(f"\n   前5只排序结果:")
        for i, stock in enumerate(formatted_stocks[:5], 1):
            print(f"   {i}. {stock['name']} | {stock['consecutive_days']} | "
                  f"成交{stock['turnover']:.2f}亿 | 市值{stock['market_cap']:.2f}亿 | "
                  f"封单{stock['seal_amount']:.2f}亿 | 首次{stock.get('first_seal_time', '-')}")

        print(f"\n[OK] {sector_name} 测试通过")

    except Exception as e:
        print(f"\n[FAIL] {sector_name} 测试失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*70)
print("验证完成")
print("="*70)
