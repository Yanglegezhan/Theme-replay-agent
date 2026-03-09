# Theme Anchor Agent CLI 使用指南

## 概述

Theme Anchor Agent CLI 是一个命令行工具，用于执行A股超短线题材锚定分析。它提供了灵活的参数配置和多种输出格式。

## 快速开始

### 基本用法

```bash
# 分析今天的市场
python theme_cli.py

# 或使用批处理脚本（Windows）
theme_cli.bat
```

### 分析指定日期

```bash
# 分析特定日期
python theme_cli.py --date 2026-01-20

# 分析昨天
python theme_cli.py --yesterday
```

## 命令行参数

### 日期参数

- `-d, --date DATE`: 指定分析日期（格式：YYYY-MM-DD）
- `-y, --yesterday`: 分析昨天的市场

**注意**: `--date` 和 `--yesterday` 互斥，只能使用其中一个。

### 配置参数

- `-c, --config CONFIG`: 指定配置文件路径
  - 默认使用 `config/config.yaml`
  - 可以指定自定义配置文件

```bash
# 使用自定义配置
python theme_cli.py --config /path/to/my_config.yaml
```

### 输出参数

- `-f, --format {markdown,json,both}`: 输出格式
  - `markdown`: 只生成Markdown报告
  - `json`: 只生成JSON报告
  - `both`: 同时生成两种格式（默认）

- `-o, --output OUTPUT`: 指定输出目录
  - 默认为 `output/reports`

- `--no-save`: 不保存报告文件，只在控制台显示结果

```bash
# 只生成JSON格式
python theme_cli.py --format json

# 指定输出目录
python theme_cli.py --output /path/to/output

# 不保存文件，只显示
python theme_cli.py --no-save
```

### 日志参数

- `-v, --verbose`: 详细输出模式（DEBUG级别）
- `-q, --quiet`: 静默模式（只输出错误）

```bash
# 详细输出
python theme_cli.py --verbose

# 静默模式
python theme_cli.py --quiet
```

## 使用示例

### 示例1: 基础分析

```bash
# 分析今天的市场，生成Markdown和JSON报告
python theme_cli.py
```

输出：
```
分析日期: 2026-01-22

初始化系统组件...
  [1/4] 初始化数据源...
  [2/4] 初始化历史追踪器...
  [3/4] 初始化LLM分析器...
  [4/4] 配置Agent参数...
✓ 系统组件初始化完成

================================================================================
开始分析: 2026-01-22
================================================================================

[步骤1] 题材筛选与强度初筛
筛选完成: 目标板块 7 个

[步骤2] 盘面联动与主动性分析
联动分析完成: 先锋板块 2 个

[步骤3] 情绪周期检测（LLM）
情绪周期检测完成: 7 个板块

[步骤4] 题材容量与结构画像
容量分析完成: 7 个板块

[步骤5] LLM深度分析
LLM深度分析完成

================================================================================
分析完成
================================================================================

保存分析报告...
✓ Markdown报告已保存: output/reports/theme_analysis_20260122.md
✓ JSON报告已保存: output/reports/theme_analysis_20260122.json

✓ 所有任务完成
```

### 示例2: 分析历史日期

```bash
# 分析2026年1月20日的市场
python theme_cli.py --date 2026-01-20
```

### 示例3: 自定义配置和输出

```bash
# 使用自定义配置，只生成JSON，保存到指定目录
python theme_cli.py \
  --config config/my_config.yaml \
  --format json \
  --output /data/reports
```

### 示例4: 快速查看（不保存）

```bash
# 快速分析，不保存报告文件
python theme_cli.py --no-save --quiet
```

### 示例5: 调试模式

```bash
# 详细输出，用于调试
python theme_cli.py --verbose
```

## 输出文件

### 文件命名规则

- Markdown: `theme_analysis_YYYYMMDD.md`
- JSON: `theme_analysis_YYYYMMDD.json`

### Markdown报告结构

```markdown
# A股超短线题材锚定分析报告

**分析日期**: 2026-01-22
**生成时间**: 2026-01-22T15:30:00

## 执行摘要
今日共筛选出 7 个核心板块...

## 市场资金意图
**主力资金流向**: ...
**板块轮动**: ...
**市场情绪**: ...

## 市场概览
- 目标板块数: 7
- 新面孔: 3 个
- 老面孔: 4 个
...

## 目标板块详情

### 1. 人工智能
**基础信息**:
- 排名: 1
- 强度分数: 12500
...

**盘面联动**:
- 先锋板块（领先大盘 8 分钟）
...

**情绪周期**: 高潮期 (置信度: 0.85)
...

**操作建议**:
- 操作方向: 低吸
- 入场时机: 回调至支撑位
...

---

## 风险提示
- 板块A：分化期，风险等级高...
...

## 免责声明
本报告由AI系统自动生成，仅供参考...
```

### JSON报告结构

