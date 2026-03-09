# LLM情绪周期分析集成文档

## 概述

本文档描述了如何使用LLM进行板块情绪周期分析。情绪周期分析是题材锚定Agent的核心功能之一，通过LLM智能判定板块所处的情绪周期阶段（启动期、高潮期、分化期、修复期、退潮期），为交易决策提供关键参考。

## 情绪周期理论

情绪周期分为五个阶段：

### 1. 启动期
- **特征**：首板数量激增，出现破局个股（一字板或秒板），分时图呈45度攻击角
- **市场表现**：题材新鲜，市场关注度高，资金开始涌入
- **风险机会**：机会大于风险，适合早期布局

### 2. 高潮期
- **特征**：涨停家数>10只，全市场炸板率低（<20%），跟风股纷纷涨停，市场情绪高涨
- **市场表现**：赚钱效应明显，资金充裕，连板梯队完整
- **风险机会**：机会与风险并存，需注意分化信号

### 3. 分化期
- **特征**：仅前排1-2只龙头涨停，中后排回撤>5%，全市场炸板率飙升（>30%），资金开始分化
- **市场表现**：亏钱效应出现，市场情绪转冷，资金撤离
- **风险机会**：风险大于机会，建议减仓或观望

### 4. 修复期
- **特征**：经历分歧后核心中军或龙头反包，板块指数收复昨日失地，情绪修复
- **市场表现**：龙头带动情绪回暖，资金重新关注
- **风险机会**：二次机会，但需谨慎判断是否为真修复

### 5. 退潮期
- **特征**：龙头跌停或断板大跌（跌幅>5%），板块整体涨停数骤减（相比前一日减少>50%），情绪退潮
- **市场表现**：题材结束，资金撤离，不再关注
- **风险机会**：风险极高，应避免参与

## 核心组件

### 1. LLMAnalyzer

负责调用LLM进行情绪周期分析。

```python
from src.llm.llm_analyzer import LLMAnalyzer
from src.models.data_models import AnalysisContext

# 初始化分析器
analyzer = LLMAnalyzer(
    api_key="your_api_key",
    provider="openai",  # 或 zhipu, qwen, deepseek
    model_name="gpt-4"
)

# 分析情绪周期
result = analyzer.analyze_emotion_cycle(
    sector_name="低空经济",
    context=context,
    limit_up_data=limit_up_data,
    intraday_data=intraday_data,
    historical_data=historical_data
)

# 结果包含：
# - stage: 周期阶段（启动期/高潮期/分化期/修复期/退潮期）
# - confidence: 判定置信度（0-1）
# - reasoning: 判定理由
# - key_indicators: 关键指标列表
# - risk_level: 风险等级（Low/Medium/High）
# - opportunity_level: 机会等级（Low/Medium/High）
```

### 2. PromptEngine

负责构建情绪周期分析提示词。

```python
from src.llm.prompt_engine import PromptEngine

# 初始化提示词引擎
prompt_engine = PromptEngine(template_dir="prompts/")

# 构建提示词
prompt = prompt_engine.build_emotion_cycle_prompt(
    sector_name="低空经济",
    context=context,
    limit_up_data=limit_up_data,
    intraday_data=intraday_data,
    historical_data=historical_data
)
```

### 3. ContextBuilder

负责格式化情绪周期分析所需的数据。

```python
from src.llm.context_builder import ContextBuilder

# 初始化上下文构建器
context_builder = ContextBuilder()

# 格式化情绪周期数据
formatted_data = context_builder.format_emotion_cycle_data(
    sector_name="低空经济",
    context=context,
    limit_up_data=limit_up_data,
    intraday_data=intraday_data,
    historical_data=historical_data
)
```

## 数据准备

### 必需数据

1. **AnalysisContext**：分析上下文
   - `date`: 分析日期
   - `target_sectors`: 目标板块列表（包含板块名称、涨停数、连板梯队等）

