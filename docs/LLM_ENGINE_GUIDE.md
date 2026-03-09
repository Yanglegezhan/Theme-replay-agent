# LLM引擎使用指南

## 概述

LLM引擎是题材锚定Agent的核心组件，负责通过大语言模型进行深度市场分析。它由三个主要模块组成：

1. **PromptEngine（提示词引擎）**：管理和生成各类分析提示词
2. **ContextBuilder（上下文构建器）**：为LLM准备结构化输入数据
3. **LLMAnalyzer（LLM分析器）**：调用大模型API进行分析

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    ThemeAnchorAgent                      │
│                    （题材锚定Agent）                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                     LLMAnalyzer                          │
│                   （LLM分析器）                          │
│  - analyze_market_intent()      资金意图分析            │
│  - analyze_emotion_cycle()      情绪周期判定            │
│  - evaluate_sustainability()    持续性评估              │
│  - generate_trading_advice()    操作建议生成            │
└────────┬──────────────────────────────┬─────────────────┘
         │                              │
         ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│  PromptEngine    │          │ ContextBuilder   │
│ （提示词引擎）    │          │（上下文构建器）   │
│                  │          │                  │
│ - 加载模板        │          │ - 构建上下文      │
│ - 渲染变量        │          │ - 格式化数据      │
│ - 生成提示词      │          │ - 控制长度        │
└──────────────────┘          └──────────────────┘
         │                              │
         ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│  prompts/        │          │  AnalysisContext │
│  模板文件目录     │          │  分析上下文数据   │
└──────────────────┘          └──────────────────┘
```

## 模块详解

### 1. PromptEngine（提示词引擎）

#### 功能
- 加载和缓存提示词模板
- 渲染模板变量
- 生成特定分析任务的提示词

#### 使用方法

```python
from src.llm import PromptEngine
from src.models.data_models import AnalysisContext

# 初始化
prompt_engine = PromptEngine(template_dir="prompts/")

# 加载模板
template = prompt_engine.load_template("market_intent")

# 渲染模板
variables = {"date": "2026-01-20", "market_data": "..."}
rendered = prompt_engine.render_template(template, variables)

# 构建特定提示词
context = AnalysisContext(...)
market_intent_prompt = prompt_engine.build_market_intent_prompt(context)
emotion_cycle_prompt = prompt_engine.build_emotion_cycle_prompt("低空经济", context)
sustainability_prompt = prompt_engine.build_sustainability_prompt("低空经济", context)
trading_advice_prompt = prompt_engine.build_trading_advice_prompt("低空经济", context)
```

#### 提示词模板

系统提供四个核心提示词模板：

1. **market_intent.md** - 市场资金意图分析
   - 角色：十年经验游资操盘手
   - 任务：分析资金流向和市场意图
   - 输出：JSON格式（资金流向、板块轮动、市场情绪、关键驱动）

2. **emotion_cycle.md** - 情绪周期判定
   - 角色：资深情绪周期分析师
   - 任务：判定板块所处的情绪周期阶段
   - 理论：启动期、高潮期、分化期、修复期、退潮期
   - 输出：JSON格式（阶段、置信度、理由、风险机会等级）

3. **sustainability.md** - 题材持续性评估
   - 角色：资深题材研究员
   - 任务：评估题材生命周期和持续性
   - 输出：JSON格式（评分、时间预期、风险因素、支撑因素）

4. **trading_advice.md** - 操作建议生成
   - 角色：实战派短线交易员
   - 任务：给出具体操作建议
   - 输出：JSON格式（操作方向、入场时机、出场策略、仓位建议）

### 2. ContextBuilder（上下文构建器）

#### 功能
- 构建完整的分析上下文
- 格式化数据为LLM友好的文本
- 控制上下文长度（默认8000 tokens）

#### 使用方法

```python
from src.llm import ContextBuilder

# 初始化
context_builder = ContextBuilder(max_tokens=8000)

# 构建分析上下文
context = context_builder.build_analysis_context(
    date="2026-01-20",
    filter_result=filter_result,
    correlation_result=correlation_result,
    emotion_cycles=emotion_cycles,
    capacity_profiles=capacity_profiles
)

# 格式化为LLM文本
formatted_text = context_builder.format_for_llm(context)

# 聚焦单个板块
sector_text = context_builder.format_for_llm(context, focus_sector="低空经济")
```

#### 上下文结构

```python
@dataclass
class AnalysisContext:
    date: str                           # 分析日期
    market_overview: Dict[str, Any]     # 市场概览
    target_sectors: List[Dict[str, Any]] # 目标板块详情
    sector_relationships: Dict[str, Any] # 板块关系图
    historical_context: Dict[str, Any]   # 历史上下文
