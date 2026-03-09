# 提示词工程说明

本文档详细说明Theme Anchor Agent的提示词设计理念、最佳实践和自定义方法。

## 概述

Theme Anchor Agent的核心价值在于通过精心设计的提示词，引导LLM模拟资深游资操盘手的思维模式，对市场数据进行深度解构和分析。

### 提示词的作用

1. **角色设定**: 让LLM扮演特定角色（游资操盘手、题材研究员、交易员）
2. **任务定义**: 明确分析目标和输出要求
3. **上下文提供**: 将结构化数据转换为LLM可理解的文本
4. **输出格式化**: 确保LLM返回结构化、可解析的结果
5. **知识注入**: 提供领域知识（如情绪周期理论）

## 提示词架构

系统使用四个核心提示词模板：

### 1. 市场资金意图分析 (market_intent.md)

**目标**: 分析市场主力资金的真实意图和流向

**角色设定**:
```
你是一位拥有十年经验的游资操盘手，擅长通过盘面细节还原市场资金的真实意图。
```

**分析维度**:
- 主力资金流向
- 板块轮动逻辑
- 市场情绪判断
- 关键驱动因素

**输出格式**: JSON结构化
```json
{
  "main_capital_flow": "资金流向描述",
  "sector_rotation": "板块轮动分析",
  "market_sentiment": "市场情绪判断",
  "key_drivers": ["驱动因素1", "驱动因素2"],
  "confidence": 0.85
}
```

### 2. 情绪周期分析 (emotion_cycle.md)

**目标**: 判定板块所处的情绪周期阶段

**角色设定**:
```
你是一位资深的情绪周期分析师，精通市场情绪周期理论。
```

**理论背景**: 提供五个阶段的典型特征
- 启动期: 涨停数增加，连板高度低，炸板率低
- 高潮期: 涨停数最多，连板高度最高，炸板率极低
- 分化期: 涨停数减少，炸板率飙升，分时走势分化
- 修复期: 涨停数稳定，炸板率下降，市场观望
- 退潮期: 涨停数持续减少，连板断层，资金撤离

**输出格式**: JSON结构化
```json
{
  "stage": "CLIMAX",
  "confidence": 0.85,
  "reasoning": "判定理由",
  "key_indicators": ["关键指标1", "关键指标2"],
  "risk_level": "MEDIUM",
  "opportunity_level": "HIGH"
}
```

### 3. 题材持续性评估 (sustainability.md)

**目标**: 评估题材的持续性和生命周期

**角色设定**:
```
你是一位资深题材研究员，擅长评估题材的持续性和生命周期。
```

**分析维度**:
- 情绪周期阶段
- 容量结构健康度
- 历史表现
- 催化剂强度

**输出格式**: JSON结构化
```json
{
  "sustainability_score": 75,
  "time_horizon": "3-5个交易日",
  "risk_factors": ["风险1", "风险2"],
  "support_factors": ["支撑1", "支撑2"],
  "reasoning": "评估理由"
}
```

### 4. 操作建议生成 (trading_advice.md)

**目标**: 生成具体的操作建议

**角色设定**:
```
你是一位实战派交易员，擅长将分析结果转化为具体的操作建议。
```

**分析维度**:
- 风险收益比
- 入场时机
- 出场策略
- 仓位管理

**输出格式**: JSON结构化
```json
{
  "action": "低吸",
  "entry_timing": "回调至支撑位时介入",
  "exit_strategy": "冲高减仓，破位止损",
  "position_sizing": "轻仓试探，盈利加仓",
  "risk_warning": "注意大盘走势",
  "reasoning": "建议理由"
}
```

## 提示词设计原则

### 1. 角色一致性

**好的示例**:
```
你是一位拥有十年经验的游资操盘手，擅长通过盘面细节还原市场资金的真实意图。
你的分析风格：
- 注重资金流向和板块轮动
- 关注龙头股的表现
- 重视市场情绪的变化
```

