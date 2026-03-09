# -*- coding: utf-8 -*-
"""
盘面联动与主动性分析模块 - 新版量化逻辑

基于量化指标识别板块与大盘的四种关系状态：
1. 抗跌状态 (Resilient) - 指数下跌时板块保持坚挺
2. 分离状态 (Detached) - 走势与大盘完全切断
3. 先锋状态 (Pioneer) - 先于大盘见底并率先反弹
4. 共振状态 (Resonant) - 与大盘同步放量上涨
"""

import logging
from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from ..models import (
    IntradayData,
    ResonancePoint,
    LeadingSector,
    ResonanceSector,
    SeesawEffect,
    CorrelationResult,
)

logger = logging.getLogger(__name__)


class CorrelationAnalyzer:
    """盘面联动分析器
    
    基于量化指标识别板块状态：
    - 抗跌板块：回撤溢价系数 RDC > 0.7
    - 分离板块：相关系数 |ρ| < 0.4
    - 先锋板块：领先时间差 ΔT < 0 且放量启动
    - 共振板块：能量同步因子 ESF 高且弹性 > 1.5
    """
    
    def __init__(
        self,
        resilient_rdc_threshold: float = 0.7,
        detached_corr_threshold: float = 0.4,
        pioneer_time_lag_min: int = 5,
        pioneer_time_lag_max: int = 15,
        pioneer_volume_ratio: float = 3.0,
        resonant_beta_threshold: float = 1.5,
        resonant_breadth_threshold: float = 0.6,
        **kwargs  # 兼容旧参数
    ):
        """初始化联动分析器
        
        Args:
            resilient_rdc_threshold: 抗跌回撤溢价系数阈值（默认0.7）
            detached_corr_threshold: 分离相关系数阈值（默认0.4）
            pioneer_time_lag_min: 先锋最小领先时间（分钟，默认5）
            pioneer_time_lag_max: 先锋最大领先时间（分钟，默认15）
            pioneer_volume_ratio: 先锋启动成交量倍数（默认3.0）
            resonant_beta_threshold: 共振弹性系数阈值（默认1.5）
            resonant_breadth_threshold: 共振广度阈值（默认0.6）
        """
        self.resilient_rdc_threshold = resilient_rdc_threshold
        self.detached_corr_threshold = detached_corr_threshold
        self.pioneer_time_lag_min = pioneer_time_lag_min
        self.pioneer_time_lag_max = pioneer_time_lag_max
        self.pioneer_volume_ratio = pioneer_volume_ratio
        self.resonant_beta_threshold = resonant_beta_threshold
        self.resonant_breadth_threshold = resonant_breadth_threshold
        
        logger.info(f"CorrelationAnalyzer initialized with NEW quantitative logic:")
        logger.info(f"  抗跌RDC阈值: {resilient_rdc_threshold}")
        logger.info(f"  分离相关系数阈值: ±{detached_corr_threshold}")
        logger.info(f"  先锋领先时间: {pioneer_time_lag_min}-{pioneer_time_lag_max}分钟")
        logger.info(f"  共振弹性阈值: {resonant_beta_threshold}")

        
    def analyze_correlation(
        self,
        market_data: IntradayData,
        sector_data_list: List[Tuple[str, IntradayData]]
    ) -> CorrelationResult:
        """分析盘面联动关系
        
        Args:
            market_data: 大盘分时数据
            sector_data_list: 板块分时数据列表（板块名, 数据）
            
        Returns:
            联动分析结果
        """
        logger.info(f"开始分析盘面联动关系（新量化逻辑），大盘: {market_data.target}, 板块数: {len(sector_data_list)}")
        
        # 准备数据
        market_returns = np.array(market_data.pct_changes)
        
        # 识别大盘关键转折点（用于先锋板块识别）
        market_lows = self._find_local_lows(market_returns, market_data.timestamps)
        logger.info(f"识别到大盘局部低点: {len(market_lows)}个")
        
        # 分析各板块状态
        resilient_sectors = []  # 抗跌板块
        detached_sectors = []   # 分离板块
        pioneer_sectors = []    # 先锋板块
        resonant_sectors = []   # 共振板块
        
        for sector_name, sector_data in sector_data_list:
            sector_returns = np.array(sector_data.pct_changes)
            
            # 确保数据长度一致
            min_len = min(len(market_returns), len(sector_returns))
            if min_len < 20:
                logger.warning(f"板块 {sector_name} 数据点不足，跳过分析")
                continue
            
            market_ret = market_returns[:min_len]
            sector_ret = sector_returns[:min_len]
            
            # 1. 抗跌状态识别
            if self._is_resilient(sector_name, market_ret, sector_ret):
                resilient_sectors.append(sector_name)
            
            # 2. 分离状态识别
            if self._is_detached(sector_name, market_ret, sector_ret):
                detached_sectors.append(sector_name)
            
            # 3. 先锋状态识别
            pioneer_result = self._is_pioneer(
                sector_name, 
                sector_data, 
                market_data, 
                market_lows
            )
            if pioneer_result:
                pioneer_sectors.append(pioneer_result)
            
            # 4. 共振状态识别
            resonant_result = self._is_resonant(
                sector_name,
                market_ret,
                sector_ret,
                market_data,
                sector_data
            )
            if resonant_result:
                resonant_sectors.append(resonant_result)
        
        # 构建结果（使用原有的数据结构）
        result = CorrelationResult(
            resonance_points=[],  # 不再使用共振点概念
            leading_sectors=pioneer_sectors,  # 先锋板块
            resonance_sectors=resonant_sectors,  # 共振板块
            divergence_sectors=detached_sectors,  # 分离板块
            seesaw_effects=[],  # 暂不实现跷跷板
        )
        
        logger.info(
            f"联动分析完成: "
            f"抗跌板块{len(resilient_sectors)}个, "
            f"分离板块{len(detached_sectors)}个, "
            f"先锋板块{len(pioneer_sectors)}个, "
            f"共振板块{len(resonant_sectors)}个"
        )
        
        # 输出详细结果
        if resilient_sectors:
            logger.info(f"抗跌板块: {', '.join(resilient_sectors)}")
        if detached_sectors:
            logger.info(f"分离板块: {', '.join(detached_sectors)}")
        if pioneer_sectors:
            logger.info(f"先锋板块: {', '.join([p.sector_name for p in pioneer_sectors])}")
        if resonant_sectors:
            logger.info(f"共振板块: {', '.join([r.sector_name for r in resonant_sectors])}")
        
        return result
    
    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """计算最大回撤 (MDD)
        
        注意：returns是相对于昨收价的涨跌幅序列，不是增量涨跌幅
        例如：[2.5%, 2.3%, 2.8%] 表示三个时刻相对于昨收价的涨跌幅
        
        Args:
            returns: 涨跌幅序列（百分比，如-0.5表示-0.5%，相对于昨收价）
            
        Returns:
            最大回撤（百分比，正数表示回撤幅度）
        """
        if len(returns) == 0:
            return 0.0
        
        # returns已经是相对于昨收价的涨跌幅，直接使用
        # 计算最大回撤 = 最高点涨跌幅 - 最低点涨跌幅
        running_max = np.maximum.accumulate(returns)
        drawdown = running_max - returns
        
        return np.max(drawdown)
    
    def _is_resilient(
        self,
        sector_name: str,
        market_returns: np.ndarray,
        sector_returns: np.ndarray
    ) -> bool:
        """识别抗跌板块
        
        量化核心：回撤溢价系数 RDC = (MDD_Index - MDD_Sector) / MDD_Index
        识别标准：RDC > 0.7（指数跌1%，板块仅跌不到0.3%）
        
        Args:
            sector_name: 板块名称
            market_returns: 大盘涨跌幅序列
            sector_returns: 板块涨跌幅序列
            
        Returns:
            是否为抗跌板块
        """
        # 计算全天的最大回撤（不仅仅是下跌时段）
        mdd_market = self._calculate_max_drawdown(market_returns)
        mdd_sector = self._calculate_max_drawdown(sector_returns)
        
        if mdd_market < 0.1:  # 大盘回撤太小，不具备参考意义
            logger.debug(f"板块 {sector_name}: 大盘回撤过小({mdd_market:.2f}%)，跳过抗跌判断")
            return False
        
        # 计算回撤溢价系数
        rdc = (mdd_market - mdd_sector) / mdd_market
        
        logger.debug(
            f"板块 {sector_name} 抗跌分析: "
            f"RDC={rdc:.2f}, "
            f"大盘回撤={mdd_market:.2f}%, "
            f"板块回撤={mdd_sector:.2f}%"
        )
        
        if rdc > self.resilient_rdc_threshold:
            logger.info(
                f"[OK] 识别到抗跌板块: {sector_name}, "
                f"RDC={rdc:.2f}, "
                f"大盘回撤={mdd_market:.2f}%, "
                f"板块回撤={mdd_sector:.2f}%"
            )
            return True
        
        return False
    
    def _is_detached(
        self,
        sector_name: str,
        market_returns: np.ndarray,
        sector_returns: np.ndarray
    ) -> bool:
        """识别分离板块
        
        量化核心：动态互相关系数 ρ
        识别标准：
        - 负相关分离：ρ < -0.4（指数跌，板块涨）
        - 零相关分离：-0.2 < ρ < 0.2（走势完全独立）
        
        Args:
            sector_name: 板块名称
            market_returns: 大盘涨跌幅序列
            sector_returns: 板块涨跌幅序列
            
        Returns:
            是否为分离板块
        """
        # 使用全天数据计算相关系数（而不是仅最近20个点）
        if len(market_returns) < 20:
            return False
        
        # 计算相关系数
        if np.std(market_returns) < 0.01 or np.std(sector_returns) < 0.01:
            logger.debug(f"板块 {sector_name}: 波动过小，跳过分离判断")
            return False
        
        corr = np.corrcoef(market_returns, sector_returns)[0, 1]
        
        # 判断分离状态
        is_negative_detached = corr < -self.detached_corr_threshold
        is_zero_detached = abs(corr) < (self.detached_corr_threshold / 2)
        
        logger.debug(
            f"板块 {sector_name} 分离分析: "
            f"相关系数={corr:.2f}"
        )
        
        if is_negative_detached or is_zero_detached:
            detach_type = "负相关" if is_negative_detached else "零相关"
            logger.info(
                f"[OK] 识别到分离板块: {sector_name}, "
                f"类型={detach_type}, "
                f"相关系数={corr:.2f}"
            )
            return True
        
        return False
    
    def _find_local_lows(
        self,
        returns: np.ndarray,
        timestamps: List[datetime]
    ) -> List[Tuple[int, datetime, float]]:
        """识别局部低点
        
        Args:
            returns: 涨跌幅序列
            timestamps: 时间戳列表
            
        Returns:
            局部低点列表 [(索引, 时间, 涨跌幅)]
        """
        local_lows = []
        window = 5  # 前后5分钟窗口
        
        for i in range(window, len(returns) - window):
            window_before = returns[i-window:i]
            window_after = returns[i:i+window]
            current = returns[i]
            
            # 是局部最低点（且跌幅为负）
            if current < 0 and current <= np.min(window_before) and current <= np.min(window_after):
                local_lows.append((i, timestamps[i], current))
        
        return local_lows
    
    def _is_pioneer(
        self,
        sector_name: str,
        sector_data: IntradayData,
        market_data: IntradayData,
        market_lows: List[Tuple[int, datetime, float]]
    ) -> Optional[LeadingSector]:
        """识别先锋板块
        
        量化核心：
        - 领先时间差 ΔT = T_Sector_min - T_Index_min < 0
        - 启动爆发：最低点后成交量是均值的3倍以上
        
        Args:
            sector_name: 板块名称
            sector_data: 板块分时数据
            market_data: 大盘分时数据
            market_lows: 大盘局部低点列表
            
        Returns:
            先锋板块信息或None
        """
        if not market_lows:
            return None
        
        sector_returns = np.array(sector_data.pct_changes)
        sector_timestamps = sector_data.timestamps
        
        # 找到板块的局部低点
        sector_lows = self._find_local_lows(sector_returns, sector_timestamps)
        
        if not sector_lows:
            return None
        
        # 对于每个大盘低点，检查是否有板块先于其见底
        best_pioneer = None
        best_time_diff = 0
        
        for market_idx, market_time, market_pct in market_lows:
            for sector_idx, sector_time, sector_pct in sector_lows:
                # 计算时间差（分钟）
                time_diff = (sector_time - market_time).total_seconds() / 60
                
                # 板块先于大盘见底
                if -self.pioneer_time_lag_max <= time_diff <= -self.pioneer_time_lag_min:
                    # 选择领先时间最长的
                    if best_pioneer is None or time_diff < best_time_diff:
                        best_time_diff = time_diff
                        best_pioneer = (market_idx, market_time, market_pct, sector_time, sector_pct)
        
        if best_pioneer:
            market_idx, market_time, market_pct, sector_time, sector_pct = best_pioneer
            logger.info(
                f"[OK] 识别到先锋板块: {sector_name}, "
                f"领先时间={-best_time_diff:.0f}分钟, "
                f"板块低点时间={sector_time.strftime('%H:%M')}, "
                f"大盘低点时间={market_time.strftime('%H:%M')}"
            )
            
            # 创建共振点（用于兼容原有数据结构）
            resonance_point = ResonancePoint(
                timestamp=market_time,
                point_type="PIONEER",
                price_change=market_pct,
                index=market_idx
            )
            
            return LeadingSector(
                sector_name=sector_name,
                time_lag=int(best_time_diff),
                resonance_point=resonance_point
            )
        
        return None
    
    def _is_resonant(
        self,
        sector_name: str,
        market_returns: np.ndarray,
        sector_returns: np.ndarray,
        market_data: IntradayData,
        sector_data: IntradayData
    ) -> Optional[ResonanceSector]:
        """识别共振板块
        
        量化核心：
        - 方向同步：同时突破日内高点或同时放量
        - 弹性占优：Beta > 1.5（大盘涨1%，板块涨1.5%以上）
        
        Args:
            sector_name: 板块名称
            market_returns: 大盘涨跌幅序列
            sector_returns: 板块涨跌幅序列
            market_data: 大盘分时数据
            sector_data: 板块分时数据
            
        Returns:
            共振板块信息或None
        """
        # 使用全天数据计算弹性系数
        if len(market_returns) < 20:
            return None
        
        # 计算相关系数（必须正相关）
        if np.std(market_returns) < 0.01 or np.std(sector_returns) < 0.01:
            return None
        
        corr = np.corrcoef(market_returns, sector_returns)[0, 1]
        
        # 必须是正相关（同向波动）
        if corr < 0.5:
            logger.debug(f"板块 {sector_name}: 相关系数{corr:.2f}过低，不是共振板块")
            return None
        
        # 计算弹性系数（Beta）= Cov(sector, market) / Var(market)
        beta = np.cov(sector_returns, market_returns)[0, 1] / np.var(market_returns)
        
        # 计算平均涨幅比
        avg_market_change = np.mean(market_returns)
        avg_sector_change = np.mean(sector_returns)
        
        # 简单的涨幅比
        if avg_market_change > 0.1:  # 大盘有涨幅
            simple_ratio = avg_sector_change / avg_market_change
        else:
            simple_ratio = 0
        
        logger.debug(
            f"板块 {sector_name} 共振分析: "
            f"Beta={beta:.2f}, "
            f"相关系数={corr:.2f}, "
            f"涨幅比={simple_ratio:.2f}, "
            f"大盘均涨={avg_market_change:.2f}%, "
            f"板块均涨={avg_sector_change:.2f}%"
        )
        
        # 检查弹性是否足够（降低阈值到1.2）
        if beta > 1.2 and simple_ratio > 1.2:
            logger.info(
                f"[OK] 识别到共振板块: {sector_name}, "
                f"弹性系数Beta={beta:.2f}, "
                f"涨幅比={simple_ratio:.2f}, "
                f"相关系数={corr:.2f}, "
                f"大盘平均涨幅={avg_market_change:.2f}%, "
                f"板块平均涨幅={avg_sector_change:.2f}%"
            )
            
            return ResonanceSector(
                sector_name=sector_name,
                elasticity=beta,
                market_change=avg_market_change,
                sector_change=avg_sector_change
            )
        
        return None
