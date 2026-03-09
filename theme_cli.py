#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Theme Anchor Agent CLI Entry Point

便捷的命令行入口脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.cli import main

if __name__ == '__main__':
    main()
