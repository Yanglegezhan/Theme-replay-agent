# -*- coding: utf-8 -*-
"""
Theme Anchor Agent CLI

命令行接口，用于执行题材锚定分析
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.data import KaipanlaDataSource, HistoryTracker
from src.llm import LLMAnalyzer
from src.agent import ThemeAnchorAgent, AgentConfig
from src.output import ReportGenerator


class ThemeCLI:
    """Theme Anchor Agent命令行接口"""
    
    def __init__(self):
        """初始化CLI"""
        self.config_manager: Optional[ConfigManager] = None
        self.logger: Optional[logging.Logger] = None
    
    def setup_logging(self, config: ConfigManager) -> None:
        """配置日志系统
        
        Args:
            config: 配置管理器
        """
        log_config = config.get_logging_config()
        
        # 创建日志目录
        log_file = log_config.get('file', 'logs/theme_anchor_agent.log')
        log_path = project_root / log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 配置日志格式
        log_format = log_config.get(
            'format',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        
        # 配置根日志记录器
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[]
        )
        
        # 添加文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=log_config.get('max_bytes', 10485760),  # 10MB
            backupCount=log_config.get('backup_count', 5),
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)
        
        # 添加控制台处理器（如果启用）
        if log_config.get('console_output', True):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(log_format))
            logging.getLogger().addHandler(console_handler)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("日志系统初始化完成")
    
    def parse_arguments(self) -> argparse.Namespace:
        """解析命令行参数
        
        Returns:
            解析后的参数
        """
        parser = argparse.ArgumentParser(
            description='A股超短线题材锚定Agent - 智能市场分析系统',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  # 分析今天的市场
  python theme_cli.py
  
  # 分析指定日期
  python theme_cli.py --date 2026-01-20
  
  # 分析昨天的市场
  python theme_cli.py --yesterday
  
  # 使用自定义配置文件
  python theme_cli.py --config /path/to/config.yaml
  
  # 只输出JSON格式
  python theme_cli.py --format json
  
  # 指定输出目录
  python theme_cli.py --output /path/to/output
            """
        )
        
        # 日期参数
        date_group = parser.add_mutually_exclusive_group()
        date_group.add_argument(
            '-d', '--date',
            type=str,
            help='分析日期 (格式: YYYY-MM-DD)，默认为今天'
        )
        date_group.add_argument(
            '-y', '--yesterday',
            action='store_true',
            help='分析昨天的市场'
        )
        
        # 配置文件
        parser.add_argument(
            '-c', '--config',
            type=str,
            help='配置文件路径，默认为 config/config.yaml'
        )
        
        # 输出格式
        parser.add_argument(
            '-f', '--format',
            type=str,
            choices=['markdown', 'json', 'both'],
            default='both',
            help='输出格式 (默认: both)'
        )
        
        # 输出目录
        parser.add_argument(
            '-o', '--output',
            type=str,
            help='输出目录，默认为 output/reports'
        )
        
        # 详细模式
        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='详细输出模式'
        )
        
        # 静默模式
        parser.add_argument(
            '-q', '--quiet',
            action='store_true',
            help='静默模式（只输出错误）'
        )
        
        # 不保存报告
        parser.add_argument(
            '--no-save',
            action='store_true',
            help='不保存报告文件（只在控制台显示）'
        )
        
        return parser.parse_args()
    
    def validate_date(self, date_str: str) -> str:
        """验证日期格式
        
        Args:
            date_str: 日期字符串
            
        Returns:
            验证后的日期字符串
            
        Raises:
            ValueError: 日期格式错误
        """
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            raise ValueError(f"日期格式错误: {date_str}，应为 YYYY-MM-DD")
    
    def get_analysis_date(self, args: argparse.Namespace) -> str:
        """获取分析日期
        
        Args:
            args: 命令行参数
            
        Returns:
            分析日期字符串
        """
        if args.yesterday:
            date = datetime.now() - timedelta(days=1)
            return date.strftime('%Y-%m-%d')
        elif args.date:
            return self.validate_date(args.date)
        else:
            return datetime.now().strftime('%Y-%m-%d')
    
    def load_config(self, config_path: Optional[str] = None) -> ConfigManager:
        """加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置管理器
        """
        try:
            if config_path:
                config = ConfigManager(config_path)
                print(f"[OK] 已加载配置文件: {config_path}")
            else:
                config = ConfigManager()
                print(f"[OK] 已加载默认配置文件")
            
            return config
        except FileNotFoundError as e:
            print(f"[ERROR] 配置文件未找到: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] 加载配置文件失败: {e}")
            sys.exit(1)
    
    def initialize_components(
        self,
        config: ConfigManager
    ) -> tuple:
        """初始化系统组件
        
        Args:
            config: 配置管理器
            
        Returns:
            (data_source, history_tracker, llm_analyzer, agent_config)
        """
        self.logger.info("初始化系统组件...")
        
        # 1. 初始化数据源
        print("  [1/4] 初始化数据源...")
        data_source = KaipanlaDataSource()
        
        # 2. 初始化历史追踪器
        print("  [2/4] 初始化历史追踪器...")
        history_config = config.get('history', {})
        storage_path = history_config.get('storage_path', 'data/history')
        history_path = project_root / storage_path / 'sector_rankings.csv'
        history_tracker = HistoryTracker(storage_path=str(history_path))
        
        # 3. 初始化LLM分析器
        print("  [3/4] 初始化LLM分析器...")
        llm_config = config.get_llm_config()
        
        if not llm_config.get('api_key'):
            self.logger.error("LLM API密钥未配置")
            print("[ERROR] 错误: LLM API密钥未配置，请在配置文件中设置 llm.api_key")
            sys.exit(1)
        
        llm_analyzer = LLMAnalyzer(
            api_key=llm_config['api_key'],
            provider=llm_config.get('provider', 'openai'),
            model_name=llm_config.get('model_name', 'gpt-4'),
            temperature=llm_config.get('temperature', 0.7),
            max_tokens=llm_config.get('max_tokens'),
            timeout=llm_config.get('timeout'),
            request_delay=llm_config.get('request_delay', 2.0)  # 添加请求延迟配置
        )
        
        # 4. 配置Agent参数
        print("  [4/4] 配置Agent参数...")
        analysis_config = config.get_analysis_config()
        
        sector_filter_config = analysis_config.get('sector_filter', {})
        correlation_config = analysis_config.get('correlation', {})
        capacity_config = analysis_config.get('capacity', {})
        
        agent_config = AgentConfig(
            high_strength_threshold=sector_filter_config.get('high_strength_threshold', 8000),
            medium_strength_min=sector_filter_config.get('medium_strength_threshold', 2000),
            target_sector_count=sector_filter_config.get('target_sector_count', 7),
            ndays_lookback=sector_filter_config.get('ndays', 7),
            leading_time_lag_min=correlation_config.get('leading_time_min', 5),
            leading_time_lag_max=correlation_config.get('leading_time_max', 10),
            resonance_elasticity_threshold=correlation_config.get('resonance_elasticity_threshold', 3.0),
            divergence_threshold=correlation_config.get('market_change_threshold', 0.01),
            large_cap_turnover_threshold=capacity_config.get('large_cap_turnover_threshold', 30.0),
            health_score_gap_penalty=0.2
        )
        
        print("[OK] 系统组件初始化完成")
        
        return data_source, history_tracker, llm_analyzer, agent_config
    
    def run_analysis(
        self,
        date: str,
        data_source: KaipanlaDataSource,
        history_tracker: HistoryTracker,
        llm_analyzer: LLMAnalyzer,
        agent_config: AgentConfig
    ):
        """执行分析流程
        
        Args:
            date: 分析日期
            data_source: 数据源
            history_tracker: 历史追踪器
            llm_analyzer: LLM分析器
            agent_config: Agent配置
            
        Returns:
            分析报告
        """
        self.logger.info(f"开始分析: {date}")
        print(f"\n{'=' * 80}")
        print(f"开始分析: {date}")
        print(f"{'=' * 80}\n")
        
        # 初始化Agent
        agent = ThemeAnchorAgent(
            data_source=data_source,
            history_tracker=history_tracker,
            llm_analyzer=llm_analyzer,
            config=agent_config
        )
        
        # 执行分析
        try:
            report = agent.analyze(date=date)
            print(f"\n{'=' * 80}")
            print(f"分析完成")
            print(f"{'=' * 80}\n")
            return report
        except Exception as e:
            self.logger.error(f"分析失败: {e}", exc_info=True)
            print(f"\n[ERROR] 分析失败: {e}")
            sys.exit(1)
    
    def save_report(
        self,
        report,
        output_format: str,
        output_dir: Optional[str],
        config: ConfigManager
    ) -> None:
        """保存分析报告
        
        Args:
            report: 分析报告
            output_format: 输出格式
            output_dir: 输出目录
            config: 配置管理器
        """
        # 确定输出目录
        if output_dir:
            report_dir = Path(output_dir)
        else:
            output_config = config.get_output_config()
            report_dir = project_root / output_config.get('report_dir', 'output/reports')
        
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成报告
        generator = ReportGenerator()
        structured_report = generator.generate_report(report)
        
        # 保存报告
        date_str = report.date.replace('-', '')
        
        if output_format in ['markdown', 'both']:
            md_path = report_dir / f"theme_analysis_{date_str}.md"
            generator.export_markdown(structured_report, str(md_path))
            print(f"[OK] Markdown报告已保存: {md_path}")
        
        if output_format in ['json', 'both']:
            json_path = report_dir / f"theme_analysis_{date_str}.json"
            generator.export_json(structured_report, str(json_path))
            print(f"[OK] JSON报告已保存: {json_path}")
    
    def display_summary(self, report) -> None:
        """显示分析摘要
        
        Args:
            report: 分析报告
        """
        print(f"\n{'=' * 80}")
        print(f"分析摘要")
        print(f"{'=' * 80}\n")
        
        print(f"日期: {report.date}")
        print(f"\n{report.executive_summary}\n")
        
        # 目标板块
        print(f"目标板块 ({len(report.filter_result.target_sectors)}个):")
        for i, sector in enumerate(report.filter_result.target_sectors[:5], 1):
            is_new = sector.sector_name in report.filter_result.new_faces
            face_type = "新面孔" if is_new else "老面孔"
            
            # 情绪周期
            emotion_stage = "未知"
            if sector.sector_name in report.emotion_cycles:
                emotion_stage = report.emotion_cycles[sector.sector_name].stage
            
            print(f"  {i}. {sector.sector_name} ({face_type}) - {emotion_stage}")
            print(f"     强度: {sector.strength_score}, 涨停数: {sector.ndays_limit_up}")
        
        if len(report.filter_result.target_sectors) > 5:
            print(f"  ... 还有 {len(report.filter_result.target_sectors) - 5} 个板块")
        
        # 风险提示
        if report.risk_warnings:
            print(f"\n风险提示 ({len(report.risk_warnings)}条):")
            for warning in report.risk_warnings[:3]:
                print(f"  [WARNING] {warning}")
            if len(report.risk_warnings) > 3:
                print(f"  ... 还有 {len(report.risk_warnings) - 3} 条风险提示")
        
        print(f"\n{'=' * 80}\n")
    
    def run(self) -> int:
        """运行CLI
        
        Returns:
            退出码 (0表示成功)
        """
        # 解析参数
        args = self.parse_arguments()
        
        # 调整日志级别
        if args.quiet:
            logging.getLogger().setLevel(logging.ERROR)
        elif args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # 加载配置
        self.config_manager = self.load_config(args.config)
        
        # 设置日志
        self.setup_logging(self.config_manager)
        
        # 获取分析日期
        analysis_date = self.get_analysis_date(args)
        print(f"\n分析日期: {analysis_date}")
        
        # 初始化组件
        print(f"\n初始化系统组件...")
        data_source, history_tracker, llm_analyzer, agent_config = \
            self.initialize_components(self.config_manager)
        
        # 执行分析
        report = self.run_analysis(
            date=analysis_date,
            data_source=data_source,
            history_tracker=history_tracker,
            llm_analyzer=llm_analyzer,
            agent_config=agent_config
        )
        
        # 显示摘要
        if not args.quiet:
            self.display_summary(report)
        
        # 保存报告
        if not args.no_save:
            print(f"保存分析报告...")
            self.save_report(
                report=report,
                output_format=args.format,
                output_dir=args.output,
                config=self.config_manager
            )
        
        print(f"\n[OK] 所有任务完成\n")
        return 0


def main():
    """主入口函数"""
    # 需要导入logging.handlers
    import logging.handlers
    
    cli = ThemeCLI()
    try:
        sys.exit(cli.run())
    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] 用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
