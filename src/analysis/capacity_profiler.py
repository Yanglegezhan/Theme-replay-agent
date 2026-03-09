# -*- coding: utf-8 -*-
"""
容量分析器

分析题材容量和结构健康度
"""

import logging
from typing import Dict, List

from ..models import TurnoverData, PyramidStructure, CapacityProfile

logger = logging.getLogger(__name__)


class CapacityProfiler:
    """容量分析器

    职责：
    - 分析板块容量类型（大容量主线 vs 中容量题材 vs 小众投机题材）
    - 构建连板梯队金字塔结构
    - 计算结构健康度
    - 评估题材持续性
    """

    def __init__(
        self,
        large_cap_turnover_threshold: float = 15.0,  # 亿元 - 降低阈值
        medium_cap_turnover_threshold: float = 5.0,   # 亿元 - 新增中容量阈值
        health_score_gap_penalty: float = 0.2
    ):
        """初始化容量分析器

        Args:
            large_cap_turnover_threshold: 大容量阈值（核心中军成交额，亿元），默认15亿
            medium_cap_turnover_threshold: 中容量阈值（核心中军成交额，亿元），默认5亿
            health_score_gap_penalty: 健康度断层惩罚系数
        """
        self.large_cap_turnover_threshold = large_cap_turnover_threshold
        self.medium_cap_turnover_threshold = medium_cap_turnover_threshold
        self.health_score_gap_penalty = health_score_gap_penalty
        
    def profile_capacity(
        self,
        sector_name: str,
        turnover_data: TurnoverData,
        consecutive_boards: Dict[int, List[str]]
    ) -> CapacityProfile:
        """分析板块容量和结构
        
        Args:
            sector_name: 板块名称
            turnover_data: 成交额数据
            consecutive_boards: 连板数据（板数 -> 股票列表）
            
        Returns:
            容量画像，包含：
            - capacity_type: 容量类型（LARGE_CAP/SMALL_CAP）
            - sector_turnover: 板块总成交额
            - leading_stock_turnover: 核心中军成交额
            - pyramid_structure: 金字塔结构
            - structure_health: 结构健康度（0-1）
            - sustainability_score: 持续性评分（0-100）
        """
        logger.info(f"开始分析板块容量: {sector_name}")
        
        # 1. 分类容量类型
        capacity_type = self._classify_capacity(turnover_data)
        logger.debug(f"容量类型: {capacity_type}")
        
        # 2. 构建金字塔结构
        pyramid = self._build_pyramid(consecutive_boards)
        logger.debug(f"金字塔结构: {pyramid}")
        
        # 3. 计算结构健康度
        structure_health = self._calculate_health_score(pyramid)
        logger.debug(f"结构健康度: {structure_health:.2f}")
        
        # 4. 计算持续性评分
        sustainability_score = self._calculate_sustainability_score(
            capacity_type,
            structure_health,
            turnover_data
        )
        logger.debug(f"持续性评分: {sustainability_score:.2f}")
        
        # 5. 获取核心中军成交额
        leading_stock_turnover = self._get_leading_stock_turnover(turnover_data)
        
        profile = CapacityProfile(
            capacity_type=capacity_type,
            sector_turnover=turnover_data.sector_turnover,
            leading_stock_turnover=leading_stock_turnover,
            pyramid_structure=pyramid,
            structure_health=structure_health,
            sustainability_score=sustainability_score
        )
        
        logger.info(f"板块容量分析完成: {sector_name}")
        return profile
        
    def _classify_capacity(self, turnover_data: TurnoverData) -> str:
        """分类容量类型

        根据核心中军成交额和市值分布判断：
        - 大容量主线：核心中军成交额 > 15亿，且有大市值股票（>100亿）
        - 中容量题材：核心中军成交额 5-15亿，或有大市值股票参与
        - 小众投机题材：无大市值股票，全靠小盘连板股（<5亿）

        Args:
            turnover_data: 成交额数据

        Returns:
            容量类型：LARGE_CAP / MEDIUM_CAP / SMALL_CAP
        """
        # 获取Top1个股成交额作为核心中军
        if not turnover_data.top5_stocks:
            logger.warning("没有Top5个股数据，默认为小容量")
            return "SMALL_CAP"

        top1_turnover = turnover_data.top5_stocks[0].get("turnover", 0)

        # 判断是否有大市值股票（流通市值 > 100亿）
        has_large_cap = False
        if turnover_data.stock_market_caps:
            for market_cap in turnover_data.stock_market_caps.values():
                if market_cap > 100:  # 100亿
                    has_large_cap = True
                    break

        # 计算板块总成交额相对市场占比（用于辅助判断）
        sector_turnover = turnover_data.sector_turnover

        # 新的三档分类逻辑
        if top1_turnover >= self.large_cap_turnover_threshold and has_large_cap:
            # 大容量：核心中军 > 15亿 且有大市值股票
            return "LARGE_CAP"
        elif top1_turnover >= self.medium_cap_turnover_threshold:
            # 中容量：核心中军 5-15亿
            return "MEDIUM_CAP"
        elif has_large_cap and sector_turnover >= 50:
            # 中容量特殊情况：有大市值股票且板块总成交 >= 50亿
            return "MEDIUM_CAP"
        else:
            # 小容量：核心中军 < 5亿，且无大市值支撑
            return "SMALL_CAP"
            
    def _build_pyramid(
        self,
        consecutive_boards: Dict[int, List[str]]
    ) -> PyramidStructure:
        """构建连板梯队金字塔
        
        统计不同连板层级的个股数量：
        - 5板及以上：高度板
        - 3-4板：中位板
        - 1-2板：低位板
        
        识别断层（缺失的板数）
        
        Args:
            consecutive_boards: 连板数据（板数 -> 股票列表）
            
        Returns:
            金字塔结构
        """
        if not consecutive_boards:
            logger.warning("没有连板数据，返回空金字塔")
            return PyramidStructure(
                board_5_plus=0,
                board_3_to_4=0,
                board_1_to_2=0,
                gaps=[],
                total_stocks=0
            )
        
        # 统计各层级个股数量
        board_5_plus = 0
        board_3_to_4 = 0
        board_1_to_2 = 0
        total_stocks = 0
        
        for board_num, stocks in consecutive_boards.items():
            stock_count = len(stocks)
            total_stocks += stock_count
            
            if board_num >= 5:
                board_5_plus += stock_count
            elif board_num >= 3:
                board_3_to_4 += stock_count
            elif board_num >= 1:
                board_1_to_2 += stock_count
        
        # 识别断层（缺失的板数）
        gaps = self._identify_gaps(consecutive_boards)
        
        return PyramidStructure(
            board_5_plus=board_5_plus,
            board_3_to_4=board_3_to_4,
            board_1_to_2=board_1_to_2,
            gaps=gaps,
            total_stocks=total_stocks
        )
        
    def _identify_gaps(self, consecutive_boards: Dict[int, List[str]]) -> List[int]:
        """识别金字塔断层
        
        断层定义：在最高板和1板之间，缺失的连板层级
        例如：有5板、3板、1板，缺失4板和2板，则断层为[4, 2]
        
        Args:
            consecutive_boards: 连板数据
            
        Returns:
            断层列表（缺失的板数）
        """
        if not consecutive_boards:
            return []
        
        board_nums = sorted(consecutive_boards.keys(), reverse=True)
        if not board_nums:
            return []
        
        max_board = board_nums[0]
        min_board = 1  # 至少要有1板
        
        # 找出所有应该存在的板数
        expected_boards = set(range(min_board, max_board + 1))
        actual_boards = set(board_nums)
        
        # 断层 = 期望存在但实际缺失的板数
        gaps = sorted(expected_boards - actual_boards, reverse=True)
        
        return gaps
        
    def _calculate_health_score(self, pyramid: PyramidStructure) -> float:
        """计算结构健康度
        
        健康度评分规则：
        1. 基础分：1.0（满分）
        2. 断层惩罚：每个断层扣除 health_score_gap_penalty 分
        3. 梯队完整性：各层级都有个股加分
        
        Args:
            pyramid: 金字塔结构
            
        Returns:
            健康度评分（0-1）
        """
        if pyramid.total_stocks == 0:
            return 0.0
        
        # 基础分
        health_score = 1.0
        
        # 断层惩罚
        gap_penalty = len(pyramid.gaps) * self.health_score_gap_penalty
        health_score -= gap_penalty
        
        # 梯队完整性加分
        # 如果三个层级都有个股，说明梯队完整，不额外扣分
        # 如果某个层级缺失，额外扣分
        if pyramid.board_5_plus == 0:
            health_score -= 0.1  # 缺少高度板
        if pyramid.board_3_to_4 == 0:
            health_score -= 0.1  # 缺少中位板
        if pyramid.board_1_to_2 == 0:
            health_score -= 0.1  # 缺少低位板
        
        # 确保分数在 [0, 1] 范围内
        health_score = max(0.0, min(1.0, health_score))
        
        return health_score
        
    def _calculate_sustainability_score(
        self,
        capacity_type: str,
        structure_health: float,
        turnover_data: TurnoverData
    ) -> float:
        """计算持续性评分
        
        持续性评分综合考虑：
        1. 容量类型：大容量主线更持久（60分基础分），小众题材波动大（40分基础分）
        2. 结构健康度：健康度越高，持续性越强（最多加30分）
        3. 成交额：成交额越大，资金关注度越高（最多加10分）
        
        Args:
            capacity_type: 容量类型
            structure_health: 结构健康度
            turnover_data: 成交额数据
            
        Returns:
            持续性评分（0-100）
        """
        # 1. 容量类型基础分
        if capacity_type == "LARGE_CAP":
            base_score = 60.0
        elif capacity_type == "MEDIUM_CAP":
            base_score = 50.0  # 中容量中等基础分
        else:
            base_score = 40.0
        
        # 2. 结构健康度加分（最多30分）
        health_bonus = structure_health * 30.0
        
        # 3. 成交额加分（最多10分）
        # 成交额越大，资金关注度越高
        turnover_bonus = 0.0
        if turnover_data.sector_turnover > 0:
            # 成交额 > 100亿：满分10分
            # 成交额 50-100亿：5-10分
            # 成交额 < 50亿：0-5分
            if turnover_data.sector_turnover >= 100:
                turnover_bonus = 10.0
            elif turnover_data.sector_turnover >= 50:
                turnover_bonus = 5.0 + (turnover_data.sector_turnover - 50) / 50 * 5.0
            else:
                turnover_bonus = turnover_data.sector_turnover / 50 * 5.0
        
        # 总分
        sustainability_score = base_score + health_bonus + turnover_bonus
        
        # 确保分数在 [0, 100] 范围内
        sustainability_score = max(0.0, min(100.0, sustainability_score))
        
        return sustainability_score
        
    def _get_leading_stock_turnover(self, turnover_data: TurnoverData) -> float:
        """获取核心中军成交额
        
        Args:
            turnover_data: 成交额数据
            
        Returns:
            核心中军成交额（亿元）
        """
        if not turnover_data.top5_stocks:
            return 0.0
        
        # 取Top1个股作为核心中军
        return turnover_data.top5_stocks[0].get("turnover", 0.0)
