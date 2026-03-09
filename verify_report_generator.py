# -*- coding: utf-8 -*-
"""
ReportGenerator功能验证脚本

快速验证ReportGenerator的核心功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.output import ReportGenerator
from src.agent.theme_anchor_agent import AnalysisReport
from src.analysis.sector_filter import FilterResult
from src.models import (
    SectorStrength,
    CorrelationResult,
    EmotionCycleAnalysis,
    CapacityProfile,
    PyramidStructure,
    MarketIntentAnalysis,
    SustainabilityEvaluation,
    TradingAdvice,
    LLMAnalysisResult
)


def create_sample_report():
    """创建示例报告用于验证"""
    # 创建筛选结果
    filter_result = FilterResult(
        target_sectors=[
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
        ],
        new_faces=['低空经济', 'AI芯片'],
        old_faces=[('固态电池', 3)]
    )
    
    # 创建联动分析结果
    correlation_result = CorrelationResult(
        resonance_points=[],
        leading_sectors=[],
        resonance_sectors=[],
        divergence_sectors=['低空经济'],
        seesaw_effects=[]
    )
    
    # 创建情绪周期
    emotion_cycles = {
        '低空经济': EmotionCycleAnalysis(
            stage='启动期',
            confidence=0.85,
            reasoning='首板激增，分时图呈45度攻击角，资金开始关注',
            key_indicators=['涨停数激增', '分时图强势', '成交量放大'],
            risk_level='Medium',
            opportunity_level='High'
        ),
        '固态电池': EmotionCycleAnalysis(
            stage='高潮期',
            confidence=0.90,
            reasoning='涨停10只，全市场炸板率低于20%，市场情绪高涨',
            key_indicators=['涨停数>10', '炸板率<20%', '龙头强势'],
            risk_level='Low',
            opportunity_level='High'
        ),
        'AI芯片': EmotionCycleAnalysis(
            stage='分化期',
            confidence=0.75,
            reasoning='仅前排龙头涨停，中后排回撤超过5%，资金开始分化',
            key_indicators=['龙头涨停', '跟风股回撤', '炸板率上升'],
            risk_level='High',
            opportunity_level='Medium'
        )
    }
    
    # 创建容量画像
    capacity_profiles = {
        '低空经济': CapacityProfile(
            capacity_type='LARGE_CAP',
            sector_turnover=150.0,
            leading_stock_turnover=35.0,
            pyramid_structure=PyramidStructure(
                board_5_plus=1,
                board_3_to_4=3,
                board_1_to_2=4,
                gaps=[],
                total_stocks=8
            ),
            structure_health=0.85,
            sustainability_score=75.0
        ),
        '固态电池': CapacityProfile(
            capacity_type='LARGE_CAP',
            sector_turnover=200.0,
            leading_stock_turnover=40.0,
            pyramid_structure=PyramidStructure(
                board_5_plus=2,
                board_3_to_4=2,
                board_1_to_2=2,
                gaps=[],
                total_stocks=6
            ),
            structure_health=0.90,
            sustainability_score=80.0
        ),
        'AI芯片': CapacityProfile(
            capacity_type='SMALL_CAP',
            sector_turnover=80.0,
            leading_stock_turnover=15.0,
            pyramid_structure=PyramidStructure(
                board_5_plus=0,
                board_3_to_4=1,
                board_1_to_2=3,
                gaps=[4, 5],
                total_stocks=4
            ),
            structure_health=0.45,
            sustainability_score=50.0
        )
    }
    
    # 创建LLM分析结果
    market_intent = MarketIntentAnalysis(
        main_capital_flow='资金主要流向低空经济和固态电池板块，AI芯片出现分化',
        sector_rotation='资金从传统锂电池板块流向固态电池，新兴的低空经济板块吸引增量资金',
        market_sentiment='市场情绪整体高涨，但局部出现分化迹象',
        key_drivers=['政策利好', '技术突破', '产业升级', '资金轮动'],
        confidence=0.85
    )
    
    sector_evaluations = {
        '低空经济': SustainabilityEvaluation(
            sustainability_score=75.0,
            time_horizon='3-5天',
            risk_factors=['政策不确定性', '题材新颖缺乏历史验证'],
            support_factors=['政策强力支持', '资金充足', '梯队完整'],
            reasoning='新题材处于启动期，有政策支持和资金关注，预计短期内有持续性'
        ),
        '固态电池': SustainabilityEvaluation(
            sustainability_score=80.0,
            time_horizon='一周以上',
            risk_factors=['高位震荡风险', '获利盘压力'],
            support_factors=['技术突破', '龙头强势', '结构健康'],
            reasoning='老题材处于高潮期，结构健康，龙头强势，预计持续性较好'
        ),
        'AI芯片': SustainabilityEvaluation(
            sustainability_score=50.0,
            time_horizon='1-2天',
            risk_factors=['分化严重', '结构断层', '跟风股回撤'],
            support_factors=['龙头尚存', '题材热度'],
            reasoning='题材进入分化期，结构健康度低，持续性存疑，需谨慎'
        )
    }
    
    trading_advices = {
        '低空经济': TradingAdvice(
            action='低吸',
            entry_timing='回调至分时均线附近介入',
            exit_strategy='见顶信号（放量滞涨、龙头跌停）立即离场',
            position_sizing='半仓试探',
            risk_warning='注意政策变化和市场情绪转向',
            reasoning='新题材启动期，有上涨空间，但需控制仓位'
        ),
        '固态电池': TradingAdvice(
            action='追涨',
            entry_timing='龙头突破前高时介入',
            exit_strategy='跌破分时均线或龙头炸板离场',
            position_sizing='重仓',
            risk_warning='注意高位风险，设置止损',
            reasoning='高潮期龙头强势，结构健康，可追涨，但需设置止损'
        ),
        'AI芯片': TradingAdvice(
            action='观望',
            entry_timing='等待修复信号再介入',
            exit_strategy='持仓者逢高减仓',
            position_sizing='轻仓或空仓',
            risk_warning='分化期风险高，不建议追高',
            reasoning='分化期风险高，结构断层，建议观望或减仓'
        )
    }
    
    llm_analysis = LLMAnalysisResult(
        market_intent=market_intent,
        emotion_cycles=emotion_cycles,
        sector_evaluations=sector_evaluations,
        trading_advices=trading_advices
    )
    
    # 创建分析报告
    report = AnalysisReport(
        date='2026-01-22',
        executive_summary='今日共筛选出 3 个核心板块，其中新面孔 2 个，老面孔 1 个。市场情绪整体高涨，但局部出现分化。',
        market_intent=market_intent,
        filter_result=filter_result,
        correlation_result=correlation_result,
        emotion_cycles=emotion_cycles,
        capacity_profiles=capacity_profiles,
        llm_analysis=llm_analysis,
        risk_warnings=[
            'AI芯片：分化期，风险等级高，分化严重，结构断层',
            'AI芯片：结构健康度低（0.45），梯队断层较多，持续性存疑'
        ]
    )
    
    return report


def main():
    """主函数"""
    print("=" * 80)
    print("ReportGenerator功能验证")
    print("=" * 80)
    
    # 创建示例报告
    print("\n1. 创建示例分析报告...")
    analysis_report = create_sample_report()
    print(f"   ✓ 分析日期: {analysis_report.date}")
    print(f"   ✓ 目标板块: {len(analysis_report.filter_result.target_sectors)} 个")
    
    # 初始化ReportGenerator
    print("\n2. 初始化ReportGenerator...")
    generator = ReportGenerator()
    print("   ✓ ReportGenerator已初始化")
    
    # 生成报告
    print("\n3. 生成结构化报告...")
    report = generator.generate_report(analysis_report)
    print(f"   ✓ 报告生成完成")
    print(f"   ✓ 包含板块: {len(report['target_sectors'])} 个")
    print(f"   ✓ 风险提示: {len(report['risk_warnings'])} 条")
    
    # 导出Markdown
    print("\n4. 导出Markdown报告...")
    md_path = 'output/reports/verification_report_20260122.md'
    generator.export_markdown(report, md_path)
    print(f"   ✓ Markdown报告已保存: {md_path}")
    
    # 验证Markdown文件
    md_file = Path(md_path)
    if md_file.exists():
        content = md_file.read_text(encoding='utf-8')
        print(f"   ✓ 文件大小: {len(content)} 字符")
        print(f"   ✓ 包含章节: {'## 执行摘要' in content}")
    
    # 导出JSON
    print("\n5. 导出JSON报告...")
    json_path = 'output/reports/verification_report_20260122.json'
    generator.export_json(report, json_path)
    print(f"   ✓ JSON报告已保存: {json_path}")
    
    # 验证JSON文件
    json_file = Path(json_path)
    if json_file.exists():
        import json
        with open(json_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        print(f"   ✓ JSON格式正确")
        print(f"   ✓ 包含板块: {len(loaded['target_sectors'])} 个")
    
    # 打印报告摘要
    print("\n" + "=" * 80)
    print("报告摘要")
    print("=" * 80)
    print(f"\n分析日期: {report['date']}")
    print(f"生成时间: {report['generated_at']}")
    
    print(f"\n执行摘要:")
    print(f"  {report['summary']['executive_summary']}")
    
    if report['summary']['market_intent']:
        print(f"\n市场资金意图:")
        intent = report['summary']['market_intent']
        print(f"  主力资金流向: {intent['main_capital_flow']}")
        print(f"  市场情绪: {intent['market_sentiment']}")
        print(f"  置信度: {intent['confidence']:.2f}")
    
    print(f"\n市场概览:")
    overview = report['market_overview']
    print(f"  目标板块数: {overview['total_sectors']}")
    print(f"  新面孔: {overview['new_faces_count']} 个")
    print(f"  老面孔: {overview['old_faces_count']} 个")
    
    print(f"\n情绪周期分布:")
    for stage, count in overview['emotion_cycle_distribution'].items():
        print(f"  {stage}: {count} 个")
    
    print(f"\n目标板块:")
    for i, sector in enumerate(report['target_sectors'], 1):
        print(f"\n  {i}. {sector['sector_name']} (排名: {sector['rank']})")
        print(f"     强度分数: {sector['strength_score']}")
        print(f"     新旧标记: {'新面孔' if sector['is_new_face'] else f'老面孔（{sector['consecutive_days']}天）'}")
        
        if sector['emotion_cycle']:
            emotion = sector['emotion_cycle']
            print(f"     情绪周期: {emotion['stage']} (置信度: {emotion['confidence']:.2f})")
            print(f"     风险等级: {emotion['risk_level']}, 机会等级: {emotion['opportunity_level']}")
        
        if sector['capacity_profile']:
            capacity = sector['capacity_profile']
            print(f"     容量类型: {capacity['capacity_type']}")
            print(f"     结构健康度: {capacity['structure_health']:.2f}")
        
        if sector['trading_advice']:
            advice = sector['trading_advice']
            print(f"     操作建议: {advice['action']} ({advice['position_sizing']})")
    
    if report['risk_warnings']:
        print(f"\n风险提示:")
        for warning in report['risk_warnings']:
            print(f"  ⚠ {warning}")
    
    print("\n" + "=" * 80)
    print("验证完成！")
    print("=" * 80)
    print(f"\n生成的报告文件:")
    print(f"  - Markdown: {md_path}")
    print(f"  - JSON: {json_path}")
    print(f"\n请查看生成的报告文件以验证格式和内容。")


if __name__ == '__main__':
    main()
