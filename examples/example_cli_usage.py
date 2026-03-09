# -*- coding: utf-8 -*-
"""
CLI使用示例

演示如何在Python代码中使用CLI类
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cli import ThemeCLI


def example_basic_usage():
    """示例1: 基本用法"""
    print("=" * 80)
    print("示例1: 基本用法 - 分析今天的市场")
    print("=" * 80)
    
    # 创建CLI实例
    cli = ThemeCLI()
    
    # 模拟命令行参数
    sys.argv = ['theme_cli.py']
    
    # 运行分析
    exit_code = cli.run()
    
    print(f"\n退出码: {exit_code}")


def example_specific_date():
    """示例2: 分析指定日期"""
    print("\n" + "=" * 80)
    print("示例2: 分析指定日期")
    print("=" * 80)
    
    cli = ThemeCLI()
    
    # 模拟命令行参数：分析2026-01-20
    sys.argv = ['theme_cli.py', '--date', '2026-01-20']
    
    exit_code = cli.run()
    
    print(f"\n退出码: {exit_code}")


def example_custom_output():
    """示例3: 自定义输出格式和目录"""
    print("\n" + "=" * 80)
    print("示例3: 自定义输出")
    print("=" * 80)
    
    cli = ThemeCLI()
    
    # 只生成JSON，保存到自定义目录
    sys.argv = [
        'theme_cli.py',
        '--format', 'json',
        '--output', 'output/custom_reports'
    ]
    
    exit_code = cli.run()
    
    print(f"\n退出码: {exit_code}")


def example_no_save():
    """示例4: 不保存报告"""
    print("\n" + "=" * 80)
    print("示例4: 不保存报告（只显示）")
    print("=" * 80)
    
    cli = ThemeCLI()
    
    # 不保存报告，静默模式
    sys.argv = [
        'theme_cli.py',
        '--no-save',
        '--quiet'
    ]
    
    exit_code = cli.run()
    
    print(f"\n退出码: {exit_code}")


def example_programmatic_usage():
    """示例5: 编程方式使用CLI组件"""
    print("\n" + "=" * 80)
    print("示例5: 编程方式使用CLI组件")
    print("=" * 80)
    
    from datetime import datetime
    from config.config_manager import ConfigManager
    from src.data import KaipanlaDataSource, HistoryTracker
    from src.llm import LLMAnalyzer
    from src.agent import ThemeAnchorAgent, AgentConfig
    from src.output import ReportGenerator
    
    # 1. 加载配置
    config = ConfigManager()
    print("✓ 配置加载完成")
    
    # 2. 初始化组件
    data_source = KaipanlaDataSource()
    history_tracker = HistoryTracker(
        storage_path='data/history/sector_rankings.csv'
    )
    
    llm_config = config.get_llm_config()
    llm_analyzer = LLMAnalyzer(
        api_key=llm_config['api_key'],
        provider=llm_config.get('provider', 'openai'),
        model_name=llm_config.get('model_name', 'gpt-4')
    )
    
    agent_config = AgentConfig()
    print("✓ 组件初始化完成")
    
    # 3. 创建Agent
    agent = ThemeAnchorAgent(
        data_source=data_source,
        history_tracker=history_tracker,
        llm_analyzer=llm_analyzer,
        config=agent_config
    )
    print("✓ Agent创建完成")
    
    # 4. 执行分析
    analysis_date = datetime.now().strftime('%Y-%m-%d')
    print(f"\n开始分析: {analysis_date}")
    
    try:
        report = agent.analyze(date=analysis_date)
        print("✓ 分析完成")
        
        # 5. 生成报告
        generator = ReportGenerator()
        structured_report = generator.generate_report(report)
        
        # 6. 保存报告
        generator.export_markdown(
            structured_report,
            f'output/reports/theme_analysis_{analysis_date.replace("-", "")}.md'
        )
        print("✓ 报告已保存")
        
        # 7. 显示摘要
        print(f"\n执行摘要:")
        print(report.executive_summary)
        
    except Exception as e:
        print(f"✗ 分析失败: {e}")


def main():
    """主函数"""
    print("\nCLI使用示例\n")
    
    # 选择要运行的示例
    examples = {
        '1': ('基本用法', example_basic_usage),
        '2': ('分析指定日期', example_specific_date),
        '3': ('自定义输出', example_custom_output),
        '4': ('不保存报告', example_no_save),
        '5': ('编程方式使用', example_programmatic_usage),
    }
    
    print("可用示例:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    choice = input("\n请选择示例 (1-5, 或按Enter运行所有): ").strip()
    
    if choice in examples:
        _, func = examples[choice]
        func()
    elif choice == '':
        # 运行所有示例
        for _, func in examples.values():
            func()
    else:
        print("无效选择")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ 用户中断")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
