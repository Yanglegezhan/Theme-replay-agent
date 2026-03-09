# -*- coding: utf-8 -*-
"""
LLM引擎真实API测试

使用真实的智谱AI API进行测试
"""

import sys
from pathlib import Path
import yaml

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.llm import LLMAnalyzer, PromptEngine, ContextBuilder
from src.models.data_models import AnalysisContext


def load_config():
    """加载配置文件"""
    config_path = project_root / "config" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def test_market_intent_analysis():
    """测试市场资金意图分析"""
    print("\n" + "=" * 60)
    print("测试1：市场资金意图分析")
    print("=" * 60)
    
    # 加载配置
    config = load_config()
    llm_config = config['llm']
    
    # 初始化LLM分析器
    llm_analyzer = LLMAnalyzer(
        api_key=llm_config['api_key'],
        provider=llm_config['provider'],
        model_name=llm_config['model_name'],
        temperature=llm_config['temperature'],
        max_tokens=llm_config.get('max_tokens'),
        timeout=llm_config.get('timeout', 60)
    )
    
    print(f"✓ LLM分析器初始化成功")
    print(f"  - 提供商: {llm_analyzer.provider}")
    print(f"  - 模型: {llm_analyzer.model_name}")
    print(f"  - API URL: {llm_analyzer.api_url}")
    
    # 创建模拟上下文
    context = AnalysisContext(
        date="2026-01-22",
        market_overview={
            '涨停数': 45,
            '跌停数': 8,
            '炸板率': '15.5%',
            '涨跌比': 1.35,
            '最高连板': '6连板'
        },
        target_sectors=[
            {
                'sector_name': '低空经济',
                'rank': 1,
                'strength_score': 12500,
                'is_new_face': True,
                'consecutive_days': 0,
                'limit_up_count': 8,
                'correlation_type': '先锋'
            },
            {
                'sector_name': '固态电池',
                'rank': 2,
                'strength_score': 10800,
                'is_new_face': False,
                'consecutive_days': 3,
                'limit_up_count': 6,
                'correlation_type': '共振'
            },
            {
                'sector_name': 'AI芯片',
                'rank': 3,
                'strength_score': 9200,
                'is_new_face': False,
                'consecutive_days': 2,
                'limit_up_count': 5,
                'correlation_type': '常规'
            }
        ],
        sector_relationships={
            'leading_sectors': ['低空经济'],
            'resonance_sectors': ['固态电池'],
            'divergence_sectors': [],
            'seesaw_effects': []
        },
        historical_context={
            'new_faces': ['低空经济'],
            'old_faces': ['固态电池', 'AI芯片']
        }
    )
    
    print("\n正在调用LLM进行市场资金意图分析...")
    try:
        result = llm_analyzer.analyze_market_intent(context)
        
        print("\n✓ 分析成功！")
        print(f"\n【主力资金流向】")
        print(result.main_capital_flow)
        print(f"\n【板块轮动分析】")
        print(result.sector_rotation)
        print(f"\n【市场情绪判断】")
        print(result.market_sentiment)
        print(f"\n【关键驱动因素】")
        for i, driver in enumerate(result.key_drivers, 1):
            print(f"  {i}. {driver}")
        print(f"\n【分析置信度】{result.confidence:.2f}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_emotion_cycle_analysis():
    """测试情绪周期分析"""
    print("\n" + "=" * 60)
    print("测试2：情绪周期分析")
    print("=" * 60)
    
    # 加载配置
    config = load_config()
    llm_config = config['llm']
    
    # 初始化LLM分析器
    llm_analyzer = LLMAnalyzer(
        api_key=llm_config['api_key'],
        provider=llm_config['provider'],
        model_name=llm_config['model_name'],
        temperature=llm_config['temperature'],
        max_tokens=llm_config.get('max_tokens'),
        timeout=llm_config.get('timeout', 60)
    )
    
    # 创建模拟上下文
    context = AnalysisContext(
        date="2026-01-22",
        market_overview={
            '涨停数': 45,
            '跌停数': 8,
            '炸板率': '15.5%'
        },
        target_sectors=[
            {
                'sector_name': '低空经济',
                'rank': 1,
                'strength_score': 12500,
                'is_new_face': True,
                'consecutive_days': 0,
                'limit_up_count': 8,
                'turnover': 150.5,
                'consecutive_boards': {
                    1: ['股票A', '股票B', '股票C'],
                    2: ['股票D', '股票E'],
                    3: ['股票F']
                },
                'intraday_summary': '分时图呈45度攻击角，早盘快速拉升后维持高位震荡'
            }
        ],
        sector_relationships={},
        historical_context={}
    )
    
    print("\n正在调用LLM进行情绪周期分析...")
    try:
        result = llm_analyzer.analyze_emotion_cycle("低空经济", context)
        
        print("\n✓ 分析成功！")
        print(f"\n【情绪周期阶段】{result.stage}")
        print(f"【判定置信度】{result.confidence:.2f}")
        print(f"【风险等级】{result.risk_level}")
        print(f"【机会等级】{result.opportunity_level}")
        print(f"\n【判定理由】")
        print(result.reasoning)
        print(f"\n【关键指标】")
        for i, indicator in enumerate(result.key_indicators, 1):
            print(f"  {i}. {indicator}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sustainability_evaluation():
    """测试持续性评估"""
    print("\n" + "=" * 60)
    print("测试3：题材持续性评估")
    print("=" * 60)
    
    # 加载配置
    config = load_config()
    llm_config = config['llm']
    
    # 初始化LLM分析器
    llm_analyzer = LLMAnalyzer(
        api_key=llm_config['api_key'],
        provider=llm_config['provider'],
        model_name=llm_config['model_name'],
        temperature=llm_config['temperature'],
        max_tokens=llm_config.get('max_tokens'),
        timeout=llm_config.get('timeout', 60)
    )
    
    # 创建模拟上下文
    context = AnalysisContext(
        date="2026-01-22",
        market_overview={},
        target_sectors=[
            {
                'sector_name': '低空经济',
                'rank': 1,
                'strength_score': 12500,
                'is_new_face': True,
                'consecutive_days': 0,
                'limit_up_count': 8,
                'emotion_cycle': {
                    'stage': '启动期',
                    'confidence': 0.85,
                    'risk_level': 'Medium',
                    'opportunity_level': 'High'
                },
                'capacity_profile': {
                    'capacity_type': '大容量主线',
                    'structure_health': 0.8
                },
                'historical_performance': '首次进入前7强，属于新面孔题材'
            }
        ],
        sector_relationships={},
        historical_context={}
    )
    
    print("\n正在调用LLM进行持续性评估...")
    try:
        result = llm_analyzer.evaluate_sustainability("低空经济", context)
        
        print("\n✓ 评估成功！")
        print(f"\n【持续性评分】{result.sustainability_score:.1f}/100")
        print(f"【预期持续时间】{result.time_horizon}")
        print(f"\n【风险因素】")
        for i, factor in enumerate(result.risk_factors, 1):
            print(f"  {i}. {factor}")
        print(f"\n【支撑因素】")
        for i, factor in enumerate(result.support_factors, 1):
            print(f"  {i}. {factor}")
        print(f"\n【评估理由】")
        print(result.reasoning)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 评估失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trading_advice():
    """测试操作建议生成"""
    print("\n" + "=" * 60)
    print("测试4：操作建议生成")
    print("=" * 60)
    
    # 加载配置
    config = load_config()
    llm_config = config['llm']
    
    # 初始化LLM分析器
    llm_analyzer = LLMAnalyzer(
        api_key=llm_config['api_key'],
        provider=llm_config['provider'],
        model_name=llm_config['model_name'],
        temperature=llm_config['temperature'],
        max_tokens=llm_config.get('max_tokens'),
        timeout=llm_config.get('timeout', 60)
    )
    
    # 创建模拟上下文
    context = AnalysisContext(
        date="2026-01-22",
        market_overview={},
        target_sectors=[
            {
                'sector_name': '低空经济',
                'rank': 1,
                'strength_score': 12500,
                'correlation_type': '先锋',
                'emotion_cycle': {
                    'stage': '启动期',
                    'risk_level': 'Medium',
                    'opportunity_level': 'High'
                },
                'capacity_profile': {
                    'capacity_type': '大容量主线',
                    'structure_health': 0.8
                },
                'sustainability': {
                    'sustainability_score': 75.0,
                    'time_horizon': '3-5天'
                }
            }
        ],
        sector_relationships={},
        historical_context={}
    )
    
    print("\n正在调用LLM生成操作建议...")
    try:
        result = llm_analyzer.generate_trading_advice("低空经济", context)
        
        print("\n✓ 生成成功！")
        print(f"\n【操作方向】{result.action}")
        print(f"【仓位建议】{result.position_sizing}")
        print(f"\n【入场时机】")
        print(result.entry_timing)
        print(f"\n【出场策略】")
        print(result.exit_strategy)
        print(f"\n【风险提示】")
        print(result.risk_warning)
        print(f"\n【建议理由】")
        print(result.reasoning)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("LLM引擎真实API测试")
    print("使用智谱AI GLM-4-Flash模型")
    print("=" * 60)
    
    results = []
    
    # 运行所有测试
    results.append(("市场资金意图分析", test_market_intent_analysis()))
    results.append(("情绪周期分析", test_emotion_cycle_analysis()))
    results.append(("题材持续性评估", test_sustainability_evaluation()))
    results.append(("操作建议生成", test_trading_advice()))
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！LLM引擎工作正常！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查配置和网络连接")


if __name__ == "__main__":
    main()
