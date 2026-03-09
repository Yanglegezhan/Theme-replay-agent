# 快速开始指南

本指南将帮助你在5分钟内开始使用Theme Anchor Agent进行市场分析。

## 前置要求

- Python 3.8+
- pip包管理器
- LLM API密钥（智谱AI、OpenAI或通义千问）

## 安装步骤

### 1. 克隆或下载项目

```bash
cd Ashare复盘multi-agents/Theme_repay_agent
```

### 2. 安装依赖

```bash
pip install -e .
```

这将安装所有必需的依赖包，包括：
- pandas: 数据处理
- pyyaml: 配置文件解析
- requests: HTTP请求
- openai: LLM API客户端
- hypothesis: 属性测试（开发用）

### 3. 配置系统

#### 3.1 复制配置模板

```bash
cp config/config.example.yaml config/config.yaml
```

#### 3.2 获取LLM API密钥

选择一个LLM提供商并获取API密钥：

**智谱AI（推荐，性价比高）**:
1. 访问 https://open.bigmodel.cn/
2. 注册账号并登录
3. 在"API密钥"页面创建新密钥
4. 复制密钥

**OpenAI（质量最佳）**:
1. 访问 https://platform.openai.com/
2. 注册账号并登录
3. 在"API Keys"页面创建新密钥
4. 复制密钥

**通义千问（国内访问快）**:
1. 访问 https://dashscope.console.aliyun.com/
2. 注册阿里云账号并登录
3. 开通DashScope服务
4. 获取API-KEY

#### 3.3 编辑配置文件

打开 `config/config.yaml`，修改以下内容：

```yaml
llm:
  provider: "zhipu"  # 或 "openai", "qwen"
  api_key: "YOUR_API_KEY_HERE"  # 替换为你的API密钥
  model_name: "glm-4-flash"  # 或其他模型
```

### 4. 验证安装

运行验证脚本确保一切正常：

```bash
python verify_setup.py
```

如果看到 "✓ All checks passed!"，说明安装成功！

## 第一次运行

### 使用命令行工具（最简单）

```bash
# 分析今天的市场
python theme_cli.py
```

或者在Windows上：

```cmd
theme_cli.bat
```

### 查看结果

分析完成后，报告将保存在 `output/reports/` 目录：

```
output/reports/
├── theme_analysis_2026-01-22.md    # Markdown格式报告
└── theme_analysis_2026-01-22.json  # JSON格式数据
```

打开Markdown文件查看详细的分析报告。

## 基本使用示例

### 示例1: 分析指定日期

```bash
python theme_cli.py --date 2026-01-20
```

### 示例2: 分析昨天的市场

```bash
python theme_cli.py --yesterday
```

### 示例3: 只生成JSON格式

```bash
python theme_cli.py --format json
```

### 示例4: 详细输出（调试模式）

```bash
python theme_cli.py --verbose
```

## 在Python代码中使用

创建一个Python脚本 `my_analysis.py`：

```python
from datetime import datetime
from src.agent import ThemeAnchorAgent
from src.data import KaipanlaDataSource
from src.data import HistoryTracker
from src.llm import LLMAnalyzer, PromptEngine, ContextBuilder
from config import ConfigManager

# 加载配置
config = ConfigManager()

# 初始化组件
data_source = KaipanlaDataSource()
history_tracker = HistoryTracker(config.get("history.storage_path"))
prompt_engine = PromptEngine()
context_builder = ContextBuilder()
llm_analyzer = LLMAnalyzer(
    api_key=config.get("llm.api_key"),
    provider=config.get("llm.provider"),
    model_name=config.get("llm.model_name"),
    prompt_engine=prompt_engine
)

# 创建Agent
agent = ThemeAnchorAgent(
    data_source=data_source,
    history_tracker=history_tracker,
    llm_analyzer=llm_analyzer,
    context_builder=context_builder,
    config=config
)

# 执行分析
date = datetime.now().strftime("%Y-%m-%d")
report = agent.analyze(date)

# 打印结果
print(f"分析日期: {report.date}")
print(f"目标板块数量: {len(report.target_sectors)}")
for sector in report.target_sectors:
    print(f"- {sector.sector_name}: {sector.strength_score}")
```

