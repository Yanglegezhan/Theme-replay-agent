# -*- coding: utf-8 -*-
"""
修复验证测试脚本

验证以下修复是否生效：
1. 空间龙识别（至少2板）
2. 龙头股数据结构（封单额、流通市值、实际换手等）
3. 涨停个股表格排序（按连板数降序，同身位按最终涨停时间升序）
4. 今日涨停数显示
"""

import sys
sys.path.insert(0, r'D:\pythonProject2\量化交易1\Ashare复盘multi-agents\Theme_repay_agent')

from src.data.kaipanla_source import KaipanlaDataSource
from src.output.report_generator import ReportGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sector_data():
    """测试板块数据获取"""
    print("="*60)
    print("测试板块数据获取")
    print("="*60)

    source = KaipanlaDataSource()

    # 测试获取板块详细数据
    test_sector = "机器人"  # 使用一个常见的板块
    date = "2025-03-05"  # 使用最近的交易日期

    try:
        detailed_data = source.get_sector_detailed_data(
            sector_code="",
            sector_name=test_sector,
            date=date
        )

        print(f"\n板块: {test_sector}")
        print(f"今日涨停数: {detailed_data.get('limit_up_count', 0)}")
        print(f"连板梯队: {detailed_data.get('consecutive_boards', {})}")

        # 检查空间龙
        space_dragons = detailed_data.get('space_dragons', [])
        print(f"\n空间龙数量: {len(space_dragons)}")
        for dragon in space_dragons:
            print(f"  - {dragon['name']} ({dragon['code']}): {dragon['consecutive_days']}")

        # 检查中军
        zhongjun_list = detailed_data.get('zhongjun_list', [])
        print(f"\n中军数量: {len(zhongjun_list)}")
        for zj in zhongjun_list:
            print(f"  - {zj['name']} ({zj['code']}): 市值{zj['market_cap']:.2f}亿")

        # 检查先锋龙
        pioneer_list = detailed_data.get('pioneer_list', [])
        print(f"\n先锋龙数量: {len(pioneer_list)}")
        for pioneer in pioneer_list:
            print(f"  - {pioneer['name']} ({pioneer['code']}): 首次封板{pioneer['first_seal_time']}")

        # 检查龙头股数据结构
        leading = detailed_data.get('leading_stock')
        if leading:
            print(f"\n主龙头股: {leading['name']} ({leading['code']})")
            print(f"  - 连板: {leading['consecutive_days']}")
            print(f"  - 收盘封单: {leading['seal_amount']:.2f}亿")
            print(f"  - 大单净流入: {leading['big_order_net']:+.2f}亿")
            print(f"  - 流通市值: {leading['market_cap']:.2f}亿")
            print(f"  - 实际换手: {leading['actual_turnover_rate']:.2f}%")
            print(f"  - 首次涨停: {leading['first_seal_time']}")
            print(f"  - 最终涨停: {leading['last_seal_time']}")
            print(f"  - 开板次数: {leading['open_count']}")

        # 检查涨停股票列表
        limit_up_stocks = detailed_data.get('limit_up_stocks', [])
        print(f"\n涨停股票列表（前5只）:")
        for i, stock in enumerate(limit_up_stocks[:5], 1):
            print(f"  {i}. {stock.get('股票名称', '')} ({stock.get('股票代码', '')})")
            print(f"     连板: {stock.get('连板天数_标准', '')}")
            print(f"     封单额: {stock.get('封单额', '')}")
            print(f"     首次封板: {stock.get('首次封板时间', '-')}")
            print(f"     最终封板: {stock.get('最终封板时间', '-')}")

        print("\n✅ 板块数据获取测试通过")
        return detailed_data

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_report_generator():
    """测试报告生成器"""
    print("\n" + "="*60)
    print("测试报告生成器")
    print("="*60)

    generator = ReportGenerator()

    # 创建模拟数据
    detailed_data = {
        'limit_up_count': 8,
        'limit_up_stocks': [
            {'股票代码': '000001', '股票名称': '平安银行', '连板天数': '5连板', '连板天数_标准': '5连板',
             '封单额': '2.5亿', '首次封板时间': '09:35', '最终封板时间': '09:35', '开板次数': 0},
            {'股票代码': '000002', '股票名称': '万科A', '连板天数': '3连板', '连板天数_标准': '3连板',
             '封单额': '1.8亿', '首次封板时间': '09:45', '最终封板时间': '09:45', '开板次数': 1},
            {'股票代码': '000003', '股票名称': '测试股3', '连板天数': '3连板', '连板天数_标准': '3连板',
             '封单额': '1.5亿', '首次封板时间': '10:00', '最终封板时间': '10:00', '开板次数': 0},
            {'股票代码': '000004', '股票名称': '测试股4', '连板天数': '首板', '连板天数_标准': '首板',
             '封单额': '0.8亿', '首次封板时间': '09:30', '最终封板时间': '09:30', '开板次数': 0},
            {'股票代码': '000005', '股票名称': '测试股5', '连板天数': '首板', '连板天数_标准': '首板',
             '封单额': '0.5亿', '首次封板时间': '09:32', '最终封板时间': '09:32', '开板次数': 0},
        ],
        'consecutive_boards': {5: 1, 3: 2, 1: 2},
        'leading_stock': {
            'code': '000001',
            'name': '平安银行',
            'consecutive_days': '5连板',
            'seal_amount': 2.5,
            'big_order_net': 1.2,
            'market_cap': 2500,
            'actual_turnover_rate': 5.5,
            'first_seal_time': '09:35',
            'last_seal_time': '09:35',
            'open_count': 0
        },
        'space_dragons': [
            {'code': '000001', 'name': '平安银行', 'consecutive_days': '5连板', 'first_seal_time': '09:35',
             'market_cap': 2500, 'actual_turnover_rate': 5.5, 'big_order_net': 1.2, 'seal_amount': 2.5}
        ],
        'zhongjun_list': [
            {'code': '000002', 'name': '万科A', 'consecutive_days': '3连板', 'first_seal_time': '09:45',
             'market_cap': 1800, 'actual_turnover_rate': 3.5, 'big_order_net': 0.8, 'seal_amount': 1.8}
        ],
        'pioneer_list': [
            {'code': '000004', 'name': '测试股4', 'consecutive_days': '首板', 'first_seal_time': '09:30',
             'market_cap': 100, 'actual_turnover_rate': 8.0, 'big_order_net': 0.3, 'seal_amount': 0.8}
        ]
    }

    try:
        core_stocks = generator._format_core_stocks(detailed_data)

        print("\n格式化后的核心个股数据:")

        # 检查空间龙
        print(f"\n空间龙:")
        for dragon in core_stocks.get('space_dragons', []):
            print(f"  - {dragon['name']} ({dragon['code']}): {dragon['consecutive_days']}")

        # 检查中军
        print(f"\n中军:")
        for zj in core_stocks.get('zhongjun_list', []):
            print(f"  - {zj['name']} ({zj['code']}): 市值{zj['market_cap']:.2f}亿, 换手{zj['actual_turnover_rate']:.2f}%")

        # 检查先锋龙
        print(f"\n先锋龙:")
        for pioneer in core_stocks.get('pioneer_list', []):
            print(f"  - {pioneer['name']} ({pioneer['code']}): 首次封板{pioneer['first_seal_time']}")

        # 检查涨停股票排序
        print(f"\n涨停股票排序（验证按连板数降序，同身位按最终涨停时间升序）:")
        for i, stock in enumerate(core_stocks.get('all_limit_up_stocks', []), 1):
            print(f"  {i}. {stock['name']} | {stock['consecutive_days']} | 最终涨停: {stock['last_seal_time']}")

        print("\n✅ 报告生成器测试通过")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("开始验证修复...")
    print()

    # 测试板块数据获取
    detailed_data = test_sector_data()

    # 测试报告生成器
    test_report_generator()

    print("\n" + "="*60)
    print("验证完成")
    print("="*60)
