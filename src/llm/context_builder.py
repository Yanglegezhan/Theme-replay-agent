# -*- coding: utf-8 -*-
"""
上下文构建器

为LLM准备结构化输入数据
"""

from typing import Dict, Any, Optional, List

from ..models.data_models import AnalysisContext

# tiktoken是可选依赖，用于精确计算token数
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class ContextBuilder:
    """上下文构建器，为LLM准备结构化输入数据"""
    
    def __init__(self, max_tokens: int = 8000):
        """初始化上下文构建器
        
        Args:
            max_tokens: 最大token数限制
        """
        self.max_tokens = max_tokens
        # 使用tiktoken估算token数（针对GPT模型）
        if TIKTOKEN_AVAILABLE:
            try:
                self.encoding = tiktoken.get_encoding("cl100k_base")
            except Exception:
                self.encoding = None
        else:
            self.encoding = None
    
    def build_analysis_context(
        self,
        date: str,
        filter_result: Optional[Dict[str, Any]] = None,
        correlation_result: Optional[Dict[str, Any]] = None,
        emotion_cycles: Optional[Dict[str, Any]] = None,
        capacity_profiles: Optional[Dict[str, Any]] = None
    ) -> AnalysisContext:
        """构建完整分析上下文
        
        Args:
            date: 分析日期
            filter_result: 筛选结果
            correlation_result: 联动分析结果
            emotion_cycles: 情绪周期数据
            capacity_profiles: 容量画像数据
            
        Returns:
            AnalysisContext对象，包含：
            - date: 分析日期
            - market_overview: 市场概览
            - target_sectors: 目标板块详情
            - sector_relationships: 板块关系图
            - historical_context: 历史上下文
        """
        # 构建市场概览
        market_overview = self._build_market_overview(
            filter_result,
            correlation_result,
            emotion_cycles
        )
        
        # 构建目标板块详情
        target_sectors = self._build_target_sectors(
            filter_result,
            correlation_result,
            emotion_cycles,
            capacity_profiles
        )
        
        # 构建板块关系图
        sector_relationships = self._build_sector_relationships(correlation_result)
        
        # 构建历史上下文
        historical_context = self._build_historical_context(filter_result)
        
        return AnalysisContext(
            date=date,
            market_overview=market_overview,
            target_sectors=target_sectors,
            sector_relationships=sector_relationships,
            historical_context=historical_context
        )
    
    def format_for_llm(
        self,
        context: AnalysisContext,
        focus_sector: Optional[str] = None
    ) -> str:
        """格式化上下文为LLM友好的文本
        
        将结构化数据转换为清晰的文本描述：
        - 使用表格展示数值数据
        - 使用列表展示关键发现
        - 突出重要信息
        - 控制总长度（避免超过token限制）
        
        Args:
            context: 分析上下文
            focus_sector: 聚焦的板块（可选，用于单板块分析）
            
        Returns:
            格式化的文本
        """
        lines = []
        
        # 市场快照
        market_snapshot = self._build_market_snapshot(context)
        lines.append(market_snapshot)
        
        # 如果指定了聚焦板块，详细展示该板块
        if focus_sector:
            sector_summary = self._summarize_sector_data(focus_sector, context)
            lines.append("\n" + sector_summary)
        else:
            # 否则展示所有目标板块的摘要
            lines.append("\n## 目标板块详情")
            for sector_data in context.target_sectors:
                sector_name = sector_data.get('sector_name', '')
                if sector_name:
                    summary = self._summarize_sector_data(sector_name, context)
                    lines.append("\n" + summary)
        
        # 组合所有内容
        full_text = "\n".join(lines)
        
        # 检查并控制长度
        full_text = self._truncate_to_token_limit(full_text)
        
        return full_text
    
    def _build_market_overview(
        self,
        filter_result: Optional[Dict[str, Any]],
        correlation_result: Optional[Dict[str, Any]],
        emotion_cycles: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """构建市场概览
        
        Args:
            filter_result: 筛选结果
            correlation_result: 联动分析结果
            emotion_cycles: 情绪周期数据
            
        Returns:
            市场概览字典
        """
        overview = {}
        
        # 从筛选结果提取市场数据
        if filter_result:
            if 'market_stats' in filter_result:
                stats = filter_result['market_stats']
                overview['涨停数'] = stats.get('limit_up_count', '-')
                overview['跌停数'] = stats.get('limit_down_count', '-')
                overview['炸板率'] = f"{stats.get('blown_limit_up_rate', 0):.1f}%"
                overview['涨跌比'] = stats.get('rise_fall_ratio', '-')
            
            if 'consecutive_boards' in filter_result:
                boards = filter_result['consecutive_boards']
                if boards:
                    max_board = max(boards.keys()) if boards else 0
                    overview['最高连板'] = f"{max_board}连板"
        
        # 从联动分析提取关键信息
        if correlation_result:
            if 'leading_sectors' in correlation_result:
                leading = correlation_result['leading_sectors']
                overview['先锋板块数'] = len(leading)
            
            if 'resonance_sectors' in correlation_result:
                resonance = correlation_result['resonance_sectors']
                overview['共振板块数'] = len(resonance)
        
        # 从情绪周期提取整体情绪
        if emotion_cycles:
            # 统计各阶段板块数
            stage_counts = {}
            for sector_name, cycle_data in emotion_cycles.items():
                stage = cycle_data.get('stage', '未知')
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
            
            # 找出主导阶段
            if stage_counts:
                dominant_stage = max(stage_counts.items(), key=lambda x: x[1])
                overview['主导情绪'] = f"{dominant_stage[0]}（{dominant_stage[1]}个板块）"
        
        return overview
    
    def _build_target_sectors(
        self,
        filter_result: Optional[Dict[str, Any]],
        correlation_result: Optional[Dict[str, Any]],
        emotion_cycles: Optional[Dict[str, Any]],
        capacity_profiles: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """构建目标板块详情列表
        
        Args:
            filter_result: 筛选结果
            correlation_result: 联动分析结果
            emotion_cycles: 情绪周期数据
            capacity_profiles: 容量画像数据
            
        Returns:
            目标板块详情列表
        """
        sectors = []
        
        if not filter_result or 'target_sectors' not in filter_result:
            return sectors
        
        # 遍历目标板块
        for sector_info in filter_result['target_sectors']:
            sector_name = sector_info.get('sector_name', '')
            
            sector_data = {
                'sector_name': sector_name,
                'rank': sector_info.get('rank', 0),
                'strength_score': sector_info.get('strength_score', 0),
                'is_new_face': sector_info.get('is_new_face', False),
                'consecutive_days': sector_info.get('consecutive_days', 0),
                'limit_up_count': sector_info.get('limit_up_count', 0)
            }
            
            # 添加联动分析结果
            if correlation_result:
                sector_data['correlation_type'] = self._get_correlation_type(
                    sector_name,
                    correlation_result
                )
            
            # 添加情绪周期
            if emotion_cycles and sector_name in emotion_cycles:
                sector_data['emotion_cycle'] = emotion_cycles[sector_name]
            
            # 添加容量画像
            if capacity_profiles and sector_name in capacity_profiles:
                sector_data['capacity_profile'] = capacity_profiles[sector_name]
            
            sectors.append(sector_data)
        
        return sectors
    
    def _build_sector_relationships(
        self,
        correlation_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """构建板块关系图
        
        Args:
            correlation_result: 联动分析结果
            
        Returns:
            板块关系字典
        """
        relationships = {}
        
        if not correlation_result:
            return relationships
        
        # 先锋板块
        if 'leading_sectors' in correlation_result:
            leading = correlation_result['leading_sectors']
            relationships['leading_sectors'] = [
                s.get('sector_name', '') for s in leading
            ]
        
        # 共振板块
        if 'resonance_sectors' in correlation_result:
            resonance = correlation_result['resonance_sectors']
            relationships['resonance_sectors'] = [
                s.get('sector_name', '') for s in resonance
            ]
        
        # 分离板块
        if 'divergence_sectors' in correlation_result:
            relationships['divergence_sectors'] = correlation_result['divergence_sectors']
        
        # 跷跷板效应
        if 'seesaw_effects' in correlation_result:
            seesaw = correlation_result['seesaw_effects']
            relationships['seesaw_effects'] = [
                f"{s.get('rising_sector', '')}↑ vs {s.get('falling_sector', '')}↓"
                for s in seesaw
            ]
        
        return relationships
    
    def _build_historical_context(
        self,
        filter_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """构建历史上下文
        
        Args:
            filter_result: 筛选结果
            
        Returns:
            历史上下文字典
        """
        historical = {}
        
        if not filter_result:
            return historical
        
        # 新面孔板块
        if 'new_faces' in filter_result:
            historical['new_faces'] = filter_result['new_faces']
        
        # 老面孔板块
        if 'old_faces' in filter_result:
            historical['old_faces'] = filter_result['old_faces']
        
        return historical
    
    def _classify_sector_strength(self, strength_score: int) -> str:
        """根据强度分数分类板块强度等级
        
        Args:
            strength_score: 板块强度分数
            
        Returns:
            强度等级描述
        """
        if strength_score >= 8000:
            return "高强度"
        elif strength_score >= 2000:
            return "中强度"
        else:
            return "低强度"
    
    def _build_market_snapshot(self, context: AnalysisContext) -> str:
        """构建市场快照
        
        Args:
            context: 分析上下文
            
        Returns:
            市场快照文本
        """
        lines = []
        
        lines.append(f"## 市场概览（{context.date}）")
        
        # 市场统计
        if context.market_overview:
            for key, value in context.market_overview.items():
                lines.append(f"- {key}：{value}")
        
        # 目标板块表格
        lines.append("\n## 目标板块（前7强）")
        lines.append("| 排名 | 板块名称 | 强度分数 | 强度等级 | 涨停数 | 新旧 | 联动类型 | 情绪阶段 |")
        lines.append("|------|---------|---------|---------|--------|------|---------|---------|")
        
        for sector in context.target_sectors:
            rank = sector.get('rank', '-')
            name = sector.get('sector_name', '-')
            score = sector.get('strength_score', '-')
            
            # 强度等级分类
            strength_level = self._classify_sector_strength(score) if isinstance(score, (int, float)) else '-'
            
            limit_up = sector.get('limit_up_count', '-')
            
            # 新旧标记
            is_new = sector.get('is_new_face', False)
            new_old = "新" if is_new else f"老{sector.get('consecutive_days', 0)}天"
            
            # 联动类型
            correlation = sector.get('correlation_type', '-')
            
            # 情绪阶段
            emotion = sector.get('emotion_cycle', {})
            stage = emotion.get('stage', '-') if isinstance(emotion, dict) else '-'
            
            lines.append(f"| {rank} | {name} | {score} | {strength_level} | {limit_up} | {new_old} | {correlation} | {stage} |")
        
        # 板块关系
        if context.sector_relationships:
            lines.append("\n## 盘面联动")
            relationships = context.sector_relationships
            
            if relationships.get('leading_sectors'):
                lines.append(f"- 先锋板块：{', '.join(relationships['leading_sectors'])}")
            
            if relationships.get('resonance_sectors'):
                lines.append(f"- 共振板块：{', '.join(relationships['resonance_sectors'])}")
            
            if relationships.get('divergence_sectors'):
                lines.append(f"- 分离板块：{', '.join(relationships['divergence_sectors'])}")
            
            if relationships.get('seesaw_effects'):
                lines.append(f"- 跷跷板效应：{'; '.join(relationships['seesaw_effects'])}")
        
        return "\n".join(lines)
    
    def _summarize_sector_data(self, sector_name: str, context: AnalysisContext) -> str:
        """总结单个板块的关键数据
        
        Args:
            sector_name: 板块名称
            context: 分析上下文
            
        Returns:
            板块摘要文本
        """
        lines = []
        
        # 查找板块数据
        sector_data = None
        for sector in context.target_sectors:
            if sector.get('sector_name') == sector_name:
                sector_data = sector
                break
        
        if not sector_data:
            return f"### {sector_name}\n未找到数据"
        
        lines.append(f"### {sector_name}")
        
        # 基本信息
        lines.append(f"- 排名：第{sector_data.get('rank', '-')}名")
        lines.append(f"- 强度分数：{sector_data.get('strength_score', '-')}")
        
        # 强度等级分类
        strength_score = sector_data.get('strength_score', 0)
        if isinstance(strength_score, (int, float)):
            strength_level = self._classify_sector_strength(strength_score)
            lines.append(f"- 强度等级：{strength_level}")
        
        lines.append(f"- 涨停数：{sector_data.get('limit_up_count', '-')}只")
        
        # 新旧标记
        is_new = sector_data.get('is_new_face', False)
        if is_new:
            lines.append("- 新旧：新面孔（首次进入前7）")
        else:
            days = sector_data.get('consecutive_days', 0)
            lines.append(f"- 新旧：老面孔（连续{days}天在前7）")
        
        # 联动类型
        correlation = sector_data.get('correlation_type', '')
        if correlation:
            lines.append(f"- 盘面联动：{correlation}")
        
        # 情绪周期
        emotion = sector_data.get('emotion_cycle', {})
        if isinstance(emotion, dict) and emotion:
            stage = emotion.get('stage', '-')
            risk = emotion.get('risk_level', '-')
            opportunity = emotion.get('opportunity_level', '-')
            lines.append(f"- 情绪周期：{stage}（风险{risk}/机会{opportunity}）")
        
        # 容量画像
        capacity = sector_data.get('capacity_profile', {})
        if isinstance(capacity, dict) and capacity:
            cap_type = capacity.get('capacity_type', '-')
            health = capacity.get('structure_health', '-')
            lines.append(f"- 容量结构：{cap_type}（健康度{health}）")
        
        return "\n".join(lines)
    
    def _get_correlation_type(
        self,
        sector_name: str,
        correlation_result: Dict[str, Any]
    ) -> str:
        """获取板块的联动类型
        
        Args:
            sector_name: 板块名称
            correlation_result: 联动分析结果
            
        Returns:
            联动类型描述
        """
        types = []
        
        # 检查是否为先锋板块
        if 'leading_sectors' in correlation_result:
            leading = correlation_result['leading_sectors']
            for s in leading:
                if s.get('sector_name') == sector_name:
                    types.append("先锋")
                    break
        
        # 检查是否为共振板块
        if 'resonance_sectors' in correlation_result:
            resonance = correlation_result['resonance_sectors']
            for s in resonance:
                if s.get('sector_name') == sector_name:
                    types.append("共振")
                    break
        
        # 检查是否为分离板块
        if 'divergence_sectors' in correlation_result:
            divergence = correlation_result['divergence_sectors']
            if sector_name in divergence:
                types.append("分离")
        
        return "、".join(types) if types else "常规"
    
    def format_emotion_cycle_data(
        self,
        sector_name: str,
        context: AnalysisContext,
        limit_up_data: Optional[Dict[str, Any]] = None,
        intraday_data: Optional[Dict[str, Any]] = None,
        historical_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """格式化情绪周期分析所需的数据
        
        准备情绪周期分析所需的完整数据：
        - 涨停数据（当前涨停数、与前一日对比）
        - 连板梯队（最高连板、各板数分布）
        - 全市场炸板率
        - 昨日涨停今日表现
        - 分时走势描述
        - 历史情绪周期信息
        
        Args:
            sector_name: 板块名称
            context: 分析上下文
            limit_up_data: 涨停数据（可选）
            intraday_data: 分时数据（可选）
            historical_data: 历史数据（可选）
            
        Returns:
            格式化的情绪周期数据文本
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
        
        lines.append(f"## {sector_name} 板块情绪周期数据")
        lines.append(f"分析日期：{context.date}")
        
        # 0. 板块详细数据（如果有）
        if historical_data and 'sector_detailed' in historical_data:
            sector_detailed = historical_data['sector_detailed']
            lines.append("\n### 0. 板块当日详细数据")
            
            # 涨停数据
            limit_up_count = sector_detailed.get('limit_up_count', 0)
            lines.append(f"- 涨停数：{limit_up_count}只")
            
            # 连板梯队
            consecutive_boards = sector_detailed.get('consecutive_boards', {})
            if consecutive_boards:
                lines.append("- 连板梯队分布：")
                for board_num in sorted(consecutive_boards.keys(), reverse=True):
                    count = consecutive_boards[board_num]
                    lines.append(f"  - {board_num}连板：{count}只")
            
            # 资金数据
            capital_inflow = sector_detailed.get('capital_inflow', 0)
            capital_inflow_rate = sector_detailed.get('capital_inflow_rate', 0)
            turnover = sector_detailed.get('turnover', 0)
            change_pct = sector_detailed.get('change_pct', 0)
            
            lines.append(f"- 主力资金净流入：{capital_inflow:.2f}亿元（{capital_inflow_rate:+.2f}%）")
            lines.append(f"- 成交额：{turnover:.2f}亿元")
            lines.append(f"- 涨跌幅：{change_pct:+.2f}%")
            
            # 龙头股信息
            leading_stock = sector_detailed.get('leading_stock')
            if leading_stock:
                lines.append(f"- 主龙头：{leading_stock['name']}（{leading_stock['code']}）")
                # 连板天数：直接使用完整描述，不再添加"天"后缀
                consecutive_days = leading_stock['consecutive_days']
                lines.append(f"  - 连板天数：{consecutive_days}")
                lines.append(f"  - 涨停价：{leading_stock['limit_up_price']:.2f}元")
                lines.append(f"  - 成交额：{leading_stock['turnover']:.2f}亿元")
                lines.append(f"  - 总市值：{leading_stock.get('market_cap', 0):.2f}亿元")
                lines.append(f"  - 封单额：{leading_stock['seal_amount']:.2f}亿元")
                
                # 添加大单流入信息
                big_order_net = leading_stock.get('big_order_net', 0)
                big_order_buy = leading_stock.get('big_order_buy', 0)
                big_order_sell = leading_stock.get('big_order_sell', 0)
                if big_order_net != 0 or big_order_buy != 0:
                    lines.append(f"  - 大单净额：{big_order_net:+.2f}亿元（买入{big_order_buy:.2f}亿，卖出{big_order_sell:.2f}亿）")
            
            # 核心中军列表
            core_leaders = sector_detailed.get('core_leaders', [])
            if core_leaders and len(core_leaders) > 1:  # 如果有多个核心中军
                lines.append(f"- 核心中军（{len(core_leaders)}只）：")
                for leader in core_leaders:
                    lines.append(f"  - {leader['type']}：{leader['name']}（{leader['code']}）")
                    lines.append(f"    连板：{leader['consecutive_days']}，成交额：{leader['turnover']:.2f}亿，市值：{leader['market_cap']:.2f}亿")
            
            # 涨停股票列表（显示前10只）
            limit_up_stocks = sector_detailed.get('limit_up_stocks', [])
            if limit_up_stocks:
                lines.append(f"- 涨停股票列表（前10只）：")
                for i, stock in enumerate(limit_up_stocks[:10], 1):
                    stock_name = stock.get('股票名称', '')
                    stock_code = stock.get('股票代码', '')
                    consecutive = stock.get('连板天数_标准', stock.get('连板天数', ''))  # 使用标准化描述
                    limit_up_time = stock.get('涨停时间', '')
                    lines.append(f"  {i}. {stock_name}（{stock_code}）- {consecutive}，涨停时间：{limit_up_time}")
        
        # 1. 涨停家数变化
        lines.append("\n### 1. 涨停家数变化")
        current_limit_up = sector_info.get('limit_up_count', 0)
        lines.append(f"- 当前涨停数：{current_limit_up}只")
        
        # 从历史数据获取前一日涨停数
        if historical_data and 'previous_limit_up_count' in historical_data:
            prev_limit_up = historical_data['previous_limit_up_count']
            change = current_limit_up - prev_limit_up
            change_pct = (change / prev_limit_up * 100) if prev_limit_up > 0 else 0
            lines.append(f"- 前一日涨停数：{prev_limit_up}只")
            lines.append(f"- 变化：{change:+d}只（{change_pct:+.1f}%）")
        
        # 2. 连板高度和梯队分布
        lines.append("\n### 2. 连板梯队")
        if 'consecutive_boards' in sector_info:
            boards = sector_info['consecutive_boards']
            if boards:
                # 找出最高连板
                max_board = max(boards.keys()) if boards else 0
                lines.append(f"- 最高连板：{max_board}连板")
                
                # 展示梯队分布
                lines.append("- 梯队分布：")
                for board_num in sorted(boards.keys(), reverse=True):
                    stocks = boards[board_num]
                    stock_count = len(stocks) if isinstance(stocks, list) else stocks
                    lines.append(f"  - {board_num}板：{stock_count}只")
                
                # 评估梯队完整性
                board_nums = sorted(boards.keys(), reverse=True)
                gaps = []
                for i in range(len(board_nums) - 1):
                    if board_nums[i] - board_nums[i+1] > 1:
                        gaps.append(f"{board_nums[i+1]+1}-{board_nums[i]-1}板")
                
                if gaps:
                    lines.append(f"- 梯队断层：{', '.join(gaps)}")
                else:
                    lines.append("- 梯队完整：无明显断层")
            else:
                lines.append("- 无连板数据")
        else:
            lines.append("- 连板数据不可用")
        
        # 3. 市场情绪指标
        lines.append("\n### 3. 市场情绪指标")
        
        # 全市场炸板率
        if limit_up_data and 'blown_limit_up_rate' in limit_up_data:
            blown_rate = limit_up_data['blown_limit_up_rate']
            lines.append(f"- 全市场炸板率：{blown_rate:.1f}%")
            
            # 根据炸板率判断市场情绪
            if blown_rate < 20:
                emotion_desc = "低（市场情绪高涨）"
            elif blown_rate < 30:
                emotion_desc = "中等（市场情绪正常）"
            else:
                emotion_desc = "高（市场情绪分化）"
            lines.append(f"  - 情绪判断：{emotion_desc}")
        
        # 昨日涨停今日表现
        if limit_up_data and 'yesterday_limit_up_performance' in limit_up_data:
            yesterday_perf = limit_up_data['yesterday_limit_up_performance']
            lines.append(f"- 昨日涨停今日表现：{yesterday_perf:+.2f}%")
            
            if yesterday_perf > 5:
                perf_desc = "强势（赚钱效应好）"
            elif yesterday_perf > 0:
                perf_desc = "正常（小幅上涨）"
            elif yesterday_perf > -5:
                perf_desc = "分化（小幅回调）"
            else:
                perf_desc = "弱势（亏钱效应明显）"
            lines.append(f"  - 赚钱效应：{perf_desc}")
        
        # 全市场涨停数
        if limit_up_data and 'limit_up_count' in limit_up_data:
            market_limit_up = limit_up_data['limit_up_count']
            lines.append(f"- 全市场涨停数：{market_limit_up}只")
        
        # 4. 资金参与度
        lines.append("\n### 4. 资金参与度")
        if 'turnover' in sector_info:
            turnover = sector_info['turnover']
            lines.append(f"- 板块总成交额：{turnover}亿元")
            
            # 根据成交额判断资金参与度
            if turnover > 100:
                participation = "极高（大资金活跃）"
            elif turnover > 50:
                participation = "高（资金充裕）"
            elif turnover > 20:
                participation = "中等（资金正常）"
            else:
                participation = "低（资金观望）"
            lines.append(f"  - 参与度：{participation}")
        
        # 龙头股表现
        if 'leading_stock' in sector_info:
            leading = sector_info['leading_stock']
            lines.append(f"- 龙头股：{leading.get('name', '-')}")
            lines.append(f"  - 涨跌幅：{leading.get('pct_change', 0):+.2f}%")
            lines.append(f"  - 成交额：{leading.get('turnover', 0):.2f}亿元")
        
        # 5. 分时走势
        lines.append("\n### 5. 分时走势")
        if intraday_data:
            # 如果有分时数据，分析走势特征
            lines.append(self._analyze_intraday_pattern(intraday_data))
        elif 'intraday_summary' in sector_info:
            # 使用预先计算的分时摘要
            lines.append(sector_info['intraday_summary'])
        else:
            lines.append("- 分时数据不可用")
        
        # 6. 历史K线走势（14日）
        if historical_data and 'kline_data' in historical_data:
            lines.append("\n### 6. 历史K线走势（14日）")
            kline_data = historical_data['kline_data']
            
            if kline_data:
                lines.append(f"- 数据周期：{kline_data[0]['date']} 至 {kline_data[-1]['date']}")
                lines.append(f"- 数据天数：{len(kline_data)}天")
                
                # 计算统计指标
                changes = [k['change_pct'] for k in kline_data]
                opens = [k.get('open', 0) for k in kline_data]
                highs = [k.get('high', 0) for k in kline_data]
                lows = [k.get('low', 0) for k in kline_data]
                closes = [k.get('close', 0) for k in kline_data]
                turnovers = [k['turnover'] / 1e8 for k in kline_data]  # 转换为亿元
                
                # 计算真实的累计涨跌幅（从第一天开盘到最后一天收盘）
                first_open = opens[0]
                last_close = closes[-1]
                if first_open > 0:
                    cumulative_change = (last_close - first_open) / first_open * 100
                else:
                    cumulative_change = 0
                lines.append(f"- 期间涨跌幅：{cumulative_change:+.2f}%（从首日开盘到末日收盘）")
                
                # 价格区间
                max_high = max(highs)
                min_low = min(lows)
                lines.append(f"- 价格区间：{min_low:.2f} - {max_high:.2f}")
                
                # 上涨天数和下跌天数
                up_days = sum(1 for c in changes if c > 0)
                down_days = sum(1 for c in changes if c < 0)
                lines.append(f"- 上涨天数：{up_days}天，下跌天数：{down_days}天")
                
                # 最大单日涨幅和跌幅
                max_gain = max(changes)
                max_loss = min(changes)
                lines.append(f"- 最大单日涨幅：{max_gain:+.2f}%")
                lines.append(f"- 最大单日跌幅：{max_loss:+.2f}%")
                
                # 平均成交额
                avg_turnover = sum(turnovers) / len(turnovers)
                lines.append(f"- 平均成交额：{avg_turnover:.2f}亿元")
                
                # 成交额趋势
                recent_turnover = sum(turnovers[-3:]) / 3  # 最近3天平均
                early_turnover = sum(turnovers[:3]) / 3  # 前3天平均
                turnover_change = (recent_turnover - early_turnover) / early_turnover * 100 if early_turnover > 0 else 0
                lines.append(f"- 成交额变化：{turnover_change:+.1f}%（最近3天vs前3天）")
                
                # 详细K线数据（最近7天）
                lines.append("\n- 最近7天K线明细：")
                for kline in kline_data[-7:]:
                    date = kline['date']
                    open_price = kline.get('open', 0)
                    high_price = kline.get('high', 0)
                    low_price = kline.get('low', 0)
                    close_price = kline.get('close', 0)
                    change = kline['change_pct']
                    turnover = kline['turnover'] / 1e8
                    
                    # K线形态描述（基于实体大小和上下影线）
                    body = abs(close_price - open_price)
                    upper_shadow = high_price - max(open_price, close_price)
                    lower_shadow = min(open_price, close_price) - low_price
                    
                    if change > 3:
                        pattern = "大阳线"
                    elif change > 1:
                        pattern = "阳线"
                    elif change > -1:
                        if change > 0:
                            pattern = "小阳线"
                        elif change < 0:
                            pattern = "小阴线"
                        else:
                            pattern = "十字星"
                    elif change > -3:
                        pattern = "阴线"
                    else:
                        pattern = "大阴线"
                    
                    # 添加特殊形态标记
                    if upper_shadow > body * 2 and change > 0:
                        pattern += "（长上影）"
                    elif lower_shadow > body * 2 and change < 0:
                        pattern += "（长下影）"
                    
                    lines.append(f"  - {date}: 开{open_price:.2f} 高{high_price:.2f} 低{low_price:.2f} 收{close_price:.2f}, {change:+.2f}% ({pattern}), 成交额{turnover:.1f}亿")
                
                # 趋势判断
                lines.append("\n- 趋势分析：")
                
                # 短期趋势（最近3天）
                recent_changes = changes[-3:]
                if all(c > 0 for c in recent_changes):
                    short_trend = "连续上涨"
                elif all(c < 0 for c in recent_changes):
                    short_trend = "连续下跌"
                elif sum(recent_changes) > 2:
                    short_trend = "震荡上行"
                elif sum(recent_changes) < -2:
                    short_trend = "震荡下行"
                else:
                    short_trend = "横盘震荡"
                lines.append(f"  - 短期趋势（3天）：{short_trend}")
                
                # 中期趋势（最近7天）
                if len(changes) >= 7:
                    mid_changes = changes[-7:]
                    mid_cumulative = sum(mid_changes)
                    if mid_cumulative > 5:
                        mid_trend = "强势上涨"
                    elif mid_cumulative > 2:
                        mid_trend = "温和上涨"
                    elif mid_cumulative > -2:
                        mid_trend = "横盘整理"
                    elif mid_cumulative > -5:
                        mid_trend = "温和下跌"
                    else:
                        mid_trend = "弱势下跌"
                    lines.append(f"  - 中期趋势（7天）：{mid_trend}")
                
                # 波动率分析
                import numpy as np
                volatility = np.std(changes)
                if volatility > 3:
                    vol_desc = "高波动（情绪剧烈）"
                elif volatility > 1.5:
                    vol_desc = "中等波动（正常）"
                else:
                    vol_desc = "低波动（平稳）"
                lines.append(f"  - 波动率：{volatility:.2f}% ({vol_desc})")
            else:
                lines.append("- 无K线数据")
        
        # 7. 历史情绪周期
        if historical_data and 'emotion_history' in historical_data:
            lines.append("\n### 7. 历史情绪周期")
            emotion_history = historical_data['emotion_history']
            
            if emotion_history:
                lines.append("- 近期情绪周期：")
                for record in emotion_history[:5]:  # 最近5天
                    date = record.get('date', '-')
                    stage = record.get('stage', '-')
                    lines.append(f"  - {date}：{stage}")
            else:
                lines.append("- 首次进入前7，无历史情绪周期数据")
        
        # 8. 新旧面孔标记
        lines.append("\n### 8. 板块特征")
        is_new = sector_info.get('is_new_face', False)
        if is_new:
            lines.append("- 新旧：新面孔（首次进入前7强）")
            lines.append("  - 特征：题材新鲜，市场关注度高，可能处于启动期")
        else:
            days = sector_info.get('consecutive_days', 0)
            lines.append(f"- 新旧：老面孔（连续{days}天在前7强）")
            lines.append(f"  - 特征：题材持续性强，需关注是否进入分化期或退潮期")
        
        return "\n".join(lines)
    
    def _analyze_intraday_pattern(self, intraday_data: Dict[str, Any]) -> str:
        """分析分时走势模式
        
        Args:
            intraday_data: 分时数据
            
        Returns:
            分时走势描述
        """
        lines = []
        
        # 提取关键数据
        pct_changes = intraday_data.get('pct_changes', [])
        
        if not pct_changes:
            return "- 分时数据不完整"
        
        # 计算关键指标
        max_pct = max(pct_changes) if pct_changes else 0
        min_pct = min(pct_changes) if pct_changes else 0
        final_pct = pct_changes[-1] if pct_changes else 0
        
        # 计算波动幅度
        volatility = max_pct - min_pct
        
        # 判断走势类型
        if final_pct > 5 and min_pct > -2:
            pattern = "强势上攻（全天保持强势，回调幅度小）"
        elif final_pct > 3 and max_pct - final_pct < 2:
            pattern = "稳步上涨（逐步走高，尾盘封板或接近涨停）"
        elif final_pct > 0 and volatility > 8:
            pattern = "震荡上行（波动较大，但整体向上）"
        elif final_pct < -3 and max_pct > 3:
            pattern = "冲高回落（早盘冲高，随后回落）"
        elif final_pct < -5:
            pattern = "弱势下跌（全天走弱，市场情绪转冷）"
        else:
            pattern = "震荡整理（涨跌幅度不大，方向不明）"
        
        lines.append(f"- 走势类型：{pattern}")
        lines.append(f"- 最高涨幅：{max_pct:+.2f}%")
        lines.append(f"- 最低涨幅：{min_pct:+.2f}%")
        lines.append(f"- 收盘涨幅：{final_pct:+.2f}%")
        lines.append(f"- 波动幅度：{volatility:.2f}%")
        
        # 计算攻击角度（简化版）
        if len(pct_changes) > 30:
            # 取前30分钟的涨幅
            early_pct = pct_changes[30] if len(pct_changes) > 30 else pct_changes[-1]
            if early_pct > 3:
                lines.append("- 攻击角度：陡峭（45度以上，启动期特征）")
            elif early_pct > 1:
                lines.append("- 攻击角度：正常（30-45度）")
            else:
                lines.append("- 攻击角度：平缓（低于30度）")
        
        return "\n".join(lines)
    
    def _truncate_to_token_limit(self, text: str) -> str:
        """截断文本以符合token限制
        
        Args:
            text: 原始文本
            
        Returns:
            截断后的文本
        """
        if self.encoding:
            # 使用tiktoken精确计算
            tokens = self.encoding.encode(text)
            if len(tokens) <= self.max_tokens:
                return text
            
            # 截断到限制
            truncated_tokens = tokens[:self.max_tokens]
            return self.encoding.decode(truncated_tokens)
        else:
            # 使用简单估算（1 token ≈ 4 chars）
            max_chars = self.max_tokens * 4
            if len(text) <= max_chars:
                return text
            
            return text[:max_chars] + "\n\n[内容已截断以符合长度限制]"
