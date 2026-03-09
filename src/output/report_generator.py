# -*- coding: utf-8 -*-
"""
报告生成器

生成结构化分析报告，支持Markdown和JSON格式导出
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from ..agent.theme_anchor_agent import AnalysisReport


logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器
    
    负责将分析结果转换为结构化报告，并支持多种格式导出
    """
    
    def __init__(self):
        """初始化报告生成器"""
        logger.info("ReportGenerator initialized")
    
    def generate_report(self, analysis_report: AnalysisReport) -> Dict[str, Any]:
        """生成综合分析报告
        
        将AnalysisReport转换为结构化的字典格式，便于导出
        
        Args:
            analysis_report: 分析报告对象
            
        Returns:
            结构化报告字典，包含：
            - date: 分析日期
            - summary: 执行摘要
            - target_sectors: 目标板块详情列表
            - market_overview: 市场概览
            - risk_warnings: 风险提示列表
        """
        logger.info(f"生成报告: {analysis_report.date}")
        
        # 构建报告结构
        report = {
            'date': analysis_report.date,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'executive_summary': analysis_report.executive_summary,
                'market_intent': self._format_market_intent(analysis_report.market_intent)
            },
            'target_sectors': self._format_target_sectors(analysis_report),
            'market_overview': self._format_market_overview(analysis_report),
            'risk_warnings': analysis_report.risk_warnings
        }
        
        logger.info(f"报告生成完成: {len(report['target_sectors'])} 个板块")
        return report
    
    def export_markdown(self, report: Dict[str, Any], output_path: str) -> None:
        """导出为Markdown格式
        
        Args:
            report: 报告字典
            output_path: 输出文件路径
        """
        logger.info(f"导出Markdown报告: {output_path}")
        
        # 确保输出目录存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 生成Markdown内容
        md_content = self._generate_markdown_content(report)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"Markdown报告已保存: {output_path}")
    
    def export_json(self, report: Dict[str, Any], output_path: str) -> None:
        """导出为JSON格式
        
        Args:
            report: 报告字典
            output_path: 输出文件路径
        """
        logger.info(f"导出JSON报告: {output_path}")
        
        # 确保输出目录存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON报告已保存: {output_path}")
    
    def _format_market_intent(self, market_intent: Any) -> Dict[str, Any]:
        """格式化市场资金意图
        
        Args:
            market_intent: 市场资金意图分析对象
            
        Returns:
            格式化的字典
        """
        if market_intent is None:
            return {}
        
        return {
            'main_capital_flow': market_intent.main_capital_flow,
            'sector_rotation': market_intent.sector_rotation,
            'market_sentiment': market_intent.market_sentiment,
            'key_drivers': market_intent.key_drivers,
            'confidence': market_intent.confidence
        }
    
    def _format_target_sectors(self, analysis_report: AnalysisReport) -> List[Dict[str, Any]]:
        """格式化目标板块详情

        Args:
            analysis_report: 分析报告对象

        Returns:
            板块详情列表
        """
        sectors = []

        for sector in analysis_report.filter_result.target_sectors:
            sector_name = sector.sector_name

            # 基础信息
            sector_info = {
                'sector_name': sector_name,
                'sector_code': sector.sector_code,
                'rank': sector.rank,
                'strength_score': sector.strength_score,
                'limit_up_count': sector.ndays_limit_up,  # N日涨停数（保留用于参考）
                'is_new_face': sector_name in analysis_report.filter_result.new_faces,
                'consecutive_days': self._get_consecutive_days(
                    sector_name,
                    analysis_report.filter_result.old_faces
                )
            }

            # 从详细数据中获取今日涨停数
            today_limit_up = 0
            if hasattr(analysis_report, 'sector_detailed_data') and analysis_report.sector_detailed_data:
                detailed_data = analysis_report.sector_detailed_data.get(sector_name, {})
                today_limit_up = detailed_data.get('limit_up_count', 0)
            sector_info['today_limit_up'] = today_limit_up  # 今日涨停数

            # 联动分析
            sector_info['correlation_analysis'] = self._format_correlation_for_sector(
                sector_name,
                analysis_report.correlation_result
            )

            # 情绪周期
            if sector_name in analysis_report.emotion_cycles:
                emotion = analysis_report.emotion_cycles[sector_name]
                sector_info['emotion_cycle'] = {
                    'stage': emotion.stage,
                    'confidence': emotion.confidence,
                    'reasoning': emotion.reasoning,
                    'key_indicators': emotion.key_indicators,
                    'risk_level': emotion.risk_level,
                    'opportunity_level': emotion.opportunity_level
                }
            else:
                sector_info['emotion_cycle'] = None

            # 容量画像
            if sector_name in analysis_report.capacity_profiles:
                capacity = analysis_report.capacity_profiles[sector_name]
                sector_info['capacity_profile'] = {
                    'capacity_type': capacity.capacity_type,
                    'sector_turnover': capacity.sector_turnover,
                    'leading_stock_turnover': capacity.leading_stock_turnover,
                    'pyramid_structure': {
                        'board_5_plus': capacity.pyramid_structure.board_5_plus,
                        'board_3_to_4': capacity.pyramid_structure.board_3_to_4,
                        'board_1_to_2': capacity.pyramid_structure.board_1_to_2,
                        'gaps': capacity.pyramid_structure.gaps,
                        'total_stocks': capacity.pyramid_structure.total_stocks
                    },
                    'structure_health': capacity.structure_health,
                    'sustainability_score': capacity.sustainability_score
                }
            else:
                sector_info['capacity_profile'] = None

            # 核心个股数据（从详细数据中提取）
            if hasattr(analysis_report, 'sector_detailed_data') and analysis_report.sector_detailed_data:
                detailed_data = analysis_report.sector_detailed_data.get(sector_name, {})
                sector_info['core_stocks'] = self._format_core_stocks(detailed_data)
                # 从详细数据中获取今日涨停数
                today_limit_up = detailed_data.get('limit_up_count', 0)
                sector_info['today_limit_up'] = today_limit_up
            else:
                sector_info['core_stocks'] = None
                sector_info['today_limit_up'] = sector.ndays_limit_up  # 降级使用N日涨停数

            # LLM分析结果
            if sector_name in analysis_report.llm_analysis.sector_evaluations:
                evaluation = analysis_report.llm_analysis.sector_evaluations[sector_name]
                sector_info['sustainability_evaluation'] = {
                    'sustainability_score': evaluation.sustainability_score,
                    'time_horizon': evaluation.time_horizon,
                    'risk_factors': evaluation.risk_factors,
                    'support_factors': evaluation.support_factors,
                    'reasoning': evaluation.reasoning
                }
            else:
                sector_info['sustainability_evaluation'] = None

            if sector_name in analysis_report.llm_analysis.trading_advices:
                advice = analysis_report.llm_analysis.trading_advices[sector_name]
                sector_info['trading_advice'] = {
                    'action': advice.action,
                    'entry_timing': advice.entry_timing,
                    'exit_strategy': advice.exit_strategy,
                    'position_sizing': advice.position_sizing,
                    'risk_warning': advice.risk_warning,
                    'reasoning': advice.reasoning
                }
            else:
                sector_info['trading_advice'] = None

            sectors.append(sector_info)

        # 按强度分数排序
        sectors.sort(key=lambda x: x['strength_score'], reverse=True)

        return sectors
    
    def _format_market_overview(self, analysis_report: AnalysisReport) -> Dict[str, Any]:
        """格式化市场概览
        
        Args:
            analysis_report: 分析报告对象
            
        Returns:
            市场概览字典
        """
        overview = {
            'total_sectors': len(analysis_report.filter_result.target_sectors),
            'new_faces_count': len(analysis_report.filter_result.new_faces),
            'old_faces_count': len(analysis_report.filter_result.old_faces),
            'leading_sectors_count': len(analysis_report.correlation_result.leading_sectors),
            'resonance_sectors_count': len(analysis_report.correlation_result.resonance_sectors),
            'divergence_sectors_count': len(analysis_report.correlation_result.divergence_sectors)
        }
        
        # 情绪周期分布
        emotion_distribution = {}
        for sector_name, emotion in analysis_report.emotion_cycles.items():
            stage = emotion.stage
            if stage not in emotion_distribution:
                emotion_distribution[stage] = 0
            emotion_distribution[stage] += 1
        
        overview['emotion_cycle_distribution'] = emotion_distribution
        
        return overview
    
    def _format_correlation_for_sector(
        self,
        sector_name: str,
        correlation_result: Any
    ) -> Dict[str, Any]:
        """格式化单个板块的联动分析
        
        Args:
            sector_name: 板块名称
            correlation_result: 联动分析结果
            
        Returns:
            联动分析字典
        """
        correlation = {
            'is_leading': False,
            'is_resonance': False,
            'is_divergence': False,
            'time_lag': None,
            'elasticity': None
        }
        
        # 检查是否为先锋板块
        for leading in correlation_result.leading_sectors:
            if leading.sector_name == sector_name:
                correlation['is_leading'] = True
                correlation['time_lag'] = leading.time_lag
                break
        
        # 检查是否为共振板块
        for resonance in correlation_result.resonance_sectors:
            if resonance.sector_name == sector_name:
                correlation['is_resonance'] = True
                correlation['elasticity'] = resonance.elasticity
                break
        
        # 检查是否为分离板块
        if sector_name in correlation_result.divergence_sectors:
            correlation['is_divergence'] = True
        
        return correlation
    
    def _get_consecutive_days(
        self,
        sector_name: str,
        old_faces: List[tuple]
    ) -> int:
        """获取板块连续天数

        Args:
            sector_name: 板块名称
            old_faces: 老面孔列表 [(名称, 天数), ...]

        Returns:
            连续天数
        """
        for name, days in old_faces:
            if name == sector_name:
                return days
        return 0

    def _format_core_stocks(self, detailed_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化核心个股数据

        Args:
            detailed_data: 板块详细数据

        Returns:
            格式化的核心个股信息
        """
        if not detailed_data:
            return None

        result = {
            'leading_stock': None,
            'core_leaders': [],
            'space_dragons': [],  # 空间龙列表
            'zhongjun_list': [],  # 中军列表
            'pioneer_list': [],   # 先锋龙列表
            'all_limit_up_stocks': []
        }

        # 格式化龙头股
        leading = detailed_data.get('leading_stock')
        if leading:
            result['leading_stock'] = {
                'code': leading.get('code', ''),
                'name': leading.get('name', ''),
                'consecutive_days': leading.get('consecutive_days', ''),
                'turnover': leading.get('turnover', 0),
                'seal_amount': leading.get('seal_amount', 0),  # 收盘封单额
                'market_cap': leading.get('market_cap', 0),
                'big_order_net': leading.get('big_order_net', 0),
                'actual_turnover_rate': leading.get('actual_turnover_rate', 0),
                'first_seal_time': leading.get('first_seal_time', ''),
                'last_seal_time': leading.get('last_seal_time', ''),
                'open_count': leading.get('open_count', 0),
            }

        # 格式化核心中军列表（新的分类：空间龙、中军、先锋龙）
        # 优先使用新的分类数据
        space_dragons = detailed_data.get('space_dragons', [])
        zhongjun_list = detailed_data.get('zhongjun_list', [])
        pioneer_list = detailed_data.get('pioneer_list', [])

        # 空间龙（最多4个）
        for dragon in space_dragons[:4]:
            result['space_dragons'].append({
                'type': '空间龙',
                'type_detail': dragon.get('type_detail', ''),
                'code': dragon.get('code', ''),
                'name': dragon.get('name', ''),
                'consecutive_days': dragon.get('consecutive_days', ''),
                'turnover': dragon.get('turnover', 0),
                'market_cap': dragon.get('market_cap', 0),
                'actual_turnover_rate': dragon.get('actual_turnover_rate', 0),
                'big_order_net': dragon.get('big_order_net', 0),
                'seal_amount': dragon.get('seal_amount', 0),
                'first_seal_time': dragon.get('first_seal_time', ''),
                'last_seal_time': dragon.get('last_seal_time', ''),
                'open_count': dragon.get('open_count', 0),
            })

        # 中军（最多2个）
        for zj in zhongjun_list[:2]:
            result['zhongjun_list'].append({
                'type': '中军',
                'type_detail': zj.get('type_detail', ''),
                'code': zj.get('code', ''),
                'name': zj.get('name', ''),
                'consecutive_days': zj.get('consecutive_days', ''),
                'turnover': zj.get('turnover', 0),
                'market_cap': zj.get('market_cap', 0),
                'actual_turnover_rate': zj.get('actual_turnover_rate', 0),
                'big_order_net': zj.get('big_order_net', 0),
                'seal_amount': zj.get('seal_amount', 0),
                'first_seal_time': zj.get('first_seal_time', ''),
                'last_seal_time': zj.get('last_seal_time', ''),
                'open_count': zj.get('open_count', 0),
            })

        # 先锋龙（最多2个）
        for pioneer in pioneer_list[:2]:
            result['pioneer_list'].append({
                'type': '先锋龙',
                'type_detail': pioneer.get('type_detail', ''),
                'code': pioneer.get('code', ''),
                'name': pioneer.get('name', ''),
                'consecutive_days': pioneer.get('consecutive_days', ''),
                'turnover': pioneer.get('turnover', 0),
                'market_cap': pioneer.get('market_cap', 0),
                'actual_turnover_rate': pioneer.get('actual_turnover_rate', 0),
                'big_order_net': pioneer.get('big_order_net', 0),
                'seal_amount': pioneer.get('seal_amount', 0),
                'first_seal_time': pioneer.get('first_seal_time', ''),
                'last_seal_time': pioneer.get('last_seal_time', ''),
                'open_count': pioneer.get('open_count', 0),
            })

        # 合并所有龙头股用于兼容旧格式
        result['core_leaders'] = result['space_dragons'] + result['zhongjun_list'] + result['pioneer_list']

        # 格式化所有涨停股票（用于表格展示）
        limit_up_stocks = detailed_data.get('limit_up_stocks', [])

        # 为每只股票获取详细数据
        formatted_stocks = []

        # 尝试使用 kaipanla 数据源补全数据
        kaipanla = None
        try:
            from ..data.kaipanla_source import KaipanlaDataSource
            kaipanla = KaipanlaDataSource()
        except Exception as e:
            logger.warning(f"初始化KaipanlaDataSource失败: {e}")

        for stock in limit_up_stocks:
            stock_code = stock.get('股票代码', '')
            stock_name = stock.get('股票名称', '')

            # 尝试补全数据
            if kaipanla:
                try:
                    stock = kaipanla._enrich_stock_data(stock_code, stock, None)
                except Exception as e:
                    logger.debug(f"补全{stock_name}数据失败: {e}")

            # 从原始数据获取成交额（元转亿元）
            turnover_raw = stock.get('成交额', 0)
            if isinstance(turnover_raw, (int, float)) and turnover_raw > 0:
                turnover = float(turnover_raw) / 100000000  # 元转亿元
            else:
                turnover = 0.0

            # 流通市值 - 直接从原始数据获取
            market_cap_raw = stock.get('流通市值', 0)
            if isinstance(market_cap_raw, (int, float)) and market_cap_raw > 1000000:
                market_cap = float(market_cap_raw) / 100000000  # 元转亿元
            elif isinstance(market_cap_raw, (int, float)) and market_cap_raw > 0:
                market_cap = float(market_cap_raw)
            else:
                # 尝试使用总市值
                total_cap_raw = stock.get('总市值', 0)
                if isinstance(total_cap_raw, (int, float)) and total_cap_raw > 1000000:
                    market_cap = float(total_cap_raw) / 100000000
                else:
                    market_cap = 0.0

            # 获取封单额（收盘封单）- 直接从原始数据转换
            seal_amount_raw = stock.get('封单额', 0)
            if isinstance(seal_amount_raw, (int, float)) and seal_amount_raw > 0:
                seal_amount = float(seal_amount_raw) / 100000000  # 元转亿元
            else:
                seal_amount = 0.0

            # 获取大单净流入 - 直接使用主力资金字段
            big_order_raw = stock.get('主力资金', 0)
            if isinstance(big_order_raw, (int, float)) and big_order_raw != 0:
                big_order_net = float(big_order_raw) / 100000000  # 元转亿元
            else:
                big_order_net = 0.0

            # 获取首次封板时间
            first_seal_time = stock.get('首次封板时间', '') or stock.get('涨停时间', '')

            # 获取换手率（从补全数据中获取）
            actual_turnover_rate = stock.get('换手率', 0) if stock.get('换手率') else 0

            # 开板次数（API暂不提供，设为默认值）
            open_count = stock.get('开板次数', 0)

            formatted_stocks.append({
                'code': stock_code,
                'name': stock_name,
                'consecutive_days': stock.get('连板天数_标准', stock.get('连板天数', '')),
                'turnover': turnover,
                'market_cap': market_cap,
                'seal_amount': seal_amount,
                'big_order_net': big_order_net,
                'actual_turnover_rate': actual_turnover_rate,
                'first_seal_time': first_seal_time,
                'last_seal_time': stock.get('最终封板时间', ''),
                'open_count': open_count,
            })

        # 按连板状态排序：先按连板数降序，同身位按最终涨停时间升序
        def sort_key(s):
            consecutive_str = s['consecutive_days']
            # 解析连板数
            import re
            match = re.search(r'(\d+)', str(consecutive_str))
            if match:
                board_num = int(match.group(1))
            else:
                board_num = 1  # 首板默认为1

            # 最终涨停时间，没有时间则排最后
            last_seal = s.get('last_seal_time', '')
            if not last_seal or last_seal == '-':
                last_seal = '99:99'

            return (-board_num, last_seal)  # 连板数降序，时间升序

        formatted_stocks.sort(key=sort_key)
        result['all_limit_up_stocks'] = formatted_stocks

        return result

    def _parse_amount(self, amount_str) -> float:
        """解析成交额字符串为数值（亿元）

        Args:
            amount_str: 成交额字符串（如"1.23亿"、"4567万"）

        Returns:
            成交额（亿元）
        """
        if isinstance(amount_str, (int, float)):
            return float(amount_str)

        if not amount_str:
            return 0.0

        try:
            s = str(amount_str).strip().replace(',', '')
            if s.endswith('亿'):
                return float(s[:-1])
            elif s.endswith('万'):
                return float(s[:-1]) / 10000
            elif s.endswith('千'):
                return float(s[:-1]) / 100000
            else:
                # 纯数字，假设是元
                val = float(s)
                return val / 100000000
        except:
            return 0.0

    def _parse_seal_amount(self, seal_amount) -> float:
        """解析封单额为数值（亿元）

        Args:
            seal_amount: 封单额（可能是字符串带单位或数值）

        Returns:
            封单额（亿元）
        """
        if isinstance(seal_amount, (int, float)):
            return float(seal_amount) / 100000000 if seal_amount > 1000000 else float(seal_amount)

        if not seal_amount or seal_amount == '-':
            return 0.0

        try:
            s = str(seal_amount).strip()
            if s.endswith('亿'):
                return float(s[:-1])
            elif s.endswith('万'):
                return float(s[:-1]) / 10000
            else:
                return float(s) / 100000000 if float(s) > 1000000 else float(s)
        except:
            return 0.0
    
    def _generate_markdown_content(self, report: Dict[str, Any]) -> str:
        """生成Markdown内容
        
        Args:
            report: 报告字典
            
        Returns:
            Markdown文本
        """
        lines = []
        
        # 标题
        lines.append(f"# A股超短线题材锚定分析报告")
        lines.append(f"")
        lines.append(f"**分析日期**: {report['date']}")
        lines.append(f"**生成时间**: {report['generated_at']}")
        lines.append(f"")
        
        # 执行摘要
        lines.append(f"## 执行摘要")
        lines.append(f"")
        lines.append(report['summary']['executive_summary'])
        lines.append(f"")
        
        # 市场资金意图
        if report['summary']['market_intent']:
            lines.append(f"## 市场资金意图")
            lines.append(f"")
            intent = report['summary']['market_intent']
            lines.append(f"**主力资金流向**: {intent.get('main_capital_flow', 'N/A')}")
            lines.append(f"")
            lines.append(f"**板块轮动**: {intent.get('sector_rotation', 'N/A')}")
            lines.append(f"")
            lines.append(f"**市场情绪**: {intent.get('market_sentiment', 'N/A')}")
            lines.append(f"")
            if intent.get('key_drivers'):
                lines.append(f"**关键驱动因素**:")
                for driver in intent['key_drivers']:
                    lines.append(f"- {driver}")
                lines.append(f"")
            lines.append(f"**置信度**: {intent.get('confidence', 0):.2f}")
            lines.append(f"")
        
        # 市场概览
        lines.append(f"## 市场概览")
        lines.append(f"")
        overview = report['market_overview']
        lines.append(f"- 目标板块数: {overview['total_sectors']}")
        lines.append(f"- 新面孔: {overview['new_faces_count']} 个")
        lines.append(f"- 老面孔: {overview['old_faces_count']} 个")
        lines.append(f"- 先锋板块: {overview['leading_sectors_count']} 个")
        lines.append(f"- 共振板块: {overview['resonance_sectors_count']} 个")
        lines.append(f"- 分离板块: {overview['divergence_sectors_count']} 个")
        lines.append(f"")
        
        # 情绪周期分布
        if overview.get('emotion_cycle_distribution'):
            lines.append(f"**情绪周期分布**:")
            for stage, count in overview['emotion_cycle_distribution'].items():
                lines.append(f"- {stage}: {count} 个")
            lines.append(f"")
        
        # 目标板块详情
        lines.append(f"## 目标板块详情")
        lines.append(f"")
        
        for i, sector in enumerate(report['target_sectors'], 1):
            lines.append(f"### {i}. {sector['sector_name']}")
            lines.append(f"")
            
            # 基础信息
            lines.append(f"**基础信息**:")
            lines.append(f"- 排名: {sector['rank']}")
            lines.append(f"- 强度分数: {sector['strength_score']}")
            # 使用今日涨停数而不是N日涨停数
            today_limit_up = sector.get('today_limit_up', sector['limit_up_count'])
            lines.append(f"- 今日涨停数: {today_limit_up}")
            lines.append(f"- 新旧标记: {'新面孔' if sector['is_new_face'] else f'老面孔（{sector['consecutive_days']}天）'}")
            lines.append(f"")
            
            # 联动分析
            if sector['correlation_analysis']:
                corr = sector['correlation_analysis']
                lines.append(f"**盘面联动**:")
                if corr['is_leading']:
                    lines.append(f"- 先锋板块（领先大盘 {abs(corr['time_lag'])} 分钟）")
                if corr['is_resonance']:
                    lines.append(f"- 强度共振（弹性系数 {corr['elasticity']:.2f}）")
                if corr['is_divergence']:
                    lines.append(f"- 分离板块（逆势上涨）")
                if not (corr['is_leading'] or corr['is_resonance'] or corr['is_divergence']):
                    lines.append(f"- 无明显联动特征")
                lines.append(f"")
            
            # 情绪周期
            if sector['emotion_cycle']:
                emotion = sector['emotion_cycle']
                lines.append(f"**情绪周期**: {emotion['stage']} (置信度: {emotion['confidence']:.2f})")
                lines.append(f"")
                lines.append(f"**判定理由**: {emotion['reasoning']}")
                lines.append(f"")
                if emotion['key_indicators']:
                    lines.append(f"**关键指标**:")
                    for indicator in emotion['key_indicators']:
                        lines.append(f"- {indicator}")
                    lines.append(f"")
                lines.append(f"**风险等级**: {emotion['risk_level']}")
                lines.append(f"")
                lines.append(f"**机会等级**: {emotion['opportunity_level']}")
                lines.append(f"")
            
            # 容量画像
            if sector['capacity_profile']:
                capacity = sector['capacity_profile']
                lines.append(f"**容量画像**:")
                # 将容量类型转换为中文显示
                capacity_type_cn = {
                    'LARGE_CAP': '大容量主线',
                    'MEDIUM_CAP': '中容量题材',
                    'SMALL_CAP': '小容量投机'
                }.get(capacity['capacity_type'], capacity['capacity_type'])
                lines.append(f"- 容量类型: {capacity_type_cn}")
                lines.append(f"- 板块成交额: {capacity['sector_turnover']:.2f} 亿元")
                lines.append(f"- 核心中军成交额: {capacity['leading_stock_turnover']:.2f} 亿元")
                lines.append(f"- 结构健康度: {capacity['structure_health']:.2f}")
                lines.append(f"- 持续性评分: {capacity['sustainability_score']:.2f}")
                lines.append(f"")

                pyramid = capacity['pyramid_structure']
                lines.append(f"**连板梯队**:")
                lines.append(f"- 5板及以上: {pyramid['board_5_plus']} 只")
                lines.append(f"- 3-4板: {pyramid['board_3_to_4']} 只")
                lines.append(f"- 1-2板: {pyramid['board_1_to_2']} 只")
                if pyramid['gaps']:
                    lines.append(f"- 断层: {', '.join(map(str, pyramid['gaps']))}板")
                lines.append(f"")

            # 核心个股分析
            if sector['core_stocks']:
                core_stocks = sector['core_stocks']
                lines.append(f"**核心个股分析**:")
                lines.append(f"")

                # 龙头股识别（空间龙、中军、先锋龙）
                if core_stocks.get('core_leaders'):
                    lines.append(f"*龙头股识别*:")

                    # 空间龙（最多4个）
                    space_dragons = core_stocks.get('space_dragons', [])
                    if space_dragons:
                        lines.append(f"- **空间龙**（最高连板，至少2板）:")
                        for dragon in space_dragons:
                            lines.append(f"  - {dragon['name']} ({dragon['code']}) | "
                                       f"{dragon['consecutive_days']} | "
                                       f"成交{dragon['turnover']:.2f}亿 | "
                                       f"流通市值{dragon['market_cap']:.2f}亿 | "
                                       f"换手{dragon['actual_turnover_rate']:.2f}% | "
                                       f"封单{dragon['seal_amount']:.2f}亿")

                    # 中军（最多2个）
                    zhongjun_list = core_stocks.get('zhongjun_list', [])
                    if zhongjun_list:
                        lines.append(f"- **中军**（市值最大）:")
                        for zj in zhongjun_list:
                            lines.append(f"  - {zj['name']} ({zj['code']}) | "
                                       f"{zj['consecutive_days']} | "
                                       f"流通市值{zj['market_cap']:.2f}亿 | "
                                       f"成交{zj['turnover']:.2f}亿 | "
                                       f"换手{zj['actual_turnover_rate']:.2f}%")

                    # 先锋龙（最多2个）
                    pioneer_list = core_stocks.get('pioneer_list', [])
                    if pioneer_list:
                        lines.append(f"- **先锋龙**（最早封板）:")
                        for pioneer in pioneer_list:
                            lines.append(f"  - {pioneer['name']} ({pioneer['code']}) | "
                                       f"{pioneer['consecutive_days']} | "
                                       f"首次封板{pioneer['first_seal_time']} | "
                                       f"成交{pioneer['turnover']:.2f}亿")

                    # 如果没有符合条件的龙头股
                    if not space_dragons and not zhongjun_list and not pioneer_list:
                        lines.append(f"- 该板块暂无符合条件的龙头股（空间龙需至少2板）")

                    lines.append(f"")

                # 涨停股票表格（删除代码和涨幅，添加大单净流入、首次涨停时间等）
                if core_stocks.get('all_limit_up_stocks'):
                    lines.append(f"*涨停个股表现*:")
                    lines.append(f"")
                    # 表头：删除代码、涨幅，添加大单净流入、首次涨停时间、开板次数、实际换手
                    lines.append(f"| 名称 | 连板状态 | 成交额(亿) | 流通市值(亿) | 收盘封单(亿) | 大单净流入(亿) | 首次涨停 | 开板次数 | 实际换手(%) |")
                    lines.append(f"|------|----------|------------|--------------|--------------|----------------|----------|----------|-------------|")

                    for stock in core_stocks['all_limit_up_stocks'][:10]:  # 最多显示10只
                        lines.append(
                            f"| {stock['name']} | {stock['consecutive_days']} | "
                            f"{stock['turnover']:.2f} | {stock['market_cap']:.2f} | "
                            f"{stock['seal_amount']:.2f} | {stock.get('big_order_net', 0):+.2f} | "
                            f"{stock.get('first_seal_time', '-')} | {stock.get('open_count', 0)} | "
                            f"{stock.get('actual_turnover_rate', 0):.2f} |"
                        )
                    lines.append(f"")

                # 主龙头股详情
                if core_stocks.get('leading_stock'):
                    leading = core_stocks['leading_stock']
                    lines.append(f"*主龙头股*: **{leading['name']} ({leading['code']})**")
                    lines.append(f"- 连板状态: {leading['consecutive_days']}")
                    lines.append(f"- 成交额: {leading['turnover']:.2f} 亿元")
                    lines.append(f"- 流通市值: {leading['market_cap']:.2f} 亿元")
                    lines.append(f"- 实际换手: {leading.get('actual_turnover_rate', 0):.2f}%")
                    lines.append(f"- 收盘封单: {leading['seal_amount']:.2f} 亿元")
                    lines.append(f"- 大单净流入: {leading.get('big_order_net', 0):+.2f} 亿元")
                    if leading.get('first_seal_time'):
                        lines.append(f"- 首次涨停: {leading['first_seal_time']}")
                    if leading.get('last_seal_time'):
                        lines.append(f"- 最终涨停: {leading['last_seal_time']}")
                    if leading.get('open_count', 0) > 0:
                        lines.append(f"- 开板次数: {leading['open_count']}")
                    lines.append(f"")
            
            # 持续性评估
            if sector['sustainability_evaluation']:
                evaluation = sector['sustainability_evaluation']
                lines.append(f"**持续性评估**:")
                lines.append(f"- 持续性评分: {evaluation['sustainability_score']:.2f}/100")
                lines.append(f"- 预期持续时间: {evaluation['time_horizon']}")
                lines.append(f"")
                
                if evaluation['support_factors']:
                    lines.append(f"**支撑因素**:")
                    for factor in evaluation['support_factors']:
                        lines.append(f"- {factor}")
                    lines.append(f"")
                
                if evaluation['risk_factors']:
                    lines.append(f"**风险因素**:")
                    for factor in evaluation['risk_factors']:
                        lines.append(f"- {factor}")
                    lines.append(f"")
                
                lines.append(f"**评估理由**: {evaluation['reasoning']}")
                lines.append(f"")
            
            # 操作建议
            if sector['trading_advice']:
                advice = sector['trading_advice']
                lines.append(f"**操作建议**:")
                lines.append(f"- 操作方向: {advice['action']}")
                lines.append(f"- 入场时机: {advice['entry_timing']}")
                lines.append(f"- 出场策略: {advice['exit_strategy']}")
                lines.append(f"- 仓位建议: {advice['position_sizing']}")
                lines.append(f"")
                lines.append(f"**风险提示**: {advice['risk_warning']}")
                lines.append(f"")
                lines.append(f"**建议理由**: {advice['reasoning']}")
                lines.append(f"")
            
            lines.append(f"---")
            lines.append(f"")
        
        # 风险提示
        if report['risk_warnings']:
            lines.append(f"## 风险提示")
            lines.append(f"")
            for warning in report['risk_warnings']:
                lines.append(f"- {warning}")
            lines.append(f"")
        
        # 免责声明
        lines.append(f"## 免责声明")
        lines.append(f"")
        lines.append(f"本报告由AI系统自动生成，仅供参考，不构成投资建议。")
        lines.append(f"投资有风险，入市需谨慎。")
        lines.append(f"")
        
        return "\n".join(lines)
