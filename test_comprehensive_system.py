# -*- coding: utf-8 -*-
"""
综合系统测试 - Task 11: Final Checkpoint

完整的端到端系统测试，验证所有组件集成和LLM分析质量
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json

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
from src.llm import LLMAnalyzer, PromptEngine, ContextBuilder
from src.agent import ThemeAnchorAgent, AgentConfig
from src.output import ReportGenerator
from src.analysis import SectorFilter, CorrelationAnalyzer, CapacityProfiler


class SystemTestSuite:
    """系统测试套件"""
    
    def __init__(self):
        self.test_results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
        self.config = None
        self.data_source = None
        self.history_tracker = None
        self.llm_analyzer = None
        self.agent = None
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 80)
        print("Theme Anchor Agent - 综合系统测试")
        print("Task 11: Final Checkpoint - 完整系统测试")
        print("=" * 80)
        
        # 1. 配置和初始化测试
        self.test_configuration()
        self.test_data_layer()
        self.test_llm_engine()
        self.test_analysis_components()
        
        # 2. 集成测试
        self.test_agent_integration()
        
        # 3. 端到端测试
        self.test_end_to_end_analysis()
        
        # 4. LLM分析质量测试
        self.test_llm_analysis_quality()
        
        # 5. 报告生成测试
        self.test_report_generation()
        
        # 6. 显示测试结果
        self.display_test_summary()
        
        return len(self.test_results['failed']) == 0
    
    def test_configuration(self):
        """测试1: 配置系统"""
        print("\n" + "=" * 80)
        print("测试1: 配置系统")
        print("=" * 80)
        
        try:
            self.config = ConfigManager()
            self._log_pass("配置文件加载")
            
            # 验证LLM配置
            llm_config = self.config.get_llm_config()
            assert llm_config.get('api_key'), "LLM API密钥未配置"
            assert llm_config.get('provider'), "LLM提供商未配置"
            self._log_pass(f"LLM配置验证 (provider: {llm_config.get('provider')})")
            
            # 验证分析配置
            analysis_config = self.config.get_analysis_config()
            assert 'sector_filter' in analysis_config, "板块筛选配置缺失"
            assert 'correlation' in analysis_config, "联动分析配置缺失"
            assert 'capacity' in analysis_config, "容量分析配置缺失"
            self._log_pass("分析配置验证")
            
        except Exception as e:
            self._log_fail("配置系统", str(e))
    
    def test_data_layer(self):
        """测试2: 数据层"""
        print("\n" + "=" * 80)
        print("测试2: 数据层")
        print("=" * 80)
        
        try:
            # 测试数据源
            self.data_source = KaipanlaDataSource()
            self._log_pass("数据源初始化")
            
            # 测试历史追踪器
            history_config = self.config.get('history', {})
            storage_path = history_config.get('storage_path', 'data/history')
            history_path = project_root / storage_path / 'sector_rankings.csv'
            self.history_tracker = HistoryTracker(storage_path=str(history_path))
            self._log_pass("历史追踪器初始化")
            
            # 测试数据获取
            test_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            ndays_data = self.data_source.get_sector_strength_ndays(
                end_date=test_date,
                num_days=7
            )
            
            if not ndays_data.empty:
                self._log_pass(f"板块强度数据获取 ({len(ndays_data)} 条记录)")
            else:
                self._log_warning("板块强度数据为空（可能是非交易日）")
            
        except Exception as e:
            self._log_fail("数据层", str(e))
    
    def test_llm_engine(self):
        """测试3: LLM引擎"""
        print("\n" + "=" * 80)
        print("测试3: LLM引擎")
        print("=" * 80)
        
        try:
            llm_config = self.config.get_llm_config()
            
            # 测试LLM分析器
            self.llm_analyzer = LLMAnalyzer(
                api_key=llm_config['api_key'],
                provider=llm_config.get('provider', 'openai'),
                model_name=llm_config.get('model_name', 'gpt-4'),
                temperature=llm_config.get('temperature', 0.7),
                max_tokens=llm_config.get('max_tokens'),
                timeout=llm_config.get('timeout')
            )
            self._log_pass("LLM分析器初始化")
            
            # 测试提示词引擎
            prompts_dir = project_root / 'prompts'
            prompt_engine = PromptEngine(template_dir=str(prompts_dir))
            self._log_pass("提示词引擎初始化")
            
            # 验证提示词模板存在
            templates = ['market_intent.md', 'emotion_cycle.md', 
                        'sustainability.md', 'trading_advice.md']
            for template in templates:
                template_path = prompts_dir / template
                if template_path.exists():
                    self._log_pass(f"提示词模板: {template}")
                else:
                    self._log_warning(f"提示词模板缺失: {template}")
            
            # 测试上下文构建器
            context_builder = ContextBuilder()
            self._log_pass("上下文构建器初始化")
            
            # 测试LLM连接（可选）
            try:
                test_prompt = "请用一句话回答：1+1等于几？"
                response = self.llm_analyzer._call_llm(test_prompt)
                if response:
                    self._log_pass("LLM连接测试")
                else:
                    self._log_warning("LLM返回空响应")
            except Exception as e:
                self._log_warning(f"LLM连接测试失败: {str(e)[:50]}...")
            
        except Exception as e:
            self._log_fail("LLM引擎", str(e))
    
    def test_analysis_components(self):
        """测试4: 分析组件"""
        print("\n" + "=" * 80)
        print("测试4: 分析组件")
        print("=" * 80)
        
        try:
            # 测试板块筛选器
            sector_filter = SectorFilter(history_tracker=self.history_tracker)
            self._log_pass("板块筛选器初始化")
            
            # 测试联动分析器
            correlation_analyzer = CorrelationAnalyzer()
            self._log_pass("联动分析器初始化")
            
            # 测试容量分析器
            capacity_profiler = CapacityProfiler()
            self._log_pass("容量分析器初始化")
            
        except Exception as e:
            self._log_fail("分析组件", str(e))
    
    def test_agent_integration(self):
        """测试5: Agent集成"""
        print("\n" + "=" * 80)
        print("测试5: Agent集成")
        print("=" * 80)
        
        try:
            analysis_config = self.config.get_analysis_config()
            
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
            self._log_pass("Agent配置创建")
            
            self.agent = ThemeAnchorAgent(
                data_source=self.data_source,
                history_tracker=self.history_tracker,
                llm_analyzer=self.llm_analyzer,
                config=agent_config
            )
            self._log_pass("ThemeAnchorAgent初始化")
            
            # 验证组件
            assert self.agent.sector_filter is not None, "SectorFilter未初始化"
            assert self.agent.correlation_analyzer is not None, "CorrelationAnalyzer未初始化"
            assert self.agent.capacity_profiler is not None, "CapacityProfiler未初始化"
            assert self.agent.context_builder is not None, "ContextBuilder未初始化"
            self._log_pass("所有分析组件验证")
            
        except Exception as e:
            self._log_fail("Agent集成", str(e))
    
    def test_end_to_end_analysis(self):
        """测试6: 端到端分析"""
        print("\n" + "=" * 80)
        print("测试6: 端到端分析")
        print("=" * 80)
        
        try:
            # 使用昨天的日期
            test_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            print(f"  分析日期: {test_date}")
            
            print("\n  开始执行完整分析...")
            self.report = self.agent.analyze(date=test_date)
            
            self._log_pass("分析流程执行")
            
            # 验证报告内容
            assert self.report.date == test_date, "报告日期不匹配"
            self._log_pass(f"报告日期验证: {self.report.date}")
            
            assert self.report.executive_summary, "执行摘要为空"
            self._log_pass("执行摘要生成")
            
            assert self.report.filter_result is not None, "筛选结果为空"
            sector_count = len(self.report.filter_result.target_sectors)
            self._log_pass(f"板块筛选完成: {sector_count} 个目标板块")
            
            assert self.report.correlation_result is not None, "联动分析结果为空"
            self._log_pass("联动分析完成")
            
            assert self.report.emotion_cycles is not None, "情绪周期分析为空"
            emotion_count = len(self.report.emotion_cycles)
            self._log_pass(f"情绪周期分析完成: {emotion_count} 个板块")
            
            assert self.report.capacity_profiles is not None, "容量分析为空"
            capacity_count = len(self.report.capacity_profiles)
            self._log_pass(f"容量分析完成: {capacity_count} 个板块")
            
            assert self.report.llm_analysis is not None, "LLM分析为空"
            self._log_pass("LLM深度分析完成")
            
        except Exception as e:
            self._log_fail("端到端分析", str(e))
            import traceback
            traceback.print_exc()
    
    def test_llm_analysis_quality(self):
        """测试7: LLM分析质量"""
        print("\n" + "=" * 80)
        print("测试7: LLM分析质量")
        print("=" * 80)
        
        if not hasattr(self, 'report') or self.report is None:
            self._log_warning("跳过LLM分析质量测试（无报告数据）")
            return
        
        try:
            # 验证市场资金意图分析
            if self.report.market_intent:
                intent = self.report.market_intent
                assert intent.main_capital_flow, "主力资金流向为空"
                assert intent.market_sentiment, "市场情绪为空"
                assert 0 <= intent.confidence <= 1, "置信度超出范围"
                self._log_pass("市场资金意图分析质量")
            else:
                self._log_warning("市场资金意图分析为空")
            
            # 验证情绪周期分析
            valid_stages = ["启动期", "高潮期", "分化期", "修复期", "退潮期", "未知"]
            for sector_name, emotion in self.report.emotion_cycles.items():
                assert emotion.stage in valid_stages, f"无效的情绪周期阶段: {emotion.stage}"
                assert 0 <= emotion.confidence <= 1, f"置信度超出范围: {emotion.confidence}"
                assert emotion.reasoning, "判定理由为空"
                assert emotion.risk_level in ["Low", "Medium", "High"], "无效的风险等级"
                assert emotion.opportunity_level in ["Low", "Medium", "High"], "无效的机会等级"
            
            if self.report.emotion_cycles:
                self._log_pass(f"情绪周期分析质量 ({len(self.report.emotion_cycles)} 个板块)")
            else:
                self._log_warning("情绪周期分析为空")
            
            # 验证持续性评估
            for sector_name, evaluation in self.report.llm_analysis.sector_evaluations.items():
                assert 0 <= evaluation.sustainability_score <= 100, "持续性评分超出范围"
                assert evaluation.time_horizon, "预期持续时间为空"
                assert evaluation.reasoning, "评估理由为空"
            
            if self.report.llm_analysis.sector_evaluations:
                self._log_pass(f"持续性评估质量 ({len(self.report.llm_analysis.sector_evaluations)} 个板块)")
            else:
                self._log_warning("持续性评估为空")
            
            # 验证操作建议
            valid_actions = ["观望", "低吸", "追涨", "减仓"]
            for sector_name, advice in self.report.llm_analysis.trading_advices.items():
                assert advice.action in valid_actions, f"无效的操作方向: {advice.action}"
                assert advice.entry_timing, "入场时机为空"
                assert advice.exit_strategy, "出场策略为空"
                assert advice.reasoning, "建议理由为空"
            
            if self.report.llm_analysis.trading_advices:
                self._log_pass(f"操作建议质量 ({len(self.report.llm_analysis.trading_advices)} 个板块)")
            else:
                self._log_warning("操作建议为空")
            
        except Exception as e:
            self._log_fail("LLM分析质量", str(e))
    
    def test_report_generation(self):
        """测试8: 报告生成"""
        print("\n" + "=" * 80)
        print("测试8: 报告生成")
        print("=" * 80)
        
        if not hasattr(self, 'report') or self.report is None:
            self._log_warning("跳过报告生成测试（无报告数据）")
            return
        
        try:
            generator = ReportGenerator()
            self._log_pass("ReportGenerator初始化")
            
            # 生成结构化报告
            structured_report = generator.generate_report(self.report)
            self._log_pass("结构化报告生成")
            
            # 验证报告结构
            assert 'date' in structured_report, "报告缺少日期"
            assert 'summary' in structured_report, "报告缺少摘要"
            assert 'target_sectors' in structured_report, "报告缺少目标板块"
            assert 'market_overview' in structured_report, "报告缺少市场概览"
            self._log_pass("报告结构验证")
            
            # 测试导出Markdown
            output_dir = project_root / 'output' / 'test_reports'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            date_str = self.report.date.replace('-', '')
            md_path = output_dir / f"comprehensive_test_{date_str}.md"
            generator.export_markdown(structured_report, str(md_path))
            self._log_pass(f"Markdown报告导出: {md_path.name}")
            
            # 测试导出JSON
            json_path = output_dir / f"comprehensive_test_{date_str}.json"
            generator.export_json(structured_report, str(json_path))
            self._log_pass(f"JSON报告导出: {json_path.name}")
            
            # 验证文件存在
            assert md_path.exists(), "Markdown文件未生成"
            assert json_path.exists(), "JSON文件未生成"
            self._log_pass("报告文件验证")
            
        except Exception as e:
            self._log_fail("报告生成", str(e))
    
    def display_test_summary(self):
        """显示测试摘要"""
        print("\n" + "=" * 80)
        print("测试结果摘要")
        print("=" * 80)
        
        print(f"\n✓ 通过: {len(self.test_results['passed'])} 项")
        print(f"✗ 失败: {len(self.test_results['failed'])} 项")
        print(f"⚠ 警告: {len(self.test_results['warnings'])} 项")
        
        if self.test_results['failed']:
            print("\n失败的测试:")
            for test_name, error in self.test_results['failed']:
                print(f"  ✗ {test_name}: {error}")
        
        if self.test_results['warnings']:
            print("\n警告:")
            for warning in self.test_results['warnings']:
                print(f"  ⚠ {warning}")
        
        # 显示分析结果摘要
        if hasattr(self, 'report') and self.report:
            print("\n" + "=" * 80)
            print("分析结果摘要")
            print("=" * 80)
            
            print(f"\n分析日期: {self.report.date}")
            print(f"\n{self.report.executive_summary}")
            
            if self.report.filter_result.target_sectors:
                print(f"\n目标板块 ({len(self.report.filter_result.target_sectors)}个):")
                for i, sector in enumerate(self.report.filter_result.target_sectors[:5], 1):
                    is_new = sector.sector_name in self.report.filter_result.new_faces
                    face_type = "新面孔" if is_new else "老面孔"
                    
                    emotion_stage = "未知"
                    if sector.sector_name in self.report.emotion_cycles:
                        emotion_stage = self.report.emotion_cycles[sector.sector_name].stage
                    
                    print(f"  {i}. {sector.sector_name} ({face_type}) - {emotion_stage}")
                    print(f"     强度: {sector.strength_score}, 涨停数: {sector.ndays_limit_up}")
                
                if len(self.report.filter_result.target_sectors) > 5:
                    print(f"  ... 还有 {len(self.report.filter_result.target_sectors) - 5} 个板块")
        
        print("\n" + "=" * 80)
        if len(self.test_results['failed']) == 0:
            print("✓ 所有测试通过！系统运行正常。")
        else:
            print("✗ 部分测试失败，请检查错误信息。")
        print("=" * 80)
    
    def _log_pass(self, test_name):
        """记录测试通过"""
        self.test_results['passed'].append(test_name)
        print(f"✓ {test_name}")
    
    def _log_fail(self, test_name, error):
        """记录测试失败"""
        self.test_results['failed'].append((test_name, error))
        print(f"✗ {test_name}: {error}")
    
    def _log_warning(self, message):
        """记录警告"""
        self.test_results['warnings'].append(message)
        print(f"⚠ {message}")


def main():
    """主测试流程"""
    test_suite = SystemTestSuite()
    success = test_suite.run_all_tests()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
