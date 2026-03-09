# LLM集成指南

本文档详细说明如何在Theme Anchor Agent中集成和使用大语言模型（LLM）。

## 概述

Theme Anchor Agent的核心是LLM分析引擎，通过调用大语言模型对市场数据进行深度分析。系统支持多种LLM提供商，包括OpenAI、智谱AI和通义千问。

## 支持的LLM提供商

### 1. 智谱AI (Zhipu)

**推荐指数**: ⭐⭐⭐⭐⭐

**优势**:
- 性价比高
- 中文理解能力强
- 国内访问速度快
- API稳定

**模型选择**:
- `glm-4`: 最强性能，适合复杂分析
- `glm-4-flash`: 速度快，性价比高（推荐）
- `glm-3-turbo`: 经济型选择

**配置示例**:
```yaml
llm:
  provider: "zhipu"
  api_key: "YOUR_ZHIPU_API_KEY"
  model_name: "glm-4-flash"
  temperature: 0.7
```

**获取API密钥**:
1. 访问 https://open.bigmodel.cn/
2. 注册并登录
3. 在"API密钥"页面创建新密钥

**定价** (截至2026年1月):
- glm-4: ¥0.1/千tokens
- glm-4-flash: ¥0.001/千tokens
- glm-3-turbo: ¥0.005/千tokens

### 2. OpenAI

**推荐指数**: ⭐⭐⭐⭐

**优势**:
- 模型质量最高
- 生态完善
- 文档详细

**劣势**:
- 价格较高
- 国内访问需要代理

**模型选择**:
- `gpt-4`: 最强性能
- `gpt-4-turbo`: 性能与速度平衡
- `gpt-3.5-turbo`: 经济型选择

**配置示例**:
```yaml
llm:
  provider: "openai"
  api_key: "YOUR_OPENAI_API_KEY"
  model_name: "gpt-4"
  temperature: 0.7
```

**获取API密钥**:
1. 访问 https://platform.openai.com/
2. 注册并登录
3. 在"API Keys"页面创建新密钥

**定价** (截至2026年1月):
- gpt-4: $0.03/1K tokens (input), $0.06/1K tokens (output)
- gpt-4-turbo: $0.01/1K tokens (input), $0.03/1K tokens (output)
- gpt-3.5-turbo: $0.0005/1K tokens (input), $0.0015/1K tokens (output)

### 3. 通义千问 (Qwen)

**推荐指数**: ⭐⭐⭐⭐

**优势**:
- 阿里云生态
- 中文能力强
- 国内访问快

**模型选择**:
- `qwen-max`: 最强性能
- `qwen-plus`: 平衡选择
- `qwen-turbo`: 速度优先

**配置示例**:
```yaml
llm:
  provider: "qwen"
  api_key: "YOUR_QWEN_API_KEY"
  model_name: "qwen-plus"
  temperature: 0.7
```

**获取API密钥**:
1. 访问 https://dashscope.console.aliyun.com/
2. 注册阿里云账号并登录
3. 开通DashScope服务
4. 获取API-KEY

**定价** (截至2026年1月):
- qwen-max: ¥0.12/千tokens
- qwen-plus: ¥0.04/千tokens
- qwen-turbo: ¥0.008/千tokens

## LLM架构设计

### 核心组件

```
┌─────────────────────────────────────────────────┐
│              ThemeAnchorAgent                   │
│         (协调分析流程)                           │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│              LLMAnalyzer                        │
│         (LLM分析引擎)                            │
│  - analyze_market_intent()                      │
│  - analyze_emotion_cycle()                      │
│  - evaluate_sustainability()                    │
│  - generate_trading_advice()                    │
└────────┬────────────────────┬───────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌──────────────────┐
│  PromptEngine   │  │ ContextBuilder   │
│  (提示词管理)    │  │ (上下文构建)      │
└─────────────────┘  └──────────────────┘
```

### LLMAnalyzer

核心分析引擎，负责调用LLM API。

**初始化**:
```python
from src.llm import LLMAnalyzer, PromptEngine

llm_analyzer = LLMAnalyzer(
    api_key="your_api_key",
    provider="zhipu",  # or "openai", "qwen"
    model_name="glm-4-flash",
    temperature=0.7,
    max_tokens=2000,
    timeout=60,
    max_retries=3,
    prompt_engine=PromptEngine()
)
```

