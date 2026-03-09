# -*- coding: utf-8 -*-
"""
数据模型定义

定义系统中使用的所有数据结构
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class IntradayData:
    """分时数据"""
    target: str                    # 目标代码（股票代码或板块代码）
    date: str                      # 日期
    timestamps: List[datetime]     # 时间戳列表
    prices: List[float]            # 价格列表
    pct_changes: List[float]       # 涨跌幅列表（相对开盘）


@dataclass
class LimitUpData:
    """涨停数据"""
    limit_up_count: int                          # 全市场涨停家数
    limit_down_count: int                        # 全市场跌停家数
    blown_limit_up_rate: float                   # 全市场炸板率（%）
    consecutive_boards: Dict[int, List[str]]     # 连板数据（板数 -> 股票列表）
    yesterday_limit_up_performance: float        # 昨日涨停今日表现（%）


@dataclass
class TurnoverData:
    """成交额数据"""
    sector_turnover: float                       # 板块总成交额（亿元）
    top5_stocks: List[Dict[str, Any]]           # Top5个股及其成交额
    stock_market_caps: Dict[str, float]         # 个股流通市值


@dataclass
class SectorStrength:
    """板块强度"""
    sector_name: str          # 板块名称
    sector_code: str          # 板块代码
    strength_score: int       # 强度分数（N日累计涨停数）
    ndays_limit_up: int       # N日涨停数
    rank: Optional[int] = None       # 排名


@dataclass
class HistoryRecord:
    """历史记录"""
    date: str                 # 日期
    rank: Optional[int]       # 排名（1-7，或None表示未进入前7）
    strength_score: int       # 强度分数


# ============ LLM Analysis Models ============

@dataclass
class AnalysisContext:
    """LLM分析上下文"""
    date: str
    market_overview: Dict[str, Any]
    target_sectors: List[Dict[str, Any]]
    sector_relationships: Dict[str, Any]
    historical_context: Dict[str, Any]


@dataclass
class MarketIntentAnalysis:
    """市场资金意图分析"""
    main_capital_flow: str        # 主力资金流向描述
    sector_rotation: str          # 板块轮动分析
    market_sentiment: str         # 市场情绪判断
    key_drivers: List[str]        # 关键驱动因素
    confidence: float             # 分析置信度


@dataclass
class EmotionCycleAnalysis:
    """情绪周期分析"""
    stage: str                    # 周期阶段（启动期/高潮期/分化期/修复期/退潮期）
    confidence: float             # 判定置信度（0-1）
    reasoning: str                # 判定理由
    key_indicators: List[str]     # 关键指标说明
    risk_level: str               # 风险等级（Low/Medium/High）
    opportunity_level: str        # 机会等级（Low/Medium/High）


@dataclass
class SustainabilityEvaluation:
    """题材持续性评估"""
    sustainability_score: float   # 持续性评分（0-100）
    time_horizon: str             # 预期持续时间
    risk_factors: List[str]       # 风险因素
    support_factors: List[str]    # 支撑因素
    reasoning: str                # 评估理由


@dataclass
class TradingAdvice:
    """操作建议"""
    action: str                   # 操作方向（观望/低吸/追涨/减仓）
    entry_timing: str             # 入场时机
    exit_strategy: str            # 出场策略
    position_sizing: str          # 仓位建议
    risk_warning: str             # 风险提示
    reasoning: str                # 建议理由


@dataclass
class LLMAnalysisResult:
    """LLM分析结果汇总"""
    market_intent: MarketIntentAnalysis
    emotion_cycles: Dict[str, EmotionCycleAnalysis]  # 板块名 -> 情绪周期分析
    sector_evaluations: Dict[str, SustainabilityEvaluation]
    trading_advices: Dict[str, TradingAdvice]


# ============ Correlation Analysis Models ============

@dataclass
class ResonancePoint:
    """共振点（大盘关键变盘节点）"""
    timestamp: datetime        # 时间戳
    point_type: str           # 类型（DIP/V_REVERSAL/BREAKTHROUGH）
    price_change: float       # 价格变化幅度（%）
    index: int                # 在时间序列中的索引


@dataclass
class LeadingSector:
    """先锋板块"""
    sector_name: str
    time_lag: int             # 时差（分钟，负数表示领先）
    resonance_point: ResonancePoint


@dataclass
class ResonanceSector:
    """共振板块"""
    sector_name: str
    elasticity: float         # 弹性系数
    market_change: float      # 大盘涨幅（%）
    sector_change: float      # 板块涨幅（%）


@dataclass
class SeesawEffect:
    """跷跷板效应"""
    rising_sector: str        # 上涨板块
    falling_sector: str       # 下跌板块
    timestamp: datetime       # 发生时间


@dataclass
class CorrelationResult:
    """盘面联动分析结果"""
    resonance_points: List[ResonancePoint]
    leading_sectors: List[LeadingSector]        # 先锋板块
    resonance_sectors: List[ResonanceSector]    # 共振板块
    divergence_sectors: List[str]               # 分离板块
    seesaw_effects: List[SeesawEffect]          # 跷跷板效应


# ============ Capacity Analysis Models ============

@dataclass
class PyramidStructure:
    """金字塔结构（连板梯队）"""
    board_5_plus: int         # 5板及以上个股数量
    board_3_to_4: int         # 3-4板个股数量
    board_1_to_2: int         # 1-2板个股数量
    gaps: List[int]           # 断层（缺失的板数）
    total_stocks: int         # 总个股数


@dataclass
class CapacityProfile:
    """容量画像"""
    capacity_type: str        # 容量类型（LARGE_CAP/SMALL_CAP）
    sector_turnover: float    # 板块总成交额（亿元）
    leading_stock_turnover: float  # 核心中军成交额（亿元）
    pyramid_structure: PyramidStructure
    structure_health: float   # 结构健康度（0-1）
    sustainability_score: float  # 持续性评分（0-100）