**不好的示例**:
```
请分析市场。
```

### 2. 任务明确性

**好的示例**:
```
请根据以下数据，判定该板块所处的情绪周期阶段（启动期/高潮期/分化期/修复期/退潮期），
并给出判定理由、置信度和风险机会等级。
```

**不好的示例**:
```
分析一下这个板块。
```

### 3. 上下文结构化

**好的示例**:
```
## 板块基本信息
- 板块名称: 人工智能
- 强度分数: 12000
- 新旧标记: 新面孔

## 涨停数据
- 今日涨停数: 25
- 昨日涨停数: 18
- 全市场炸板率: 15%

## 连板梯队
- 5板及以上: 2只
- 3-4板: 5只
- 1-2板: 18只
```

**不好的示例**:
```
数据: 人工智能, 12000, 25, 18, 15%, 2, 5, 18
```

### 4. 输出格式约束

**好的示例**:
```
请以JSON格式返回分析结果，必须包含以下字段：
{
  "stage": "阶段名称（必须是以下之一：启动期/高潮期/分化期/修复期/退潮期）",
  "confidence": 置信度（0-1之间的浮点数）,
  "reasoning": "判定理由（字符串）",
  "risk_level": "风险等级（Low/Medium/High）"
}

不要包含任何其他文本，只返回JSON。
```

**不好的示例**:
```
返回分析结果。
```

### 5. 领域知识注入

**好的示例**:
```
## 情绪周期理论

情绪周期是市场资金情绪的演变过程，通常经历五个阶段：

1. **启动期**
   - 特征: 涨停数开始增加，连板高度较低（1-2板为主），炸板率低
   - 资金行为: 试探性进场，观望情绪浓厚
   - 风险: 低，机会: 中

2. **高潮期**
   - 特征: 涨停数达到峰值，连板高度最高（3板以上增多），炸板率极低（<20%）
   - 资金行为: 大量资金涌入，追涨情绪高涨
   - 风险: 中，机会: 高

[继续其他阶段...]
```

**不好的示例**:
```
根据情绪周期理论分析。
```

## 提示词优化技巧

### 1. Few-Shot Learning

在提示词中提供示例，帮助LLM理解期望的输出：

```markdown
## 示例分析

### 示例1: 高潮期判定
输入数据:
- 涨停数: 30 (昨日: 25)
- 连板梯队: 5板3只, 3板8只, 1板19只
- 炸板率: 12%

输出:
{
  "stage": "高潮期",
  "confidence": 0.9,
  "reasoning": "涨停数持续增加，连板高度达到5板，炸板率极低，资金追涨情绪高涨",
  "risk_level": "MEDIUM",
  "opportunity_level": "HIGH"
}

### 示例2: 分化期判定
输入数据:
- 涨停数: 18 (昨日: 30)
- 连板梯队: 5板1只, 3板3只, 1板14只
- 炸板率: 35%

输出:
{
  "stage": "分化期",
  "confidence": 0.85,
  "reasoning": "涨停数大幅减少，炸板率飙升至35%，高位股开始分化",
  "risk_level": "HIGH",
  "opportunity_level": "LOW"
}

## 现在请分析以下数据
[实际数据]
```

### 2. Chain-of-Thought (思维链)

引导LLM逐步推理：

```markdown
请按以下步骤分析：

1. **数据观察**: 列出关键数据点（涨停数变化、连板高度、炸板率）
2. **特征匹配**: 将观察到的特征与五个阶段的典型特征对比
3. **初步判定**: 给出最可能的阶段
4. **置信度评估**: 评估判定的可信度
5. **风险机会评级**: 基于阶段特征评估风险和机会
6. **最终结论**: 输出结构化结果
```

### 3. 温度参数调优

不同任务使用不同的temperature：

