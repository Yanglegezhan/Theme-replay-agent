# -*- coding: utf-8 -*-
"""
题材筛选与强度初筛模块

执行题材筛选与强度初筛逻辑，识别当日最强势的核心板块
"""

import logging
import pandas as pd
from typing import List, Tuple, Optional
from dataclasses import dataclass

from ..models import SectorStrength
from ..data import HistoryTracker


logger = logging.getLogger(__name__)


@dataclass
class FilterResult:
    """筛选结果"""
    target_sectors: List[SectorStrength]  # 目标板块列表（7个）
    new_faces: List[str]                  # 新面孔板块列表
    old_faces: List[Tuple[str, int]]      # 老面孔板块列表（板块名, 持续天数）


class SectorFilter:
    """题材筛选器"""
    
    def __init__(self, history_tracker: HistoryTracker):
        """初始化筛选器
        
        Args:
            history_tracker: 历史追踪器
        """
        self.history_tracker = history_tracker
        logger.info("SectorFilter initialized")
    
    def filter_sectors(
        self,
        ndays_data: pd.DataFrame,
        current_date: str,
        high_threshold: int = 8000,
        medium_threshold: int = 2000,
        target_count: int = 7
    ) -> FilterResult:
        """筛选目标板块集合
        
        Args:
            ndays_data: N日板块强度数据（来自get_sector_strength_ndays）
                       包含列：日期, 板块代码, 板块名称, 涨停数, 涨停股票
            current_date: 当前日期，格式 'YYYY-MM-DD'
            high_threshold: 高强度阈值（累计涨停数）
            medium_threshold: 中等强度阈值
            target_count: 目标板块数量
            
        Returns:
            筛选结果，包含：
            - target_sectors: 目标板块列表（7个）
            - new_faces: 新面孔板块列表
            - old_faces: 老面孔板块列表（含持续天数）
        """
        logger.info(
            f"开始筛选板块: date={current_date}, "
            f"high_threshold={high_threshold}, "
            f"medium_threshold={medium_threshold}, "
            f"target_count={target_count}"
        )
        
        # 1. 计算每个板块的强度分数
        sector_scores = self._calculate_all_strength_scores(ndays_data)
        
        logger.info(f"计算得到 {len(sector_scores)} 个板块的强度分数")
        
        # 2. 选择前N强板块
        selected_sectors = self._select_top_sectors(
            sector_scores,
            high_threshold,
            medium_threshold,
            target_count
        )
        
        logger.info(f"选择了 {len(selected_sectors)} 个目标板块")
        
        # 3. 创建SectorStrength对象列表
        target_sectors = []
        for rank, (sector_name, sector_code, score) in enumerate(selected_sectors, 1):
            target_sectors.append(SectorStrength(
                sector_name=sector_name,
                sector_code=sector_code,
                strength_score=score,
                ndays_limit_up=score,  # 强度分数就是N日累计涨停数
                rank=rank
            ))
        
        # 4. 判断新旧面孔
        new_faces = []
        old_faces = []
        
        for sector in target_sectors:
            is_new = self.history_tracker.is_new_face(
                sector.sector_name,
                current_date
            )
            
            if is_new:
                new_faces.append(sector.sector_name)
                logger.info(f"新面孔: {sector.sector_name}")
            else:
                consecutive_days = self.history_tracker.get_consecutive_days(
                    sector.sector_name,
                    current_date
                )
                old_faces.append((sector.sector_name, consecutive_days))
                logger.info(
                    f"老面孔: {sector.sector_name}, 连续{consecutive_days}天"
                )
        
        # 5. 保存当日排名到历史
        self.history_tracker.save_daily_ranking(current_date, target_sectors)
        
        result = FilterResult(
            target_sectors=target_sectors,
            new_faces=new_faces,
            old_faces=old_faces
        )
        
        logger.info(
            f"筛选完成: 目标板块{len(target_sectors)}个, "
            f"新面孔{len(new_faces)}个, 老面孔{len(old_faces)}个"
        )
        
        return result
    
    def _calculate_all_strength_scores(
        self,
        ndays_data: pd.DataFrame
    ) -> List[Tuple[str, str, int]]:
        """计算所有板块的强度分数
        
        Args:
            ndays_data: N日板块强度数据
            
        Returns:
            列表，每项为 (板块名称, 板块代码, 强度分数)
        """
        logger.info("计算所有板块的强度分数")
        
        # 按板块分组，计算累计涨停数
        sector_scores = []
        
        for sector_name in ndays_data['板块名称'].unique():
            # 排除ST板块和其他不需要的板块
            if self._should_exclude_sector(sector_name):
                logger.info(f"排除板块: {sector_name}")
                continue
                
            sector_data = ndays_data[ndays_data['板块名称'] == sector_name]
            
            # 获取板块代码（取第一条记录的代码）
            sector_code = sector_data['板块代码'].iloc[0]
            
            # 计算强度分数（N日累计涨停数）
            score = self._calculate_strength_score(ndays_data, sector_name)
            
            sector_scores.append((sector_name, sector_code, score))
        
        # 按强度分数降序排序
        sector_scores.sort(key=lambda x: x[2], reverse=True)
        
        return sector_scores
    
    def _should_exclude_sector(self, sector_name: str) -> bool:
        """判断是否应该排除该板块
        
        Args:
            sector_name: 板块名称
            
        Returns:
            True表示应该排除，False表示保留
        """
        # 排除ST板块
        if 'ST' in sector_name.upper():
            return True
        
        # 排除其他不需要的板块类型
        exclude_keywords = [
            '退市', '暂停', '停牌', '风险警示', 
            '其他', '未分类', '综合', '多元化'
        ]
        
        for keyword in exclude_keywords:
            if keyword in sector_name:
                return True
        
        return False
    
    def _calculate_strength_score(
        self,
        ndays_data: pd.DataFrame,
        sector_name: str
    ) -> int:
        """获取板块强度分数（直接从API获取，无需计算）
        
        Args:
            ndays_data: N日板块强度数据
            sector_name: 板块名称
            
        Returns:
            强度分数（直接从API获取的真实强度值）
        """
        # 筛选该板块的数据
        sector_data = ndays_data[ndays_data['板块名称'] == sector_name]
        
        if sector_data.empty:
            return 0
        
        # 获取板块代码和最新日期
        sector_code = sector_data['板块代码'].iloc[0]
        latest_date = sector_data['日期'].max()
        
        # 使用新的直接强度获取API
        try:
            from ..data.kaipanla_source import KaipanlaDataSource
            data_source = KaipanlaDataSource()
            
            # 直接获取板块强度（无需计算）
            strength_result = data_source.crawler.get_sector_strength(sector_code, latest_date)
            
            if strength_result['success']:
                strength_score = strength_result['strength']
                logger.info(f"板块 {sector_name} ({sector_code}) 直接获取强度: {strength_score}")
                return int(strength_score)
            else:
                logger.warning(f"直接获取板块 {sector_name} 强度失败: {strength_result['error']}")
        
        except Exception as e:
            logger.warning(f"获取板块 {sector_name} 直接强度失败: {e}")
        
        # 备用方案：使用累计涨停数
        total_limit_up = sector_data['涨停数'].sum()
        logger.info(f"板块 {sector_name} 使用涨停数作为强度: {total_limit_up}")
        return int(total_limit_up)
    
    def _select_top_sectors(
        self,
        sector_scores: List[Tuple[str, str, int]],
        high_threshold: int,
        medium_threshold: int,
        target_count: int
    ) -> List[Tuple[str, str, int]]:
        """选择前N强板块（按规则补齐）
        
        规则：
        1. 优先选择强度分数 > high_threshold 的板块
        2. 如果不足target_count个，从 medium_threshold 到 high_threshold 范围内按分数降序补齐
        3. 如果中等以上强度板块不足target_count个，则取所有中等以上强度的板块
        4. 如果没有中等以上强度的板块，则返回空列表
        
        Args:
            sector_scores: 板块分数列表 [(板块名称, 板块代码, 分数), ...]
            high_threshold: 高强度阈值
            medium_threshold: 中等强度阈值
            target_count: 目标数量
            
        Returns:
            选中的板块列表 [(板块名称, 板块代码, 分数), ...]
        """
        logger.info(
            f"选择前{target_count}强板块: "
            f"high_threshold={high_threshold}, "
            f"medium_threshold={medium_threshold}"
        )
        
        # 1. 选择所有中等以上强度的板块（分数 >= medium_threshold）
        medium_and_above_sectors = [
            (name, code, score)
            for name, code, score in sector_scores
            if score >= medium_threshold
        ]
        
        # 按分数降序排序
        medium_and_above_sectors.sort(key=lambda x: x[2], reverse=True)
        
        logger.info(
            f"中等以上强度板块（>={medium_threshold}）: {len(medium_and_above_sectors)}个"
        )
        
        # 2. 如果没有中等以上强度的板块，返回空列表
        if len(medium_and_above_sectors) == 0:
            logger.warning("没有中等以上强度的板块，返回空列表")
            return []
        
        # 3. 如果中等以上强度板块不足target_count个，返回所有中等以上强度的板块
        if len(medium_and_above_sectors) < target_count:
            logger.info(
                f"中等以上强度板块不足{target_count}个，"
                f"返回所有{len(medium_and_above_sectors)}个中等以上强度板块"
            )
            return medium_and_above_sectors
        
        # 4. 如果中等以上强度板块足够，返回前target_count个
        selected = medium_and_above_sectors[:target_count]
        logger.info(f"中等以上强度板块足够，选择前{target_count}个")
        
        # 统计高强度和中等强度的数量
        high_count = sum(1 for _, _, score in selected if score > high_threshold)
        medium_count = len(selected) - high_count
        logger.info(
            f"选中板块分布: 高强度{high_count}个, 中等强度{medium_count}个"
        )
        
        return selected