```

#### 格式化输出示例

```
## 市场概览（2026-01-20）
- 涨停数：45
- 跌停数：8
- 炸板率：15.5%
- 涨跌比：1.35

## 目标板块（前7强）
| 排名 | 板块名称 | 强度分数 | 涨停数 | 新旧 | 联动类型 | 情绪阶段 |
|------|---------|---------|--------|------|---------|---------|
| 1    | 低空经济 | 12500   | 8      | 新   | 先锋    | 启动期   |
| 2    | 固态电池 | 10800   | 6      | 老3天 | 共振    | 高潮期   |

## 盘面联动
- 先锋板块：低空经济
- 共振板块：固态电池
```

### 3. LLMAnalyzer（LLM分析器）

#### 功能
- 调用多种LLM API（OpenAI、智谱、通义千问、DeepSeek）
- 执行四种核心分析任务
- 解析和验证LLM响应
- 错误处理和降级策略

#### 支持的LLM提供商

| 提供商 | 标识 | API兼容性 | 推荐模型 |
|--------|------|-----------|---------|
| OpenAI | openai | OpenAI API | gpt-4, gpt-3.5-turbo |
| 智谱AI | zhipu | OpenAI API | glm-4 |
| 通义千问 | qwen | 通义API | qwen-turbo, qwen-plus |
| DeepSeek | deepseek | OpenAI API | deepseek-chat |

#### 使用方法

```python
from src.llm import LLMAnalyzer, PromptEngine, ContextBuilder
from src.models.data_models import AnalysisContext

# 初始化
llm_analyzer = LLMAnalyzer(
    api_key="your_api_key",
    provider="openai",      # openai/zhipu/qwen/deepseek
    model_name="gpt-4",
    temperature=0.7,
    max_tokens=2000,
    timeout=60
)

# 准备上下文
context = AnalysisContext(...)

# 1. 分析市场资金意图
market_intent = llm_analyzer.analyze_market_intent(context)
print(f"资金流向: {market_intent.main_capital_flow}")
print(f"板块轮动: {market_intent.sector_rotation}")
print(f"市场情绪: {market_intent.market_sentiment}")

# 2. 分析情绪周期
emotion_cycle = llm_analyzer.analyze_emotion_cycle("低空经济", context)
print(f"情绪阶段: {emotion_cycle.stage}")
print(f"置信度: {emotion_cycle.confidence}")
print(f"风险等级: {emotion_cycle.risk_level}")

# 3. 评估持续性
sustainability = llm_analyzer.evaluate_sustainability("低空经济", context)
print(f"持续性评分: {sustainability.sustainability_score}")
print(f"预期时间: {sustainability.time_horizon}")

# 4. 生成操作建议
trading_advice = llm_analyzer.generate_trading_advice("低空经济", context)
print(f"操作方向: {trading_advice.action}")
print(f"入场时机: {trading_advice.entry_timing}")
print(f"仓位建议: {trading_advice.position_sizing}")
```

#### 返回数据结构

```python
# 1. 市场资金意图分析
@dataclass
class MarketIntentAnalysis:
    main_capital_flow: str      # 主力资金流向描述
    sector_rotation: str        # 板块轮动分析
    market_sentiment: str       # 市场情绪判断
    key_drivers: List[str]      # 关键驱动因素
    confidence: float           # 分析置信度

# 2. 情绪周期分析
@dataclass
class EmotionCycleAnalysis:
    stage: str                  # 周期阶段（启动期/高潮期/分化期/修复期/退潮期）
    confidence: float           # 判定置信度（0-1）
    reasoning: str              # 判定理由
    key_indicators: List[str]   # 关键指标说明
    risk_level: str             # 风险等级（Low/Medium/High）
    opportunity_level: str      # 机会等级（Low/Medium/High）

# 3. 持续性评估
@dataclass
class SustainabilityEvaluation:
    sustainability_score: float # 持续性评分（0-100）
    time_horizon: str           # 预期持续时间
    risk_factors: List[str]     # 风险因素
    support_factors: List[str]  # 支撑因素
    reasoning: str              # 评估理由

# 4. 操作建议
@dataclass
class TradingAdvice:
    action: str                 # 操作方向（观望/低吸/追涨/减仓）
    entry_timing: str           # 入场时机
    exit_strategy: str          # 出场策略
    position_sizing: str        # 仓位建议
    risk_warning: str           # 风险提示
    reasoning: str              # 建议理由