**主要方法**:

1. **analyze_market_intent()**: 分析市场资金意图
```python
result = llm_analyzer.analyze_market_intent(context)
# 返回: MarketIntentAnalysis对象
```

2. **analyze_emotion_cycle()**: 分析情绪周期
```python
result = llm_analyzer.analyze_emotion_cycle(
    sector_name="人工智能",
    context=context
)
# 返回: EmotionCycleAnalysis对象
```

3. **evaluate_sustainability()**: 评估持续性
```python
result = llm_analyzer.evaluate_sustainability(
    sector_name="人工智能",
    context=context
)
# 返回: SustainabilityEvaluation对象
```

4. **generate_trading_advice()**: 生成操作建议
```python
result = llm_analyzer.generate_trading_advice(
    sector_name="人工智能",
    context=context
)
# 返回: TradingAdvice对象
```

### PromptEngine

提示词引擎，管理和生成提示词。

**初始化**:
```python
from src.llm import PromptEngine

prompt_engine = PromptEngine(template_dir="prompts")
```

**主要方法**:

1. **load_template()**: 加载模板
```python
template = prompt_engine.load_template("market_intent.md")
```

2. **render_template()**: 渲染模板
```python
prompt = prompt_engine.render_template(
    template,
    {"data": formatted_data}
)
```

3. **build_xxx_prompt()**: 构建特定提示词
```python
prompt = prompt_engine.build_market_intent_prompt(context)
prompt = prompt_engine.build_emotion_cycle_prompt("人工智能", context)
prompt = prompt_engine.build_sustainability_prompt("人工智能", context)
prompt = prompt_engine.build_trading_advice_prompt("人工智能", context)
```

### ContextBuilder

上下文构建器，将结构化数据转换为LLM友好的文本。

**初始化**:
```python
from src.llm import ContextBuilder

context_builder = ContextBuilder()
```

**主要方法**:

1. **build_analysis_context()**: 构建完整上下文
```python
context = context_builder.build_analysis_context(
    date="2026-01-22",
    filter_result=filter_result,
    correlation_result=correlation_result,
    emotion_cycles=emotion_cycles,
    capacity_profiles=capacity_profiles
)
```

2. **format_for_llm()**: 格式化为文本
```python
formatted_text = context_builder.format_for_llm(
    context,
    focus_sector="人工智能"
)
```

## API调用流程

### 完整流程

```python
# 1. 准备数据
filter_result = sector_filter.filter_sectors(ndays_data, date)
correlation_result = correlation_analyzer.analyze_correlation(
    market_data, sector_data_list
)

# 2. 构建上下文
context = context_builder.build_analysis_context(
    date=date,
    filter_result=filter_result,
    correlation_result=correlation_result,
    emotion_cycles={},
    capacity_profiles={}
)

# 3. 调用LLM分析
market_intent = llm_analyzer.analyze_market_intent(context)

for sector in filter_result.target_sectors:
    # 情绪周期分析
    emotion_cycle = llm_analyzer.analyze_emotion_cycle(
        sector_name=sector.sector_name,
        context=context
    )
    
    # 持续性评估
    sustainability = llm_analyzer.evaluate_sustainability(
        sector_name=sector.sector_name,
        context=context
    )
    
    # 操作建议
    trading_advice = llm_analyzer.generate_trading_advice(
        sector_name=sector.sector_name,
        context=context
    )
```

### 错误处理

```python
try:
    result = llm_analyzer.analyze_emotion_cycle(
        sector_name="人工智能",
        context=context
    )
except LLMAPIError as e:
    # API调用失败
    logger.error(f"LLM API error: {e}")
    result = get_default_emotion_cycle()
except LLMParseError as e:
    # 响应解析失败
    logger.error(f"Failed to parse LLM response: {e}")
    result = get_default_emotion_cycle()
except Exception as e:
    # 其他错误
    logger.error(f"Unexpected error: {e}")
    result = get_default_emotion_cycle()
```

## 高级配置

### 1. 自定义API端点

使用代理或私有部署：

