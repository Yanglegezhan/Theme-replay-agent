# -*- coding: utf-8 -*-
"""
ReportGenerator使用示例

演示如何使用ReportGenerator生成和导出分析报告
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.output import ReportGenerator
from src.agent import ThemeAnchorAgent, AgentConfig
from src.data import KaipanlaDataSource, HistoryTracker
from src.llm import LLMAnalyzer, PromptEngine
from src.utils import setup_logger


def main():
    """主函数"""
    # 设置日志
    logger = setup_logger('example_report_generator', 'logs/example_report_generator.log')
    logger.info("=" * 80)
    logger.info("ReportGenerator使用示例")
    logger.info("=" * 80)
    
    # 配置
    date = '2026-01-20'
    
    # 初始化组件
    logger.info("\n初始化组件...")
    data_source = KaipanlaDataSource()
    history_tracker = HistoryTracker(storage_path='data/history/sector_rankings.csv')
    
    # 初始化LLM（使用示例配置）
    prompt_engine = PromptEngine(template_dir='prompts/')
    llm_analyzer = LLMAnalyzer(
        api_key='your_api_key_here',  # 替换为实际API密钥
        model_name='gpt-4',
        prompt_engine=prompt_engine
    )
    
    # 初始化Agent
    config = AgentConfig()
    agent = ThemeAnchorAgent(
        data_source=data_source,
        history_tracker=history_tracker,
        llm_analyzer=llm_analyzer,
        config=config
    )
    
    # 执行分析
    logger.info(f"\n执行分析: {date}")
    try:
        analysis_report = agent.analyze(date)
        logger.info("分析完成")
    except Exception as e:
        logger.error(f"分析失败: {e}")
        return
    
    # 初始化ReportGenerator
    logger.info("\n初始化ReportGenerator...")
    report_generator = ReportGenerator()
    
    # 生成报告
    logger.info("\n生成报告...")
    report = report_generator.generate_report(analysis_report)
    logger.info(f"报告生成完成，包含 {len(report['target_sectors'])} 个板块")
    
    # 导出Markdown
    logger.info("\n导出Markdown报告...")
    md_output_path = f'output/reports/theme_anchor_report_{date}.md'
    report_generator.export_markdown(report, md_output_path)
    logger.info(f"Markdown报告已保存: {md_output_path}")
    
    # 导出JSON
    logger.info("\n导出JSON报告...")
    json_output_path = f'output/reports/theme_anchor_report_{date}.json'
    report_generator.export_json(report, json_output_path)
    logger.info(f"JSON报告已保存: {json_output_path}")
    
    # 打印报告摘要
    logger.info("\n" + "=" * 80)
    logger.info("报告摘要")
    logger.info("=" * 80)
    logger.info(f"分析日期: {report['date']}")
    logger.info(f"生成时间: {report['generated_at']}")
    logger.info(f"\n执行摘要:")
    logger.info(report['summary']['executive_summary'])
    
    if report['summary']['market_intent']:
        logger.info(f"\n市场资金意图:")
        intent = report['summary']['market_intent']
        logger.info(f"  主力资金流向: {intent.get('main_capital_flow', 'N/A')}")
        logger.info(f"  市场情绪: {intent.get('market_sentiment', 'N/A')}")
    
    logger.info(f"\n市场概览:")
    overview = report['market_overview']
    logger.info(f"  目标板块数: {overview['total_sectors']}")
    logger.info(f"  新面孔: {overview['new_faces_count']} 个")
    logger.info(f"  老面孔: {overview['old_faces_count']} 个")
    
    logger.info(f"\n目标板块:")
    for i, sector in enumerate(report['target_sectors'][:5], 1):  # 只显示前5个
        logger.info(f"  {i}. {sector['sector_name']} (强度: {sector['strength_score']})")
        if sector['emotion_cycle']:
            logger.info(f"     情绪周期: {sector['emotion_cycle']['stage']}")
        if sector['trading_advice']:
            logger.info(f"     操作建议: {sector['trading_advice']['action']}")
    
    if len(report['target_sectors']) > 5:
        logger.info(f"  ... 还有 {len(report['target_sectors']) - 5} 个板块")
    
    if report['risk_warnings']:
        logger.info(f"\n风险提示:")
        for warning in report['risk_warnings'][:3]:  # 只显示前3个
            logger.info(f"  - {warning}")
    
    logger.info("\n" + "=" * 80)
    logger.info("示例完成")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
