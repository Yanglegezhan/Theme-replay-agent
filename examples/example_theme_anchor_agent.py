# -*- coding: utf-8 -*-
"""
ThemeAnchorAgent使用示例

演示如何使用ThemeAnchorAgent进行完整的题材分析
"""

import sys
import os
import logging
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data import KaipanlaDataSource, HistoryTracker
from src.llm import LLMAnalyzer
from src.agent import ThemeAnchorAgent, AgentConfig


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """主函数"""
    # 1. 初始化数据源
    logger.info("初始化数据源...")
    data_source = KaipanlaDataSource()
    
    # 2. 初始化历史追踪器
    logger.info("初始化历史追踪器...")
    history_tracker = HistoryTracker(
        storage_path='data/history/sector_rankings.csv'
    )
    
    # 3. 初始化LLM分析器
    logger.info("初始化LLM分析器...")
    
    # 从环境变量或配置文件读取API密钥
    api_key = os.getenv('LLM_API_KEY', 'your-api-key-here')
    
    llm_analyzer = LLMAnalyzer(
        api_key=api_key,
        provider='openai',  # 或 'zhipu', 'qwen', 'deepseek'
        model_name='gpt-4',
        temperature=0.7,
        max_tokens=2000,
        timeout=60
    )
    
    # 4. 配置Agent参数
    config = AgentConfig(
        high_strength_threshold=8000,
        medium_strength_min=2000,
        target_sector_count=7,
        ndays_lookback=7,
        leading_time_lag_min=5,
        leading_time_lag_max=10,
        resonance_elasticity_threshold=3.0,
        divergence_threshold=0.5,
        large_cap_turnover_threshold=30.0,
        health_score_gap_penalty=0.2
    )
    
    # 5. 初始化ThemeAnchorAgent
    logger.info("初始化ThemeAnchorAgent...")
    agent = ThemeAnchorAgent(
        data_source=data_source,
        history_tracker=history_tracker,
        llm_analyzer=llm_analyzer,
        config=config
    )
    
    # 6. 执行分析
    # 使用今天的日期，或指定日期
    analysis_date = datetime.now().strftime('%Y-%m-%d')
    # analysis_date = '2026-01-20'  # 或指定具体日期
    
    logger.info(f"开始分析: {analysis_date}")
    
    try:
        report = agent.analyze(date=analysis_date)
        
        # 7. 输出分析结果
        logger.info("\n" + "=" * 80)
        logger.info("分析报告")
        logger.info("=" * 80)
        
        logger.info(f"\n日期: {report.date}")
        logger.info(f"\n执行摘要:\n{report.executive_summary}")
        
        logger.info(f"\n市场资金意图:")
        logger.info(f"  主力资金流向: {report.market_intent.main_capital_flow}")
        logger.info(f"  板块轮动: {report.market_intent.sector_rotation}")
        logger.info(f"  市场情绪: {report.market_intent.market_sentiment}")
        
        logger.info(f"\n目标板块 ({len(report.filter_result.target_sectors)}个):")
        for sector in report.filter_result.target_sectors:
            logger.info(f"  {sector.rank}. {sector.sector_name} (强度: {sector.strength_score})")
            
            # 情绪周期
            if sector.sector_name in report.emotion_cycles:
                emotion = report.emotion_cycles[sector.sector_name]
                logger.info(f"     情绪周期: {emotion.stage} (置信度: {emotion.confidence:.2f})")
            
            # 容量画像
            if sector.sector_name in report.capacity_profiles:
                capacity = report.capacity_profiles[sector.sector_name]
                logger.info(f"     容量类型: {capacity.capacity_type}, 健康度: {capacity.structure_health:.2f}")
            
            # 操作建议
            if sector.sector_name in report.llm_analysis.trading_advices:
                advice = report.llm_analysis.trading_advices[sector.sector_name]
                logger.info(f"     操作建议: {advice.action} - {advice.entry_timing}")
        
        logger.info(f"\n风险提示 ({len(report.risk_warnings)}条):")
        for warning in report.risk_warnings:
            logger.info(f"  ⚠️  {warning}")
        
        logger.info("\n" + "=" * 80)
        logger.info("分析完成")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"分析失败: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
