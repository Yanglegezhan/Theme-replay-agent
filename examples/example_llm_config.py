"""
LLM配置示例

演示如何配置和使用不同的LLM提供商。
"""

import sys
from pathlib import Path
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.llm import LLMAnalyzer, PromptEngine
from config import ConfigManager


def example_1_zhipu_config():
    """示例1: 配置智谱AI"""
    
    print("=" * 60)
    print("示例1: 配置智谱AI (Zhipu)")
    print("=" * 60)
    print()
    
    # 方式1: 通过配置文件
    print("方式1: 通过配置文件")
    print("-" * 60)
    print("""
在 config/config.yaml 中配置:

llm:
  provider: "zhipu"
  api_key: "YOUR_ZHIPU_API_KEY"
  model_name: "glm-4-flash"  # 或 "glm-4", "glm-3-turbo"
  temperature: 0.7
  max_tokens: 2000
  timeout: 60
  max_retries: 3
""")
    
    # 方式2: 通过代码
    print("方式2: 通过代码")
    print("-" * 60)
    
    llm_analyzer = LLMAnalyzer(
        api_key="your_zhipu_api_key_here",
        provider="zhipu",
        model_name="glm-4-flash",
        temperature=0.7,
        max_tokens=2000,
        timeout=60,
        max_retries=3
    )
    
    print("✓ 智谱AI配置完成")
    print(f"  提供商: {llm_analyzer.provider}")
    print(f"  模型: {llm_analyzer.model_name}")
    print()
    
    # 获取API密钥说明
    print("获取API密钥:")
    print("  1. 访问 https://open.bigmodel.cn/")
    print("  2. 注册并登录")
    print("  3. 在'API密钥'页面创建新密钥")
    print()
    
    # 模型选择建议
    print("模型选择建议:")
    print("  - glm-4: 最强性能，适合复杂分析")
    print("  - glm-4-flash: 速度快，性价比高（推荐）")
    print("  - glm-3-turbo: 经济型选择")
    print()


def example_2_openai_config():
    """示例2: 配置OpenAI"""
    
    print("=" * 60)
    print("示例2: 配置OpenAI")
    print("=" * 60)
    print()
    
    # 方式1: 通过配置文件
    print("方式1: 通过配置文件")
    print("-" * 60)
    print("""
在 config/config.yaml 中配置:

llm:
  provider: "openai"
  api_key: "YOUR_OPENAI_API_KEY"
  model_name: "gpt-4"  # 或 "gpt-4-turbo", "gpt-3.5-turbo"
  temperature: 0.7
  max_tokens: 2000
  timeout: 60
""")
    
    # 方式2: 通过代码
    print("方式2: 通过代码")
    print("-" * 60)
    
    llm_analyzer = LLMAnalyzer(
        api_key="your_openai_api_key_here",
        provider="openai",
        model_name="gpt-4",
        temperature=0.7
    )
    
    print("✓ OpenAI配置完成")
    print()
    
    # 使用代理
    print("使用代理:")
    print("-" * 60)
    print("""
如果需要通过代理访问OpenAI:

llm:
  provider: "openai"
  api_key: "YOUR_API_KEY"
  api_base: "http://your-proxy:port/v1"

或设置环境变量:
export HTTP_PROXY="http://your-proxy:port"
export HTTPS_PROXY="http://your-proxy:port"
""")
    
    # 获取API密钥说明
    print("获取API密钥:")
    print("  1. 访问 https://platform.openai.com/")
    print("  2. 注册并登录")
    print("  3. 在'API Keys'页面创建新密钥")
    print()
    
    # 模型选择建议
    print("模型选择建议:")
    print("  - gpt-4: 最强性能")
    print("  - gpt-4-turbo: 性能与速度平衡")
    print("  - gpt-3.5-turbo: 经济型选择")
    print()