```python
# 情绪周期判定 - 需要一定创造性
llm_analyzer.analyze_emotion_cycle(
    sector_name="人工智能",
    context=context,
    temperature=0.7  # 平衡创造性和一致性
)

# 数据总结 - 需要确定性
llm_analyzer.summarize_data(
    data=data,
    temperature=0.3  # 更确定的输出
)

# 创意建议 - 需要创造性
llm_analyzer.generate_trading_advice(
    sector_name="人工智能",
    context=context,
    temperature=0.8  # 更多样化的建议
)
```

### 4. 上下文长度控制

避免超过LLM的token限制：

```python
class ContextBuilder:
    def format_for_llm(
        self,
        context: AnalysisContext,
        max_tokens: int = 8000
    ) -> str:
        """格式化上下文，控制长度"""
        
        # 优先级排序
        essential_data = self._get_essential_data(context)
        supplementary_data = self._get_supplementary_data(context)
        
        # 估算token数（粗略估计：1 token ≈ 1.5 字符）
        formatted = essential_data
        current_tokens = len(formatted) / 1.5
        
        # 逐步添加补充数据，直到接近限制
        for data_chunk in supplementary_data:
            chunk_tokens = len(data_chunk) / 1.5
            if current_tokens + chunk_tokens < max_tokens * 0.9:
                formatted += data_chunk
                current_tokens += chunk_tokens
            else:
                break
        
        return formatted
```

### 5. 错误处理和降级

处理LLM返回格式错误：

```python
def parse_llm_response(response: str) -> Dict[str, Any]:
    """解析LLM响应，带降级处理"""
    
    try:
        # 尝试直接解析JSON
        return json.loads(response)
    except json.JSONDecodeError:
        # 尝试提取JSON块
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        # 降级：返回默认结构
        logger.warning(f"Failed to parse LLM response: {response}")
        return {
            "stage": "UNKNOWN",
            "confidence": 0.0,
            "reasoning": "解析失败",
            "risk_level": "UNKNOWN",
            "opportunity_level": "UNKNOWN"
        }
```

## 自定义提示词

### 方法1: 修改现有模板

1. 复制模板文件：
```bash
cp prompts/market_intent.md prompts/market_intent_custom.md
```

2. 编辑模板，修改角色设定或分析维度

3. 在代码中使用自定义模板：
```python
prompt_engine = PromptEngine(template_dir="prompts")
prompt = prompt_engine.load_template("market_intent_custom.md")
```

### 方法2: 创建新模板

1. 创建新文件 `prompts/my_analysis.md`：

```markdown
# 我的自定义分析

## 角色设定
你是一位[角色描述]。

## 任务
请分析[任务描述]。

## 输入数据
{data}

## 输出格式
请以JSON格式返回：
{
  "field1": "...",
  "field2": "..."
}
```

2. 在代码中使用：
```python
prompt_engine = PromptEngine()
template = prompt_engine.load_template("my_analysis.md")
prompt = prompt_engine.render_template(
    template,
    {"data": formatted_data}
)
result = llm_analyzer._call_llm(prompt)
```

### 方法3: 动态构建提示词

```python
def build_custom_prompt(
    role: str,
    task: str,
    data: Dict[str, Any],
    output_format: Dict[str, str]
) -> str:
    """动态构建提示词"""
    
    prompt = f"""# {task}

## 角色设定
{role}

## 任务描述
{task}

## 输入数据
"""
    
    for key, value in data.items():
        prompt += f"- {key}: {value}\n"
    
    prompt += "\n## 输出格式\n请以JSON格式返回：\n"
    prompt += json.dumps(output_format, indent=2, ensure_ascii=False)
    
    return prompt
```

## 提示词测试和评估

### 1. 单元测试

```python
def test_emotion_cycle_prompt():
    """测试情绪周期提示词生成"""
    
    prompt_engine = PromptEngine()
    context = create_test_context()
    
    prompt = prompt_engine.build_emotion_cycle_prompt(
        sector_name="人工智能",
        context=context
    )
    
    # 验证提示词包含必要元素
    assert "情绪周期" in prompt
    assert "启动期" in prompt
    assert "高潮期" in prompt
    assert "JSON" in prompt
```