```yaml
llm:
  provider: "openai"
  api_key: "your_key"
  api_base: "http://your-proxy:port/v1"
```

或在代码中：

```python
llm_analyzer = LLMAnalyzer(
    api_key="your_key",
    provider="openai",
    api_base="http://your-proxy:port/v1"
)
```

### 2. 调整温度参数

不同任务使用不同的temperature：

```python
# 需要确定性的任务（数据总结）
llm_analyzer._call_llm(prompt, temperature=0.3)

# 平衡任务（情绪周期判定）
llm_analyzer._call_llm(prompt, temperature=0.7)

# 需要创造性的任务（操作建议）
llm_analyzer._call_llm(prompt, temperature=0.8)
```

### 3. 控制输出长度

```python
# 限制输出token数
llm_analyzer._call_llm(
    prompt,
    max_tokens=2000  # 限制为2000 tokens
)
```

### 4. 设置超时和重试

```python
llm_analyzer = LLMAnalyzer(
    api_key="your_key",
    provider="zhipu",
    timeout=60,  # 60秒超时
    max_retries=3,  # 最多重试3次
    retry_delay=1.0  # 重试间隔1秒
)
```

### 5. 使用环境变量

```bash
# 设置环境变量
export THEME_ANCHOR_LLM_API_KEY="your_api_key"
export THEME_ANCHOR_LLM_PROVIDER="zhipu"
export THEME_ANCHOR_LLM_MODEL="glm-4-flash"
```

系统会自动读取环境变量，优先级高于配置文件。

## 性能优化

### 1. 批量处理

对多个板块进行批量分析：

```python
async def analyze_sectors_batch(
    sectors: List[str],
    context: AnalysisContext
) -> Dict[str, EmotionCycleAnalysis]:
    """批量分析板块情绪周期"""
    
    tasks = [
        llm_analyzer.analyze_emotion_cycle_async(
            sector_name=sector,
            context=context
        )
        for sector in sectors
    ]
    
    results = await asyncio.gather(*tasks)
    return dict(zip(sectors, results))
```

### 2. 缓存结果

缓存LLM响应以减少API调用：

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_llm_call(prompt: str, temperature: float) -> str:
    """缓存LLM调用结果"""
    return llm_analyzer._call_llm(prompt, temperature)
```

### 3. 上下文压缩

减少上下文长度以降低成本：

```python
def compress_context(
    context: AnalysisContext,
    max_tokens: int = 4000
) -> str:
    """压缩上下文"""
    
    # 只保留关键信息
    essential_data = {
        "date": context.date,
        "top_sectors": context.target_sectors[:5],  # 只保留前5个
        "market_overview": context.market_overview
    }
    
    return context_builder.format_for_llm(essential_data)
```

### 4. 流式输出

使用流式API减少等待时间：

```python
def stream_llm_response(prompt: str):
    """流式获取LLM响应"""
    
    response = ""
    for chunk in llm_analyzer._call_llm_stream(prompt):
        response += chunk
        print(chunk, end="", flush=True)
    
    return response