### 重要数据（强烈建议）

2. **limit_up_data**：涨停数据
   ```python
   limit_up_data = {
       "limit_up_count": 45,              # 全市场涨停数
       "limit_down_count": 8,             # 全市场跌停数
       "blown_limit_up_rate": 25.5,       # 全市场炸板率（%）
       "yesterday_limit_up_performance": 3.2  # 昨日涨停今日表现（%）
   }
   ```

3. **intraday_data**：分时数据
   ```python
   intraday_data = {
       "pct_changes": [0.5, 1.2, 2.5, ...]  # 分时涨跌幅列表
   }
   ```

4. **historical_data**：历史数据
   ```python
   historical_data = {
       "previous_limit_up_count": 3,      # 前一日涨停数
       "emotion_history": [               # 历史情绪周期
           {"date": "2026-01-21", "stage": "高潮期"},
           {"date": "2026-01-20", "stage": "启动期"}
       ]
   }
   ```

### 数据来源

- **涨停数据**：`kaipanla_crawler.get_sector_limit_up_ladder()`
- **连板数据**：`kaipanla_crawler.get_realtime_rise_fall_analysis()`
- **分时数据**：`kaipanla_crawler.get_sector_intraday()`
- **成交额数据**：`kaipanla_crawler.get_sector_capital_data()`
- **历史数据**：`HistoryTracker.get_history()`

## 完整使用示例

```python
from src.llm.llm_analyzer import LLMAnalyzer
from src.models.data_models import AnalysisContext

# 1. 准备分析上下文
context = AnalysisContext(
    date="2026-01-22",
    market_overview={
        "涨停数": 45,
        "跌停数": 8,
        "炸板率": "25.5%"
    },
    target_sectors=[
        {
            "sector_name": "低空经济",
            "rank": 1,
            "strength_score": 12500,
            "is_new_face": True,
            "consecutive_days": 0,
            "limit_up_count": 8,
            "turnover": 85.5,
            "consecutive_boards": {
                6: ["博菲电气"],
                3: ["股票A", "股票B"],
                1: ["股票C", "股票D", "股票E"]
            }
        }
    ],
    sector_relationships={},
    historical_context={}
)

# 2. 准备额外数据
limit_up_data = {
    "limit_up_count": 45,
    "blown_limit_up_rate": 25.5,
    "yesterday_limit_up_performance": 3.2
}

intraday_data = {
    "pct_changes": [0.5, 1.2, 2.5, 3.8, 5.2, 6.5, 7.2, 8.5, 9.2, 9.8]
}

historical_data = {
    "previous_limit_up_count": 3,
    "emotion_history": []
}

# 3. 初始化LLM分析器
analyzer = LLMAnalyzer(
    api_key="your_api_key",
    provider="openai",
    model_name="gpt-4"
)

# 4. 执行情绪周期分析
result = analyzer.analyze_emotion_cycle(
    sector_name="低空经济",
    context=context,
    limit_up_data=limit_up_data,
    intraday_data=intraday_data,
    historical_data=historical_data
)

# 5. 使用分析结果
print(f"情绪周期阶段: {result.stage}")
print(f"判定置信度: {result.confidence}")
print(f"判定理由: {result.reasoning}")
print(f"风险等级: {result.risk_level}")
print(f"机会等级: {result.opportunity_level}")
```

## 分析结果解读

### EmotionCycleAnalysis 结构

```python
@dataclass
class EmotionCycleAnalysis:
    stage: str                    # 周期阶段（启动期/高潮期/分化期/修复期/退潮期）
    confidence: float             # 判定置信度（0-1）
    reasoning: str                # 判定理由
    key_indicators: List[str]     # 关键指标说明
    risk_level: str               # 风险等级（Low/Medium/High）
    opportunity_level: str        # 机会等级（Low/Medium/High）
```

### 操作建议

根据情绪周期阶段制定交易策略：

