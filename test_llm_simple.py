# -*- coding: utf-8 -*-
"""
LLM引擎简单测试 - 只测试一个API调用
"""

import sys
from pathlib import Path
import yaml
import time

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.llm import LLMAnalyzer
from src.models.data_models import AnalysisContext


def load_config():
    """加载配置文件"""
    config_path = project_root / "config" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("LLM引擎简单测试")
    print("=" * 60)
    
    # 加载配置
    config = load_config()
    llm_config = config['llm']
    
    print(f"\n配置信息:")
    print(f"  - 提供商: {llm_config['provider']}")
    print(f"  - 模型: {llm_config['model_name']}")
    print(f"  - API Key: {llm_config['api_key'][:20]}...")
    
    # 初始化LLM分析器
    llm_analyzer = LLMAnalyzer(
        api_key=llm_config['api_key'],
        provider=llm_config['provider'],
        model_name=llm_config['model_name'],
        temperature=llm_config['temperature'],
        max_tokens=llm_config.get('max_tokens'),
        timeout=llm_config.get('timeout')
    )
    
    print(f"\n✓ LLM分析器初始化成功")
    print(f"  - API URL: {llm_analyzer.api_url}")
    
    # 创建简单的测试上下文
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
                'limit_up_count': 8
            }
        ],
        sector_relationships={},
        historical_context={}
    )
    
    print("\n正在调用LLM进行情绪周期分析...")
    print("（这可能需要几秒钟时间）\n")
    
    try:
        result = llm_analyzer.analyze_emotion_cycle("低空经济", context)
        
        print("\n" + "=" * 60)
        print("✓ 分析成功！")
        print("=" * 60)
        print(f"\n【情绪周期阶段】{result.stage}")
        print(f"【判定置信度】{result.confidence:.2f}")
        print(f"【风险等级】{result.risk_level}")
        print(f"【机会等级】{result.opportunity_level}")
        print(f"\n【判定理由】")
        print(result.reasoning)
        print(f"\n【关键指标】")
        for i, indicator in enumerate(result.key_indicators, 1):
            print(f"  {i}. {indicator}")
        
        print("\n" + "=" * 60)
        print("🎉 测试成功！LLM引擎工作正常！")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ 测试失败")
        print("=" * 60)
        print(f"\n错误信息: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