运行脚本：

```bash
python my_analysis.py
```

## 理解输出报告

### Markdown报告结构

```markdown
# A股超短线题材锚定分析报告

## 执行摘要
[LLM生成的市场概览和关键发现]

## 市场资金意图分析
[主力资金流向、板块轮动、市场情绪]

## 目标板块分析

### 1. [板块名称] (强度分数: XXXX)
- **新旧标记**: 新面孔/老面孔
- **盘面联动**: 先锋/共振/分离
- **情绪周期**: 启动期/高潮期/分化期/修复期/退潮期
- **容量类型**: 大容量主线/小众投机题材
- **持续性评分**: XX/100
- **操作建议**: [LLM生成的具体建议]

[重复每个目标板块]

## 风险提示
[关键风险因素]
```

### JSON数据结构

```json
{
  "date": "2026-01-22",
  "executive_summary": "...",
  "market_intent": {
    "main_capital_flow": "...",
    "sector_rotation": "...",
    "market_sentiment": "...",
    "key_drivers": [...]
  },
  "target_sectors": [
    {
      "sector_name": "...",
      "rank": 1,
      "strength_score": 12000,
      "is_new_face": true,
      "emotion_cycle": {
        "stage": "CLIMAX",
        "confidence": 0.85,
        "risk_level": "MEDIUM"
      },
      "capacity_profile": {
        "capacity_type": "LARGE_CAP",
        "sector_turnover": 150.5
      },
      "trading_advice": {
        "action": "低吸",
        "entry_timing": "...",
        "position_sizing": "..."
      }
    }
  ]
}
```

## 常见问题

### Q: API调用失败怎么办？

**A**: 检查以下几点：
1. API密钥是否正确
2. 网络连接是否正常
3. API配额是否充足
4. 尝试增加 `timeout` 和 `max_retries` 配置

### Q: 分析速度很慢？

**A**: 可以尝试：
1. 使用更快的模型（如 `glm-4-flash`）
2. 减少 `target_sector_count`（分析更少的板块）
3. 设置 `max_tokens` 限制输出长度

### Q: 数据获取失败？

**A**: 系统会自动尝试备用数据源（akshare）。如果仍然失败：
1. 检查网络连接
2. 确认是交易日（非交易日无数据）
3. 查看日志文件了解详细错误

### Q: 如何自定义分析参数？

**A**: 编辑 `config/config.yaml` 中的 `analysis` 部分：

```yaml
analysis:
  sector_filter:
    high_strength_threshold: 8000  # 调整此值
    target_sector_count: 7  # 调整此值
```

### Q: 如何使用代理？

**A**: 在配置文件中设置：

```yaml
llm:
  api_base: "http://your-proxy:port/v1"
```

或设置环境变量：

```bash
export HTTP_PROXY="http://your-proxy:port"
export HTTPS_PROXY="http://your-proxy:port"
```

## 下一步

现在你已经成功运行了第一次分析！接下来可以：

1. **深入了解配置**: 阅读 [配置指南](CONFIGURATION_GUIDE.md)
2. **学习提示词工程**: 阅读 [提示词工程说明](PROMPT_ENGINEERING.md)
3. **了解LLM集成**: 阅读 [LLM集成指南](LLM_INTEGRATION.md)
4. **查看示例代码**: 浏览 `examples/` 目录
5. **自定义分析**: 修改提示词模板或分析参数

## 获取帮助

- 查看完整文档: `docs/` 目录
- 查看示例代码: `examples/` 目录
- 查看设计文档: `.kiro/specs/theme-anchor-agent/design.md`
- 提交Issue: 在项目仓库提交问题

## 最佳实践

1. **每日运行**: 建议每个交易日收盘后运行分析
2. **保存历史**: 系统会自动保存历史数据，用于判断新旧面孔
3. **对比分析**: 对比多日报告，观察题材演变
4. **结合实盘**: 将分析结果与实际盘面对照，验证准确性
5. **迭代优化**: 根据效果调整配置参数和提示词

祝你使用愉快！
