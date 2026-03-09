# -*- coding: utf-8 -*-
"""
提示词引擎

管理和生成各类分析提示词
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

from ..models.data_models import AnalysisContext


class PromptEngine:
    """提示词引擎，管理和生成各类分析提示词"""
    
    def __init__(self, template_dir: Optional[str] = None):
        """初始化提示词引擎
        
        Args:
            template_dir: 提示词模板目录（可选，默认为项目根目录下的prompts文件夹）
        """
        if template_dir is None:
            # 默认使用项目根目录下的prompts文件夹
            # __file__ -> src/llm/prompt_engine.py
            # parent -> src/llm
            # parent -> src
            # parent -> Theme_repay_agent
            # parent / "prompts" -> Theme_repay_agent/prompts
            self.template_dir = Path(__file__).parent.parent.parent / "prompts"
        else:
            self.template_dir = Path(template_dir)
        self._template_cache: Dict[str, str] = {}
        
    def load_template(self, template_name: str) -> str:
        """加载提示词模板
        
        Args:
            template_name: 模板名称（不含扩展名）
            
        Returns:
            模板内容
            
        Raises:
            FileNotFoundError: 模板文件不存在
        """
        # 检查缓存
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        # 构建模板文件路径
        template_path = self.template_dir / f"{template_name}.md"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        # 读取模板内容
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # 缓存模板
        self._template_cache[template_name] = template_content
        
        return template_content
    
    def render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """渲染提示词模板（填充变量）
        
        Args:
            template: 模板内容
            variables: 变量字典
            
        Returns:
            渲染后的提示词
        """
        rendered = template
        
        # 替换所有变量
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            # 将值转换为字符串
            str_value = str(value) if not isinstance(value, str) else value
            rendered = rendered.replace(placeholder, str_value)
        
        return rendered
    
    def build_market_intent_prompt(self, context: AnalysisContext) -> str:
        """构建资金意图分析提示词
        
        提示词结构：
        1. 角色设定：十年经验游资操盘手
        2. 任务描述：分析市场资金真实意图
        3. 数据输入：结构化的市场数据
        4. 分析维度：资金流向、板块轮动、情绪判断
        5. 输出格式：JSON结构化输出
        
        Args:
            context: 分析上下文
            
        Returns:
            渲染后的提示词
        """
        # 加载模板
        template = self.load_template("market_intent")
        
        # 格式化市场数据
        market_data = self._format_market_data(context)
        
        # 渲染模板
        variables = {
            "date": context.date,
            "market_data": market_data
        }
        
        return self.render_template(template, variables)
    
    def build_emotion_cycle_prompt(
        self,
        sector_name: str,
        context: AnalysisContext,
        limit_up_data: Optional[Dict[str, Any]] = None,
        intraday_data: Optional[Dict[str, Any]] = None,
        historical_data: Optional[Dict[str, Any]] = None,
        historical_cycle_analysis: Optional[Dict[str, Any]] = None
    ) -> str:
        """构建情绪周期分析提示词
        
        提示词结构：
        1. 角色设定：资深情绪周期分析师
        2. 任务描述：判定板块所处的情绪周期阶段
        3. 理论背景：情绪周期理论（启动期、高潮期、分化期、修复期、退潮期）
        4. 历史数据分析方法：基于7天历史数据的分析方法
        5. 数据输入：板块涨停数据、连板梯队、炸板率、分时走势、历史表现、历史周期分析
        6. 分析维度：涨停家数变化、连板高度、市场情绪、资金参与度、历史趋势分析
        7. 输出格式：JSON结构化输出（阶段、置信度、理由、风险机会等级）
        
        Args:
            sector_name: 板块名称
            context: 分析上下文
            limit_up_data: 涨停数据（可选）
            intraday_data: 分时数据（可选）
            historical_data: 历史数据（可选）
            historical_cycle_analysis: 历史周期分析结果（可选）
            
        Returns:
            渲染后的提示词
        """
        # 加载模板
        template = self.load_template("emotion_cycle")
        
        # 使用ContextBuilder格式化情绪周期专用数据
        from .context_builder import ContextBuilder
        context_builder = ContextBuilder()
        
        sector_data = context_builder.format_emotion_cycle_data(
            sector_name=sector_name,
            context=context,
            limit_up_data=limit_up_data,
            intraday_data=intraday_data,
            historical_data=historical_data
        )
        
        # 如果有历史周期分析结果，添加到数据中
        if historical_cycle_analysis:
            sector_data += "\n\n" + self._format_historical_cycle_analysis(historical_cycle_analysis)
        
        # 渲染模板
        variables = {
            "sector_name": sector_name,
            "date": context.date,
            "sector_data": sector_data
        }
        
        return self.render_template(template, variables)
    
    def build_sustainability_prompt(
        self,
        sector_name: str,
        context: AnalysisContext,
        emotion_cycle: Optional[Any] = None,
        capacity_profile: Optional[Any] = None
    ) -> str:
        """构建题材持续性评估提示词
        
        提示词结构：
        1. 角色设定：资深题材研究员
        2. 任务描述：评估题材持续性
        3. 数据输入：板块详细数据（包含情绪周期和容量结构）
        4. 分析维度：情绪周期、容量结构、历史表现
        5. 输出格式：评分+理由
        
        Args:
            sector_name: 板块名称
            context: 分析上下文
            emotion_cycle: 情绪周期分析结果（可选）
            capacity_profile: 容量画像（可选）
            
        Returns:
            渲染后的提示词
        """
        # 加载模板
        template = self.load_template("sustainability")
        
        # 格式化板块数据（包含情绪周期和容量数据）
        sector_data = self._format_sector_data_with_analysis(
            sector_name,
            context,
            emotion_cycle,
            capacity_profile
        )
        
        # 渲染模板
        variables = {
            "sector_name": sector_name,
            "sector_data": sector_data
        }
        
        return self.render_template(template, variables)
    
    def build_trading_advice_prompt(
        self,
        sector_name: str,
        context: AnalysisContext
    ) -> str:
        """构建操作建议生成提示词
        
        提示词结构：
        1. 角色设定：实战派交易员
        2. 任务描述：给出具体操作建议
        3. 数据输入：综合分析结果
        4. 分析维度：风险收益比、时机选择、仓位管理
        5. 输出格式：结构化建议
        
        Args:
            sector_name: 板块名称
            context: 分析上下文
            
        Returns:
            渲染后的提示词
        """
        # 加载模板
        template = self.load_template("trading_advice")
        
        # 格式化综合分析摘要
        analysis_summary = self._format_analysis_summary(sector_name, context)
        
        # 渲染模板
        variables = {
            "sector_name": sector_name,
            "analysis_summary": analysis_summary
        }
        
        return self.render_template(template, variables)
    
    def _format_market_data(self, context: AnalysisContext) -> str:
        """格式化市场数据为文本
        
        Args:
            context: 分析上下文
            
        Returns:
            格式化的市场数据文本
        """
        lines = []
        
        # 市场概览
        lines.append("## 市场概览")
        market_overview = context.market_overview
        if market_overview:
            for key, value in market_overview.items():
                lines.append(f"- {key}: {value}")
        
        # 目标板块
        lines.append("\n## 目标板块（前7强）")
        lines.append("| 排名 | 板块名称 | 强度分数 | 涨停数 | 新旧 |")
        lines.append("|------|---------|---------|--------|------|")
        
        for sector in context.target_sectors:
            rank = sector.get('rank', '-')
            name = sector.get('sector_name', '-')
            score = sector.get('strength_score', '-')
            limit_up = sector.get('limit_up_count', '-')
            is_new = "新" if sector.get('is_new_face', False) else f"老{sector.get('consecutive_days', 0)}天"
            lines.append(f"| {rank} | {name} | {score} | {limit_up} | {is_new} |")
        
        # 板块关系
        if context.sector_relationships:
            lines.append("\n## 盘面联动分析")
            relationships = context.sector_relationships
            
            if 'leading_sectors' in relationships:
                leading = relationships['leading_sectors']
                if leading:
                    lines.append(f"- 先锋板块：{', '.join(leading)}")
            
            if 'resonance_sectors' in relationships:
                resonance = relationships['resonance_sectors']
                if resonance:
                    lines.append(f"- 共振板块：{', '.join(resonance)}")
            
            if 'divergence_sectors' in relationships:
                divergence = relationships['divergence_sectors']
                if divergence:
                    lines.append(f"- 分离板块：{', '.join(divergence)}")
            
            if 'seesaw_effects' in relationships:
                seesaw = relationships['seesaw_effects']
                if seesaw:
                    lines.append(f"- 跷跷板效应：{', '.join(seesaw)}")
        
        return "\n".join(lines)
    
    def _format_sector_data(self, sector_name: str, context: AnalysisContext) -> str:
        """格式化板块数据为文本
        
        Args:
            sector_name: 板块名称
            context: 分析上下文
            
        Returns:
            格式化的板块数据文本
        """
        lines = []
        
        # 查找目标板块数据
        sector_info = None
        for sector in context.target_sectors:
            if sector.get('sector_name') == sector_name:
                sector_info = sector
                break
        
        if not sector_info:
            return f"未找到板块 {sector_name} 的数据"
        
        # 基本信息
        lines.append(f"## {sector_name} 板块数据")
        lines.append(f"- 强度分数：{sector_info.get('strength_score', '-')}")
        lines.append(f"- 排名：{sector_info.get('rank', '-')}")
        lines.append(f"- 涨停数：{sector_info.get('limit_up_count', '-')}")
        
        is_new = sector_info.get('is_new_face', False)
        if is_new:
            lines.append("- 新旧：新面孔")
        else:
            days = sector_info.get('consecutive_days', 0)
            lines.append(f"- 新旧：老面孔（连续{days}天）")
        
        # 成交额数据
        if 'turnover' in sector_info:
            turnover = sector_info['turnover']
            lines.append(f"\n### 成交额")
            lines.append(f"- 板块总成交额：{turnover}亿元")
        
        # 连板梯队
        if 'consecutive_boards' in sector_info:
            boards = sector_info['consecutive_boards']
            lines.append(f"\n### 连板梯队")
            for board_num, stocks in sorted(boards.items(), reverse=True):
                lines.append(f"- {board_num}板：{len(stocks)}只")
        
        # 分时走势描述
        if 'intraday_summary' in sector_info:
            lines.append(f"\n### 分时走势")
            lines.append(sector_info['intraday_summary'])
        
        # 历史表现
        if 'historical_performance' in sector_info:
            lines.append(f"\n### 历史表现")
            lines.append(sector_info['historical_performance'])
        
        return "\n".join(lines)
    
    def _format_analysis_summary(self, sector_name: str, context: AnalysisContext) -> str:
        """格式化综合分析摘要
        
        Args:
            sector_name: 板块名称
            context: 分析上下文
            
        Returns:
            格式化的分析摘要文本
        """
        lines = []
        
        # 查找目标板块数据
        sector_info = None
        for sector in context.target_sectors:
            if sector.get('sector_name') == sector_name:
                sector_info = sector
                break
        
        if not sector_info:
            return f"未找到板块 {sector_name} 的分析数据"
        
        lines.append(f"## {sector_name} 综合分析")
        
        # 板块基本信息
        lines.append(f"\n### 基本信息")
        lines.append(f"- 强度分数：{sector_info.get('strength_score', '-')}")
        lines.append(f"- 排名：{sector_info.get('rank', '-')}")
        
        # 盘面联动
        if 'correlation_type' in sector_info:
            lines.append(f"\n### 盘面联动")
            lines.append(f"- 类型：{sector_info['correlation_type']}")
        
        # 情绪周期
        if 'emotion_cycle' in sector_info:
            lines.append(f"\n### 情绪周期")
            emotion = sector_info['emotion_cycle']
            lines.append(f"- 阶段：{emotion.get('stage', '-')}")
            lines.append(f"- 风险等级：{emotion.get('risk_level', '-')}")
            lines.append(f"- 机会等级：{emotion.get('opportunity_level', '-')}")
        
        # 容量结构
        if 'capacity_profile' in sector_info:
            lines.append(f"\n### 容量结构")
            capacity = sector_info['capacity_profile']
            lines.append(f"- 容量类型：{capacity.get('capacity_type', '-')}")
            lines.append(f"- 结构健康度：{capacity.get('structure_health', '-')}")
        
        # 持续性评估
        if 'sustainability' in sector_info:
            lines.append(f"\n### 持续性评估")
            sustainability = sector_info['sustainability']
            lines.append(f"- 评分：{sustainability.get('sustainability_score', '-')}")
            lines.append(f"- 预期持续时间：{sustainability.get('time_horizon', '-')}")
        
        return "\n".join(lines)
    
    def _format_historical_cycle_analysis(self, historical_cycle_analysis: Dict[str, Any]) -> str:
        """格式化历史周期分析结果为文本
        
        Args:
            historical_cycle_analysis: 历史周期分析结果
            
        Returns:
            格式化的历史周期分析文本
        """
        lines = []
        
        lines.append("## 历史周期分析（基于最近7天数据）")
        
        # 基本信息
        cycle_stage = historical_cycle_analysis.get('cycle_stage', '未知')
        confidence = historical_cycle_analysis.get('confidence', 0)
        lines.append(f"- **历史数据判断结果**：{cycle_stage}（置信度：{confidence:.2f}）")
        
        # 关键指标
        key_indicators = historical_cycle_analysis.get('key_indicators', [])
        if key_indicators:
            lines.append("\n### 历史关键指标")
            for indicator in key_indicators:
                lines.append(f"- {indicator}")
        
        # 趋势分析
        trends = historical_cycle_analysis.get('trends', {})
        if trends:
            lines.append("\n### 趋势分析")
            
            # 涨停数趋势
            limit_up_stats = trends.get('limit_up_stats', {})
            if limit_up_stats:
                current = limit_up_stats.get('current', 0)
                max_val = limit_up_stats.get('max', 0)
                avg = limit_up_stats.get('avg', 0)
                trend_slope = limit_up_stats.get('trend_slope', 0)
                lines.append(f"- 涨停数趋势：当前{current}只，7日最高{max_val}只，平均{avg:.1f}只")
                lines.append(f"  - 趋势斜率：{trend_slope:+.2f}（正值上升，负值下降）")
            
            # 价格趋势
            price_stats = trends.get('price_stats', {})
            if price_stats:
                change_pct = price_stats.get('change_pct', 0)
                volatility = price_stats.get('volatility', 0)
                lines.append(f"- 价格趋势：7日累计涨跌{change_pct:+.2f}%，波动率{volatility:.2f}")
            
            # 整体波动率
            overall_volatility = trends.get('overall_volatility', 'unknown')
            lines.append(f"- 整体波动率：{overall_volatility}")
        
        # 历史摘要
        historical_summary = historical_cycle_analysis.get('historical_summary', {})
        if historical_summary:
            lines.append("\n### 历史数据摘要")
            
            data_period = historical_summary.get('data_period', '')
            if data_period:
                lines.append(f"- 数据周期：{data_period}")
            
            limit_up_summary = historical_summary.get('limit_up_summary', {})
            if limit_up_summary:
                total_days = limit_up_summary.get('total_days_with_limit_ups', 0)
                max_single = limit_up_summary.get('max_single_day', 0)
                trend = limit_up_summary.get('trend', '未知')
                lines.append(f"- 涨停表现：{total_days}天有涨停，单日最高{max_single}只，整体趋势{trend}")
            
            price_summary = historical_summary.get('price_summary', {})
            if price_summary:
                total_return = price_summary.get('total_return', 0)
                volatility = price_summary.get('volatility', 0)
                lines.append(f"- 价格表现：总收益率{total_return:+.2f}%，波动率{volatility:.2f}%")
        
        # 周期判断理由
        cycle_reasoning = historical_cycle_analysis.get('cycle_reasoning', '')
        if cycle_reasoning:
            lines.append("\n### 历史数据分析理由")
            lines.append(f"- {cycle_reasoning}")
        
        # 数据质量
        data_quality = historical_cycle_analysis.get('data_quality', {})
        if data_quality:
            grade = data_quality.get('grade', '未知')
            overall_score = data_quality.get('overall_score', 0)
            lines.append(f"\n### 数据质量评估")
            lines.append(f"- 数据质量：{grade}（评分：{overall_score:.2f}）")
        
        return "\n".join(lines)

    def _format_sector_data_with_analysis(
        self,
        sector_name: str,
        context: AnalysisContext,
        emotion_cycle: Optional[Any] = None,
        capacity_profile: Optional[Any] = None
    ) -> str:
        """格式化板块数据（包含情绪周期和容量分析结果）
        
        Args:
            sector_name: 板块名称
            context: 分析上下文
            emotion_cycle: 情绪周期分析结果
            capacity_profile: 容量画像
            
        Returns:
            格式化的板块数据文本
        """
        lines = []
        
        # 基础数据
        sector_data = self._format_sector_data(sector_name, context)
        lines.append(sector_data)
        
        # 情绪周期分析结果
        if emotion_cycle:
            lines.append("\n### 情绪周期分析")
            lines.append(f"- 当前阶段：{emotion_cycle.stage}")
            lines.append(f"- 置信度：{emotion_cycle.confidence:.2f}")
            lines.append(f"- 风险等级：{emotion_cycle.risk_level}")
            lines.append(f"- 机会等级：{emotion_cycle.opportunity_level}")
            lines.append(f"- 判定理由：{emotion_cycle.reasoning}")
            if emotion_cycle.key_indicators:
                lines.append("- 关键指标：")
                for indicator in emotion_cycle.key_indicators:
                    lines.append(f"  - {indicator}")
        
        # 容量结构分析结果
        if capacity_profile:
            lines.append("\n### 容量结构分析")
            lines.append(f"- 容量类型：{capacity_profile.capacity_type}")
            lines.append(f"- 板块总成交额：{capacity_profile.sector_turnover:.2f}亿元")
            lines.append(f"- 核心中军成交额：{capacity_profile.leading_stock_turnover:.2f}亿元")
            lines.append(f"- 结构健康度：{capacity_profile.structure_health:.2f}")
            lines.append(f"- 持续性评分：{capacity_profile.sustainability_score:.2f}")
            
            # 金字塔结构
            pyramid = capacity_profile.pyramid_structure
            lines.append("\n#### 连板梯队金字塔")
            lines.append(f"- 5板及以上：{pyramid.board_5_plus}只")
            lines.append(f"- 3-4板：{pyramid.board_3_to_4}只")
            lines.append(f"- 1-2板：{pyramid.board_1_to_2}只")
            lines.append(f"- 总计：{pyramid.total_stocks}只")
            if pyramid.gaps:
                lines.append(f"- 梯队断层：{', '.join(map(str, pyramid.gaps))}板")
            else:
                lines.append("- 梯队完整：无断层")
        
        return "\n".join(lines)
