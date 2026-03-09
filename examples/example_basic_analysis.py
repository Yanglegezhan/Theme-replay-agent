"""
基础分析示例

演示如何使用Theme Anchor Agent进行基本的市场分析。
这是最简单的使用方式，适合快速上手。
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent import ThemeAnchorAgent
from src.data import KaipanlaDataSource, HistoryTracker
from src.llm import LLMAnalyzer, PromptEngine, ContextBuilder
from src.output import ReportGenerator
from config import ConfigManager


def main():
    """基础分析示例主函数"""
    
    print("=" * 60)
    print("Theme Anchor Agent - 基础分析示例")
    print("=" * 60)
    print()
    
    # 1. 加载配置
    print("📋 步骤1: 加载配置...")
    config = ConfigManager()
    print(f"   ✓ LLM提供商: {config.get('llm.provider')}")
    print(f"   ✓ 模型: {config.get('llm.model_name')}")
    print()
    
    # 2. 初始化数据源
    print("📊 步骤2: 初始化数据源...")
    data_source = KaipanlaDataSource()
    print("   ✓ 主数据源: kaipanla")
    print("   ✓ 备用数据源: akshare")
    print()
    
    # 3. 初始化历史追踪器
    print("📚 步骤3: 初始化历史追踪器...")
    history_path = config.get("history.storage_path", "data/history")
    history_tracker = HistoryTracker(history_path)
    print(f"   ✓ 历史数据路径: {history_path}")
    print()
    
    # 4. 初始化LLM组件
    print("🤖 步骤4: 初始化LLM分析引擎...")
    prompt_engine = PromptEngine()
    context_builder = ContextBuilder()
    llm_analyzer = LLMAnalyzer(
        api_key=config.get("llm.api_key"),
        provider=config.get("llm.provider"),
        model_name=config.get("llm.model_name"),
        temperature=config.get("llm.temperature", 0.7),
        max_tokens=config.get("llm.max_tokens"),
        timeout=config.get("llm.timeout"),
        max_retries=config.get("llm.max_retries", 3),
        prompt_engine=prompt_engine
    )
    print("   ✓ LLM分析引擎已就绪")
    print()
    
    # 5. 创建Agent
    print("🎯 步骤5: 创建Theme Anchor Agent...")
    agent = ThemeAnchorAgent(
        data_source=data_source,
        history_tracker=history_tracker,
        llm_analyzer=llm_analyzer,
        context_builder=context_builder,
        config=config
    )
    print("   ✓ Agent已创建")
    print()
    
    # 6. 执行分析
    date = datetime.now().strftime("%Y-%m-%d")
    print(f"🔍 步骤6: 执行市场分析 (日期: {date})...")
    print("   这可能需要几分钟时间，请耐心等待...")
    print()
    
    try:
        report = agent.analyze(date)
        
        # 7. 显示分析结果
        print("=" * 60)
        print("📊 分析结果")
        print("=" * 60)
        print()
        
        print(f"分析日期: {report.date}")
        print(f"目标板块数量: {len(report.target_sectors)}")
        print()
        
        print("🎯 目标板块列表:")
        print("-" * 60)
        for i, sector in enumerate(report.target_sectors, 1):
            print(f"{i}. {sector.sector_name}")
            print(f"   强度分数: {sector.strength_score}")
            print(f"   新旧标记: {'🆕 新面孔' if sector.is_new_face else f'🔄 老面孔 (连续{sector.consecutive_days}天)'}")
            
            if sector.emotion_cycle:
                print(f"   情绪周期: {sector.emotion_cycle.stage}")
                print(f"   风险等级: {sector.emotion_cycle.risk_level}")
                print(f"   机会等级: {sector.emotion_cycle.opportunity_level}")
            
            if sector.capacity_profile:
                print(f"   容量类型: {sector.capacity_profile.capacity_type}")
                print(f"   板块成交额: {sector.capacity_profile.sector_turnover:.2f}亿")
            
            if sector.trading_advice:
                print(f"   操作建议: {sector.trading_advice.action}")
            
            print()
        
        # 8. 生成报告
        print("=" * 60)
        print("📝 步骤7: 生成分析报告...")
        print("=" * 60)
        print()
        
        report_generator = ReportGenerator()
        output_dir = config.get("output.report_dir", "output/reports")
        
        # 生成Markdown报告
        md_path = report_generator.export_markdown(report, output_dir)
        print(f"   ✓ Markdown报告: {md_path}")
        
        # 生成JSON报告
        json_path = report_generator.export_json(report, output_dir)
        print(f"   ✓ JSON报告: {json_path}")
        print()
        
        print("=" * 60)
        print("✅ 分析完成！")
        print("=" * 60)
        print()
        print(f"请查看报告文件获取详细分析结果：")
        print(f"  - Markdown: {md_path}")
        print(f"  - JSON: {json_path}")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
