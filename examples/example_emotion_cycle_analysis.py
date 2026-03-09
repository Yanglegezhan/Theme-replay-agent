# -*- coding: utf-8 -*-
"""
情绪周期分析示例

演示如何使用LLM进行板块情绪周期分析
"""

import sys
import os

# 添加父目录到路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.llm.llm_analyzer import LLMAnalyzer
from src.llm.prompt_engine import PromptEngine
from src.llm.context_builder import ContextBuilder
from src.models.data_models import AnalysisContext


def example_basic_emotion_cycle_analysis():
    """基础情绪周期分析示例"""
    print("=" * 70)
    print("示例1: 基础情绪周期分析")
    print("=" * 70)
    
    # 1. 准备分析上下文
    context = AnalysisContext(
        date="2026-01-22",
        market_overview={
            "涨停数": 45,
            "跌停数": 8,
            "炸板率": "25.5%",
            "最高连板": "6连板"
        },
        target_sectors=[
            {
                "sector_name": "低空经济",
                "rank": 1,
                "strength_score": 12500,
                "is_new_face": True,
                "consecutive_days": 0,
                "limit_up_count": 8,
                "turnover": 85.5,
                "consecutive_boards": {
                    6: ["博菲电气"],
                    3: ["股票A", "股票B"],
                    1: ["股票C", "股票D", "股票E"]
                },
                "intraday_summary": "强势上攻，全天保持强势"
            }
        ],
        sector_relationships={},
        historical_context={}
    )
    
    # 2. 准备额外的情绪周期数据
    limit_up_data = {
        "limit_up_count": 45,
        "limit_down_count": 8,
        "blown_limit_up_rate": 25.5,
        "yesterday_limit_up_performance": 3.2
    }
    
    intraday_data = {
        "pct_changes": [0.5, 1.2, 2.5, 3.8, 5.2, 6.5, 7.2, 8.5, 9.2, 9.8]
    }
    
    historical_data = {
        "previous_limit_up_count": 3,
        "emotion_history": []
    }
    
    # 3. 构建提示词（不调用LLM，仅展示提示词）
    prompt_engine = PromptEngine(template_dir=os.path.join(parent_dir, "prompts"))
    
    prompt = prompt_engine.build_emotion_cycle_prompt(
        sector_name="低空经济",
        context=context,
        limit_up_data=limit_up_data,
        intraday_data=intraday_data,
        historical_data=historical_data
    )
    
    print("\n生成的提示词：")
    print("-" * 70)
    print(prompt)
    print("-" * 70)
    
    print("\n✓ 提示词已生成，可以发送给LLM进行分析")
    print("\n注意：实际调用LLM需要配置API密钥")


def example_with_historical_context():
    """带历史上下文的情绪周期分析示例"""
    print("\n" + "=" * 70)
    print("示例2: 带历史上下文的情绪周期分析")
    print("=" * 70)
    
    # 准备带历史数据的上下文
    context = AnalysisContext(
        date="2026-01-22",
        market_overview={
            "涨停数": 35,
            "跌停数": 12,
            "炸板率": "35.5%",
            "最高连板": "5连板"
        },
        target_sectors=[
            {
                "sector_name": "固态电池",
                "rank": 2,
                "strength_score": 10800,
                "is_new_face": False,
                "consecutive_days": 3,
                "limit_up_count": 6,
                "turnover": 120.5,
                "consecutive_boards": {
                    5: ["龙头股"],
                    3: ["跟风股A", "跟风股B"],
                    1: ["补涨股A", "补涨股B", "补涨股C"]
                }
            }
        ],
        sector_relationships={},
        historical_context={}
    )
    
    # 准备历史情绪周期数据
    historical_data = {
        "previous_limit_up_count": 10,  # 前一日涨停数更多，说明在降温
        "emotion_history": [
            {"date": "2026-01-21", "stage": "高潮期"},
            {"date": "2026-01-20", "stage": "启动期"},
            {"date": "2026-01-19", "stage": "启动期"}
        ]
    }
    
    limit_up_data = {
        "blown_limit_up_rate": 35.5,  # 炸板率高，说明分化
        "yesterday_limit_up_performance": -2.5  # 昨日涨停今日表现差
    }
    
    # 构建提示词
    context_builder = ContextBuilder()
    
    formatted_data = context_builder.format_emotion_cycle_data(
        sector_name="固态电池",
        context=context,
        limit_up_data=limit_up_data,
        historical_data=historical_data
    )
    
    print("\n格式化的数据（包含历史信息）：")
    print("-" * 70)
    print(formatted_data)
    print("-" * 70)
    
    print("\n✓ 数据已准备完毕")
    print("\n分析要点：")
    print("  - 涨停数从10只降至6只（-40%）")
    print("  - 炸板率高达35.5%（分化期特征）")
    print("  - 昨日涨停今日表现-2.5%（亏钱效应）")
    print("  - 历史：启动期 → 高潮期 → 当前（可能进入分化期）")


