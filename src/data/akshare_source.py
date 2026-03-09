# -*- coding: utf-8 -*-
"""
Akshare数据源

封装akshare接口，作为备用数据源补充缺失数据
"""

import logging
import pandas as pd
from datetime import datetime
from typing import Optional

try:
    import akshare as ak
except ImportError:
    raise ImportError("无法导入akshare，请安装: pip install akshare")


logger = logging.getLogger(__name__)


class AkshareDataSource:
    """Akshare数据源（备用）"""
    
    def __init__(self):
        """初始化akshare数据源"""
        logger.info("AkshareDataSource initialized")
    
    def get_stock_zh_a_hist(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        period: str = "daily",
        adjust: str = "qfq"
    ) -> pd.DataFrame:
        """获取个股历史数据
        
        Args:
            stock_code: 股票代码（如 '000001'）
            start_date: 开始日期，格式 'YYYYMMDD'
            end_date: 结束日期，格式 'YYYYMMDD'
            period: 周期（daily/weekly/monthly）
            adjust: 复权类型（qfq前复权/hfq后复权/空不复权）
            
        Returns:
            包含价格、成交量等的DataFrame
            
        Raises:
            Exception: API调用失败
        """
        logger.info(
            f"获取个股历史数据: stock_code={stock_code}, "
            f"start={start_date}, end={end_date}"
        )
        
        try:
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            if df is None or df.empty:
                logger.warning(f"个股历史数据为空: {stock_code}")
                return pd.DataFrame()
            
            logger.info(f"成功获取个股历史数据: {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"获取个股历史数据失败: {e}")
            raise
    
    def get_stock_board_industry_name_em(self) -> pd.DataFrame:
        """获取行业板块列表
        
        Returns:
            行业板块DataFrame，包含板块代码和名称
            
        Raises:
            Exception: API调用失败
        """
        logger.info("获取行业板块列表")
        
        try:
            df = ak.stock_board_industry_name_em()
            
            if df is None or df.empty:
                logger.warning("行业板块列表为空")
                return pd.DataFrame()
            
            logger.info(f"成功获取行业板块列表: {len(df)} 个板块")
            return df
            
        except Exception as e:
            logger.error(f"获取行业板块列表失败: {e}")
            raise
    
    def get_stock_board_concept_name_em(self) -> pd.DataFrame:
        """获取概念板块列表
        
        Returns:
            概念板块DataFrame，包含板块代码和名称
            
        Raises:
            Exception: API调用失败
        """
        logger.info("获取概念板块列表")
        
        try:
            df = ak.stock_board_concept_name_em()
            
            if df is None or df.empty:
                logger.warning("概念板块列表为空")
                return pd.DataFrame()
            
            logger.info(f"成功获取概念板块列表: {len(df)} 个板块")
            return df
            
        except Exception as e:
            logger.error(f"获取概念板块列表失败: {e}")
            raise
    
    def get_stock_zh_a_minute(
        self,
        stock_code: str,
        period: str = "1",
        adjust: str = "qfq"
    ) -> pd.DataFrame:
        """获取个股分时数据
        
        Args:
            stock_code: 股票代码（如 '000001'）
            period: 周期（1/5/15/30/60分钟）
            adjust: 复权类型（qfq前复权/hfq后复权/空不复权）
            
        Returns:
            分时数据DataFrame
            
        Raises:
            Exception: API调用失败
        """
        logger.info(f"获取个股分时数据: stock_code={stock_code}, period={period}")
        
        try:
            df = ak.stock_zh_a_hist_min_em(
                symbol=stock_code,
                period=period,
                adjust=adjust
            )
            
            if df is None or df.empty:
                logger.warning(f"个股分时数据为空: {stock_code}")
                return pd.DataFrame()
            
            logger.info(f"成功获取个股分时数据: {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"获取个股分时数据失败: {e}")
            raise
    
    def get_stock_board_industry_cons_em(
        self,
        board_name: str
    ) -> pd.DataFrame:
        """获取行业板块成分股
        
        Args:
            board_name: 板块名称
            
        Returns:
            成分股DataFrame
            
        Raises:
            Exception: API调用失败
        """
        logger.info(f"获取行业板块成分股: board_name={board_name}")
        
        try:
            df = ak.stock_board_industry_cons_em(symbol=board_name)
            
            if df is None or df.empty:
                logger.warning(f"行业板块成分股为空: {board_name}")
                return pd.DataFrame()
            
            logger.info(f"成功获取行业板块成分股: {len(df)} 只股票")
            return df
            
        except Exception as e:
            logger.error(f"获取行业板块成分股失败: {e}")
            raise
    
    def get_stock_board_concept_cons_em(
        self,
        board_name: str
    ) -> pd.DataFrame:
        """获取概念板块成分股
        
        Args:
            board_name: 板块名称
            
        Returns:
            成分股DataFrame
            
        Raises:
            Exception: API调用失败
        """
        logger.info(f"获取概念板块成分股: board_name={board_name}")
        
        try:
            df = ak.stock_board_concept_cons_em(symbol=board_name)
            
            if df is None or df.empty:
                logger.warning(f"概念板块成分股为空: {board_name}")
                return pd.DataFrame()
            
            logger.info(f"成功获取概念板块成分股: {len(df)} 只股票")
            return df
            
        except Exception as e:
            logger.error(f"获取概念板块成分股失败: {e}")
            raise
