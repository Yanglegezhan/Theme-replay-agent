# -*- coding: utf-8 -*-
"""
历史数据收集器

收集板块的历史K线数据、涨停数据和强度数据用于情绪周期分析
"""

import sys
import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# 添加kaipanla_crawler到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../../kaipanla_crawler'))

try:
    from kaipanla_crawler import KaipanlaCrawler
except ImportError:
    raise ImportError("无法导入kaipanla_crawler，请确保kaipanla_crawler目录存在")

logger = logging.getLogger(__name__)


class HistoricalDataCollector:
    """历史数据收集器"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """初始化数据收集器
        
        Args:
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
        """
        self.crawler = KaipanlaCrawler()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        logger.info("HistoricalDataCollector initialized")
    
    def collect_sector_historical_data(
        self,
        sector_code: str,
        sector_name: str,
        end_date: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """收集板块历史数据
        
        Args:
            sector_code: 板块代码
            sector_name: 板块名称
            end_date: 结束日期，格式 'YYYY-MM-DD'
            days: 收集天数，默认7天
            
        Returns:
            历史数据字典，包含：
            - daily_klines: 日K线数据
            - daily_limit_ups: 每日涨停数据
            - daily_strength: 每日强度数据
            - collection_summary: 收集摘要
        """
        logger.info(f"开始收集板块 {sector_name}({sector_code}) 的历史数据")
        
        # 计算日期范围
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        start_dt = end_dt - timedelta(days=days-1)
        start_date = start_dt.strftime('%Y-%m-%d')
        
        result = {
            "sector_code": sector_code,
            "sector_name": sector_name,
            "date_range": [start_date, end_date],
            "daily_klines": [],
            "daily_limit_ups": [],
            "daily_strength": [],
            "collection_summary": {}
        }
        
        try:
            # 1. 收集日K线数据（如果有板块指数）
            kline_data = self._collect_daily_klines(sector_code, start_date, end_date)
            result["daily_klines"] = kline_data
            
            # 2. 收集每日涨停数据
            limit_up_data = self._collect_daily_limit_ups(sector_code, start_date, end_date)
            result["daily_limit_ups"] = limit_up_data
            
            # 3. 收集每日强度数据
            strength_data = self._collect_daily_strength(sector_code, start_date, end_date)
            result["daily_strength"] = strength_data
            
            # 4. 生成收集摘要
            result["collection_summary"] = self._generate_collection_summary(
                kline_data, limit_up_data, strength_data, days
            )
            
            logger.info(f"板块 {sector_name} 历史数据收集完成")
            return result
            
        except Exception as e:
            logger.error(f"收集板块 {sector_name} 历史数据失败: {e}")
            result["collection_summary"] = {
                "success": False,
                "error": str(e),
                "data_quality": "失败"
            }
            return result
    
    def _collect_daily_klines(
        self,
        sector_code: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """收集日K线数据"""
        logger.info(f"收集板块 {sector_code} 的日K线数据")
        
        kline_data = []
        
        try:
            # 生成日期列表
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            current_dt = start_dt
            while current_dt <= end_dt:
                date_str = current_dt.strftime('%Y-%m-%d')
                
                try:
                    # 获取板块分时数据来构造日K线
                    intraday_result = self.crawler.get_sector_intraday(sector_code, date_str)
                    
                    if intraday_result and 'data' in intraday_result:
                        intraday_df = intraday_result['data']
                        
                        if not intraday_df.empty and 'price' in intraday_df.columns:
                            # 从分时数据构造日K线
                            prices = intraday_df['price'].dropna()
                            
                            if len(prices) > 0:
                                daily_kline = {
                                    'date': date_str,
                                    'open': float(prices.iloc[0]),
                                    'high': float(prices.max()),
                                    'low': float(prices.min()),
                                    'close': float(prices.iloc[-1]),
                                    'volume': len(prices),  # 用数据点数量代替成交量
                                    'data_source': 'intraday_derived'
                                }
                                kline_data.append(daily_kline)
                                logger.debug(f"成功获取 {date_str} 的K线数据")
                
                except Exception as e:
                    logger.warning(f"获取 {date_str} K线数据失败: {e}")
                
                current_dt += timedelta(days=1)
            
            logger.info(f"K线数据收集完成: {len(kline_data)} 天")
            return kline_data
            
        except Exception as e:
            logger.error(f"收集K线数据失败: {e}")
            return []
    
    def _collect_daily_limit_ups(
        self,
        sector_code: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """收集每日涨停数据"""
        logger.info(f"收集板块 {sector_code} 的每日涨停数据")
        
        limit_up_data = []
        
        try:
            # 生成日期列表
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            current_dt = start_dt
            while current_dt <= end_dt:
                date_str = current_dt.strftime('%Y-%m-%d')
                
                try:
                    # 获取该日期的板块排名数据
                    sector_ranking = self.crawler.get_sector_ranking(date_str)
                    
                    if sector_ranking and 'sectors' in sector_ranking:
                        # 查找目标板块
                        target_sector = None
                        for sector in sector_ranking['sectors']:
                            if sector.get('sector_code') == sector_code:
                                target_sector = sector
                                break
                        
                        if target_sector:
                            limit_up_count = len(target_sector.get('stocks', []))
                            
                            daily_limit_up = {
                                'date': date_str,
                                'limit_up_count': limit_up_count,
                                'sector_code': sector_code,
                                'stocks': target_sector.get('stocks', []),
                                'data_source': 'sector_ranking'
                            }
                            limit_up_data.append(daily_limit_up)
                            logger.debug(f"成功获取 {date_str} 的涨停数据: {limit_up_count}只")
                        else:
                            # 如果没有找到该板块，说明当天该板块没有涨停股票
                            daily_limit_up = {
                                'date': date_str,
                                'limit_up_count': 0,
                                'sector_code': sector_code,
                                'stocks': [],
                                'data_source': 'sector_ranking'
                            }
                            limit_up_data.append(daily_limit_up)
                            logger.debug(f"{date_str} 该板块无涨停股票")
                
                except Exception as e:
                    logger.warning(f"获取 {date_str} 涨停数据失败: {e}")
                    # 添加空数据点
                    daily_limit_up = {
                        'date': date_str,
                        'limit_up_count': 0,
                        'sector_code': sector_code,
                        'stocks': [],
                        'data_source': 'failed',
                        'error': str(e)
                    }
                    limit_up_data.append(daily_limit_up)
                
                current_dt += timedelta(days=1)
            
            logger.info(f"涨停数据收集完成: {len(limit_up_data)} 天")
            return limit_up_data
            
        except Exception as e:
            logger.error(f"收集涨停数据失败: {e}")
            return []
    
    def _collect_daily_strength(
        self,
        sector_code: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """收集每日强度数据"""
        logger.info(f"收集板块 {sector_code} 的每日强度数据")
        
        strength_data = []
        
        try:
            # 生成日期列表
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            current_dt = start_dt
            while current_dt <= end_dt:
                date_str = current_dt.strftime('%Y-%m-%d')
                
                try:
                    # 获取板块强度数据
                    strength_result = self.crawler.get_sector_strength(sector_code, date_str)
                    
                    if strength_result and strength_result.get('success'):
                        daily_strength = {
                            'date': date_str,
                            'strength': strength_result.get('strength', 0),
                            'sector_code': sector_code,
                            'raw_data': strength_result.get('raw_data', []),
                            'data_source': 'kaipanla_api',
                            'is_historical': strength_result.get('is_historical', True)
                        }
                        strength_data.append(daily_strength)
                        logger.debug(f"成功获取 {date_str} 的强度数据: {strength_result.get('strength', 0)}")
                    else:
                        # 强度数据获取失败
                        daily_strength = {
                            'date': date_str,
                            'strength': 0,
                            'sector_code': sector_code,
                            'raw_data': [],
                            'data_source': 'failed',
                            'error': strength_result.get('error', '未知错误')
                        }
                        strength_data.append(daily_strength)
                        logger.warning(f"获取 {date_str} 强度数据失败")
                
                except Exception as e:
                    logger.warning(f"获取 {date_str} 强度数据失败: {e}")
                    # 添加空数据点
                    daily_strength = {
                        'date': date_str,
                        'strength': 0,
                        'sector_code': sector_code,
                        'raw_data': [],
                        'data_source': 'failed',
                        'error': str(e)
                    }
                    strength_data.append(daily_strength)
                
                current_dt += timedelta(days=1)
            
            logger.info(f"强度数据收集完成: {len(strength_data)} 天")
            return strength_data
            
        except Exception as e:
            logger.error(f"收集强度数据失败: {e}")
            return []
    
    def _generate_collection_summary(
        self,
        kline_data: List[Dict],
        limit_up_data: List[Dict],
        strength_data: List[Dict],
        expected_days: int
    ) -> Dict[str, Any]:
        """生成数据收集摘要"""
        summary = {
            "expected_days": expected_days,
            "collected_days": {
                "klines": len(kline_data),
                "limit_ups": len(limit_up_data),
                "strength": len(strength_data)
            },
            "data_completeness": {},
            "data_quality": "未知",
            "success": True
        }
        
        # 计算数据完整性
        for data_type, count in summary["collected_days"].items():
            completeness = count / expected_days if expected_days > 0 else 0
            summary["data_completeness"][data_type] = {
                "ratio": completeness,
                "percentage": f"{completeness * 100:.1f}%"
            }
        
        # 评估整体数据质量
        avg_completeness = sum(
            summary["data_completeness"][dt]["ratio"] 
            for dt in summary["data_completeness"]
        ) / len(summary["data_completeness"])
        
        if avg_completeness >= 0.9:
            summary["data_quality"] = "优秀"
        elif avg_completeness >= 0.7:
            summary["data_quality"] = "良好"
        elif avg_completeness >= 0.5:
            summary["data_quality"] = "一般"
        else:
            summary["data_quality"] = "较差"
            summary["success"] = False
        
        # 统计有效数据
        valid_limit_ups = sum(1 for item in limit_up_data if item.get('data_source') != 'failed')
        valid_strengths = sum(1 for item in strength_data if item.get('data_source') != 'failed')
        
        summary["valid_data_points"] = {
            "klines": len(kline_data),
            "limit_ups": valid_limit_ups,
            "strength": valid_strengths
        }
        
        # 数据范围统计
        if limit_up_data:
            limit_up_counts = [item.get('limit_up_count', 0) for item in limit_up_data]
            summary["limit_up_stats"] = {
                "max": max(limit_up_counts),
                "min": min(limit_up_counts),
                "avg": sum(limit_up_counts) / len(limit_up_counts),
                "total_days_with_limit_ups": sum(1 for count in limit_up_counts if count > 0)
            }
        
        if strength_data:
            strengths = [item.get('strength', 0) for item in strength_data if item.get('strength', 0) > 0]
            if strengths:
                summary["strength_stats"] = {
                    "max": max(strengths),
                    "min": min(strengths),
                    "avg": sum(strengths) / len(strengths)
                }
        
        return summary
    
    def get_sector_code_by_name(self, sector_name: str) -> Optional[str]:
        """根据板块名称获取板块代码

        Args:
            sector_name: 板块名称

        Returns:
            板块代码，如果找不到返回None

        Note:
            从 data/history/sector_rankings.csv 读取正确的板块代码映射
        """
        import os
        import pandas as pd

        try:
            csv_path = os.path.join(
                os.path.dirname(__file__),
                '../../../data/history/sector_rankings.csv'
            )
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path, encoding='utf-8-sig')
                # 查找匹配的板块名称
                match = df[df['板块名称'] == sector_name]
                if not match.empty:
                    code = str(match.iloc[0]['板块代码'])
                    logger.debug(f"从CSV找到板块代码: {sector_name} -> {code}")
                    return code

            logger.warning(f"在CSV中找不到板块代码: {sector_name}")
            return None

        except Exception as e:
            logger.error(f"读取板块代码映射失败: {e}")
            return None
    
    def batch_collect_sectors_data(
        self,
        sectors: List[Dict[str, str]],
        end_date: str,
        days: int = 7
    ) -> Dict[str, Dict[str, Any]]:
        """批量收集多个板块的历史数据
        
        Args:
            sectors: 板块列表，每个元素包含 {'name': '板块名称', 'code': '板块代码'}
            end_date: 结束日期
            days: 收集天数
            
        Returns:
            以板块名称为key的历史数据字典
        """
        logger.info(f"开始批量收集 {len(sectors)} 个板块的历史数据")
        
        results = {}
        
        for i, sector in enumerate(sectors, 1):
            sector_name = sector.get('name', '')
            sector_code = sector.get('code', '')
            
            if not sector_code:
                sector_code = self.get_sector_code_by_name(sector_name)
            
            if not sector_code:
                logger.warning(f"无法找到板块 {sector_name} 的代码")
                continue
            
            logger.info(f"收集板块 {sector_name} ({i}/{len(sectors)})")
            
            try:
                sector_data = self.collect_sector_historical_data(
                    sector_code, sector_name, end_date, days
                )
                results[sector_name] = sector_data
                
                # 添加延迟避免请求过快
                import time
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"收集板块 {sector_name} 数据失败: {e}")
                results[sector_name] = {
                    "sector_name": sector_name,
                    "sector_code": sector_code,
                    "error": str(e),
                    "collection_summary": {"success": False, "data_quality": "失败"}
                }
        
        logger.info(f"批量收集完成: {len(results)} 个板块")
        return results