```

## 配置说明

### 配置文件示例（config/config.yaml）

```yaml
llm:
  provider: "openai"              # LLM提供商
  api_key: "your_api_key_here"   # API密钥
  model_name: "gpt-4"             # 模型名称
  temperature: 0.7                # 温度参数（0-1）
  max_tokens: 2000                # 最大token数
  timeout: 60                     # 超时时间（秒）

prompts:
  template_dir: "prompts/"        # 提示词模板目录
  context_max_tokens: 8000        # 上下文最大token数
```

### 不同提供商的配置

#### OpenAI
```yaml
llm:
  provider: "openai"
  api_key: "sk-..."
  model_name: "gpt-4"
```

#### 智谱AI
```yaml
llm:
  provider: "zhipu"
  api_key: "..."
  model_name: "glm-4"
```

#### 通义千问
```yaml
llm:
  provider: "qwen"
  api_key: "sk-..."
  model_name: "qwen-turbo"
```

#### DeepSeek
```yaml
llm:
  provider: "deepseek"
  api_key: "sk-..."
  model_name: "deepseek-chat"
```

## 错误处理

### 1. API调用失败

LLMAnalyzer会自动重试（最多3次），如果仍然失败，会返回默认值：

```python
# 示例：情绪周期分析失败
EmotionCycleAnalysis(
    stage='未知',
    confidence=0.0,
    reasoning='分析失败',
    key_indicators=[],
    risk_level='High',
    opportunity_level='Low'
)
```

### 2. JSON解析失败

系统会尝试多种方式提取JSON：
1. 直接解析
2. 提取```json ... ```代码块
3. 提取``` ... ```代码块
4. 查找第一个{和最后一个}

### 3. 响应验证

- 情绪周期阶段必须是五个有效阶段之一
- 数值字段会转换为float类型
- 列表字段会确保是列表类型

## 最佳实践

### 1. 提示词优化

- **明确角色设定**：让LLM扮演特定角色（游资操盘手、分析师等）
- **提供理论背景**：如情绪周期理论的五个阶段特征
- **结构化输出**：要求JSON格式输出，便于解析
- **具体分析维度**：明确列出需要分析的维度

### 2. 上下文管理

- **控制长度**：默认8000 tokens，避免超过模型限制
- **优先级排序**：当前数据 > 近期数据 > 历史统计
- **聚焦分析**：单板块分析时使用focus_sector参数

### 3. 性能优化

- **模板缓存**：PromptEngine会自动缓存加载的模板
- **批量分析**：对多个板块分析时，复用context对象
- **超时设置**：根据网络情况调整timeout参数

### 4. 成本控制

- **选择合适模型**：gpt-3.5-turbo成本更低，gpt-4效果更好
- **控制token数**：通过max_tokens和context_max_tokens控制
- **降低温度**：temperature=0.3可以减少随机性，提高一致性

## 示例代码

完整示例请参考：
- `examples/example_llm_engine.py` - LLM引擎基础使用
- `examples/example_basic_analysis.py` - 完整分析流程（待实现）

## 故障排查

### 问题1：ModuleNotFoundError: No module named 'tiktoken'

**解决方案**：tiktoken是可选依赖，系统会自动降级到简单估算。如需精确计算：
```bash
pip install tiktoken
```

### 问题2：API调用超时

**解决方案**：增加timeout参数
```python
llm_analyzer = LLMAnalyzer(api_key="...", timeout=120)
```

### 问题3：JSON解析失败

**解决方案**：检查LLM响应格式，可能需要优化提示词，明确要求JSON格式输出

### 问题4：情绪周期判定不准确

**解决方案**：
1. 检查输入数据是否完整（涨停数、连板梯队、炸板率等）
2. 优化emotion_cycle.md模板，添加更多示例
3. 尝试使用更强大的模型（如gpt-4）

## 未来扩展

### 计划功能

1. **Few-shot Learning**：在提示词中添加示例，提升分析质量
2. **多轮对话**：支持追问和澄清，深化分析
3. **结果缓存**：缓存相同输入的分析结果，节省成本
4. **A/B测试**：对比不同提示词和模型的效果
5. **评估指标**：建立LLM分析质量的评估体系

### 自定义扩展

可以通过继承LLMAnalyzer添加自定义分析方法：

```python
class CustomLLMAnalyzer(LLMAnalyzer):
    def analyze_custom_task(self, context: AnalysisContext):
        # 自定义分析逻辑
        prompt = "..."
        response = self._call_llm(prompt)
        return self._parse_json_response(response)
```

## 参考资料

- [OpenAI API文档](https://platform.openai.com/docs/api-reference)
- [智谱AI API文档](https://open.bigmodel.cn/dev/api)
- [通义千问API文档](https://help.aliyun.com/zh/dashscope/)
- [提示词工程指南](https://www.promptingguide.ai/)