def example_3_qwen_config():
    """示例3: 配置通义千问"""
    
    print("=" * 60)
    print("示例3: 配置通义千问 (Qwen)")
    print("=" * 60)
    print()
    
    # 方式1: 通过配置文件
    print("方式1: 通过配置文件")
    print("-" * 60)
    print("""
在 config/config.yaml 中配置:

llm:
  provider: "qwen"
  api_key: "YOUR_QWEN_API_KEY"
  model_name: "qwen-plus"  # 或 "qwen-max", "qwen-turbo"
  temperature: 0.7
  max_tokens: 2000
""")
    
    # 方式2: 通过代码
    print("方式2: 通过代码")
    print("-" * 60)
    
    llm_analyzer = LLMAnalyzer(
        api_key="your_qwen_api_key_here",
        provider="qwen",
        model_name="qwen-plus",
        temperature=0.7
    )
    
    print("✓ 通义千问配置完成")
    print()
    
    # 获取API密钥说明
    print("获取API密钥:")
    print("  1. 访问 https://dashscope.console.aliyun.com/")
    print("  2. 注册阿里云账号并登录")
    print("  3. 开通DashScope服务")
    print("  4. 获取API-KEY")
    print()
    
    # 模型选择建议
    print("模型选择建议:")
    print("  - qwen-max: 最强性能")
    print("  - qwen-plus: 平衡选择（推荐）")
    print("  - qwen-turbo: 速度优先")
    print()


def example_4_environment_variables():
    """示例4: 使用环境变量配置"""
    
    print("=" * 60)
    print("示例4: 使用环境变量配置")
    print("=" * 60)
    print()
    
    print("环境变量配置（优先级高于配置文件）:")
    print("-" * 60)
    print("""
# Linux/Mac
export THEME_ANCHOR_LLM_API_KEY="your_api_key"
export THEME_ANCHOR_LLM_PROVIDER="zhipu"
export THEME_ANCHOR_LLM_MODEL="glm-4-flash"

# Windows (CMD)
set THEME_ANCHOR_LLM_API_KEY=your_api_key
set THEME_ANCHOR_LLM_PROVIDER=zhipu
set THEME_ANCHOR_LLM_MODEL=glm-4-flash

# Windows (PowerShell)
$env:THEME_ANCHOR_LLM_API_KEY="your_api_key"
$env:THEME_ANCHOR_LLM_PROVIDER="zhipu"
$env:THEME_ANCHOR_LLM_MODEL="glm-4-flash"
""")
    
    # 在代码中读取环境变量
    print("在代码中读取环境变量:")
    print("-" * 60)
    print("""
import os

api_key = os.getenv("THEME_ANCHOR_LLM_API_KEY")
provider = os.getenv("THEME_ANCHOR_LLM_PROVIDER", "zhipu")
model_name = os.getenv("THEME_ANCHOR_LLM_MODEL", "glm-4-flash")

llm_analyzer = LLMAnalyzer(
    api_key=api_key,
    provider=provider,
    model_name=model_name
)
""")
    print()


def example_5_advanced_parameters():
    """示例5: 高级参数配置"""
    
    print("=" * 60)
    print("示例5: 高级参数配置")
    print("=" * 60)
    print()
    
    print("Temperature（温度）参数:")
    print("-" * 60)
    print("""
temperature控制输出的随机性和创造性:
- 0.0-0.3: 确定性输出，适合数据总结
- 0.4-0.7: 平衡创造性和一致性（推荐）
- 0.8-1.0: 高创造性，输出更多样化

示例:
# 需要确定性的任务
llm_analyzer._call_llm(prompt, temperature=0.3)

# 需要创造性的任务
llm_analyzer._call_llm(prompt, temperature=0.8)
""")
    
    print("Max Tokens（最大令牌数）:")
    print("-" * 60)
    print("""
max_tokens限制LLM响应的长度:
- null: 不限制（默认）
- 1000-2000: 简短回答
- 2000-4000: 详细分析（推荐）
- 4000+: 非常详细的输出

示例:
llm_analyzer = LLMAnalyzer(
    api_key="your_key",
    max_tokens=2000  # 限制为2000 tokens
)
""")
    
    print("Timeout（超时）和重试:")
    print("-" * 60)
    print("""
timeout和max_retries控制API调用的可靠性:

llm_analyzer = LLMAnalyzer(
    api_key="your_key",
    timeout=60,        # 60秒超时
    max_retries=3,     # 最多重试3次
    retry_delay=1.0    # 重试间隔1秒
)
""")
    print()