### 2. 集成测试

```python
def test_llm_emotion_cycle_analysis():
    """测试完整的LLM情绪周期分析"""
    
    llm_analyzer = LLMAnalyzer(api_key="test_key")
    context = create_test_context()
    
    result = llm_analyzer.analyze_emotion_cycle(
        sector_name="人工智能",
        context=context
    )
    
    # 验证返回结果
    assert result["stage"] in ["启动期", "高潮期", "分化期", "修复期", "退潮期"]
    assert 0 <= result["confidence"] <= 1
    assert "reasoning" in result
```

### 3. A/B测试

对比不同提示词版本的效果：

```python
def compare_prompts(
    prompt_v1: str,
    prompt_v2: str,
    test_cases: List[Dict]
) -> Dict[str, float]:
    """对比两个提示词版本"""
    
    results = {"v1": [], "v2": []}
    
    for test_case in test_cases:
        # 测试版本1
        response_v1 = llm_analyzer._call_llm(
            prompt_v1.format(**test_case)
        )
        score_v1 = evaluate_response(response_v1, test_case["expected"])
        results["v1"].append(score_v1)
        
        # 测试版本2
        response_v2 = llm_analyzer._call_llm(
            prompt_v2.format(**test_case)
        )
        score_v2 = evaluate_response(response_v2, test_case["expected"])
        results["v2"].append(score_v2)
    
    return {
        "v1_avg": sum(results["v1"]) / len(results["v1"]),
        "v2_avg": sum(results["v2"]) / len(results["v2"])
    }
```

## 常见问题

### Q: LLM返回格式不一致怎么办？

**A**: 
1. 在提示词中明确要求JSON格式
2. 提供输出示例
3. 使用更低的temperature（如0.3）
4. 实现robust的解析逻辑

### Q: 如何提高分析质量？

**A**:
1. 提供更详细的角色设定和领域知识
2. 使用Few-Shot Learning提供示例
3. 使用Chain-of-Thought引导推理
4. 选择更强大的模型（如GPT-4）

### Q: 如何减少API成本？

**A**:
1. 使用更便宜的模型（如glm-4-flash）
2. 减少上下文长度
3. 设置max_tokens限制
4. 缓存重复的分析结果

### Q: 如何处理中文和英文混合？

**A**: 
1. 在提示词中明确要求使用中文
2. 使用中文模型（如GLM-4、通义千问）
3. 在输出格式中使用中文字段名

## 最佳实践总结

1. **角色设定要具体**: 不要只说"你是分析师"，要说"你是拥有十年经验的游资操盘手"
2. **任务要明确**: 清楚说明要分析什么、输出什么
3. **数据要结构化**: 使用表格、列表等清晰的格式
4. **输出要约束**: 明确指定JSON格式和必需字段
5. **知识要注入**: 提供必要的领域知识和理论背景
6. **示例要充分**: 使用Few-Shot Learning提供示例
7. **推理要引导**: 使用Chain-of-Thought引导逐步推理
8. **错误要处理**: 实现robust的解析和降级逻辑
9. **测试要充分**: 使用单元测试和集成测试验证效果
10. **迭代要持续**: 根据实际效果不断优化提示词

## 相关资源

- [LLM集成指南](LLM_INTEGRATION.md)
- [配置指南](CONFIGURATION_GUIDE.md)
- [提示词模板目录](../prompts/)
- [示例代码](../examples/)

## 参考文献

- OpenAI Prompt Engineering Guide: https://platform.openai.com/docs/guides/prompt-engineering
- Anthropic Prompt Engineering: https://docs.anthropic.com/claude/docs/prompt-engineering
- 智谱AI文档: https://open.bigmodel.cn/dev/howuse/prompts
