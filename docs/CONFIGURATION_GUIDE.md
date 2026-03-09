# Configuration Guide

本文档详细说明了Theme Anchor Agent的配置选项和最佳实践。

## 快速开始

1. 复制示例配置文件：
```bash
cp config/config.example.yaml config/config.yaml
```

2. 编辑 `config/config.yaml` 并填入你的API密钥和其他设置

3. 验证配置：
```bash
python verify_setup.py
```

## 配置项详解

### LLM配置 (llm)

LLM配置控制大语言模型的行为和API调用。

#### provider
- **类型**: string
- **可选值**: `openai`, `zhipu`, `qwen`
- **默认值**: `zhipu`
- **说明**: LLM提供商选择
  - `openai`: OpenAI GPT系列模型
  - `zhipu`: 智谱AI GLM系列模型
  - `qwen`: 阿里通义千问系列模型

#### api_key
- **类型**: string
- **必填**: 是
- **说明**: LLM API密钥，从对应提供商获取
- **获取方式**:
  - OpenAI: https://platform.openai.com/api-keys
  - 智谱AI: https://open.bigmodel.cn/
  - 通义千问: https://dashscope.console.aliyun.com/

#### api_base
- **类型**: string
- **可选**: 是
- **默认值**: 空（使用默认端点）
- **说明**: 自定义API端点，用于代理或私有部署

#### model_name
- **类型**: string
- **说明**: 模型名称，取决于provider
- **推荐配置**:
  - OpenAI: `gpt-4` (最佳质量) 或 `gpt-3.5-turbo` (性价比)
  - 智谱AI: `glm-4` (最佳质量) 或 `glm-4-flash` (速度快)
  - 通义千问: `qwen-max` (最佳质量) 或 `qwen-turbo` (速度快)

#### temperature
- **类型**: float
- **范围**: 0.0 - 1.0
- **默认值**: 0.7
- **说明**: 控制输出的随机性和创造性
  - 0.0: 确定性输出，适合需要一致性的场景
  - 0.7: 平衡创造性和一致性（推荐）
  - 1.0: 最大创造性，输出更多样化

#### max_tokens
- **类型**: integer 或 null
- **默认值**: null
- **说明**: 限制LLM响应的最大token数
  - null: 不限制
  - 建议值: 2000-4000（足够详细的分析）

#### timeout
- **类型**: integer 或 null
- **默认值**: null
- **说明**: API请求超时时间（秒）
  - null: 不限制
  - 建议值: 60-120（复杂分析可能需要更长时间）

#### max_retries
- **类型**: integer
- **默认值**: 3
- **说明**: API调用失败时的重试次数

#### retry_delay
- **类型**: float
- **默认值**: 1.0
- **说明**: 重试之间的延迟时间（秒）

### 数据源配置 (data_source)

#### primary (主数据源 - kaipanla)
- **enabled**: 是否启用主数据源
- **timeout**: 请求超时时间（秒）
- **max_retries**: 最大重试次数

#### fallback (备用数据源 - akshare)
- **enabled**: 是否启用备用数据源
- **timeout**: 请求超时时间（秒）
- **说明**: 当主数据源失败时自动切换到备用数据源

### 分析参数配置 (analysis)

#### sector_filter (板块筛选)
- **high_strength_threshold**: 高强度阈值（累计涨停数）
  - 默认: 8000
  - 说明: 超过此阈值的板块直接入选
- **medium_strength_threshold**: 中等强度阈值
  - 默认: 2000
  - 说明: 用于补齐目标板块数量
- **target_sector_count**: 目标板块数量
  - 默认: 7
  - 说明: 最终筛选出的板块数量
- **ndays**: N日强度统计天数
  - 默认: 7
  - 说明: 计算板块强度的时间窗口

#### correlation (盘面联动)
- **time_lag_threshold**: 时差阈值（分钟）
  - 默认: 10
  - 说明: 用于判定板块与大盘的联动关系
- **leading_time_min**: 先锋板块最小领先时间
  - 默认: 5分钟
- **leading_time_max**: 先锋板块最大领先时间
  - 默认: 10分钟
- **resonance_elasticity_threshold**: 共振弹性系数阈值
  - 默认: 3.0
  - 说明: 板块涨幅/大盘涨幅 >= 3.0 视为强度共振
- **market_change_threshold**: 大盘变化阈值
  - 默认: 0.01 (1%)
  - 说明: 用于识别大盘显著变化

#### capacity (容量分析)
- **large_cap_turnover_threshold**: 大容量阈值（亿元）
  - 默认: 30
  - 说明: 核心中军成交额超过此值视为大容量主线
- **leading_stock_turnover_threshold**: 核心中军成交额阈值
  - 默认: 30亿元

#### emotion_cycle (情绪周期)
- **blown_board_rate_high**: 高潮期炸板率上限
  - 默认: 0.20 (20%)
  - 说明: 炸板率低于此值可能处于高潮期
