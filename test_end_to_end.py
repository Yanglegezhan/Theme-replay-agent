# -*- coding: utf-8 -*-
"""
端到端系统测试

验证Theme Anchor Agent的完整分析流程
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 设置Windows控制台UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.data import KaipanlaDataSource, HistoryTracker
from src.llm import LLMAnalyzer
from src.agent import ThemeAnchorAgent, AgentConfig
from src.output import ReportGenerator


def test_configuration():
    """测试1: 配置加载"""
    print("\n" + "=" * 80)
    print("测试1: 配置加载")
    print("=" * 80)
    
    try:
        config = ConfigManager()
        print("✓ 配置文件加载成功")
        
        # 验证关键配置
        llm_config = config.get_llm_config()
        assert llm_config.get('api_key'), "LLM API密钥未配置"
        print(f"✓ LLM配置验证通过 (provider: {llm_config.get('provider')})")
        
        analysis_config = config.get_analysis_config()
        assert 'sector_filter' in analysis_config, "分析配置缺失"
        print("✓ 分析配置验证通过")
        
        return config
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        raise


def test_data_source():
    """测试2: 数据源连接"""
    print("\n" + "=" * 80)
    print("测试2: 数据源连接")
    print("=" * 80)
    
    try:
        data_source = KaipanlaDataSource()
        print("✓ 数据源初始化成功")
        
        # 测试获取板块强度数据
        test_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"  测试日期: {test_date}")
        
        ndays_data = data_source.get_sector_strength_ndays(
            end_date=test_date,
            num_days=7
        )
        
        if not ndays_data.empty:
            print(f"✓ 板块强度数据获取成功 (共 {len(ndays_data)} 条记录)")
            print(f"  数据列: {list(ndays_data.columns)}")
            # 尝试显示第一行数据
            if len(ndays_data) > 0:
                first_row = ndays_data.iloc[0]
                # 尝试不同的列名
                sector_name = first_row.get('板块名称', first_row.get('sector_name', '未知'))
                print(f"  示例板块: {sector_name}")
        else:
            print("⚠ 板块强度数据为空（可能是非交易日）")
        
        return data_source
    except Exception as e:
        print(f"✗ 数据源测试失败: {e}")
        raise


def test_history_tracker(config):
    """测试3: 历史追踪器"""
    print("\n" + "=" * 80)
    print("测试3: 历史追踪器")
    print("=" * 80)
    
    try:
        history_config = config.get('history', {})
        storage_path = history_config.get('storage_path', 'data/history')
        history_path = project_root / storage_path / 'sector_rankings.csv'
        
        history_tracker = HistoryTracker(storage_path=str(history_path))
        print("✓ 历史追踪器初始化成功")
        
        # 测试查询历史
        history_records = history_tracker.get_history(
            sector_name="测试板块",
            days=7
        )
        print(f"✓ 历史查询功能正常 (查询到 {len(history_records)} 条记录)")
        
        return history_tracker
    except Exception as e:
        print(f"✗ 历史追踪器测试失败: {e}")
        raise


def test_llm_analyzer(config):
    """测试4: LLM分析器"""
    print("\n" + "=" * 80)
    print("测试4: LLM分析器")
    print("=" * 80)
    
    try:
        llm_config = config.get_llm_config()
        
        llm_analyzer = LLMAnalyzer(
            api_key=llm_config['api_key'],
            provider=llm_config.get('provider', 'openai'),
            model_name=llm_config.get('model_name', 'gpt-4'),
            temperature=llm_config.get('temperature', 0.7),
            max_tokens=llm_config.get('max_tokens'),
            timeout=llm_config.get('timeout')
        )
        print("✓ LLM分析器初始化成功")
        print(f"  Provider: {llm_config.get('provider')}")
        print(f"  Model: {llm_config.get('model_name')}")
        
        # 测试简单的LLM调用
        print("  测试LLM连接...")
        test_prompt = "请用一句话回答：今天天气怎么样？"
        
        try:
            response = llm_analyzer._call_llm(test_prompt)
            if response:
                print(f"✓ LLM连接测试成功")
                print(f"  响应示例: {response[:50]}...")
            else:
                print("⚠ LLM返回空响应")
        except Exception as e:
            print(f"⚠ LLM连接测试失败: {e}")
            print("  注意: 这可能是API配置问题，但不影响其他测试")
        
        return llm_analyzer
    except Exception as e:
        print(f"✗ LLM分析器测试失败: {e}")
        raise


def test_agent_initialization(data_source, history_tracker, llm_analyzer, config):
    """测试5: Agent初始化"""
    print("\n" + "=" * 80)
    print("测试5: Agent初始化")
    print("=" * 80)
    
    try:
        analysis_config = config.get_analysis_config()
        
        sector_filter_config = analysis_config.get('sector_filter', {})
        correlation_config = analysis_config.get('correlation', {})
        capacity_config = analysis_config.get('capacity', {})
        
        agent_config = AgentConfig(
            high_strength_threshold=sector_filter_config.get('high_strength_threshold', 8000),
            medium_strength_min=sector_filter_config.get('medium_strength_threshold', 2000),
            target_sector_count=sector_filter_config.get('target_sector_count', 7),
            ndays_lookback=sector_filter_config.get('ndays', 7),
            leading_time_lag_min=correlation_config.get('leading_time_min', 5),
            leading_time_lag_max=correlation_config.get('leading_time_max', 10),
            resonance_elasticity_threshold=correlation_config.get('resonance_elasticity_threshold', 3.0),
            divergence_threshold=correlation_config.get('market_change_threshold', 0.01),
            large_cap_turnover_threshold=capacity_config.get('large_cap_turnover_threshold', 30.0),
            health_score_gap_penalty=0.2
        )
        print("✓ Agent配置创建成功")
        
        agent = ThemeAnchorAgent(
            data_source=data_source,
            history_tracker=history_tracker,
            llm_analyzer=llm_analyzer,
            config=agent_config
        )
        print("✓ ThemeAnchorAgent初始化成功")
        
        # 验证组件
        assert agent.sector_filter is not None, "SectorFilter未初始化"
        assert agent.correlation_analyzer is not None, "CorrelationAnalyzer未初始化"
        assert agent.capacity_profiler is not None, "CapacityProfiler未初始化"
        assert agent.context_builder is not None, "ContextBuilder未初始化"
        print("✓ 所有分析组件验证通过")
        
        return agent
    except Exception as e:
        print(f"✗ Agent初始化失败: {e}")
        raise


def test_full_analysis(agent):
    """测试6: 完整分析流程"""
    print("\n" + "=" * 80)
    print("测试6: 完整分析流程")
    print("=" * 80)
    
    try:
        # 使用昨天的日期（避免当天数据可能不完整）
        test_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"  分析日期: {test_date}")
        
        print("\n  开始执行完整分析...")
        report = agent.analyze(date=test_date)
        
        print("\n✓ 分析流程执行成功")
        
        # 验证报告内容
        assert report.date == test_date, "报告日期不匹配"
        print(f"✓ 报告日期验证通过: {report.date}")
        
        assert report.executive_summary, "执行摘要为空"
        print(f"✓ 执行摘要生成成功")
        
        assert report.filter_result is not None, "筛选结果为空"
        print(f"✓ 板块筛选完成: {len(report.filter_result.target_sectors)} 个目标板块")
        
        assert report.correlation_result is not None, "联动分析结果为空"
        print(f"✓ 联动分析完成")
        
        assert report.emotion_cycles is not None, "情绪周期分析为空"
        print(f"✓ 情绪周期分析完成: {len(report.emotion_cycles)} 个板块")
        
        assert report.capacity_profiles is not None, "容量分析为空"
        print(f"✓ 容量分析完成: {len(report.capacity_profiles)} 个板块")
        
        assert report.llm_analysis is not None, "LLM分析为空"
        print(f"✓ LLM深度分析完成")
        
        return report
    except Exception as e:
        print(f"✗ 完整分析流程失败: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_report_generation(report):
    """测试7: 报告生成"""
    print("\n" + "=" * 80)
    print("测试7: 报告生成")
    print("=" * 80)
    
    try:
        generator = ReportGenerator()
        print("✓ ReportGenerator初始化成功")
        
        # 生成结构化报告
        structured_report = generator.generate_report(report)
        print("✓ 结构化报告生成成功")
        
        # 验证报告结构
        assert 'date' in structured_report, "报告缺少日期"
        assert 'summary' in structured_report, "报告缺少摘要"
        assert 'target_sectors' in structured_report, "报告缺少目标板块"
        assert 'market_overview' in structured_report, "报告缺少市场概览"
        print("✓ 报告结构验证通过")
        
        # 测试导出Markdown
        output_dir = project_root / 'output' / 'test_reports'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        date_str = report.date.replace('-', '')
        md_path = output_dir / f"test_report_{date_str}.md"
        generator.export_markdown(structured_report, str(md_path))
        print(f"✓ Markdown报告导出成功: {md_path}")
        
        # 测试导出JSON
        json_path = output_dir / f"test_report_{date_str}.json"
        generator.export_json(structured_report, str(json_path))
        print(f"✓ JSON报告导出成功: {json_path}")
        
        return structured_report
    except Exception as e:
        print(f"✗ 报告生成失败: {e}")
        raise


def display_test_summary(report):
    """显示测试摘要"""
    print("\n" + "=" * 80)
    print("测试结果摘要")
    print("=" * 80)
    
    print(f"\n分析日期: {report.date}")
    print(f"\n{report.executive_summary}")
    
    print(f"\n目标板块 ({len(report.filter_result.target_sectors)}个):")
    for i, sector in enumerate(report.filter_result.target_sectors[:5], 1):
        is_new = sector.sector_name in report.filter_result.new_faces
        face_type = "新面孔" if is_new else "老面孔"
        
        emotion_stage = "未知"
        if sector.sector_name in report.emotion_cycles:
            emotion_stage = report.emotion_cycles[sector.sector_name].stage
        
        print(f"  {i}. {sector.sector_name} ({face_type}) - {emotion_stage}")
        print(f"     强度: {sector.strength_score}, 涨停数: {sector.ndays_limit_up}")
    
    if len(report.filter_result.target_sectors) > 5:
        print(f"  ... 还有 {len(report.filter_result.target_sectors) - 5} 个板块")
    
    if report.risk_warnings:
        print(f"\n风险提示 ({len(report.risk_warnings)}条):")
        for warning in report.risk_warnings[:3]:
            print(f"  ⚠️  {warning}")


def main():
    """主测试流程"""
    print("\n" + "=" * 80)
    print("Theme Anchor Agent - 端到端系统测试")
    print("=" * 80)
    
    test_results = {
        'passed': 0,
        'failed': 0,
        'warnings': 0
    }
    
    try:
        # 测试1: 配置加载
        config = test_configuration()
        test_results['passed'] += 1
        
        # 测试2: 数据源
        data_source = test_data_source()
        test_results['passed'] += 1
        
        # 测试3: 历史追踪器
        history_tracker = test_history_tracker(config)
        test_results['passed'] += 1
        
        # 测试4: LLM分析器
        llm_analyzer = test_llm_analyzer(config)
        test_results['passed'] += 1
        
        # 测试5: Agent初始化
        agent = test_agent_initialization(
            data_source, history_tracker, llm_analyzer, config
        )
        test_results['passed'] += 1
        
        # 测试6: 完整分析流程
        report = test_full_analysis(agent)
        test_results['passed'] += 1
        
        # 测试7: 报告生成
        structured_report = test_report_generation(report)
        test_results['passed'] += 1
        
        # 显示测试摘要
        display_test_summary(report)
        
    except Exception as e:
        test_results['failed'] += 1
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 最终结果
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
    print(f"\n通过: {test_results['passed']}")
    print(f"失败: {test_results['failed']}")
    print(f"警告: {test_results['warnings']}")
    
    if test_results['failed'] == 0:
        print("\n✓ 所有测试通过！系统运行正常。")
        return 0
    else:
        print("\n✗ 部分测试失败，请检查错误信息。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
