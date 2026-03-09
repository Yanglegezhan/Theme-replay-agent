# -*- coding: utf-8 -*-
"""
数据源降级管理器

实现主数据源（kaipanla）+ 备用数据源（akshare）的降级逻辑
"""

import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from .kaipanla_source import KaipanlaDataSource
from .akshare_source import AkshareDataSource
from ..models import IntradayData, LimitUpData, TurnoverData


logger = logging.getLogger(__name__)


class DataSourceFallback:
    """数据源降级管理器"""
    
    def __init__(
        self,
        primary_source: Optional[KaipanlaDataSource] = None,
        fallback_source: Optional[AkshareDataSource] = None
    ):
        """初始化数据源降级管理器
        
        Args:
            primary_source: 主数据源（kaipanla）
            fallback_source: 备用数据源（akshare）
        """
        self.primary_source = primary_source or KaipanlaDataSource()
        self.fallback_source = fallback_source or AkshareDataSource()
        self.usage_log = []  # 记录数据源使用情况
        logger.info("DataSourceFallback initialized")
    
    def _log_source_usage(
        self,
        method: str,
        source: str,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """记录数据源使用情况
        
        Args:
            method: 方法名
            source: 数据源（primary/fallback）
            success: 是否成功
            error: 错误信息（如果失败）
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'source': source,
            'success': success,
            'error': error
        }
        self.usage_log.append(log_entry)
        
        if success:
            logger.info(f"{method} 使用 {source} 数据源成功")
        else:
            logger.warning(f"{method} 使用 {source} 数据源失败: {error}")
    
    def get_sector_strength_ndays(
        self,
        end_date: str,
        num_days: int = 7
    ) -> pd.DataFrame:
        """获取N日板块强度数据（带降级）
        
        优先使用kaipanla，失败时尝试从akshare构建
        
        Args:
            end_date: 结束日期，格式 'YYYY-MM-DD'
            num_days: 查询天数，默认7天
            
        Returns:
            DataFrame包含板块强度数据
        """
        method_name = "get_sector_strength_ndays"
        
        # 尝试主数据源
        try:
            result = self.primary_source.get_sector_strength_ndays(
                end_date=end_date,
                num_days=num_days
            )
            
            if result is not None and not result.empty:
                self._log_source_usage(method_name, "primary", True)
                return result
            else:
                self._log_source_usage(
                    method_name, "primary", False, "返回空数据"
                )
        except Exception as e:
            self._log_source_usage(method_name, "primary", False, str(e))
        
        # 主数据源失败，尝试备用数据源
        logger.info(f"{method_name} 主数据源失败，尝试备用数据源")
        
        try:
            # akshare没有直接的板块强度接口，这里返回空DataFrame
            # 实际使用中可以通过其他方式构建
            logger.warning(f"{method_name} 备用数据源不支持此功能")
            self._log_source_usage(
                method_name, "fallback", False, "不支持此功能"
            )
            return pd.DataFrame()
            
        except Exception as e:
            self._log_source_usage(method_name, "fallback", False, str(e))
            return pd.DataFrame()
    
    def get_intraday_data(
        self,
        target: str,
        date: str
    ) -> IntradayData:
        """获取分时数据（带降级）
        
        优先使用kaipanla，失败时使用akshare
        
        Args:
            target: 目标代码
            date: 日期字符串
            
        Returns:
            分时数据
        """
        method_name = "get_intraday_data"
        
        # 尝试主数据源
        try:
            result = self.primary_source.get_intraday_data(
                target=target,
                date=date
            )
            
            if result and result.timestamps:
                self._log_source_usage(method_name, "primary", True)
                return result
            else:
                self._log_source_usage(
                    method_name, "primary", False, "返回空数据"
                )
        except Exception as e:
            self._log_source_usage(method_name, "primary", False, str(e))
        
        # 主数据源失败，尝试备用数据源
        logger.info(f"{method_name} 主数据源失败，尝试备用数据源")
        
        try:
            # 使用akshare获取分时数据
            # 提取股票代码（去掉SH/SZ前缀）
            stock_code = target
            if target.startswith('SH') or target.startswith('SZ'):
                stock_code = target[2:]
            
            df = self.fallback_source.get_stock_zh_a_minute(
                stock_code=stock_code,
                period="1"
            )
            
            if df is None or df.empty:
                self._log_source_usage(
                    method_name, "fallback", False, "返回空数据"
                )
                return IntradayData(
                    target=target,
                    date=date,
                    timestamps=[],
                    prices=[],
                    pct_changes=[]
                )
            
            # 转换为系统标准格式
            result = self._convert_akshare_intraday(df, target, date)
            self._log_source_usage(method_name, "fallback", True)
            return result
            
        except Exception as e:
            self._log_source_usage(method_name, "fallback", False, str(e))
            return IntradayData(
                target=target,
                date=date,
                timestamps=[],
                prices=[],
                pct_changes=[]
            )
    
    def get_limit_up_data(self, date: str) -> LimitUpData:
        """获取涨停数据（带降级）
        
        优先使用kaipanla，失败时返回空数据
        
        Args:
            date: 日期字符串
            
        Returns:
            涨停数据
        """
        method_name = "get_limit_up_data"
        
        # 尝试主数据源
        try:
            result = self.primary_source.get_limit_up_data(date=date)
            self._log_source_usage(method_name, "primary", True)
            return result
            
        except Exception as e:
            self._log_source_usage(method_name, "primary", False, str(e))
        
        # 主数据源失败，备用数据源不支持此功能
        logger.warning(f"{method_name} 主数据源失败，备用数据源不支持此功能")
        self._log_source_usage(
            method_name, "fallback", False, "不支持此功能"
        )
        
        return LimitUpData(
            limit_up_count=0,
            limit_down_count=0,
            blown_limit_up_rate=0.0,
            consecutive_boards={},
            yesterday_limit_up_performance=0.0
        )
    
    def get_sector_turnover_data(
        self,
        sector_code: str,
        date: str
    ) -> TurnoverData:
        """获取板块成交额数据（带降级）
        
        优先使用kaipanla，失败时返回空数据
        
        Args:
            sector_code: 板块代码
            date: 日期字符串
            
        Returns:
            成交额数据
        """
        method_name = "get_sector_turnover_data"
        
        # 尝试主数据源
        try:
            result = self.primary_source.get_sector_turnover_data(
                sector_code=sector_code,
                date=date
            )
            self._log_source_usage(method_name, "primary", True)
            return result
            
        except Exception as e:
            self._log_source_usage(method_name, "primary", False, str(e))
        
        # 主数据源失败，备用数据源不支持此功能
        logger.warning(f"{method_name} 主数据源失败，备用数据源不支持此功能")
        self._log_source_usage(
            method_name, "fallback", False, "不支持此功能"
        )
        
        return TurnoverData(
            sector_turnover=0.0,
            top5_stocks=[],
            stock_market_caps={}
        )
    
    def _convert_akshare_intraday(
        self,
        df: pd.DataFrame,
        target: str,
        date: str
    ) -> IntradayData:
        """将akshare分时数据转换为系统标准格式
        
        Args:
            df: akshare返回的DataFrame
            target: 目标代码
            date: 日期
            
        Returns:
            IntradayData对象
        """
        timestamps = []
        prices = []
        pct_changes = []
        
        # akshare分时数据格式：时间、开盘、收盘、最高、最低、成交量、成交额
        if '时间' in df.columns and '收盘' in df.columns:
            # 只保留当天的数据
            for _, row in df.iterrows():
                time_str = str(row['时间'])
                
                # 解析时间
                try:
                    if len(time_str) == 16:  # YYYY-MM-DD HH:MM
                        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                    elif len(time_str) == 10:  # YYYY-MM-DD
                        continue  # 跳过日期行
                    else:
                        continue
                    
                    # 只保留当天数据
                    if dt.strftime("%Y-%m-%d") != date:
                        continue
                    
                    timestamps.append(dt)
                    prices.append(float(row['收盘']))
                    
                    # 计算涨跌幅（相对开盘价）
                    if len(prices) > 1 and prices[0] > 0:
                        pct_change = (prices[-1] - prices[0]) / prices[0] * 100
                        pct_changes.append(pct_change)
                    else:
                        pct_changes.append(0.0)
                        
                except Exception as e:
                    logger.warning(f"解析时间失败: {time_str}, {e}")
                    continue
        
        return IntradayData(
            target=target,
            date=date,
            timestamps=timestamps,
            prices=prices,
            pct_changes=pct_changes
        )
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """获取数据源使用统计
        
        Returns:
            统计信息字典
        """
        if not self.usage_log:
            return {
                'total_requests': 0,
                'primary_success': 0,
                'primary_failure': 0,
                'fallback_success': 0,
                'fallback_failure': 0
            }
        
        total = len(self.usage_log)
        primary_success = sum(
            1 for log in self.usage_log
            if log['source'] == 'primary' and log['success']
        )
        primary_failure = sum(
            1 for log in self.usage_log
            if log['source'] == 'primary' and not log['success']
        )
        fallback_success = sum(
            1 for log in self.usage_log
            if log['source'] == 'fallback' and log['success']
        )
        fallback_failure = sum(
            1 for log in self.usage_log
            if log['source'] == 'fallback' and not log['success']
        )
        
        return {
            'total_requests': total,
            'primary_success': primary_success,
            'primary_failure': primary_failure,
            'fallback_success': fallback_success,
            'fallback_failure': fallback_failure,
            'primary_success_rate': (
                primary_success / (primary_success + primary_failure)
                if (primary_success + primary_failure) > 0 else 0
            ),
            'fallback_success_rate': (
                fallback_success / (fallback_success + fallback_failure)
                if (fallback_success + fallback_failure) > 0 else 0
            )
        }
