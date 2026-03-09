# A股超短线题材锚定Agent

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

智能市场分析系统，模拟资深游资操盘手的决策思维，通过多维度数据解构识别当日热点题材。

## ✨ 功能特性

- **🎯 题材筛选**: 自动识别强势板块，区分新面孔和老面孔
- **🔗 盘面联动**: 分析板块与大盘的联动关系，识别先锋板块
- **📊 情绪周期**: 基于LLM判定题材所处的情绪周期阶段
- **💰 容量结构**: 分析题材资金容量和内部结构健康度
- **🤖 智能分析**: 集成LLM进行深度市场分析和操作建议
- **📝 报告生成**: 自动生成Markdown和JSON格式的分析报告
- **🔄 数据降级**: 主备数据源自动切换，确保数据可用性

## 项目结构

```
Theme_repay_agent/
├── config/                 # 配置文件
│   ├── config.yaml        # 主配置文件（需从example复制）
│   ├── config.example.yaml # 配置模板
│   └── config_manager.py  # 配置管理器
├── src/                   # 源代码
│   ├── data/             # 数据层（数据源集成）
│   ├── analysis/         # 分析层（市场分析模块）
│   ├── llm/              # LLM集成层
│   ├── agent/            # Agent协调层
│   ├── output/           # 输出层（报告生成）
│   ├── models/           # 数据模型
│   └── utils/            # 工具函数
├── prompts/              # LLM提示词模板
├── tests/                # 测试代码
├── examples/             # 示例代码
├── data/                 # 数据存储
│   └── history/         # 历史数据
├── output/               # 输出目录
│   └── reports/         # 分析报告
├── logs/                 # 日志文件
└── pyproject.toml        # 项目配置

```

## 📚 文档

- **[快速开始指南](docs/QUICKSTART.md)** - 5分钟快速上手
- **[配置指南](docs/CONFIGURATION_GUIDE.md)** - 详细的配置说明
- **[LLM集成指南](docs/LLM_INTEGRATION.md)** - LLM集成和使用
- **[提示词工程说明](docs/PROMPT_ENGINEERING.md)** - 提示词设计和优化
- **[CLI使用指南](docs/CLI_USAGE_GUIDE.md)** - 命令行工具使用
- **[设计文档](../../.kiro/specs/theme-anchor-agent/design.md)** - 系统架构设计

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -e .
```

### 2. 配置

复制配置模板并填写必要信息：

```bash
cp config/config.example.yaml config/config.yaml
```

编辑 `config/config.yaml`，填写：
- LLM API密钥（智谱AI/OpenAI/通义千问）
- 数据源配置
- 分析参数

详细配置说明见：[配置指南](docs/CONFIGURATION_GUIDE.md)

### 3. 运行分析

#### 使用命令行工具（推荐）

```bash
# 分析今天的市场
python theme_cli.py

# 分析指定日期
python theme_cli.py --date 2026-01-20

# 分析昨天
python theme_cli.py --yesterday

# 查看所有选项
python theme_cli.py --help
```

#### Windows用户

```cmd
REM 使用批处理脚本
theme_cli.bat

REM 或指定日期
theme_cli.bat --date 2026-01-20
```

#### 在Python代码中使用

```python
from src.cli import ThemeCLI

cli = ThemeCLI()
exit_code = cli.run()
```

详细的CLI使用指南见：[CLI使用指南](docs/CLI_USAGE_GUIDE.md)

完整的快速开始指南见：[快速开始](docs/QUICKSTART.md)

## ⚙️ 配置说明

### LLM配置

支持多种LLM提供商：

| 提供商 | 模型 | 特点 | 推荐度 |
|--------|------|------|--------|
| 智谱AI | glm-4-flash | 性价比高，速度快 | ⭐⭐⭐⭐⭐ |
| OpenAI | gpt-4 | 质量最高 | ⭐⭐⭐⭐ |
| 通义千问 | qwen-plus | 国内访问快 | ⭐⭐⭐⭐ |

详细配置说明见：[配置指南](docs/CONFIGURATION_GUIDE.md)

### 数据源

- **主数据源**: kaipanla（开盘啦）- 专业涨停和连板数据
- **备用数据源**: akshare - 数据缺失时自动降级

### 分析参数

可在配置文件中调整：
- 板块筛选阈值
- 联动分析参数
- 情绪周期判定标准
- 容量分类标准

完整配置说明见：[配置指南](docs/CONFIGURATION_GUIDE.md)

## CLI命令行工具

### 基本命令

```bash
# 分析今天的市场
python theme_cli.py

# 分析指定日期
python theme_cli.py --date 2026-01-20

# 分析昨天
python theme_cli.py --yesterday
```

### 输出控制

```bash
# 只生成JSON格式
python theme_cli.py --format json

# 指定输出目录
python theme_cli.py --output /path/to/output

# 不保存文件，只显示结果
python theme_cli.py --no-save
```

### 日志控制

```bash
# 详细输出（调试）
python theme_cli.py --verbose

# 静默模式（只显示错误）
python theme_cli.py --quiet
```

### 自定义配置

```bash
# 使用自定义配置文件
python theme_cli.py --config /path/to/config.yaml
```

完整的CLI使用指南见：[docs/CLI_USAGE_GUIDE.md](docs/CLI_USAGE_GUIDE.md)

## 🛠️ 开发

### 运行测试

```bash
# 运行所有测试
pytest

# 运行带覆盖率的测试
pytest --cov=src --cov-report=html

# 运行属性测试
pytest tests/ -k "property"
```

### 代码格式化

```bash
black src/ tests/
```

### 类型检查

```bash
mypy src/
```

## 🏗️ 架构设计

系统采用模块化架构，分为五个核心层次：

1. **数据层**: 封装数据源API，支持主备降级
2. **分析层**: 实现四大分析维度（筛选、联动、周期、容量）
3. **LLM层**: 提示词工程和大模型集成
4. **Agent层**: 协调分析流程，整合结果
5. **输出层**: 生成结构化报告

详细设计文档见：[设计文档](../../.kiro/specs/theme-anchor-agent/design.md)

## 📖 示例代码

查看 `examples/` 目录获取更多示例：

- `example_basic_analysis.py` - 基础分析示例
- `example_custom_prompts.py` - 自定义提示词示例
- `example_llm_config.py` - LLM配置示例
- `example_theme_anchor_agent.py` - 完整Agent使用示例

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [kaipanla_crawler](../../kaipanla_crawler/) - 数据源支持
- [OpenAI](https://openai.com/) - GPT模型
- [智谱AI](https://open.bigmodel.cn/) - GLM模型
- [通义千问](https://tongyi.aliyun.com/) - Qwen模型
