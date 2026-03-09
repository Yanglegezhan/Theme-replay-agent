# -*- coding: utf-8 -*-
"""
LLM引擎使用示例

演示如何使用PromptEngine、ContextBuilder和LLMAnalyzer
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.llm import LLMAnalyzer, PromptEngine, ContextBuilder
from src.models.data_models import AnalysisContext


def example_prompt_engine():
    """示例：使用PromptEngine加载和渲染模板"""
    print("=" * 60)
    print("示例1：PromptEngine - 提示词引擎")
    print("=" * 60)
    
    # 初始化提示词引擎
    prompt_engine = PromptEngine(template_dir="prompts/")
    
    # 加载模板
    print("\n1. 加载市场资金意图分析模板...")
    template = prompt_engine.load_template("market_intent")
    print(f"模板长度: {len(template)} 字符")
    print(f"模板前200字符:\n{template[:200]}...")
    
    # 渲染模板
    print("\n2. 渲染模板...")
    variables = {
        "date": "2026-01-20",
        "market_data": "涨停数: 45只\n跌停数: 8只\n..."
    }
    rendered = prompt_engine.render_template(template, variables)
    print(f"渲染后长度: {len(rendered)} 字符")
    print(f"渲染后前200字符:\n{rendered[:200]}...")


def example_context_builder():
    """示例：使用ContextBuilder构建分析上下文"""
    print("\n" + "=" * 60)
    print("示例2：ContextBuilder - 上下文构建器")
    print("=" * 60)
    
    # 初始化上下文构建器
    context_builder = ContextBuilder(max_tokens=8000)
    
    # 准备模拟数据
    filter_result = {
        'target_sectors': [
            {
                'sector_name': '低空经济',
                'rank': 1,
                'strength_score': 12500,
                'is_new_face': True,
                'consecutive_days': 0,
                'limit_up_count': 8
            },
            {
                'sector_name': '固态电池',
                'rank': 2,
                'strength_score': 10800,
                'is_new_face': False,
                'consecutive_days': 3,
                'limit_up_count': 6
            }
        ],
        'market_stats': {
            'limit_up_count': 45,
            'limit_down_count': 8,
            'blown_limit_up_rate': 15.5,
            'rise_fall_ratio': 1.35
        },
        'new_faces': ['低空经济'],
        'old_faces': ['固态电池']
    }
    
    correlation_result = {
        'leading_sectors': [
            {'sector_name': '低空经济', 'time_lag': -8}
        ],
        'resonance_sectors': [
            {'sector_name': '固态电池', 'elasticity': 3.2}
        ],
        'divergence_sectors': [],
        'seesaw_effects': []
    }
    
    # 构建分析上下文
    print("\n1. 构建分析上下文...")
    context = context_builder.build_analysis_context(
        date="2026-01-20",
        filter_result=filter_result,
        correlation_result=correlation_result
    )
    
    print(f"日期: {context.date}")
    print(f"市场概览: {context.market_overview}")
    print(f"目标板块数: {len(context.target_sectors)}")
    print(f"板块关系: {context.sector_relationships}")
    
    # 格式化为LLM友好的文本
    print("\n2. 格式化为LLM文本...")
    formatted_text = context_builder.format_for_llm(context)
    print(f"格式化文本长度: {len(formatted_text)} 字符")
    print(f"格式化文本前500字符:\n{formatted_text[:500]}...")


def example_llm_analyzer():
    """示例：使用LLMAnalyzer进行分析（需要API密钥）"""
    print("\n" + "=" * 60)
    print("示例3：LLMAnalyzer - LLM分析引擎")
    print("=" * 60)
    
    print("\n注意：此示例需要有效的LLM API密钥才能运行")
    print("请在config/config.yaml中配置API密钥")
    
    # 初始化LLM分析器（使用占位符API密钥）
    try:
        llm_analyzer = LLMAnalyzer(
            api_key="your_api_key_here",
            provider="openai",
            model_name="gpt-4",
            temperature=0.7,
            max_tokens=2000
        )
        
        print(f"\nLLM分析器已初始化:")
        print(f"- 提供商: {llm_analyzer.provider}")
        print(f"- 模型: {llm_analyzer.model_name}")
        print(f"- API URL: {llm_analyzer.api_url}")
        
        # 创建模拟上下文
        context = AnalysisContext(
            date="2026-01-20",
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
                    'is_new_face': True
                }
            ],
            sector_relationships={
                'leading_sectors': ['低空经济']
            },
            historical_context={}
        )
        
        print("\n如果有有效的API密钥，可以调用以下方法:")
        print("- llm_analyzer.analyze_market_intent(context)")
        print("- llm_analyzer.analyze_emotion_cycle('低空经济', context)")
        print("- llm_analyzer.evaluate_sustainability('低空经济', context)")
        print("- llm_analyzer.generate_trading_advice('低空经济', context)")
        
    except Exception as e:
        print(f"\n初始化失败: {e}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("LLM引擎使用示例")
    print("=" * 60)
    
    # 运行示例
    example_prompt_engine()
    example_context_builder()
    example_llm_analyzer()
    
    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
