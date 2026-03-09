# -*- coding: utf-8 -*-
"""
ReportGenerator单元测试

测试报告生成和导出功能
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

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


@pytest.fixture
def sample_analysis_report():
    """创建示例分析报告"""
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
            )
        ],
        new_faces=['低空经济'],
        old_faces=[('固态电池', 3)]
    )
    
    # 创建联动分析结果
    correlation_result = CorrelationResult(
        resonance_points=[],
        leading_sectors=[],
        resonance_sectors=[],
        divergence_sectors=[],
        seesaw_effects=[]
    )
    
    # 创建情绪周期
    emotion_cycles = {
        '低空经济': EmotionCycleAnalysis(
            stage='启动期',
            confidence=0.85,
            reasoning='首板激增，45度攻击波',
            key_indicators=['涨停数激增', '分时图强势'],
            risk_level='Medium',
            opportunity_level='High'
        ),
        '固态电池': EmotionCycleAnalysis(
            stage='高潮期',
            confidence=0.90,
            reasoning='涨停10只，炸板率低',
            key_indicators=['涨停数>10', '炸板率<20%'],
            risk_level='Low',
            opportunity_level='High'
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
        )
    }
    
    # 创建LLM分析结果
    market_intent = MarketIntentAnalysis(
        main_capital_flow='资金流向低空经济和固态电池',
        sector_rotation='从锂电池流向固态电池',
        market_sentiment='情绪高涨',
        key_drivers=['政策利好', '技术突破'],
        confidence=0.85
    )
    
    sector_evaluations = {
        '低空经济': SustainabilityEvaluation(
            sustainability_score=75.0,
            time_horizon='3-5天',
            risk_factors=['政策不确定性'],
            support_factors=['政策利好', '资金充足'],
            reasoning='新题材，有政策支持'
        ),
        '固态电池': SustainabilityEvaluation(
            sustainability_score=80.0,
            time_horizon='一周以上',
            risk_factors=['高位震荡'],
            support_factors=['技术突破', '龙头强势'],
            reasoning='老题材，结构健康'
        )
    }
    
    trading_advices = {
        '低空经济': TradingAdvice(
            action='低吸',
            entry_timing='回调时介入',
            exit_strategy='见顶信号离场',
            position_sizing='半仓',
            risk_warning='注意政策变化',
            reasoning='新题材，有上涨空间'
        ),
        '固态电池': TradingAdvice(
            action='追涨',
            entry_timing='突破时介入',
            exit_strategy='跌破支撑离场',
            position_sizing='重仓',
            risk_warning='注意高位风险',
            reasoning='龙头强势，可追涨'
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
        date='2026-01-20',
        executive_summary='今日共筛选出 2 个核心板块，其中新面孔 1 个，老面孔 1 个。',
        market_intent=market_intent,
        filter_result=filter_result,
        correlation_result=correlation_result,
        emotion_cycles=emotion_cycles,
        capacity_profiles=capacity_profiles,
        llm_analysis=llm_analysis,
        risk_warnings=['固态电池：高潮期，风险等级低，涨停10只，炸板率低']
    )
    
    return report


class TestReportGenerator:
    """ReportGenerator测试类"""
    
    def test_initialization(self):
        """测试初始化"""
        generator = ReportGenerator()
        assert generator is not None
    
    def test_generate_report(self, sample_analysis_report):
        """测试生成报告"""
        generator = ReportGenerator()
        report = generator.generate_report(sample_analysis_report)
        
        # 验证报告结构
        assert 'date' in report
        assert 'generated_at' in report
        assert 'summary' in report
        assert 'target_sectors' in report
        assert 'market_overview' in report
        assert 'risk_warnings' in report
        
        # 验证日期
        assert report['date'] == '2026-01-20'
        
        # 验证摘要
        assert 'executive_summary' in report['summary']
        assert 'market_intent' in report['summary']
        
        # 验证目标板块
        assert len(report['target_sectors']) == 2
        
        # 验证板块排序（按强度分数降序）
        assert report['target_sectors'][0]['strength_score'] >= report['target_sectors'][1]['strength_score']
    
    def test_target_sectors_format(self, sample_analysis_report):
        """测试目标板块格式化"""
        generator = ReportGenerator()
        report = generator.generate_report(sample_analysis_report)
        
        # 检查第一个板块
        sector = report['target_sectors'][0]
        
        # 基础信息
        assert 'sector_name' in sector
        assert 'sector_code' in sector
        assert 'rank' in sector
        assert 'strength_score' in sector
        assert 'limit_up_count' in sector
        assert 'is_new_face' in sector
        assert 'consecutive_days' in sector
        
        # 分析结果
        assert 'correlation_analysis' in sector
        assert 'emotion_cycle' in sector
        assert 'capacity_profile' in sector
        assert 'sustainability_evaluation' in sector
        assert 'trading_advice' in sector
    
    def test_market_overview_format(self, sample_analysis_report):
        """测试市场概览格式化"""
        generator = ReportGenerator()
        report = generator.generate_report(sample_analysis_report)
        
        overview = report['market_overview']
        
        # 验证统计数据
        assert overview['total_sectors'] == 2
        assert overview['new_faces_count'] == 1
        assert overview['old_faces_count'] == 1
        assert 'emotion_cycle_distribution' in overview
        
        # 验证情绪周期分布
        emotion_dist = overview['emotion_cycle_distribution']
        assert '启动期' in emotion_dist
        assert '高潮期' in emotion_dist
    
    def test_export_markdown(self, sample_analysis_report):
        """测试导出Markdown"""
        generator = ReportGenerator()
        report = generator.generate_report(sample_analysis_report)
        
        # 使用临时文件
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test_report.md'
            generator.export_markdown(report, str(output_path))
            
            # 验证文件存在
            assert output_path.exists()
            
            # 验证文件内容
            content = output_path.read_text(encoding='utf-8')
            assert '# A股超短线题材锚定分析报告' in content
            assert '2026-01-20' in content
            assert '低空经济' in content
            assert '固态电池' in content
            assert '执行摘要' in content
            assert '市场资金意图' in content
            assert '目标板块详情' in content
    
    def test_export_json(self, sample_analysis_report):
        """测试导出JSON"""
        generator = ReportGenerator()
        report = generator.generate_report(sample_analysis_report)
        
        # 使用临时文件
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test_report.json'
            generator.export_json(report, str(output_path))
            
            # 验证文件存在
            assert output_path.exists()
            
            # 验证JSON格式
            with open(output_path, 'r', encoding='utf-8') as f:
                loaded_report = json.load(f)
            
            # 验证内容
            assert loaded_report['date'] == '2026-01-20'
            assert len(loaded_report['target_sectors']) == 2
            assert loaded_report['target_sectors'][0]['sector_name'] in ['低空经济', '固态电池']
    
    def test_markdown_content_structure(self, sample_analysis_report):
        """测试Markdown内容结构"""
        generator = ReportGenerator()
        report = generator.generate_report(sample_analysis_report)
        
        # 生成Markdown内容
        md_content = generator._generate_markdown_content(report)
        
        # 验证主要章节存在
        assert '# A股超短线题材锚定分析报告' in md_content
        assert '## 执行摘要' in md_content
        assert '## 市场资金意图' in md_content
        assert '## 市场概览' in md_content
        assert '## 目标板块详情' in md_content
        assert '## 风险提示' in md_content
        assert '## 免责声明' in md_content
        
        # 验证板块详情
        assert '### 1. ' in md_content  # 第一个板块
        assert '**基础信息**:' in md_content
        assert '**盘面联动**:' in md_content
        assert '**情绪周期**:' in md_content
        assert '**容量画像**:' in md_content
        assert '**持续性评估**:' in md_content
        assert '**操作建议**:' in md_content
    
    def test_empty_report_handling(self):
        """测试空报告处理"""
        # 创建空的分析报告
        empty_report = AnalysisReport(
            date='2026-01-20',
            executive_summary='无数据',
            market_intent=None,
            filter_result=FilterResult(
                target_sectors=[],
                new_faces=[],
                old_faces=[]
            ),
            correlation_result=CorrelationResult(
                resonance_points=[],
                leading_sectors=[],
                resonance_sectors=[],
                divergence_sectors=[],
                seesaw_effects=[]
            ),
            emotion_cycles={},
            capacity_profiles={},
            llm_analysis=LLMAnalysisResult(
                market_intent=MarketIntentAnalysis(
                    main_capital_flow='',
                    sector_rotation='',
                    market_sentiment='',
                    key_drivers=[],
                    confidence=0.0
                ),
                emotion_cycles={},
                sector_evaluations={},
                trading_advices={}
            ),
            risk_warnings=[]
        )
        
        generator = ReportGenerator()
        report = generator.generate_report(empty_report)
        
        # 验证空报告也能正常生成
        assert report['date'] == '2026-01-20'
        assert len(report['target_sectors']) == 0
        assert report['market_overview']['total_sectors'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