def example_6_cost_estimation():
    """示例6: 成本估算"""
    
    print("=" * 60)
    print("示例6: 成本估算")
    print("=" * 60)
    print()
    
    print("单次分析成本估算（7个板块）:")
    print("-" * 60)
    print()
    
    # 估算参数
    num_sectors = 7
    calls_per_sector = 3  # 情绪周期、持续性、操作建议
    market_intent_calls = 1
    total_calls = market_intent_calls + (num_sectors * calls_per_sector)
    avg_input_tokens = 2000
    avg_output_tokens = 500
    
    print(f"LLM调用次数: {total_calls}")
    print(f"平均输入tokens: {avg_input_tokens}")
    print(f"平均输出tokens: {avg_output_tokens}")
    print()
    
    # 智谱AI成本
    zhipu_cost_per_1k = 0.001  # 人民币
    zhipu_total_tokens = total_calls * (avg_input_tokens + avg_output_tokens)
    zhipu_cost = (zhipu_total_tokens / 1000) * zhipu_cost_per_1k
    
    print(f"智谱AI (glm-4-flash):")
    print(f"  单价: ¥{zhipu_cost_per_1k}/千tokens")
    print(f"  单次成本: ¥{zhipu_cost:.4f}")
    print(f"  月度成本 (20个交易日): ¥{zhipu_cost * 20:.2f}")
    print()
    
    # OpenAI成本
    openai_input_cost = 0.03  # 美元/千tokens
    openai_output_cost = 0.06  # 美元/千tokens
    openai_total_input = total_calls * avg_input_tokens
    openai_total_output = total_calls * avg_output_tokens
    openai_cost_usd = (openai_total_input / 1000 * openai_input_cost + 
                       openai_total_output / 1000 * openai_output_cost)
    openai_cost_cny = openai_cost_usd * 7  # 假设汇率7
    
    print(f"OpenAI (gpt-4):")
    print(f"  输入单价: ${openai_input_cost}/千tokens")
    print(f"  输出单价: ${openai_output_cost}/千tokens")
    print(f"  单次成本: ${openai_cost_usd:.2f} (约¥{openai_cost_cny:.2f})")
    print(f"  月度成本 (20个交易日): ${openai_cost_usd * 20:.2f} (约¥{openai_cost_cny * 20:.2f})")
    print()
    
    # 通义千问成本
    qwen_cost_per_1k = 0.04  # 人民币
    qwen_total_tokens = total_calls * (avg_input_tokens + avg_output_tokens)
    qwen_cost = (qwen_total_tokens / 1000) * qwen_cost_per_1k
    
    print(f"通义千问 (qwen-plus):")
    print(f"  单价: ¥{qwen_cost_per_1k}/千tokens")
    print(f"  单次成本: ¥{qwen_cost:.4f}")
    print(f"  月度成本 (20个交易日): ¥{qwen_cost * 20:.2f}")
    print()


def example_7_test_connection():
    """示例7: 测试LLM连接"""
    
    print("=" * 60)
    print("示例7: 测试LLM连接")
    print("=" * 60)
    print()
    
    # 加载配置
    config = ConfigManager()
    
    print(f"当前配置:")
    print(f"  提供商: {config.get('llm.provider')}")
    print(f"  模型: {config.get('llm.model_name')}")
    print()
    
    # 初始化LLM分析器
    try:
        llm_analyzer = LLMAnalyzer(
            api_key=config.get("llm.api_key"),
            provider=config.get("llm.provider"),
            model_name=config.get("llm.model_name")
        )
        
        print("正在测试连接...")
        
        # 发送简单的测试请求
        test_prompt = "请用一句话介绍你自己。"
        response = llm_analyzer._call_llm(test_prompt, temperature=0.7)
        
        print("✓ 连接成功！")
        print()
        print("LLM响应:")
        print("-" * 60)
        print(response)
        print()
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print()
        print("请检查:")
        print("  1. API密钥是否正确")
        print("  2. 网络连接是否正常")
        print("  3. API配额是否充足")
        print()


def main():
    """主函数"""
    
    print()
    print("🤖 LLM配置示例")
    print()
    
    # 运行所有示例
    example_1_zhipu_config()
    example_2_openai_config()
    example_3_qwen_config()
    example_4_environment_variables()
    example_5_advanced_parameters()
    example_6_cost_estimation()
    
    # 示例7需要有效的API密钥，可选运行
    print("是否测试LLM连接（需要有效的API密钥）？[y/N]: ", end="")
    choice = input().strip().lower()
    if choice == 'y':
        example_7_test_connection()
    
    print("=" * 60)
    print("✅ 所有示例运行完成！")
    print("=" * 60)
    print()
    print("提示:")
    print("  - 选择合适的LLM提供商和模型")
    print("  - 根据需求调整temperature和max_tokens")
    print("  - 使用环境变量保护API密钥")
    print("  - 定期检查API使用情况和成本")
    print()
    print("相关文档:")
    print("  - 配置指南: docs/CONFIGURATION_GUIDE.md")
    print("  - LLM集成指南: docs/LLM_INTEGRATION.md")
    print()


if __name__ == "__main__":
    main()
