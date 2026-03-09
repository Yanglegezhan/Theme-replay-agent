# -*- coding: utf-8 -*-
"""
历史数据追踪器

管理板块历史排名数据的存储和查询
"""

import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

from ..models import HistoryRecord, SectorStrength


logger = logging.getLogger(__name__)


class HistoryTracker:
    """历史数据追踪器"""
    
    def __init__(self, storage_path: str):
        """初始化历史追踪器
        
        Args:
            storage_path: CSV文件存储路径
        """
        # 修复Windows临时目录权限问题：使用当前目录而不是系统临时目录
        if 'Temp' in storage_path and os.name == 'nt':  # Windows系统
            # 使用当前目录下的临时文件
            filename = os.path.basename(storage_path)
            storage_path = os.path.join('.', 'temp_data', filename)
            logger.info(f"Windows系统检测到临时目录，改用当前目录: {storage_path}")
        
        self.storage_path = storage_path
        
        # 确保存储目录存在
        storage_dir = os.path.dirname(storage_path)
        if storage_dir:
            Path(storage_dir).mkdir(parents=True, exist_ok=True)
        
        # 初始化或加载历史数据
        self._init_storage()
        
        logger.info(f"HistoryTracker initialized with storage: {storage_path}")
    
    def _init_storage(self) -> None:
        """初始化存储文件"""
        if not os.path.exists(self.storage_path):
            # 创建空的DataFrame
            df = pd.DataFrame(columns=[
                '日期',
                '板块名称',
                '板块代码',
                '排名',
                '强度分数'
            ])
            df.to_csv(self.storage_path, index=False, encoding='utf-8-sig')
            logger.info(f"创建新的历史数据文件: {self.storage_path}")
        else:
            logger.info(f"加载现有历史数据文件: {self.storage_path}")
    
    def save_daily_ranking(
        self,
        date: str,
        rankings: List[SectorStrength]
    ) -> None:
        """保存当日板块排名
        
        Args:
            date: 日期字符串，格式 'YYYY-MM-DD'
            rankings: 板块排名列表（前7强）
        """
        logger.info(f"保存当日排名: date={date}, count={len(rankings)}")
        
        try:
            # 读取现有数据
            df = pd.read_csv(self.storage_path, encoding='utf-8-sig')
            
            # 删除当日已有的数据（避免重复）
            df = df[df['日期'] != date]
            
            # 添加新数据
            new_records = []
            for sector in rankings:
                new_records.append({
                    '日期': date,
                    '板块名称': sector.sector_name,
                    '板块代码': sector.sector_code,
                    '排名': sector.rank,
                    '强度分数': sector.strength_score
                })
            
            new_df = pd.DataFrame(new_records)
            df = pd.concat([df, new_df], ignore_index=True)
            
            # 按日期排序
            df = df.sort_values('日期', ascending=False)
            
            # 保存
            df.to_csv(self.storage_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"成功保存当日排名: {len(new_records)} 条记录")
            
        except Exception as e:
            logger.error(f"保存当日排名失败: {e}")
            raise
    
    def get_history(
        self,
        sector_name: str,
        days: int = 7
    ) -> List[HistoryRecord]:
        """查询板块历史排名
        
        Args:
            sector_name: 板块名称
            days: 查询天数
            
        Returns:
            历史记录列表，每项包含：
            - date: 日期
            - rank: 排名（1-7，或None表示未进入前7）
            - strength_score: 强度分数
        """
        logger.info(f"查询历史排名: sector_name={sector_name}, days={days}")
        
        try:
            # 读取数据
            df = pd.read_csv(self.storage_path, encoding='utf-8-sig')
            
            if df.empty:
                logger.info("历史数据为空")
                return []
            
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 筛选板块和日期范围
            sector_df = df[df['板块名称'] == sector_name].copy()
            sector_df['日期'] = pd.to_datetime(sector_df['日期'])
            sector_df = sector_df[
                (sector_df['日期'] >= start_date) &
                (sector_df['日期'] <= end_date)
            ]
            
            # 转换为HistoryRecord列表
            records = []
            for _, row in sector_df.iterrows():
                records.append(HistoryRecord(
                    date=row['日期'].strftime('%Y-%m-%d'),
                    rank=int(row['排名']) if pd.notna(row['排名']) else None,
                    strength_score=int(row['强度分数'])
                ))
            
            # 按日期排序（最新的在前）
            records.sort(key=lambda x: x.date, reverse=True)
            
            logger.info(f"查询到 {len(records)} 条历史记录")
            return records
            
        except Exception as e:
            logger.error(f"查询历史排名失败: {e}")
            return []
    
    def is_new_face(
        self,
        sector_name: str,
        current_date: str
    ) -> bool:
        """判断板块是否为新面孔
        
        Args:
            sector_name: 板块名称
            current_date: 当前日期，格式 'YYYY-MM-DD'
            
        Returns:
            True表示新面孔，False表示老面孔
        """
        logger.info(f"判断新旧面孔: sector_name={sector_name}, date={current_date}")
        
        try:
            # 读取数据
            df = pd.read_csv(self.storage_path, encoding='utf-8-sig')
            
            if df.empty:
                logger.info("历史数据为空，标记为新面孔")
                return True
            
            # 计算7日前的日期
            current = datetime.strptime(current_date, '%Y-%m-%d')
            start_date = current - timedelta(days=7)
            
            # 筛选板块和日期范围（不包括当前日期）
            sector_df = df[df['板块名称'] == sector_name].copy()
            sector_df['日期'] = pd.to_datetime(sector_df['日期'])
            sector_df = sector_df[
                (sector_df['日期'] >= start_date) &
                (sector_df['日期'] < current)
            ]
            
            # 检查是否有进入前7的记录
            top7_records = sector_df[sector_df['排名'] <= 7]
            
            is_new = len(top7_records) == 0
            
            logger.info(
                f"板块 {sector_name} 在过去7日{'未' if is_new else ''}进入过前7强"
            )
            
            return is_new
            
        except Exception as e:
            logger.error(f"判断新旧面孔失败: {e}")
            # 出错时默认为新面孔
            return True
    
    def get_consecutive_days(
        self,
        sector_name: str,
        current_date: str
    ) -> int:
        """获取板块连续进入前7的天数
        
        Args:
            sector_name: 板块名称
            current_date: 当前日期，格式 'YYYY-MM-DD'
            
        Returns:
            连续天数（包括当前日期）
        """
        logger.info(
            f"统计连续天数: sector_name={sector_name}, date={current_date}"
        )
        
        try:
            # 读取数据
            df = pd.read_csv(self.storage_path, encoding='utf-8-sig')
            
            if df.empty:
                logger.info("历史数据为空，连续天数为1")
                return 1
            
            # 筛选板块
            sector_df = df[df['板块名称'] == sector_name].copy()
            sector_df['日期'] = pd.to_datetime(sector_df['日期'])
            
            # 按日期排序（最新的在前）
            sector_df = sector_df.sort_values('日期', ascending=False)
            
            # 从当前日期开始往前统计连续天数
            current = datetime.strptime(current_date, '%Y-%m-%d')
            consecutive_days = 0
            
            for _, row in sector_df.iterrows():
                record_date = row['日期']
                rank = row['排名']
                
                # 检查是否在前7
                if pd.notna(rank) and rank <= 7:
                    # 检查日期是否连续
                    expected_date = current - timedelta(days=consecutive_days)
                    
                    # 允许1天的误差（跳过周末）
                    date_diff = abs((record_date - expected_date).days)
                    
                    if date_diff <= 3:  # 允许跳过周末
                        consecutive_days += 1
                    else:
                        # 日期不连续，停止统计
                        break
                else:
                    # 未进入前7，停止统计
                    break
            
            # 如果没有找到历史记录，说明是第一次进入，返回1
            if consecutive_days == 0:
                consecutive_days = 1
            
            logger.info(f"板块 {sector_name} 连续进入前7强 {consecutive_days} 天")
            
            return consecutive_days
            
        except Exception as e:
            logger.error(f"统计连续天数失败: {e}")
            # 出错时默认为1天
            return 1
    
    def get_all_sectors(self) -> List[str]:
        """获取所有出现过的板块名称
        
        Returns:
            板块名称列表
        """
        try:
            df = pd.read_csv(self.storage_path, encoding='utf-8-sig')
            
            if df.empty:
                return []
            
            sectors = df['板块名称'].unique().tolist()
            logger.info(f"共有 {len(sectors)} 个板块")
            
            return sectors
            
        except Exception as e:
            logger.error(f"获取板块列表失败: {e}")
            return []
    
    def clear_old_data(self, days_to_keep: int = 30) -> None:
        """清理旧数据
        
        Args:
            days_to_keep: 保留的天数
        """
        logger.info(f"清理旧数据: 保留最近 {days_to_keep} 天")
        
        try:
            df = pd.read_csv(self.storage_path, encoding='utf-8-sig')
            
            if df.empty:
                logger.info("历史数据为空，无需清理")
                return
            
            # 计算截止日期
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # 筛选数据
            df['日期'] = pd.to_datetime(df['日期'])
            df = df[df['日期'] >= cutoff_date]
            
            # 保存
            df.to_csv(self.storage_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"清理完成，保留 {len(df)} 条记录")
            
        except Exception as e:
            logger.error(f"清理旧数据失败: {e}")
