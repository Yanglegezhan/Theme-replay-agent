# 项目结构说明

## 目录结构

```
Theme_repay_agent/
├── config/                          # 配置文件目录
│   ├── __init__.py
│   ├── config_manager.py           # 配置管理器
│   ├── config.example.yaml         # 配置模板
│   └── config.yaml                 # 实际配置（需手动创建）
│
├── src/                            # 源代码目录
│   ├── __init__.py
│   │
│   ├── data/                       # 数据层
│   │   ├── __init__.py
│   │   ├── kaipanla_source.py     # 开盘啦数据源
│   │   ├── akshare_source.py      # akshare数据源
│   │   ├── data_fallback.py       # 数据源降级管理
│   │   ├── history_tracker.py     # 历史数据追踪
│   │   └── validators.py          # 数据验证
│   │
│   ├── analysis/                   # 分析层
│   │   ├── __init__.py
│   │   ├── sector_filter.py       # 题材筛选
│   │   ├── correlation_analyzer.py # 盘面联动分析
│   │   ├── capacity_profiler.py   # 容量结构分析
│   │   └── utils.py               # 分析工具函数
│   │
│   ├── llm/                        # LLM集成层
│   │   ├── __init__.py
│   │   ├── llm_analyzer.py        # LLM分析引擎
│   │   ├── prompt_engine.py       # 提示词引擎
│   │   ├── context_builder.py     # 上下文构建器
│   │   └── providers/             # LLM提供商适配器
│   │       ├── __init__.py
│   │       ├── openai_provider.py
│   │       ├── zhipu_provider.py
│   │       └── qwen_provider.py
│   │
│   ├── agent/                      # Agent协调层
│   │   ├── __init__.py
│   │   ├── theme_anchor_agent.py  # 核心Agent
│   │   └── orchestrator.py        # 流程编排器
│   │
│   ├── output/                     # 输出层
│   │   ├── __init__.py
│   │   ├── report_generator.py    # 报告生成器
│   │   └── exporters.py           # 导出器（Markdown/JSON）
│   │
│   ├── models/                     # 数据模型
│   │   ├── __init__.py
│   │   ├── sector.py              # 板块相关模型
│   │   ├── analysis.py            # 分析结果模型
│   │   ├── llm.py                 # LLM相关模型
│   │   └── report.py              # 报告模型
│   │
│   ├── cli/                        # 命令行接口
│   │   ├── __init__.py
│   │   └── theme_cli.py           # CLI主程序
│   │
│   └── utils/                      # 工具函数
│       ├── __init__.py
│       ├── logger.py              # 日志工具
│       ├── date_utils.py          # 日期工具
│       └── validators.py          # 验证工具
│
├── prompts/                        # LLM提示词模板
│   ├── README.md
│   ├── market_intent.md           # 资金意图分析模板
│   ├── emotion_cycle.md           # 情绪周期分析模板
│   ├── sustainability.md          # 持续性评估模板
│   └── trading_advice.md          # 操作建议模板
│
├── tests/                          # 测试代码
│   ├── __init__.py
│   ├── test_data/                 # 数据层测试
│   ├── test_analysis/             # 分析层测试
│   ├── test_llm/                  # LLM层测试
│   ├── test_agent/                # Agent层测试
│   └── test_integration/          # 集成测试
│
├── examples/                       # 示例代码
│   ├── __init__.py
│   ├── example_basic_analysis.py  # 基础分析示例
│   ├── example_custom_prompts.py  # 自定义提示词示例
│   └── example_llm_config.py      # LLM配置示例
│
├── data/                           # 数据存储
│   └── history/                   # 历史数据
│       └── .gitkeep
│
├── output/                         # 输出目录
│   └── reports/                   # 分析报告
│       └── .gitkeep
│
├── logs/                           # 日志文件
│   └── .gitkeep
│
├── docs/                           # 文档（可选）
│   ├── QUICKSTART.md              # 快速开始
│   ├── PROMPT_ENGINEERING.md      # 提示词工程
│   └── LLM_INTEGRATION.md         # LLM集成指南
│
├── .gitignore                      # Git忽略文件
├── README.md                       # 项目说明
├── PROJECT_STRUCTURE.md            # 本文件
├── pyproject.toml                  # 项目配置
└── setup.py                        # 安装脚本（可选）
```

## 模块说明

### 数据层 (src/data/)

负责数据获取和管理：
- **kaipanla_source.py**: 封装开盘啦API，获取涨停、连板等专业数据
- **akshare_source.py**: 封装akshare接口，作为备用数据源
- **data_fallback.py**: 实现主备数据源降级逻辑
- **history_tracker.py**: 管理板块历史排名数据的持久化

### 分析层 (src/analysis/)

实现四大分析维度：
- **sector_filter.py**: 题材筛选，识别强势板块
- **correlation_analyzer.py**: 盘面联动分析，识别先锋板块
- **capacity_profiler.py**: 容量结构分析，评估题材健康度

### LLM层 (src/llm/)

LLM集成和提示词工程：
- **llm_analyzer.py**: LLM分析引擎，调用大模型进行深度分析
- **prompt_engine.py**: 提示词引擎，管理和渲染提示词模板
- **context_builder.py**: 上下文构建器，为LLM准备结构化输入
- **providers/**: 支持多种LLM提供商（OpenAI、智谱、通义千问）

### Agent层 (src/agent/)

协调整个分析流程：
- **theme_anchor_agent.py**: 核心Agent，编排五个分析步骤
- **orchestrator.py**: 流程编排器，管理数据传递

### 输出层 (src/output/)

生成和导出分析报告：
- **report_generator.py**: 报告生成器，整合所有分析结果
- **exporters.py**: 支持Markdown和JSON格式导出

### 模型层 (src/models/)

定义数据结构：
- **sector.py**: 板块相关数据模型
- **analysis.py**: 分析结果数据模型
- **llm.py**: LLM分析相关模型
- **report.py**: 报告数据模型

## 数据流

```
1. CLI接收用户输入（日期）
   ↓
2. Agent初始化，加载配置
   ↓
3. 数据层获取市场数据（kaipanla/akshare）
   ↓
4. 分析层执行四大分析
   ↓
5. LLM层进行深度分析（情绪周期、资金意图、持续性、操作建议）
   ↓
6. Agent整合所有结果
   ↓
7. 输出层生成报告
   ↓
8. 导出为Markdown/JSON
```

## 配置管理

配置文件采用YAML格式，包含：
- LLM配置（API密钥、模型选择）
- 数据源配置（超时、重试）
- 分析参数（阈值、权重）
- 输出配置（格式、路径）
- 日志配置（级别、文件）

## 测试策略

- **单元测试**: 测试各模块的核心功能
- **属性测试**: 使用hypothesis进行属性测试（最少100次迭代）
- **集成测试**: 测试端到端分析流程
- **Mock测试**: 对LLM调用进行Mock测试

## 开发工作流

1. 从requirements.md理解需求
2. 参考design.md实现设计
3. 按tasks.md顺序开发
4. 编写测试确保质量
5. 更新文档保持同步
