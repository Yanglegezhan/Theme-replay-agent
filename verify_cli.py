# -*- coding: utf-8 -*-
"""
CLI验证脚本

验证CLI功能是否正常工作
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'=' * 80}")
    print(f"测试: {description}")
    print(f"命令: {cmd}")
    print(f"{'=' * 80}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(f"\n退出码: {result.returncode}")
        
        if result.stdout:
            print(f"\n标准输出:")
            print(result.stdout)
        
        if result.stderr:
            print(f"\n标准错误:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("✗ 命令超时")
        return False
    except Exception as e:
        print(f"✗ 执行失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("CLI功能验证")
    print("=" * 80)
    
    # 切换到项目目录
    project_dir = Path(__file__).parent
    
    tests = [
        # 1. 帮助信息
        (
            "python theme_cli.py --help",
            "显示帮助信息"
        ),
        
        # 2. 语法检查
        (
            "python -m py_compile src/cli/theme_cli.py",
            "Python语法检查"
        ),
        
        # 3. 导入测试
        (
            "python -c \"from src.cli import ThemeCLI, main; print('Import successful')\"",
            "模块导入测试"
        ),
    ]
    
    results = []
    
    for cmd, description in tests:
        success = run_command(cmd, description)
        results.append((description, success))
    
    # 显示总结
    print(f"\n{'=' * 80}")
    print("验证总结")
    print(f"{'=' * 80}\n")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{status}: {description}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n✓ 所有验证通过！CLI功能正常。")
        return 0
    else:
        print(f"\n✗ {total - passed} 个测试失败。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
