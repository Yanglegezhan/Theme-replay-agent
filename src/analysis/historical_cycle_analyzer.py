# -*- coding: utf-8 -*-
"""
历史周期分析器

基于最近七天的日K线数据和每日涨停家数分析板块情绪周期
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class HistoricalCycleAnalyzer:
    """历史周期分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.cycle_patterns = {
            "启动期": {
                "limit_up_trend": "increasing",  # 涨停数递增
                "price_trend": "rising",         # 价格上涨
                "volume_trend": "increasing",    # 成交量放大
                "volatility": "low_to_medium"    # 波动率从低到中
            },
            "高潮期": {
                "limit_up_trend": "peak",        # 涨停数达到峰值
                "price_trend": "accelerating",   # 价格加速上涨
                "volume_trend": "peak",          # 成交量达到峰值
                "volatility": "high"             # 高波动率
            },
            "分化期": {
                "limit_up_trend": "decreasing",  # 涨停数下降
                "price_trend": "diverging",      # 价格分化
                "volume_trend": "decreasing",    # 成交量萎缩
                "volatility": "very_high"        # 极高波动率
            },
            "修复期": {
                "limit_up_trend": "stabilizing", # 涨停数企稳
                "price_trend": "recovering",     # 价格修复
                "volume_trend": "moderate",      # 成交量适中
                "volatility": "medium"           # 中等波动率
            },
            "退潮期": {
                "limit_up_trend": "low",         # 涨停数很少
                "price_trend": "declining",      # 价格下跌
                "volume_trend": "low",           # 成交量低迷
                "volatility": "low"              # 低波动率
            }
        }
    
    def analyze_sector_cycle(
        self,
        sector_name: str,
        historical_data: Dict[str, Any],
        current_date: str
    ) -> Dict[str, Any]:
        """分析板块情绪周期
        
        Args:
            sector_name: 板块名称
            historical_data: 历史数据，包含：
                - daily_klines: 日K线数据
                - daily_limit_ups: 每日涨停数据
                - daily_strength: 每日强度数据
            current_date: 当前分析日期
            
        Returns:
            周期分析结果
        """
        logger.info(f"开始分析板块 {sector_name} 的历史情绪周期")
        
        try:
            # 1. 提取和验证数据
            kline_data = historical_data.get('daily_klines', [])
            limit_up_data = historical_data.get('daily_limit_ups', [])
            strength_data = historical_data.get('daily_strength', [])
            
            if not kline_data or not limit_up_data:
                logger.warning(f"板块 {sector_name} 历史数据不足")
                return self._create_default_result(sector_name, "数据不足")
            
            # 2. 数据预处理
            processed_data = self._preprocess_data(
                kline_data, limit_up_data, strength_data, current_date
            )
            
            if processed_data is None or processed_data.empty:
                return self._create_default_result(sector_name, "数据预处理失败")
            
            # 3. 趋势分析
            trends = self._analyze_trends(processed_data)
            
            # 4. 周期判断
            cycle_stage = self._determine_cycle_stage(trends)
            
            # 5. 置信度计算
            confidence = self._calculate_confidence(trends, processed_data)
            
            # 6. 生成分析结果
            result = {
                "sector_name": sector_name,
                "analysis_date": current_date,
                "cycle_stage": cycle_stage,
                "confidence": confidence,
                "trends": trends,
                "historical_summary": self._generate_historical_summary(processed_data),
                "key_indicators": self._extract_key_indicators(trends, processed_data),
                "cycle_reasoning": self._generate_cycle_reasoning(cycle_stage, trends),
                "data_quality": self._assess_data_quality(processed_data)
            }
            
            logger.info(f"板块 {sector_name} 周期分析完成: {cycle_stage} (置信度: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"分析板块 {sector_name} 周期失败: {e}")
            return self._create_default_result(sector_name, f"分析失败: {e}")
    
    def _preprocess_data(
        self,
        kline_data: List[Dict],
        limit_up_data: List[Dict],
        strength_data: List[Dict],
        current_date: str
    ) -> Optional[pd.DataFrame]:
        """预处理历史数据"""
        try:
            # 转换为DataFrame
            df_kline = pd.DataFrame(kline_data) if kline_data else pd.DataFrame()
            df_limit = pd.DataFrame(limit_up_data) if limit_up_data else pd.DataFrame()
            df_strength = pd.DataFrame(strength_data) if strength_data else pd.DataFrame()
            
            # 确保日期格式统一
            if not df_kline.empty and 'date' in df_kline.columns:
                df_kline['date'] = pd.to_datetime(df_kline['date'])
            if not df_limit.empty and 'date' in df_limit.columns:
                df_limit['date'] = pd.to_datetime(df_limit['date'])
            if not df_strength.empty and 'date' in df_strength.columns:
                df_strength['date'] = pd.to_datetime(df_strength['date'])
            
            # 合并数据
            if not df_kline.empty and not df_limit.empty:
                merged = pd.merge(df_kline, df_limit, on='date', how='outer')
                if not df_strength.empty:
                    merged = pd.merge(merged, df_strength, on='date', how='outer')
            elif not df_limit.empty:
                # 如果只有涨停数据，也可以进行分析
                merged = df_limit.copy()
                if not df_strength.empty:
                    merged = pd.merge(merged, df_strength, on='date', how='outer')
            else:
                logger.warning("K线和涨停数据都为空")
                return None
            
            # 按日期排序
            merged = merged.sort_values('date')
            
            # 只保留最近7天的数据
            end_date = pd.to_datetime(current_date)
            start_date = end_date - timedelta(days=6)
            merged = merged[
                (merged['date'] >= start_date) & (merged['date'] <= end_date)
            ]
            
            # 数据质量检查
            if len(merged) < 3:
                logger.warning(f"有效数据点不足: {len(merged)}")
                return None
            
            # 填充缺失值
            merged = merged.ffill().fillna(0)
            
            return merged
            
        except Exception as e:
            logger.error(f"数据预处理失败: {e}")
            return None
    
    def _analyze_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析各项指标的趋势"""
        trends = {}
        
        try:
            # 1. 涨停数趋势分析
            if 'limit_up_count' in data.columns:
                limit_ups = data['limit_up_count'].values
                trends['limit_up_trend'] = self._analyze_trend_pattern(limit_ups)
                trends['limit_up_stats'] = {
                    'current': int(limit_ups[-1]) if len(limit_ups) > 0 else 0,
                    'max': int(np.max(limit_ups)) if len(limit_ups) > 0 else 0,
                    'min': int(np.min(limit_ups)) if len(limit_ups) > 0 else 0,
                    'avg': float(np.mean(limit_ups)) if len(limit_ups) > 0 else 0,
                    'trend_slope': self._calculate_trend_slope(limit_ups)
                }
            
            # 2. 价格趋势分析
            if 'close' in data.columns:
                prices = data['close'].values
                trends['price_trend'] = self._analyze_price_trend(prices)
                trends['price_stats'] = {
                    'current': float(prices[-1]) if len(prices) > 0 else 0,
                    'change_pct': self._calculate_total_change(prices),
                    'volatility': float(np.std(prices)) if len(prices) > 1 else 0,
                    'trend_slope': self._calculate_trend_slope(prices)
                }
            
            # 3. 成交量趋势分析
            if 'volume' in data.columns:
                volumes = data['volume'].values
                trends['volume_trend'] = self._analyze_trend_pattern(volumes)
                trends['volume_stats'] = {
                    'current': float(volumes[-1]) if len(volumes) > 0 else 0,
                    'avg': float(np.mean(volumes)) if len(volumes) > 0 else 0,
                    'trend_slope': self._calculate_trend_slope(volumes)
                }
            
            # 4. 强度趋势分析
            if 'strength' in data.columns:
                strengths = data['strength'].values
                trends['strength_trend'] = self._analyze_trend_pattern(strengths)
                trends['strength_stats'] = {
                    'current': float(strengths[-1]) if len(strengths) > 0 else 0,
                    'max': float(np.max(strengths)) if len(strengths) > 0 else 0,
                    'trend_slope': self._calculate_trend_slope(strengths)
                }
            
            # 5. 综合波动率分析
            trends['overall_volatility'] = self._calculate_overall_volatility(data)
            
            return trends
            
        except Exception as e:
            logger.error(f"趋势分析失败: {e}")
            return {}
    
    def _analyze_trend_pattern(self, values: np.ndarray) -> str:
        """分析数值序列的趋势模式"""
        if len(values) < 2:
            return "insufficient_data"
        
        # 计算趋势斜率
        slope = self._calculate_trend_slope(values)
        
        # 计算变化率
        recent_change = (values[-1] - values[0]) / (values[0] + 1e-6)
        
        # 判断趋势模式
        if slope > 0.1 and recent_change > 0.2:
            return "increasing"
        elif slope < -0.1 and recent_change < -0.2:
            return "decreasing"
        elif abs(slope) < 0.05:
            if np.max(values) == values[-1] or np.max(values) == values[-2]:
                return "peak"
            else:
                return "stabilizing"
        else:
            return "fluctuating"
    
    def _analyze_price_trend(self, prices: np.ndarray) -> str:
        """分析价格趋势"""
        if len(prices) < 2:
            return "insufficient_data"
        
        # 计算价格变化
        total_change = (prices[-1] - prices[0]) / prices[0]
        slope = self._calculate_trend_slope(prices)
        
        # 计算加速度（二阶导数）
        if len(prices) >= 3:
            acceleration = self._calculate_acceleration(prices)
        else:
            acceleration = 0
        
        # 判断价格趋势
        if total_change > 0.05 and slope > 0:
            if acceleration > 0:
                return "accelerating"
            else:
                return "rising"
        elif total_change < -0.05 and slope < 0:
            return "declining"
        elif abs(total_change) < 0.02:
            return "sideways"
        else:
            return "diverging"
    
    def _calculate_trend_slope(self, values: np.ndarray) -> float:
        """计算趋势斜率"""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        try:
            slope, _ = np.polyfit(x, values, 1)
            return float(slope)
        except:
            return 0.0
    
    def _calculate_acceleration(self, values: np.ndarray) -> float:
        """计算加速度（二阶导数）"""
        if len(values) < 3:
            return 0.0
        
        # 计算一阶导数
        first_derivative = np.diff(values)
        # 计算二阶导数
        second_derivative = np.diff(first_derivative)
        
        return float(np.mean(second_derivative))
    
    def _calculate_total_change(self, values: np.ndarray) -> float:
        """计算总变化率"""
        if len(values) < 2 or values[0] == 0:
            return 0.0
        
        return float((values[-1] - values[0]) / values[0])
    
    def _calculate_overall_volatility(self, data: pd.DataFrame) -> str:
        """计算整体波动率等级"""
        volatilities = []
        
        # 价格波动率
        if 'close' in data.columns:
            price_vol = np.std(data['close']) / np.mean(data['close'])
            volatilities.append(price_vol)
        
        # 涨停数波动率
        if 'limit_up_count' in data.columns:
            limit_vol = np.std(data['limit_up_count']) / (np.mean(data['limit_up_count']) + 1)
            volatilities.append(limit_vol)
        
        if not volatilities:
            return "unknown"
        
        avg_volatility = np.mean(volatilities)
        
        if avg_volatility > 0.3:
            return "very_high"
        elif avg_volatility > 0.2:
            return "high"
        elif avg_volatility > 0.1:
            return "medium"
        else:
            return "low"
    
    def _determine_cycle_stage(self, trends: Dict[str, Any]) -> str:
        """根据趋势分析确定情绪周期阶段"""
        if not trends:
            return "未知"
        
        # 提取关键趋势指标
        limit_up_trend = trends.get('limit_up_trend', 'unknown')
        price_trend = trends.get('price_trend', 'unknown')
        volume_trend = trends.get('volume_trend', 'unknown')
        volatility = trends.get('overall_volatility', 'unknown')
        
        # 获取统计数据
        limit_up_stats = trends.get('limit_up_stats', {})
        price_stats = trends.get('price_stats', {})
        
        current_limit_ups = limit_up_stats.get('current', 0)
        max_limit_ups = limit_up_stats.get('max', 0)
        price_change = price_stats.get('change_pct', 0)
        
        # 周期判断逻辑
        scores = {
            "启动期": 0,
            "高潮期": 0,
            "分化期": 0,
            "修复期": 0,
            "退潮期": 0
        }
        
        # 1. 启动期特征
        if limit_up_trend == "increasing" and price_trend in ["rising", "accelerating"]:
            scores["启动期"] += 3
        if volume_trend == "increasing":
            scores["启动期"] += 2
        if volatility in ["low", "medium"]:
            scores["启动期"] += 1
        if current_limit_ups > 0 and current_limit_ups < max_limit_ups * 0.7:
            scores["启动期"] += 1
        
        # 2. 高潮期特征
        if limit_up_trend == "peak" or current_limit_ups == max_limit_ups:
            scores["高潮期"] += 3
        if price_trend == "accelerating":
            scores["高潮期"] += 2
        if volume_trend == "peak":
            scores["高潮期"] += 2
        if volatility == "high":
            scores["高潮期"] += 1
        if current_limit_ups >= 5:  # 涨停数较多
            scores["高潮期"] += 1
        
        # 3. 分化期特征
        if limit_up_trend == "decreasing" and current_limit_ups < max_limit_ups * 0.5:
            scores["分化期"] += 3
        if price_trend == "diverging":
            scores["分化期"] += 2
        if volume_trend == "decreasing":
            scores["分化期"] += 2
        if volatility == "very_high":
            scores["分化期"] += 2
        if price_change < -0.05:  # 价格下跌
            scores["分化期"] += 1
        
        # 4. 修复期特征
        if limit_up_trend == "stabilizing" and price_trend == "recovering":
            scores["修复期"] += 3
        if volume_trend in ["moderate", "stabilizing"]:
            scores["修复期"] += 2
        if volatility == "medium":
            scores["修复期"] += 1
        if 0 < current_limit_ups < max_limit_ups * 0.6:
            scores["修复期"] += 1
        
        # 5. 退潮期特征
        if current_limit_ups == 0 or (current_limit_ups < max_limit_ups * 0.3 and limit_up_trend == "decreasing"):
            scores["退潮期"] += 3
        if price_trend == "declining":
            scores["退潮期"] += 2
        if volume_trend == "low":
            scores["退潮期"] += 2
        if volatility == "low":
            scores["退潮期"] += 1
        if price_change < -0.1:  # 大幅下跌
            scores["退潮期"] += 1
        
        # 选择得分最高的阶段
        best_stage = max(scores.items(), key=lambda x: x[1])
        
        # 如果最高分数太低，返回未知
        if best_stage[1] < 2:
            return "未明确"
        
        return best_stage[0]
    
    def _calculate_confidence(self, trends: Dict[str, Any], data: pd.DataFrame) -> float:
        """计算周期判断的置信度"""
        confidence_factors = []
        
        # 1. 数据完整性
        data_completeness = len(data) / 7.0  # 期望7天数据
        confidence_factors.append(min(data_completeness, 1.0))
        
        # 2. 趋势一致性
        trend_consistency = self._calculate_trend_consistency(trends)
        confidence_factors.append(trend_consistency)
        
        # 3. 指标强度
        indicator_strength = self._calculate_indicator_strength(trends)
        confidence_factors.append(indicator_strength)
        
        # 4. 数据质量
        data_quality = self._assess_data_quality(data)
        quality_score = data_quality.get('overall_score', 0.5)
        confidence_factors.append(quality_score)
        
        # 计算加权平均置信度
        weights = [0.2, 0.3, 0.3, 0.2]
        confidence = sum(f * w for f, w in zip(confidence_factors, weights))
        
        return min(max(confidence, 0.0), 1.0)
    
    def _calculate_trend_consistency(self, trends: Dict[str, Any]) -> float:
        """计算趋势一致性"""
        # 检查各个趋势指标是否相互支持
        limit_up_trend = trends.get('limit_up_trend', 'unknown')
        price_trend = trends.get('price_trend', 'unknown')
        volume_trend = trends.get('volume_trend', 'unknown')
        
        consistency_score = 0.0
        total_checks = 0
        
        # 上升趋势一致性
        if limit_up_trend == "increasing":
            total_checks += 1
            if price_trend in ["rising", "accelerating"]:
                consistency_score += 1
        
        # 下降趋势一致性
        if limit_up_trend == "decreasing":
            total_checks += 1
            if price_trend in ["declining", "diverging"]:
                consistency_score += 1
        
        # 成交量与价格一致性
        if price_trend in ["rising", "accelerating"]:
            total_checks += 1
            if volume_trend in ["increasing", "peak"]:
                consistency_score += 1
        
        return consistency_score / max(total_checks, 1)
    
    def _calculate_indicator_strength(self, trends: Dict[str, Any]) -> float:
        """计算指标强度"""
        strength_score = 0.0
        
        # 涨停数强度
        limit_up_stats = trends.get('limit_up_stats', {})
        current_limit_ups = limit_up_stats.get('current', 0)
        max_limit_ups = limit_up_stats.get('max', 1)
        
        if max_limit_ups > 0:
            limit_up_strength = current_limit_ups / max_limit_ups
            strength_score += limit_up_strength * 0.4
        
        # 价格变化强度
        price_stats = trends.get('price_stats', {})
        price_change = abs(price_stats.get('change_pct', 0))
        price_strength = min(price_change / 0.1, 1.0)  # 10%变化为满分
        strength_score += price_strength * 0.3
        
        # 趋势斜率强度
        limit_up_slope = abs(limit_up_stats.get('trend_slope', 0))
        slope_strength = min(limit_up_slope / 1.0, 1.0)  # 斜率1为满分
        strength_score += slope_strength * 0.3
        
        return min(strength_score, 1.0)
    
    def _generate_historical_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """生成历史数据摘要"""
        summary = {
            "data_period": f"{data['date'].min().strftime('%Y-%m-%d')} 至 {data['date'].max().strftime('%Y-%m-%d')}",
            "data_points": len(data),
            "trading_days": len(data)
        }
        
        # 涨停数摘要
        if 'limit_up_count' in data.columns:
            limit_ups = data['limit_up_count']
            summary['limit_up_summary'] = {
                "total_days_with_limit_ups": int((limit_ups > 0).sum()),
                "max_single_day": int(limit_ups.max()),
                "avg_per_day": float(limit_ups.mean()),
                "trend": "上升" if limit_ups.iloc[-1] > limit_ups.iloc[0] else "下降"
            }
        
        # 价格摘要
        if 'close' in data.columns:
            prices = data['close']
            summary['price_summary'] = {
                "total_return": float((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0] * 100),
                "max_price": float(prices.max()),
                "min_price": float(prices.min()),
                "volatility": float(prices.std() / prices.mean() * 100)
            }
        
        return summary
    
    def _extract_key_indicators(self, trends: Dict[str, Any], data: pd.DataFrame) -> List[str]:
        """提取关键指标"""
        indicators = []
        
        # 涨停数指标
        limit_up_stats = trends.get('limit_up_stats', {})
        current_limit_ups = limit_up_stats.get('current', 0)
        max_limit_ups = limit_up_stats.get('max', 0)
        
        indicators.append(f"当前涨停数: {current_limit_ups}只")
        indicators.append(f"7日最高涨停数: {max_limit_ups}只")
        
        # 价格指标
        price_stats = trends.get('price_stats', {})
        price_change = price_stats.get('change_pct', 0)
        indicators.append(f"7日累计涨跌幅: {price_change:+.2f}%")
        
        # 趋势指标
        limit_up_trend = trends.get('limit_up_trend', 'unknown')
        price_trend = trends.get('price_trend', 'unknown')
        indicators.append(f"涨停数趋势: {self._translate_trend(limit_up_trend)}")
        indicators.append(f"价格趋势: {self._translate_trend(price_trend)}")
        
        # 波动率指标
        volatility = trends.get('overall_volatility', 'unknown')
        indicators.append(f"整体波动率: {self._translate_volatility(volatility)}")
        
        return indicators
    
    def _generate_cycle_reasoning(self, cycle_stage: str, trends: Dict[str, Any]) -> str:
        """生成周期判断理由"""
        reasoning_parts = []
        
        # 基础判断
        reasoning_parts.append(f"基于最近7天的日K线和涨停数据分析，判断该板块处于{cycle_stage}。")
        
        # 具体理由
        limit_up_stats = trends.get('limit_up_stats', {})
        price_stats = trends.get('price_stats', {})
        
        current_limit_ups = limit_up_stats.get('current', 0)
        max_limit_ups = limit_up_stats.get('max', 0)
        price_change = price_stats.get('change_pct', 0)
        limit_up_trend = trends.get('limit_up_trend', 'unknown')
        
        if cycle_stage == "启动期":
            reasoning_parts.append(f"涨停数呈{self._translate_trend(limit_up_trend)}趋势，当前{current_limit_ups}只，显示资金开始关注。")
            if price_change > 0:
                reasoning_parts.append(f"价格上涨{price_change:.2f}%，板块开始启动。")
        
        elif cycle_stage == "高潮期":
            reasoning_parts.append(f"涨停数达到峰值{max_limit_ups}只，市场情绪高涨。")
            reasoning_parts.append(f"价格表现强势，资金大量涌入。")
        
        elif cycle_stage == "分化期":
            reasoning_parts.append(f"涨停数从峰值{max_limit_ups}只下降至{current_limit_ups}只，市场开始分化。")
            if price_change < 0:
                reasoning_parts.append(f"价格回调{abs(price_change):.2f}%，前排股票开始分歧。")
        
        elif cycle_stage == "修复期":
            reasoning_parts.append(f"经历分化后，涨停数企稳在{current_limit_ups}只，市场情绪修复。")
            reasoning_parts.append(f"价格走势趋于稳定，资金重新布局。")
        
        elif cycle_stage == "退潮期":
            reasoning_parts.append(f"涨停数降至{current_limit_ups}只，市场关注度大幅下降。")
            if price_change < -0.05:
                reasoning_parts.append(f"价格下跌{abs(price_change):.2f}%，资金撤离明显。")
        
        return " ".join(reasoning_parts)
    
    def _assess_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """评估数据质量"""
        quality_metrics = {}
        
        # 数据完整性
        expected_days = 7
        actual_days = len(data)
        completeness = actual_days / expected_days
        quality_metrics['completeness'] = completeness
        
        # 数据连续性
        if len(data) > 1:
            date_gaps = (data['date'].diff().dt.days > 1).sum()
            continuity = 1.0 - (date_gaps / len(data))
        else:
            continuity = 1.0
        quality_metrics['continuity'] = continuity
        
        # 数据有效性
        valid_data_ratio = 1.0
        if 'limit_up_count' in data.columns:
            valid_limit_ups = (data['limit_up_count'] >= 0).sum() / len(data)
            valid_data_ratio *= valid_limit_ups
        
        if 'close' in data.columns:
            valid_prices = (data['close'] > 0).sum() / len(data)
            valid_data_ratio *= valid_prices
        
        quality_metrics['validity'] = valid_data_ratio
        
        # 综合评分
        overall_score = (completeness * 0.4 + continuity * 0.3 + valid_data_ratio * 0.3)
        quality_metrics['overall_score'] = overall_score
        
        # 质量等级
        if overall_score >= 0.9:
            quality_metrics['grade'] = "优秀"
        elif overall_score >= 0.7:
            quality_metrics['grade'] = "良好"
        elif overall_score >= 0.5:
            quality_metrics['grade'] = "一般"
        else:
            quality_metrics['grade'] = "较差"
        
        return quality_metrics
    
    def _translate_trend(self, trend: str) -> str:
        """翻译趋势描述"""
        translations = {
            "increasing": "上升",
            "decreasing": "下降",
            "peak": "峰值",
            "stabilizing": "企稳",
            "fluctuating": "波动",
            "rising": "上涨",
            "declining": "下跌",
            "accelerating": "加速上涨",
            "diverging": "分化",
            "recovering": "修复",
            "sideways": "横盘"
        }
        return translations.get(trend, trend)
    
    def _translate_volatility(self, volatility: str) -> str:
        """翻译波动率描述"""
        translations = {
            "very_high": "极高",
            "high": "高",
            "medium": "中等",
            "low": "低"
        }
        return translations.get(volatility, volatility)
    
    def _create_default_result(self, sector_name: str, reason: str) -> Dict[str, Any]:
        """创建默认结果"""
        return {
            "sector_name": sector_name,
            "analysis_date": datetime.now().strftime('%Y-%m-%d'),
            "cycle_stage": "未知",
            "confidence": 0.0,
            "trends": {},
            "historical_summary": {},
            "key_indicators": [f"分析失败: {reason}"],
            "cycle_reasoning": f"由于{reason}，无法进行周期分析。",
            "data_quality": {"grade": "无数据", "overall_score": 0.0}
        }