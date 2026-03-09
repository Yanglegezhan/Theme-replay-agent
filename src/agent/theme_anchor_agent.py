# -*- coding: utf-8 -*-
"""
题材锚定Agent

核心协调器，编排整个分析流程，集成LLM进行深度分析
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Tuple
from dataclasses import dataclass

from ..data import KaipanlaDataSource, HistoryTracker
from ..analysis import SectorFilter, CorrelationAnalyzer, CapacityProfiler
from ..llm import LLMAnalyzer, ContextBuilder
from ..models import (
    SectorStrength,
    IntradayData,
    LimitUpData,
    TurnoverData,
    CorrelationResult,
    EmotionCycleAnalysis,
    CapacityProfile,
    AnalysisContext,
    LLMAnalysisResult,
)
from ..analysis.sector_filter import FilterResult


logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Agent配置"""
    # 筛选参数
    high_strength_threshold: int = 8000
    medium_strength_min: int = 2000
    target_sector_count: int = 7
    ndays_lookback: int = 7
    
    # 联动分析参数
    leading_time_lag_min: int = 5
    leading_time_lag_max: int = 10
    resonance_elasticity_threshold: float = 3.0
    divergence_threshold: float = 0.5
    
    # 容量分析参数
    large_cap_turnover_threshold: float = 30.0
    health_score_gap_penalty: float = 0.2


@dataclass
class AnalysisReport:
    """综合分析报告"""
    date: str
    executive_summary: str                      # 执行摘要（LLM生成）
    market_intent: Any                          # 资金意图分析
    filter_result: FilterResult                 # 筛选结果
    correlation_result: CorrelationResult       # 联动分析结果
    emotion_cycles: Dict[str, EmotionCycleAnalysis]  # 情绪周期
    capacity_profiles: Dict[str, CapacityProfile]    # 容量画像
    llm_analysis: LLMAnalysisResult            # LLM深度分析
    risk_warnings: List[str]                    # 风险提示
    sector_detailed_data: Dict[str, Dict[str, Any]] = None  # 板块详细数据（包含涨停股票列表）