```

## 成本估算

### 单次分析成本估算

假设分析7个板块，每个板块需要4次LLM调用：
- 市场资金意图分析: 1次
- 情绪周期分析: 7次
- 持续性评估: 7次
- 操作建议: 7次

总计: 22次LLM调用

**使用glm-4-flash (¥0.001/千tokens)**:
- 平均每次调用: 2000 tokens (input) + 500 tokens (output) = 2500 tokens
- 总tokens: 22 × 2500 = 55,000 tokens
- 成本: 55 × ¥0.001 = ¥0.055 (约5分钱)

**使用gpt-4 ($0.03/1K input, $0.06/1K output)**:
- Input tokens: 22 × 2000 = 44,000 tokens
- Output tokens: 22 × 500 = 11,000 tokens
- 成本: 44 × $0.03 + 11 × $0.06 = $1.98 (约¥14)

### 月度成本估算

假设每个交易日运行一次（每月约20个交易日）：

- glm-4-flash: ¥0.055 × 20 = ¥1.1/月
- gpt-4: $1.98 × 20 = $39.6/月 (约¥280/月)

## 故障排除

### 问题1: API密钥无效

**症状**:
```
LLMAPIError: Authentication failed
```

**解决方案**:
1. 检查API密钥是否正确
2. 确认API密钥有足够的配额
3. 检查provider配置是否匹配

### 问题2: 请求超时

**症状**:
```
LLMAPIError: Request timeout
```

**解决方案**:
1. 增加timeout配置
2. 检查网络连接
3. 减少上下文长度
4. 使用更快的模型

### 问题3: 响应格式错误

**症状**:
```
LLMParseError: Failed to parse JSON response
```

**解决方案**:
1. 降低temperature（提高确定性）
2. 在提示词中更明确地要求JSON格式
3. 提供输出示例
4. 检查解析逻辑是否robust

### 问题4: 速率限制

**症状**:
```
LLMAPIError: Rate limit exceeded
```

**解决方案**:
1. 增加重试延迟
2. 使用批量处理
3. 升级API套餐
4. 实现请求队列

### 问题5: 内容过滤

**症状**:
```
LLMAPIError: Content filtered
```

**解决方案**:
1. 检查输入内容是否包含敏感词
2. 调整提示词措辞
3. 联系API提供商

## 测试

### 单元测试

```python
def test_llm_analyzer_initialization():
    """测试LLM分析器初始化"""
    
    analyzer = LLMAnalyzer(
        api_key="test_key",
        provider="zhipu",
        model_name="glm-4-flash"
    )
    
    assert analyzer.provider == "zhipu"
    assert analyzer.model_name == "glm-4-flash"

def test_emotion_cycle_analysis():
    """测试情绪周期分析"""
    
    analyzer = LLMAnalyzer(api_key="test_key")
    context = create_test_context()
    
    result = analyzer.analyze_emotion_cycle(
        sector_name="人工智能",
        context=context
    )
    
    assert result.stage in ["启动期", "高潮期", "分化期", "修复期", "退潮期"]
    assert 0 <= result.confidence <= 1
```

### 集成测试

```python
def test_full_llm_pipeline():
    """测试完整LLM分析流程"""
    
    # 初始化组件
    config = ConfigManager()
    llm_analyzer = LLMAnalyzer(
        api_key=config.get("llm.api_key"),
        provider=config.get("llm.provider")
    )
    context_builder = ContextBuilder()
    
    # 准备数据
    context = context_builder.build_analysis_context(...)
    
    # 执行分析
    market_intent = llm_analyzer.analyze_market_intent(context)
    emotion_cycle = llm_analyzer.analyze_emotion_cycle("人工智能", context)
    
    # 验证结果
    assert market_intent is not None
    assert emotion_cycle is not None
```

### Mock测试

```python
from unittest.mock import Mock, patch

def test_llm_with_mock():
    """使用Mock测试LLM调用"""
    
    with patch.object(LLMAnalyzer, '_call_llm') as mock_call:
        mock_call.return_value = json.dumps({
            "stage": "高潮期",
            "confidence": 0.85,
            "reasoning": "测试理由",
            "risk_level": "MEDIUM",
            "opportunity_level": "HIGH"
        })
        
        analyzer = LLMAnalyzer(api_key="test_key")
        result = analyzer.analyze_emotion_cycle("人工智能", context)
        
        assert result.stage == "高潮期"
        assert result.confidence == 0.85
```

## 最佳实践

1. **选择合适的模型**: 根据需求平衡质量和成本
2. **控制上下文长度**: 避免超过token限制
3. **设置合理的超时**: 避免长时间等待
4. **实现错误处理**: 确保系统稳定性
5. **使用缓存**: 减少重复调用
6. **监控成本**: 定期检查API使用情况
7. **测试充分**: 使用单元测试和集成测试
8. **迭代优化**: 根据效果调整提示词和参数
9. **日志记录**: 记录所有API调用和错误
10. **备份方案**: 准备降级策略

## 相关文档

- [提示词工程说明](PROMPT_ENGINEERING.md)
- [配置指南](CONFIGURATION_GUIDE.md)
- [快速开始](QUICKSTART.md)

## 参考资源

- OpenAI API文档: https://platform.openai.com/docs/api-reference
- 智谱AI文档: https://open.bigmodel.cn/dev/api
- 通义千问文档: https://help.aliyun.com/zh/dashscope/