- **blown_board_rate_divergence**: 分化期炸板率下限
  - 默认: 0.30 (30%)
  - 说明: 炸板率高于此值可能处于分化期

### 历史数据存储 (history)
- **storage_path**: 历史数据存储路径
- **file_format**: 存储格式（目前仅支持csv）
- **retention_days**: 数据保留天数

### 输出配置 (output)
- **report_dir**: 报告输出目录
- **format**: 输出格式列表（支持markdown和json）
- **include_charts**: 是否包含图表（未来功能）

### 日志配置 (logging)
- **level**: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- **format**: 日志格式字符串
- **file**: 日志文件路径
- **max_bytes**: 单个日志文件最大大小
- **backup_count**: 保留的备份日志文件数量
- **console_output**: 是否输出到控制台

### 提示词配置 (prompts)
- **template_dir**: 提示词模板目录
- **context_max_tokens**: LLM上下文最大token数

## 配置最佳实践

### 1. 选择合适的LLM提供商

**成本优先**:
```yaml
llm:
  provider: "zhipu"
  model_name: "glm-4-flash"
  temperature: 0.7
```

**质量优先**:
```yaml
llm:
  provider: "openai"
  model_name: "gpt-4"
  temperature: 0.7
```

**平衡选择**:
```yaml
llm:
  provider: "qwen"
  model_name: "qwen-plus"
  temperature: 0.7
```

### 2. 调整分析参数

**激进策略**（捕捉更多机会）:
```yaml
analysis:
  sector_filter:
    high_strength_threshold: 5000  # 降低阈值
    target_sector_count: 10  # 增加板块数量
```

**保守策略**（聚焦核心题材）:
```yaml
analysis:
  sector_filter:
    high_strength_threshold: 10000  # 提高阈值
    target_sector_count: 5  # 减少板块数量
```

### 3. 优化LLM性能

**提高响应速度**:
```yaml
llm:
  model_name: "glm-4-flash"  # 使用快速模型
  max_tokens: 2000  # 限制输出长度
  timeout: 30  # 设置超时
```

**提高分析质量**:
```yaml
llm:
  model_name: "gpt-4"  # 使用高质量模型
  temperature: 0.5  # 降低随机性
  max_tokens: 4000  # 允许更详细的输出
```

### 4. 数据源配置

**网络不稳定环境**:
```yaml
data_source:
  primary:
    timeout: 60  # 增加超时时间
    max_retries: 5  # 增加重试次数
  fallback:
    enabled: true  # 确保启用备用数据源
```

### 5. 日志配置

**开发调试**:
```yaml
logging:
  level: "DEBUG"
  console_output: true
```

**生产环境**:
```yaml
logging:
  level: "INFO"
  console_output: false
  max_bytes: 52428800  # 50MB
  backup_count: 10
```

## 环境变量支持

系统支持通过环境变量覆盖配置文件中的敏感信息：

```bash
# LLM API密钥
export THEME_ANCHOR_LLM_API_KEY="your_api_key_here"

# LLM提供商
export THEME_ANCHOR_LLM_PROVIDER="openai"

# 模型名称
export THEME_ANCHOR_LLM_MODEL="gpt-4"
```

环境变量优先级高于配置文件。

## 配置验证

使用内置的验证脚本检查配置是否正确：

```bash
python verify_setup.py
```

验证内容包括：
- 配置文件格式正确性
- API密钥有效性
- 目录结构完整性
- 依赖包安装情况

## 故障排除

### API密钥无效
**症状**: `Authentication failed` 或 `Invalid API key`
**解决**: 检查API密钥是否正确，是否有足够的配额

### 请求超时
**症状**: `Request timeout` 或 `Connection timeout`
**解决**: 增加 `timeout` 值或检查网络连接

### 数据源失败
**症状**: `Data source error` 或 `Failed to fetch data`
**解决**: 
1. 检查网络连接
2. 确保备用数据源已启用
3. 增加重试次数和超时时间

### LLM响应格式错误
**症状**: `Failed to parse LLM response`
**解决**:
1. 降低 `temperature` 值（提高确定性）
2. 检查提示词模板是否正确
3. 尝试更换模型

## 高级配置

### 自定义提示词模板

1. 复制默认模板：
```bash
cp prompts/market_intent.md prompts/market_intent_custom.md
```

2. 编辑自定义模板

3. 在代码中指定使用自定义模板：
```python
prompt_engine = PromptEngine(template_dir="prompts")
prompt = prompt_engine.load_template("market_intent_custom.md")
```

### 使用代理

如果需要通过代理访问LLM API：

```yaml
llm:
  api_base: "http://your-proxy-server:port/v1"
```

或设置环境变量：
```bash
export HTTP_PROXY="http://your-proxy:port"
export HTTPS_PROXY="http://your-proxy:port"
```

## 配置模板示例

完整的配置示例请参考 `config/config.example.yaml`。

## 相关文档

- [快速开始指南](QUICKSTART.md)
- [LLM集成指南](LLM_INTEGRATION.md)
- [提示词工程说明](PROMPT_ENGINEERING.md)