class ThemeAnchorAgent:
    """题材锚定Agent
    
    核心协调器，编排整个分析流程：
    1. 题材筛选
    2. 盘面联动分析
    3. 情绪周期检测（通过LLM）
    4. 容量结构分析
    5. LLM深度分析（资金意图、持续性、操作建议）
    """
    
    def __init__(
        self,
        data_source: KaipanlaDataSource,
        history_tracker: HistoryTracker,
        llm_analyzer: LLMAnalyzer,
        config: Optional[AgentConfig] = None
    ):
        """初始化题材锚定Agent
        
        Args:
            data_source: 数据源
            history_tracker: 历史追踪器
            llm_analyzer: LLM分析引擎
            config: 配置对象（可选）
        """
        self.data_source = data_source
        self.history_tracker = history_tracker
        self.llm_analyzer = llm_analyzer
        self.config = config or AgentConfig()
        
        # 初始化分析组件
        self.sector_filter = SectorFilter(history_tracker)
        
        self.correlation_analyzer = CorrelationAnalyzer(
            leading_time_lag_min=self.config.leading_time_lag_min,
            leading_time_lag_max=self.config.leading_time_lag_max,
            resonance_elasticity_threshold=self.config.resonance_elasticity_threshold,
            divergence_threshold=self.config.divergence_threshold
        )
        
        self.capacity_profiler = CapacityProfiler(
            large_cap_turnover_threshold=self.config.large_cap_turnover_threshold,
            health_score_gap_penalty=self.config.health_score_gap_penalty
        )
        
        self.context_builder = ContextBuilder()
        
        logger.info("ThemeAnchorAgent initialized")
    
    def analyze(self, date: str) -> AnalysisReport:
        """执行完整分析流程
        
        Args:
            date: 分析日期，格式 'YYYY-MM-DD'
            
        Returns:
            综合分析报告
        """
        logger.info(f"=" * 80)
        logger.info(f"开始分析: {date}")
        logger.info(f"=" * 80)
        
        try:
            # 步骤1: 题材筛选
            logger.info("\n[步骤1] 题材筛选与强度初筛")
            filter_result = self._step1_filter_sectors(date)
            self.filter_result = filter_result  # 保存以便后续步骤使用
            logger.info(f"筛选完成: 目标板块 {len(filter_result.target_sectors)} 个")
            
            # 步骤2: 盘面联动分析
            logger.info("\n[步骤2] 盘面联动与主动性分析")
            correlation_result = self._step2_analyze_correlation(
                filter_result.target_sectors,  # 传递完整的SectorStrength对象列表
                date
            )
            logger.info(f"联动分析完成: 先锋板块 {len(correlation_result.leading_sectors)} 个")
            
            # 步骤3: 情绪周期检测（通过LLM）
            logger.info("\n[步骤3] 情绪周期检测（LLM）")
            emotion_cycles = self._step3_detect_emotion_cycles(
                filter_result.target_sectors,  # 传递完整的SectorStrength对象列表
                date
            )
            logger.info(f"情绪周期检测完成: {len(emotion_cycles)} 个板块")
            
            # 步骤4: 容量结构分析
            logger.info("\n[步骤4] 题材容量与结构画像")
            capacity_profiles, sector_detailed_data = self._step4_profile_capacity(
                [s.sector_name for s in filter_result.target_sectors],  # 传递板块名称列表
                date
            )
            logger.info(f"容量分析完成: {len(capacity_profiles)} 个板块")
            
            # 步骤5: LLM深度分析
            logger.info("\n[步骤5] LLM深度分析")
            llm_analysis = self._step5_llm_deep_analysis(
                filter_result,
                correlation_result,
                emotion_cycles,
                capacity_profiles,
                date
            )
            logger.info("LLM深度分析完成")
            
            # 生成执行摘要和风险提示
            executive_summary = self._generate_executive_summary(
                filter_result,
                llm_analysis
            )
            
            risk_warnings = self._generate_risk_warnings(
                emotion_cycles,
                capacity_profiles
            )
            
            # 构建报告
            report = AnalysisReport(
                date=date,
                executive_summary=executive_summary,
                market_intent=llm_analysis.market_intent,
                filter_result=filter_result,
                correlation_result=correlation_result,
                emotion_cycles=emotion_cycles,
                capacity_profiles=capacity_profiles,
                llm_analysis=llm_analysis,
                risk_warnings=risk_warnings,
                sector_detailed_data=sector_detailed_data
            )
            
            logger.info(f"\n{'=' * 80}")
            logger.info(f"分析完成: {date}")
            logger.info(f"{'=' * 80}\n")
            
            return report
            
        except Exception as e:
            logger.error(f"分析失败: {e}", exc_info=True)
            raise
    
    def _step1_filter_sectors(self, date: str) -> FilterResult:
        """步骤1: 题材筛选
        
        Args:
            date: 分析日期
            
        Returns:
            筛选结果
        """
        # 获取N日板块强度数据
        ndays_data = self.data_source.get_sector_strength_ndays(
            end_date=date,
            num_days=self.config.ndays_lookback
        )
        
        if ndays_data.empty:
            logger.warning(f"板块强度数据为空: {date}")
            return FilterResult(
                target_sectors=[],
                new_faces=[],
                old_faces=[]
            )
        
        # 执行筛选
        filter_result = self.sector_filter.filter_sectors(
            ndays_data=ndays_data,
            current_date=date,
            high_threshold=self.config.high_strength_threshold,
            medium_threshold=self.config.medium_strength_min,
            target_count=self.config.target_sector_count
        )
        
        return filter_result
    
    def _step2_analyze_correlation(
        self,
        target_sectors: List[SectorStrength],  # 修改：接收SectorStrength对象列表
        date: str
    ) -> CorrelationResult:
        """步骤2: 盘面联动分析
        
        Args:
            target_sectors: 目标板块SectorStrength对象列表
            date: 分析日期
            
        Returns:
            联动分析结果
        """
        # 获取大盘分时数据
        market_data = self.data_source.get_intraday_data(
            target='SH000001',  # 上证指数
            date=date
        )
        
        if not market_data.timestamps:
            logger.warning(f"大盘分时数据为空: {date}")
            return CorrelationResult(
                resonance_points=[],
                leading_sectors=[],
                resonance_sectors=[],
                divergence_sectors=[],
                seesaw_effects=[]
            )
        
        # 获取各板块分时数据
        sector_data_list = []
        for sector in target_sectors:
            try:
                # 使用板块代码而不是板块名称
                sector_data = self.data_source.get_intraday_data(
                    target=sector.sector_code,  # 使用板块代码
                    date=date
                )
                
                if sector_data.timestamps:
                    sector_data_list.append((sector.sector_name, sector_data))
                else:
                    logger.warning(f"板块分时数据为空: {sector.sector_name}")
                    
            except Exception as e:
                logger.error(f"获取板块分时数据失败: {sector.sector_name}, {e}")
        
        # 执行联动分析
        if not sector_data_list:
            logger.warning("没有可用的板块分时数据")
            return CorrelationResult(
                resonance_points=[],
                leading_sectors=[],
                resonance_sectors=[],
                divergence_sectors=[],
                seesaw_effects=[]
            )
        
        correlation_result = self.correlation_analyzer.analyze_correlation(
            market_data=market_data,
            sector_data_list=sector_data_list
        )
        
        return correlation_result
    
    def _step3_detect_emotion_cycles(
        self,
        target_sectors: List[SectorStrength],  # 修改：接收SectorStrength对象列表
        date: str
    ) -> Dict[str, EmotionCycleAnalysis]:
        """步骤3: 情绪周期检测（通过LLM）
        
        收集板块涨停数据、连板梯队、炸板率、分时走势等信息，
        调用LLM进行情绪周期判定
        
        Args:
            target_sectors: 目标板块SectorStrength对象列表
            date: 分析日期
            
        Returns:
            板块名 -> 情绪周期分析
        """
        emotion_cycles = {}
        
        # 获取全市场涨停数据
        try:
            limit_up_data = self.data_source.get_limit_up_data(date)
        except Exception as e:
            logger.error(f"获取涨停数据失败: {e}")
            limit_up_data = None
        
        # 为每个板块分析情绪周期
        for sector in target_sectors:
            try:
                # 获取板块详细数据（涨停数、连板梯队、资金流入等）
                sector_detailed_data = None
                try:
                    sector_detailed_data = self.data_source.get_sector_detailed_data(
                        sector_code=sector.sector_code,
                        sector_name=sector.sector_name,
                        date=date
                    )
                except Exception as e:
                    logger.warning(f"获取板块详细数据失败: {sector.sector_name}, {e}")
                
                # 使用板块代码获取分时数据
                intraday_data = self.data_source.get_intraday_data(
                    target=sector.sector_code,  # 使用板块代码
                    date=date
                )
                
                # 获取板块历史数据
                history_records = self.history_tracker.get_history(
                    sector_name=sector.sector_name,  # 使用板块名称
                    days=7
                )
                
                # 获取板块14日K线数据
                kline_data = None
                try:
                    kline_result = self.data_source.get_sector_kline_ndays(
                        sector_code=sector.sector_code,
                        end_date=date,
                        num_days=14
                    )
                    if kline_result and kline_result.get('kline_data'):
                        kline_data = kline_result['kline_data']
                except Exception as e:
                    logger.warning(f"获取板块K线数据失败: {sector.sector_name}, {e}")
                
                # 构建分析上下文
                context = self._build_emotion_cycle_context(
                    sector_name=sector.sector_name,  # 使用板块名称
                    date=date,
                    limit_up_data=limit_up_data,
                    intraday_data=intraday_data,
                    history_records=history_records
                )
                
                # 调用LLM分析
                emotion_cycle = self.llm_analyzer.analyze_emotion_cycle(
                    sector_name=sector.sector_name,  # 使用板块名称
                    context=context,
                    limit_up_data=self._format_limit_up_data(limit_up_data) if limit_up_data else None,
                    intraday_data=self._format_intraday_data(intraday_data) if intraday_data.timestamps else None,
                    historical_data=self._format_historical_data(history_records, kline_data, sector_detailed_data) if history_records else None
                )
                
                emotion_cycles[sector.sector_name] = emotion_cycle
                logger.info(f"板块 {sector.sector_name} 情绪周期: {emotion_cycle.stage}")
                
            except Exception as e:
                logger.error(f"情绪周期分析失败: {sector.sector_name}, {e}")
                # 使用默认值
                emotion_cycles[sector.sector_name] = EmotionCycleAnalysis(
                    stage='未知',
                    confidence=0.0,
                    reasoning='分析失败',
                    key_indicators=[],
                    risk_level='High',
                    opportunity_level='Low'
                )
        
        return emotion_cycles
    
    def _step4_profile_capacity(
        self,
        target_sectors: List[str],
        date: str
    ) -> tuple[Dict[str, CapacityProfile], Dict[str, Dict[str, Any]]]:
        """步骤4: 容量结构分析

        Args:
            target_sectors: 目标板块名称列表
            date: 分析日期

        Returns:
            (板块名 -> 容量画像, 板块名 -> 详细数据)
        """
        capacity_profiles = {}
        sector_detailed_data = {}  # 存储每个板块的详细数据

        # 为每个板块分析容量
        for sector_name in target_sectors:
            try:
                # 查找板块代码
                sector_code = None
                for sector in self.filter_result.target_sectors if hasattr(self, 'filter_result') else []:
                    if sector.sector_name == sector_name:
                        sector_code = sector.sector_code
                        break
                
                if not sector_code:
                    logger.warning(f"未找到板块代码: {sector_name}")
                    continue
                
                # 获取板块详细数据（包含连板梯队和涨停股票）
                sector_detailed = self.data_source.get_sector_detailed_data(
                    sector_code=sector_code,
                    sector_name=sector_name,
                    date=date
                )

                # 保存板块详细数据供报告使用
                sector_detailed_data[sector_name] = sector_detailed
                
                # 获取板块成交额数据
                turnover_data = self.data_source.get_sector_turnover_data(
                    sector_code=sector_code,
                    date=date
                )
                
                # 构建Top5股票数据（从涨停股票列表中选取）
                limit_up_stocks = sector_detailed.get('limit_up_stocks', [])
                if limit_up_stocks:
                    # 按连板天数和封单额排序，选出Top5
                    sorted_stocks = sorted(
                        limit_up_stocks,
                        key=lambda s: (
                            self.data_source._get_consecutive_board_number(s.get('连板天数', '')),
                            s.get('封单额', 0)
                        ),
                        reverse=True
                    )[:5]
                    
                    # 为Top5股票获取真实成交额
                    top5_stocks = []
                    for stock in sorted_stocks:
                        stock_code = stock.get('股票代码', '')
                        stock_name = stock.get('股票名称', '')
                        
                        # 获取真实成交额
                        try:
                            # 判断是否为当日
                            from datetime import datetime
                            today = datetime.now().strftime('%Y-%m-%d')
                            is_today = (date == today)
                            api_date = None if is_today else date
                            
                            stock_data = self.data_source._retry_request(
                                self.data_source.crawler.get_stock_intraday,
                                stock_code=stock_code,
                                date=api_date
                            )
                            if stock_data and 'total_turnover' in stock_data:
                                turnover = float(stock_data['total_turnover']) / 100000000  # 转换为亿元
                                logger.debug(f"获取{stock_name}成交额: {turnover:.2f}亿元")
                            else:
                                # 降级方案：使用流通市值
                                turnover = stock.get('流通市值', 0) / 100000000
                                logger.debug(f"{stock_name}成交额获取失败，使用流通市值: {turnover:.2f}亿元")
                        except Exception as e:
                            logger.warning(f"获取{stock_name}成交额失败: {e}")
                            # 降级方案：使用流通市值
                            turnover = stock.get('流通市值', 0) / 100000000
                        
                        top5_stocks.append({
                            'stock_code': stock_code,
                            'stock_name': stock_name,
                            'turnover': turnover
                        })
                    
                    # 更新turnover_data的top5_stocks
                    turnover_data.top5_stocks = top5_stocks
                    logger.info(f"板块 {sector_name} Top5股票成交额已获取")
                
                # 构建连板梯队数据结构（板数 -> 股票列表）
                # 从sector_detailed中获取涨停股票列表，按连板天数分组
                consecutive_boards_dict = {}
                for stock in sector_detailed.get('limit_up_stocks', []):
                    consecutive_num = self.data_source._get_consecutive_board_number(stock.get('连板天数', ''))
                    if consecutive_num > 0:
                        if consecutive_num not in consecutive_boards_dict:
                            consecutive_boards_dict[consecutive_num] = []
                        consecutive_boards_dict[consecutive_num].append(stock.get('股票代码', ''))
                
                # 执行容量分析
                capacity_profile = self.capacity_profiler.profile_capacity(
                    sector_name=sector_name,
                    turnover_data=turnover_data,
                    consecutive_boards=consecutive_boards_dict
                )

                capacity_profiles[sector_name] = capacity_profile

                # 保存板块详细数据（包含涨停股票列表和龙头股信息）
                sector_detailed_data[sector_name] = {
                    'limit_up_count': sector_detailed.get('limit_up_count', len(sector_detailed.get('limit_up_stocks', []))),
                    'limit_up_stocks': sector_detailed.get('limit_up_stocks', []),
                    'leading_stock': sector_detailed.get('leading_stock'),
                    'core_leaders': sector_detailed.get('core_leaders', []),
                    'space_dragons': sector_detailed.get('space_dragons', []),
                    'zhongjun_list': sector_detailed.get('zhongjun_list', []),
                    'pioneer_list': sector_detailed.get('pioneer_list', []),
                    'consecutive_boards': sector_detailed.get('consecutive_boards', {}),
                    'capital_inflow': sector_detailed.get('capital_inflow', 0),
                    'turnover': sector_detailed.get('turnover', 0),
                    'change_pct': sector_detailed.get('change_pct', 0)
                }

                logger.info(
                    f"板块 {sector_name} 容量: {capacity_profile.capacity_type}, "
                    f"健康度: {capacity_profile.structure_health:.2f}"
                )
                
            except Exception as e:
                logger.error(f"容量分析失败: {sector_name}, {e}")
                import traceback
                logger.error(traceback.format_exc())
                # 使用默认值
                from ..models import PyramidStructure
                capacity_profiles[sector_name] = CapacityProfile(
                    capacity_type='UNKNOWN',
                    sector_turnover=0.0,
                    leading_stock_turnover=0.0,
                    pyramid_structure=PyramidStructure(
                        board_5_plus=0,
                        board_3_to_4=0,
                        board_1_to_2=0,
                        gaps=[],
                        total_stocks=0
                    ),
                    structure_health=0.0,
                    sustainability_score=0.0
                )
                # 错误情况下也保存空数据
                sector_detailed_data[sector_name] = {
                    'limit_up_count': 0,
                    'limit_up_stocks': [],
                    'leading_stock': None,
                    'core_leaders': [],
                    'space_dragons': [],
                    'zhongjun_list': [],
                    'pioneer_list': [],
                    'consecutive_boards': {},
                    'capital_inflow': 0,
                    'turnover': 0,
                    'change_pct': 0
                }

        return capacity_profiles, sector_detailed_data
    
    def _step5_llm_deep_analysis(
        self,
        filter_result: FilterResult,
        correlation_result: CorrelationResult,
        emotion_cycles: Dict[str, EmotionCycleAnalysis],
        capacity_profiles: Dict[str, CapacityProfile],
        date: str
    ) -> LLMAnalysisResult:
        """步骤5: LLM深度分析
        
        整合前四步的数据，调用LLM进行：
        - 资金意图还原
        - 题材持续性判断
        - 风险机会评估
        - 操作建议生成
        
        Args:
            filter_result: 筛选结果
            correlation_result: 联动分析结果
            emotion_cycles: 情绪周期
            capacity_profiles: 容量画像
            date: 分析日期
            
        Returns:
            LLM分析结果汇总
        """
        # 转换数据结构为字典格式（ContextBuilder期望的格式）
        filter_result_dict = self._convert_filter_result_to_dict(filter_result)
        correlation_result_dict = self._convert_correlation_result_to_dict(correlation_result)
        emotion_cycles_dict = self._convert_emotion_cycles_to_dict(emotion_cycles)
        capacity_profiles_dict = self._convert_capacity_profiles_to_dict(capacity_profiles)
        
        # 构建完整分析上下文
        context = self.context_builder.build_analysis_context(
            date=date,
            filter_result=filter_result_dict,
            correlation_result=correlation_result_dict,
            emotion_cycles=emotion_cycles_dict,
            capacity_profiles=capacity_profiles_dict
        )
        
        # 1. 分析市场资金意图
        logger.info("分析市场资金意图...")
        market_intent = self.llm_analyzer.analyze_market_intent(context)
        
        # 2. 评估各板块持续性
        logger.info("评估板块持续性...")
        sector_evaluations = {}
        for sector_name in [s.sector_name for s in filter_result.target_sectors]:
            # 获取该板块的情绪周期和容量数据
            emotion_cycle = emotion_cycles.get(sector_name)
            capacity_profile = capacity_profiles.get(sector_name)
            
            evaluation = self.llm_analyzer.evaluate_sustainability(
                sector_name=sector_name,
                context=context,
                emotion_cycle=emotion_cycle,
                capacity_profile=capacity_profile
            )
            sector_evaluations[sector_name] = evaluation
        
        # 3. 生成操作建议
        logger.info("生成操作建议...")
        trading_advices = {}
        for sector_name in [s.sector_name for s in filter_result.target_sectors]:
            advice = self.llm_analyzer.generate_trading_advice(
                sector_name=sector_name,
                context=context
            )
            trading_advices[sector_name] = advice
        
        # 构建结果
        llm_analysis = LLMAnalysisResult(
            market_intent=market_intent,
            emotion_cycles=emotion_cycles,
            sector_evaluations=sector_evaluations,
            trading_advices=trading_advices
        )
        
        return llm_analysis
    
    def _build_emotion_cycle_context(
        self,
        sector_name: str,
        date: str,
        limit_up_data: Optional[LimitUpData],
        intraday_data: Optional[IntradayData],
        history_records: List[Any]
    ) -> AnalysisContext:
        """构建情绪周期分析上下文
        
        Args:
            sector_name: 板块名称
            date: 日期
            limit_up_data: 涨停数据
            intraday_data: 分时数据
            history_records: 历史记录
            
        Returns:
            分析上下文
        """
        # 构建市场概览
        market_overview = {}
        if limit_up_data:
            market_overview = {
                '涨停数': limit_up_data.limit_up_count,
                '跌停数': limit_up_data.limit_down_count,
                '炸板率': limit_up_data.blown_limit_up_rate,
                '昨日涨停今日表现': limit_up_data.yesterday_limit_up_performance
            }
        
        # 构建目标板块信息
        target_sectors = [{
            'sector_name': sector_name,
            'date': date
        }]
        
        # 构建历史上下文
        historical_context = {}
        if history_records:
            historical_context = {
                'history_records': [
                    {
                        'date': r.date,
                        'rank': r.rank,
                        'strength_score': r.strength_score
                    }
                    for r in history_records
                ]
            }
        
        return AnalysisContext(
            date=date,
            market_overview=market_overview,
            target_sectors=target_sectors,
            sector_relationships={},
            historical_context=historical_context
        )
    
    def _format_limit_up_data(self, limit_up_data: LimitUpData) -> Dict[str, Any]:
        """格式化涨停数据为字典"""
        return {
            'limit_up_count': limit_up_data.limit_up_count,
            'limit_down_count': limit_up_data.limit_down_count,
            'blown_limit_up_rate': limit_up_data.blown_limit_up_rate,
            'consecutive_boards': limit_up_data.consecutive_boards,
            'yesterday_limit_up_performance': limit_up_data.yesterday_limit_up_performance
        }
    
    def _format_intraday_data(self, intraday_data: IntradayData) -> Dict[str, Any]:
        """格式化分时数据为字典"""
        return {
            'target': intraday_data.target,
            'date': intraday_data.date,
            'data_points': len(intraday_data.timestamps),
            'price_range': {
                'min': min(intraday_data.prices) if intraday_data.prices else 0,
                'max': max(intraday_data.prices) if intraday_data.prices else 0
            },
            'pct_change_range': {
                'min': min(intraday_data.pct_changes) if intraday_data.pct_changes else 0,
                'max': max(intraday_data.pct_changes) if intraday_data.pct_changes else 0
            }
        }
    
    def _format_historical_data(
        self,
        history_records: List[Any],
        kline_data: Optional[List[Dict[str, Any]]] = None,
        sector_detailed_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """格式化历史数据为字典
        
        Args:
            history_records: 历史排名记录
            kline_data: K线数据（可选）
            sector_detailed_data: 板块详细数据（可选）
            
        Returns:
            包含历史排名、K线数据和板块详细数据的字典
        """
        result = {
            'records_count': len(history_records),
            'records': [
                {
                    'date': r.date,
                    'rank': r.rank,
                    'strength_score': r.strength_score
                }
                for r in history_records
            ]
        }
        
        # 添加K线数据
        if kline_data:
            result['kline_data'] = kline_data
        
        # 添加板块详细数据
        if sector_detailed_data:
            result['sector_detailed'] = sector_detailed_data
        
        return result
    
    def _generate_executive_summary(
        self,
        filter_result: FilterResult,
        llm_analysis: LLMAnalysisResult
    ) -> str:
        """生成执行摘要
        
        Args:
            filter_result: 筛选结果
            llm_analysis: LLM分析结果
            
        Returns:
            执行摘要文本
        """
        summary_parts = []
        
        # 板块概况
        summary_parts.append(
            f"今日共筛选出 {len(filter_result.target_sectors)} 个核心板块，"
            f"其中新面孔 {len(filter_result.new_faces)} 个，"
            f"老面孔 {len(filter_result.old_faces)} 个。"
        )
        
        # 市场资金意图
        if llm_analysis.market_intent:
            summary_parts.append(
                f"市场资金意图：{llm_analysis.market_intent.main_capital_flow}"
            )
        
        # 情绪周期概况
        emotion_stages = {}
        for sector_name, emotion in llm_analysis.emotion_cycles.items():
            stage = emotion.stage
            if stage not in emotion_stages:
                emotion_stages[stage] = []
            emotion_stages[stage].append(sector_name)
        
        if emotion_stages:
            stage_summary = "，".join([
                f"{stage}期{len(sectors)}个"
                for stage, sectors in emotion_stages.items()
            ])
            summary_parts.append(f"情绪周期分布：{stage_summary}。")
        
        return " ".join(summary_parts)
    
    def _generate_risk_warnings(
        self,
        emotion_cycles: Dict[str, EmotionCycleAnalysis],
        capacity_profiles: Dict[str, CapacityProfile]
    ) -> List[str]:
        """生成风险提示
        
        Args:
            emotion_cycles: 情绪周期
            capacity_profiles: 容量画像
            
        Returns:
            风险提示列表
        """
        warnings = []
        
        # 检查高风险情绪周期
        for sector_name, emotion in emotion_cycles.items():
            if emotion.risk_level == 'High':
                warnings.append(
                    f"{sector_name}：{emotion.stage}，风险等级高，{emotion.reasoning}"
                )
        
        # 检查结构健康度低的板块
        for sector_name, profile in capacity_profiles.items():
            if profile.structure_health < 0.5:
                warnings.append(
                    f"{sector_name}：结构健康度低（{profile.structure_health:.2f}），"
                    f"梯队断层较多，持续性存疑"
                )
        
        return warnings
    
    def _convert_filter_result_to_dict(self, filter_result: FilterResult) -> Dict[str, Any]:
        """转换FilterResult为字典格式"""
        return {
            'target_sectors': [
                {
                    'sector_name': s.sector_name,
                    'sector_code': s.sector_code,
                    'rank': s.rank,
                    'strength_score': s.strength_score,
                    'limit_up_count': s.ndays_limit_up,
                    'is_new_face': s.sector_name in filter_result.new_faces,
                    'consecutive_days': next(
                        (days for name, days in filter_result.old_faces if name == s.sector_name),
                        0
                    )
                }
                for s in filter_result.target_sectors
            ],
            'new_faces': filter_result.new_faces,
            'old_faces': filter_result.old_faces
        }
    
    def _convert_correlation_result_to_dict(self, correlation_result: CorrelationResult) -> Dict[str, Any]:
        """转换CorrelationResult为字典格式"""
        return {
            'resonance_points': [
                {
                    'timestamp': rp.timestamp.isoformat(),
                    'point_type': rp.point_type,
                    'price_change': rp.price_change,
                    'index': rp.index
                }
                for rp in correlation_result.resonance_points
            ],
            'leading_sectors': [
                {
                    'sector_name': ls.sector_name,
                    'time_lag': ls.time_lag
                }
                for ls in correlation_result.leading_sectors
            ],
            'resonance_sectors': [
                {
                    'sector_name': rs.sector_name,
                    'elasticity': rs.elasticity,
                    'market_change': rs.market_change,
                    'sector_change': rs.sector_change
                }
                for rs in correlation_result.resonance_sectors
            ],
            'divergence_sectors': correlation_result.divergence_sectors,
            'seesaw_effects': [
                {
                    'rising_sector': se.rising_sector,
                    'falling_sector': se.falling_sector,
                    'timestamp': se.timestamp.isoformat()
                }
                for se in correlation_result.seesaw_effects
            ]
        }
    
    def _convert_emotion_cycles_to_dict(self, emotion_cycles: Dict[str, EmotionCycleAnalysis]) -> Dict[str, Any]:
        """转换情绪周期为字典格式"""
        return {
            sector_name: {
                'stage': ec.stage,
                'confidence': ec.confidence,
                'reasoning': ec.reasoning,
                'key_indicators': ec.key_indicators,
                'risk_level': ec.risk_level,
                'opportunity_level': ec.opportunity_level
            }
            for sector_name, ec in emotion_cycles.items()
        }
    
    def _convert_capacity_profiles_to_dict(self, capacity_profiles: Dict[str, CapacityProfile]) -> Dict[str, Any]:
        """转换容量画像为字典格式"""
        return {
            sector_name: {
                'capacity_type': cp.capacity_type,
                'sector_turnover': cp.sector_turnover,
                'leading_stock_turnover': cp.leading_stock_turnover,
                'pyramid_structure': {
                    'board_5_plus': cp.pyramid_structure.board_5_plus,
                    'board_3_to_4': cp.pyramid_structure.board_3_to_4,
                    'board_1_to_2': cp.pyramid_structure.board_1_to_2,
                    'gaps': cp.pyramid_structure.gaps,
                    'total_stocks': cp.pyramid_structure.total_stocks
                },
                'structure_health': cp.structure_health,
                'sustainability_score': cp.sustainability_score
            }
            for sector_name, cp in capacity_profiles.items()
        }