| 阶段 | 风险等级 | 机会等级 | 操作建议 |
|------|---------|---------|---------|
| 启动期 | Low | High | 积极关注，早期布局 |
| 高潮期 | Medium | High | 可参与，但需警惕分化信号 |
| 分化期 | High | Low | 减仓或观望，避免追高 |
| 修复期 | Medium | Medium | 谨慎参与，关注龙头反包 |
| 退潮期 | High | Low | 避免参与，寻找新题材 |

## 错误处理

系统具有完善的错误处理机制：

1. **数据缺失**：返回明确的错误信息，不会崩溃
2. **LLM调用失败**：返回默认的"未知"阶段，并记录错误日志
3. **无效阶段标签**：自动验证并修正为"未知"
4. **JSON解析失败**：尝试多种解析策略，提取有效信息

```python
# 错误处理示例
try:
    result = analyzer.analyze_emotion_cycle(
        sector_name="低空经济",
        context=context
    )
except Exception as e:
    print(f"分析失败: {e}")
    # 系统会返回默认值，不会崩溃
```

## 性能优化

1. **提示词模板缓存**：PromptEngine自动缓存模板，避免重复读取
2. **上下文长度控制**：ContextBuilder自动截断超长文本，控制在8000 tokens以内
3. **批量分析**：可以对多个板块并行调用，提高效率

## 配置说明

在 `config/config.yaml` 中配置LLM参数：

```yaml
llm:
  provider: "openai"  # openai, zhipu, qwen, deepseek
  api_key: "your_api_key"
  model_name: "gpt-4"
  temperature: 0.7
  max_tokens: 2000
  timeout: 60

prompts:
  template_dir: "prompts/"
  context_max_tokens: 8000
```

## 测试

运行测试验证功能：

```bash
# 运行集成测试
python test_emotion_cycle_integration.py

# 运行示例
python examples/example_emotion_cycle_analysis.py
```

## 常见问题

### Q1: LLM返回的阶段不在预定义列表中怎么办？

A: 系统会自动验证阶段标签，如果不在预定义列表中（启动期、高潮期、分化期、修复期、退潮期），会自动设置为"未知"并记录警告日志。

### Q2: 如何提高情绪周期判定的准确性？

A: 
1. 提供完整的数据（特别是历史数据和分时数据）
2. 确保数据质量（涨停数、炸板率等关键指标准确）
3. 使用更强大的LLM模型（如GPT-4）
4. 根据实际效果调整提示词模板

### Q3: 可以不使用LLM，用规则判定吗？

A: 可以，但不推荐。情绪周期判定需要综合考虑多个因素，规则难以覆盖所有情况。LLM能够更灵活地理解市场状态，提供更准确的判定。

### Q4: 支持哪些LLM提供商？

A: 目前支持：
- OpenAI (GPT-4, GPT-3.5)
- 智谱AI (GLM-4)
- 阿里通义千问
- DeepSeek

### Q5: 如何处理API调用失败？

A: 系统内置重试机制（最多3次），如果仍然失败，会返回默认的"未知"阶段，并记录详细的错误日志。不会影响整体分析流程。

## 参考资料

- [情绪周期理论详解](../docs/EMOTION_CYCLE_THEORY.md)
- [LLM集成指南](../docs/LLM_INTEGRATION.md)
- [提示词工程最佳实践](../docs/PROMPT_ENGINEERING.md)
- [API参考文档](../docs/API_REFERENCE.md)

## 更新日志

### v1.0.0 (2026-01-22)
- ✓ 实现LLMAnalyzer.analyze_emotion_cycle()方法
- ✓ 实现PromptEngine.build_emotion_cycle_prompt()方法
- ✓ 实现ContextBuilder.format_emotion_cycle_data()方法
- ✓ 添加完整的错误处理和默认值逻辑
- ✓ 创建测试和示例代码
- ✓ 编写完整文档
