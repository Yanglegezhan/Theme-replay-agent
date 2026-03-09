# -*- coding: utf-8 -*-
"""
测试情绪周期分析集成

验证LLM情绪周期分析的完整流程
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.llm.llm_analyzer import LLMAnalyzer
from src.llm.prompt_engine import PromptEngine
from src.llm.context_builder import ContextBuilder
from src.models.data_models import AnalysisContext


def test_emotion_cycle_data_formatting():
    """测试情绪周期数据格式化"""
    print("=" * 60)
    print("测试1: 情绪周期数据格式化")
    print("=" * 60)
    
    # 创建测试上下文
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
    
    # 准备额外数据
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
    
    # 创建ContextBuilder并格式化数据
    context_builder = ContextBuilder()
    
    formatted_data = context_builder.format_emotion_cycle_data(
        sector_name="低空经济",
        context=context,
        limit_up_data=limit_up_data,
        intraday_data=intraday_data,
        historical_data=historical_data
    )
    
    print("\n格式化的情绪周期数据：")
    print("-" * 60)
    print(formatted_data)
    print("-" * 60)
    
    # 验证关键信息是否存在
    assert "低空经济" in formatted_data
    assert "涨停家数变化" in formatted_data
    assert "连板梯队" in formatted_data
    assert "市场情绪指标" in formatted_data
    assert "资金参与度" in formatted_data
    assert "分时走势" in formatted_data
    
    print("\n✓ 数据格式化测试通过")
    return True


def test_emotion_cycle_prompt_building():
    """测试情绪周期提示词构建"""
    print("\n" + "=" * 60)
    print("测试2: 情绪周期提示词构建")
    print("=" * 60)
    
    # 创建测试上下文
    context = AnalysisContext(
        date="2026-01-22",
        market_overview={},
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
    
    limit_up_data = {
        "blown_limit_up_rate": 18.5,
        "yesterday_limit_up_performance": 5.8
    }
    
    # 创建PromptEngine并构建提示词
    prompt_engine = PromptEngine(template_dir="prompts/")
    
    try:
        prompt = prompt_engine.build_emotion_cycle_prompt(
            sector_name="固态电池",
            context=context,
            limit_up_data=limit_up_data
        )
        
        print("\n构建的提示词（前500字符）：")
        print("-" * 60)
        print(prompt[:500] + "...")
        print("-" * 60)
        
        # 验证提示词包含关键元素
        assert "情绪周期" in prompt
        assert "固态电池" in prompt
        assert "启动期" in prompt or "高潮期" in prompt  # 理论描述
        assert "JSON" in prompt  # 输出格式要求
        
        print("\n✓ 提示词构建测试通过")
        return True
        
    except FileNotFoundError as e:
        print(f"\n✗ 提示词模板文件未找到: {e}")
        print("  请确保 prompts/emotion_cycle.md 文件存在")
        return False


def test_llm_analyzer_signature():
    """测试LLMAnalyzer的analyze_emotion_cycle方法签名"""
    print("\n" + "=" * 60)
    print("测试3: LLMAnalyzer方法签名验证")
    print("=" * 60)
    
    # 验证方法存在且签名正确
    import inspect
    
    # 获取方法签名
    sig = inspect.signature(LLMAnalyzer.analyze_emotion_cycle)
    params = list(sig.parameters.keys())
    
    print(f"\n方法参数: {params}")
    
    # 验证必需参数
    assert 'self' in params
    assert 'sector_name' in params
    assert 'context' in params
    
    # 验证可选参数
    assert 'limit_up_data' in params
    assert 'intraday_data' in params
    assert 'historical_data' in params
    
    print("\n✓ 方法签名验证通过")
    print("  - 必需参数: sector_name, context")
    print("  - 可选参数: limit_up_data, intraday_data, historical_data")
    
    return True


def test_error_handling():
    """测试错误处理和默认值逻辑"""
    print("\n" + "=" * 60)
    print("测试4: 错误处理和默认值")
    print("=" * 60)
    
    # 创建一个无效的上下文（缺少板块数据）
    context = AnalysisContext(
        date="2026-01-22",
        market_overview={},
        target_sectors=[],  # 空列表
        sector_relationships={},
        historical_context={}
    )
    
    context_builder = ContextBuilder()
    
    # 尝试格式化不存在的板块数据
    formatted_data = context_builder.format_emotion_cycle_data(
        sector_name="不存在的板块",
        context=context
    )
    
    print("\n处理不存在板块的结果：")
    print("-" * 60)
    print(formatted_data)
    print("-" * 60)
    
    # 验证返回了错误信息而不是崩溃
    assert "未找到板块" in formatted_data or "不存在的板块" in formatted_data
    
    print("\n✓ 错误处理测试通过")
    print("  - 系统能够优雅地处理缺失数据")
    print("  - 返回明确的错误信息而不是崩溃")
    
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("LLM情绪周期分析集成测试")
    print("=" * 60)
    
    tests = [
        ("数据格式化", test_emotion_cycle_data_formatting),
        ("提示词构建", test_emotion_cycle_prompt_building),
        ("方法签名验证", test_llm_analyzer_signature),
        ("错误处理", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ 测试失败: {test_name}")
            print(f"  错误: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！LLM情绪周期分析集成完成。")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查实现。")
        return 1


if __name__ == "__main__":
    exit(main())