def example_multiple_sectors():
    """多板块情绪周期分析示例"""
    print("\n" + "=" * 70)
    print("示例3: 多板块情绪周期对比分析")
    print("=" * 70)
    
    # 准备多个板块的数据
    sectors_data = [
        {
            "name": "低空经济",
            "stage_hint": "启动期",
            "limit_up_count": 8,
            "prev_limit_up": 3,
            "blown_rate": 15.0,
            "is_new": True
        },
        {
            "name": "固态电池",
            "stage_hint": "分化期",
            "limit_up_count": 6,
            "prev_limit_up": 10,
            "blown_rate": 35.5,
            "is_new": False
        },
        {
            "name": "AI芯片",
            "stage_hint": "高潮期",
            "limit_up_count": 12,
            "prev_limit_up": 8,
            "blown_rate": 18.0,
            "is_new": False
        }
    ]
    
    print("\n板块情绪周期对比：")
    print("-" * 70)
    print(f"{'板块':<12} {'涨停数':<8} {'变化':<10} {'炸板率':<10} {'预期阶段':<10}")
    print("-" * 70)
    
    for sector in sectors_data:
        change = sector['limit_up_count'] - sector['prev_limit_up']
        change_pct = (change / sector['prev_limit_up'] * 100) if sector['prev_limit_up'] > 0 else 0
        
        print(f"{sector['name']:<12} {sector['limit_up_count']:<8} "
              f"{change:+d}({change_pct:+.0f}%){'':<3} "
              f"{sector['blown_rate']:.1f}%{'':<5} "
              f"{sector['stage_hint']:<10}")
    
    print("-" * 70)
    
    print("\n分析建议：")
    print("  1. 低空经济：新面孔，涨停数激增，炸板率低 → 启动期，可关注")
    print("  2. 固态电池：老面孔，涨停数下降，炸板率高 → 分化期，需谨慎")
    print("  3. AI芯片：涨停数持续增加，炸板率低 → 高潮期，可参与但注意风险")


def example_data_preparation_checklist():
    """数据准备清单示例"""
    print("\n" + "=" * 70)
    print("示例4: 情绪周期分析数据准备清单")
    print("=" * 70)
    
    checklist = {
        "必需数据": [
            "✓ 板块名称",
            "✓ 分析日期",
            "✓ 当前涨停数",
            "✓ 连板梯队分布",
            "✓ 板块成交额"
        ],
        "重要数据（强烈建议）": [
            "✓ 前一日涨停数（用于计算变化）",
            "✓ 全市场炸板率",
            "✓ 昨日涨停今日表现",
            "✓ 分时走势数据",
            "✓ 新旧面孔标记"
        ],
        "可选数据（增强分析）": [
            "✓ 历史情绪周期记录",
            "✓ 龙头股表现",
            "✓ 全市场涨停数",
            "✓ 板块排名变化",
            "✓ 盘面联动信息"
        ]
    }
    
    for category, items in checklist.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  {item}")
    
    print("\n" + "-" * 70)
    print("\n数据来源：")
    print("  - 涨停数据：kaipanla_crawler.get_sector_limit_up_ladder()")
    print("  - 连板数据：kaipanla_crawler.get_realtime_rise_fall_analysis()")
    print("  - 分时数据：kaipanla_crawler.get_sector_intraday()")
    print("  - 成交额数据：kaipanla_crawler.get_sector_capital_data()")
    print("  - 历史数据：HistoryTracker.get_history()")


def main():
    """运行所有示例"""
    print("\n" + "=" * 70)
    print("LLM情绪周期分析完整示例")
    print("=" * 70)
    
    examples = [
        example_basic_emotion_cycle_analysis,
        example_with_historical_context,
        example_multiple_sectors,
        example_data_preparation_checklist
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n✗ 示例执行失败: {example_func.__name__}")
            print(f"  错误: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("示例演示完成")
    print("=" * 70)
    print("\n使用说明：")
    print("  1. 准备AnalysisContext和额外数据（limit_up_data等）")
    print("  2. 使用PromptEngine.build_emotion_cycle_prompt()构建提示词")
    print("  3. 使用LLMAnalyzer.analyze_emotion_cycle()调用LLM分析")
    print("  4. 解析返回的EmotionCycleAnalysis结果")
    print("\n注意：实际使用需要配置LLM API密钥")


if __name__ == "__main__":
    main()