```json
{
  "date": "2026-01-22",
  "generated_at": "2026-01-22T15:30:00",
  "summary": {
    "executive_summary": "...",
    "market_intent": {
      "main_capital_flow": "...",
      "sector_rotation": "...",
      "market_sentiment": "...",
      "key_drivers": [...],
      "confidence": 0.85
    }
  },
  "target_sectors": [
    {
      "sector_name": "人工智能",
      "rank": 1,
      "strength_score": 12500,
      "emotion_cycle": {
        "stage": "高潮期",
        "confidence": 0.85,
        ...
      },
      "capacity_profile": {...},
      "trading_advice": {...}
    },
    ...
  ],
  "market_overview": {...},
  "risk_warnings": [...]
}
```

## 配置文件

CLI使用 `config/config.yaml` 作为默认配置文件。主要配置项：

```yaml
# LLM配置
llm:
  provider: "zhipu"  # openai, zhipu, qwen
  api_key: "your-api-key"
  model_name: "glm-4-flash"
  temperature: 0.7

# 分析参数
analysis:
  sector_filter:
    high_strength_threshold: 8000
    target_sector_count: 7
  correlation:
    leading_time_min: 5
    leading_time_max: 10
  capacity:
    large_cap_turnover_threshold: 30

# 输出配置
output:
  report_dir: "output/reports"
  format: ["markdown", "json"]

# 日志配置
logging:
  level: "INFO"
  file: "logs/theme_anchor_agent.log"
```

## 错误处理

### 常见错误

1. **配置文件未找到**
   ```
   ✗ 配置文件未找到: config/config.yaml
   ```
   解决：确保配置文件存在，或使用 `--config` 指定正确路径

2. **API密钥未配置**
   ```
   ✗ 错误: LLM API密钥未配置
   ```
   解决：在配置文件中设置 `llm.api_key`

3. **日期格式错误**
   ```
   日期格式错误: 2026/01/20，应为 YYYY-MM-DD
   ```
   解决：使用正确的日期格式 `2026-01-20`

4. **数据获取失败**
   ```
   ✗ 分析失败: 无法获取板块数据
   ```
   解决：检查网络连接和数据源API状态

### 中断处理

按 `Ctrl+C` 可以随时中断程序：
```
^C
✗ 用户中断
```

## 进阶用法

### 批量分析

创建脚本批量分析多个日期：

```bash
#!/bin/bash
# batch_analysis.sh

dates=("2026-01-15" "2026-01-16" "2026-01-17" "2026-01-18" "2026-01-19")

for date in "${dates[@]}"
do
  echo "分析日期: $date"
  python theme_cli.py --date $date --quiet
done
```

### 定时任务

使用cron（Linux/Mac）或任务计划程序（Windows）设置定时分析：

```bash
# 每天15:30执行分析
30 15 * * * cd /path/to/Theme_repay_agent && python theme_cli.py
```

### 集成到工作流

```python
# workflow.py
from src.cli import ThemeCLI

def daily_analysis():
    cli = ThemeCLI()
    cli.config_manager = cli.load_config()
    cli.setup_logging(cli.config_manager)
    
    # 执行分析
    exit_code = cli.run()
    
    if exit_code == 0:
        print("分析成功")
        # 发送通知、上传报告等
    else:
        print("分析失败")
        # 错误处理
```

## 性能优化

### 加速分析

1. **使用更快的LLM模型**
   ```yaml
   llm:
     model_name: "glm-4-flash"  # 更快的模型
   ```

2. **减少分析板块数量**
   ```yaml
   analysis:
     sector_filter:
       target_sector_count: 5  # 从7减少到5
   ```

3. **调整超时设置**
   ```yaml
   llm:
     timeout: 30  # 减少超时时间
   ```

## 故障排查

### 启用详细日志

```bash
python theme_cli.py --verbose
```

### 检查日志文件

```bash
# 查看最新日志
tail -f logs/theme_anchor_agent.log

# 搜索错误
grep ERROR logs/theme_anchor_agent.log
```

### 测试配置

```bash
# 使用--no-save快速测试
python theme_cli.py --no-save --verbose
```

## 最佳实践

1. **每日分析**: 建议在收盘后（15:30-16:00）执行分析
2. **配置备份**: 定期备份配置文件
3. **报告归档**: 定期归档历史报告
4. **日志监控**: 定期检查日志文件，及时发现问题
5. **API限流**: 注意LLM API的调用频率限制

## 支持与反馈

如遇到问题或有改进建议，请：
1. 查看日志文件 `logs/theme_anchor_agent.log`
2. 检查配置文件是否正确
3. 确认网络连接和API状态
4. 提交Issue或联系开发团队

## 更新日志

### v0.1.0 (2026-01-22)
- 初始版本发布
- 支持基本的命令行参数
- 支持Markdown和JSON输出
- 集成LLM分析引擎
- 完整的错误处理和日志记录
