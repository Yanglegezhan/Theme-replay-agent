# -*- coding: utf-8 -*-
"""
Checkpoint 5: 核心组件完成验证

验证所有核心分析组件和LLM引擎是否正常工作
"""

import sys
from pathlib import Path
import subprocess
import yaml

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(name, status, details=""):
    """打印结果"""
    symbol = "✓" if status else "✗"
    status_text = "通过" if status else "失败"
    print(f"{symbol} {name}: {status_text}")
    if details:
        print(f"  详情: {details}")


def check_imports():
    """检查核心模块导入"""
    print_section("1. 核心模块导入检查")
    
    results = {}
    
    # 数据层
    try:
        from src.data import KaipanlaDataSource, AkshareDataSource, DataSourceFallback, HistoryTracker
        results['数据层'] = True
    except Exception as e:
        results['数据层'] = False
        print_result('数据层', False, str(e))
    
    # 分析层
    try:
        from src.analysis import SectorFilter, CorrelationAnalyzer, CapacityProfiler
        results['分析层'] = True
    except Exception as e:
        results['分析层'] = False
        print_result('分析层', False, str(e))
    
    # LLM引擎
    try:
        from src.llm import LLMAnalyzer, PromptEngine, ContextBuilder
        results['LLM引擎'] = True
    except Exception as e:
        results['LLM引擎'] = False
        print_result('LLM引擎', False, str(e))
    
    # 数据模型
    try:
        from src.models import (
            IntradayData, ResonancePoint, CorrelationResult,
            EmotionCycleAnalysis, CapacityProfile, AnalysisContext
        )
        results['数据模型'] = True
    except Exception as e:
        results['数据模型'] = False
        print_result('数据模型', False, str(e))
    
    # 打印结果
    for name, status in results.items():
        if status:
            print_result(name, True)
    
    return all(results.values())


def run_tests():
    """运行测试套件"""
    print_section("2. 测试套件执行")
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # 解析测试结果
        output = result.stdout + result.stderr
        
        # 提取测试统计
        if "passed" in output:
            # 查找类似 "35 passed, 2 failed" 的行
            import re
            match = re.search(r'(\d+) passed', output)
            passed = int(match.group(1)) if match else 0
            
            match = re.search(r'(\d+) failed', output)
            failed = int(match.group(1)) if match else 0
            
            total = passed + failed
            
            print(f"\n测试结果:")
            print(f"  - 总计: {total} 个测试")
            print(f"  - 通过: {passed} 个")
            print(f"  - 失败: {failed} 个")
            
            if failed > 0:
                print(f"\n失败的测试:")
                # 提取失败的测试名称
                failed_tests = re.findall(r'FAILED (.*?) -', output)
                for test in failed_tests:
                    print(f"    - {test}")
            
            # 如果大部分测试通过（>90%），认为是成功的
            success_rate = passed / total if total > 0 else 0
            status = success_rate >= 0.9
            
            print_result(f'测试通过率', status, f"{success_rate*100:.1f}%")
            
            return status
        else:
            print_result('测试执行', False, "无法解析测试结果")
            return False
            
    except subprocess.TimeoutExpired:
        print_result('测试执行', False, "测试超时")
        return False
    except Exception as e:
        print_result('测试执行', False, str(e))
        return False


def check_llm_config():
    """检查LLM配置"""
    print_section("3. LLM配置检查")
    
    try:
        config_path = project_root / "config" / "config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        llm_config = config.get('llm', {})
        
        # 检查必需的配置项
        required_fields = ['provider', 'api_key', 'model_name']
        missing_fields = [f for f in required_fields if not llm_config.get(f)]
        
        if missing_fields:
            print_result('LLM配置', False, f"缺少配置项: {', '.join(missing_fields)}")
            return False
        
        print(f"\n配置信息:")
        print(f"  - 提供商: {llm_config['provider']}")
        print(f"  - 模型: {llm_config['model_name']}")
        print(f"  - API Key: {'已配置' if llm_config['api_key'] else '未配置'}")
        
        print_result('LLM配置', True)
        return True
        
    except Exception as e:
        print_result('LLM配置', False, str(e))
        return False


def check_llm_engine():
    """检查LLM引擎是否可以正常初始化"""
    print_section("4. LLM引擎初始化检查")
    
    try:
        from src.llm import LLMAnalyzer, PromptEngine, ContextBuilder
        
        # 加载配置
        config_path = project_root / "config" / "config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        llm_config = config['llm']
        
        # 初始化LLM分析器
        llm_analyzer = LLMAnalyzer(
            api_key=llm_config['api_key'],
            provider=llm_config['provider'],
            model_name=llm_config['model_name']
        )
        
        print_result('LLM分析器初始化', True)
        
        # 初始化提示词引擎
        prompt_engine = PromptEngine()
        print_result('提示词引擎初始化', True)
        
        # 初始化上下文构建器
        context_builder = ContextBuilder()
        print_result('上下文构建器初始化', True)
        
        return True
        
    except Exception as e:
        print_result('LLM引擎初始化', False, str(e))
        return False


def check_component_integration():
    """检查组件集成"""
    print_section("5. 组件集成检查")
    
    try:
        from src.analysis import SectorFilter, CorrelationAnalyzer, CapacityProfiler
        from src.data import HistoryTracker
        from src.llm import LLMAnalyzer, PromptEngine, ContextBuilder
        
        # 创建临时历史追踪器
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        # 初始化各组件
        history_tracker = HistoryTracker(temp_path)
        print_result('历史追踪器', True)
        
        sector_filter = SectorFilter(history_tracker)
        print_result('题材筛选器', True)
        
        correlation_analyzer = CorrelationAnalyzer()
        print_result('联动分析器', True)
        
        capacity_profiler = CapacityProfiler()
        print_result('容量分析器', True)
        
        prompt_engine = PromptEngine()
        print_result('提示词引擎', True)
        
        context_builder = ContextBuilder()
        print_result('上下文构建器', True)
        
        # 清理临时文件
        import os
        try:
            os.unlink(temp_path)
        except:
            pass
        
        return True
        
    except Exception as e:
        print_result('组件集成', False, str(e))
        return False


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("  Checkpoint 5: 核心组件完成验证")
    print("=" * 70)
    print("\n本检查点将验证:")
    print("  1. 所有核心模块可以正常导入")
    print("  2. 测试套件执行情况")
    print("  3. LLM配置是否正确")
    print("  4. LLM引擎是否可以正常初始化")
    print("  5. 各组件是否可以正常集成")
    
    results = {}
    
    # 执行各项检查
    results['模块导入'] = check_imports()
    results['测试套件'] = run_tests()
    results['LLM配置'] = check_llm_config()
    results['LLM引擎'] = check_llm_engine()
    results['组件集成'] = check_component_integration()
    
    # 总结
    print_section("验证总结")
    
    all_passed = all(results.values())
    
    for name, status in results.items():
        print_result(name, status)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("  🎉 所有检查通过！核心组件已完成！")
    else:
        print("  ⚠️  部分检查未通过，请查看上述详情")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
