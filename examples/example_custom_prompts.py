"""
自定义提示词示例

演示如何自定义提示词模板，以适应特定的分析需求。
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.llm import PromptEngine, LLMAnalyzer, ContextBuilder
from src.data import KaipanlaDataSource
from config import ConfigManager


def example_1_modify_existing_template():
    """示例1: 修改现有模板"""
    
    print("=" * 60)
    print("示例1: 修改现有提示词模板")
    print("=" * 60)
    print()
    
    # 创建自定义模板
    custom_template = """# 市场资金意图分析（自定义版本）

## 角色设定
你是一位拥有十五年经验的顶级游资操盘手，专注于短线题材炒作。
你的分析风格更加激进，注重捕捉市场情绪的微妙变化。

## 任务
请根据以下市场数据，分析主力资金的真实意图和流向。

## 输入数据
{context}

## 输出格式
请以JSON格式返回分析结果。
"""
    
    # 保存自定义模板
    custom_template_path = project_root / "prompts" / "market_intent_custom.md"
    with open(custom_template_path, "w", encoding="utf-8") as f:
        f.write(custom_template)
    
    print(f"✓ 自定义模板已保存: {custom_template_path}")
    print()
    
    # 使用自定义模板
    prompt_engine = PromptEngine()
    template = prompt_engine.load_template("market_intent_custom.md")
    
    print("自定义模板内容:")
    print("-" * 60)
    print(template[:200] + "...")
    print()


def example_2_create_new_template():
    """示例2: 创建全新的分析模板"""
    
    print("=" * 60)
    print("示例2: 创建全新的分析模板")
    print("=" * 60)
    print()
    
    # 创建一个新的分析模板：板块龙头识别
    new_template = """# 板块龙头识别分析

## 角色设定
你是一位专注于龙头股识别的资深分析师。

## 任务
请根据以下板块数据，识别该板块的龙头股和潜力股。

## 输入数据
板块名称: {sector_name}
板块成交额: {sector_turnover}亿
个股列表:
{stock_list}

## 分析维度
1. 成交额排名
2. 涨幅排名
3. 连板高度
4. 市场地位
5. 题材纯正度

## 输出格式
请以JSON格式返回：
{{
  "leading_stock": "龙头股名称",
  "potential_stocks": ["潜力股1", "潜力股2"],
  "reasoning": "判定理由",
  "confidence": 0.85
}}
"""
    
    # 保存新模板
    new_template_path = project_root / "prompts" / "leading_stock_analysis.md"
    with open(new_template_path, "w", encoding="utf-8") as f:
        f.write(new_template)
    
    print(f"✓ 新模板已创建: {new_template_path}")
    print()
    
    # 使用新模板
    prompt_engine = PromptEngine()
    template = prompt_engine.load_template("leading_stock_analysis.md")
    
    # 渲染模板
    prompt = prompt_engine.render_template(
        template,
        {
            "sector_name": "人工智能",
            "sector_turnover": "150.5",
            "stock_list": "股票A: 30亿\n股票B: 25亿\n股票C: 20亿"
        }
    )
    
    print("渲染后的提示词:")
    print("-" * 60)
    print(prompt[:300] + "...")
    print()


def example_3_dynamic_prompt_building():
    """示例3: 动态构建提示词"""
    
    print("=" * 60)
    print("示例3: 动态构建提示词")
    print("=" * 60)
    print()
    
    def build_custom_analysis_prompt(
        role: str,
        task: str,
        data: dict,
        output_format: dict
    ) -> str:
        """动态构建自定义分析提示词"""
        
        prompt = f"""# 自定义分析

## 角色设定
{role}

## 任务描述
{task}

## 输入数据
"""
        
        for key, value in data.items():
            prompt += f"- {key}: {value}\n"
        
        prompt += "\n## 输出格式\n请以JSON格式返回：\n"
        import json
        prompt += json.dumps(output_format, indent=2, ensure_ascii=False)
        
        return prompt
    
    # 构建自定义提示词
    custom_prompt = build_custom_analysis_prompt(
        role="你是一位风险控制专家",
        task="请评估该板块的风险等级",
        data={
            "板块名称": "人工智能",
            "涨停数": 25,
            "炸板率": "35%",
            "连板高度": "5板"
        },
        output_format={
            "risk_level": "风险等级（Low/Medium/High）",
            "risk_factors": ["风险因素1", "风险因素2"],
            "mitigation": "风险缓解建议"
        }
    )
    
    print("动态构建的提示词:")
    print("-" * 60)
    print(custom_prompt)
    print()


def example_4_use_custom_prompt_with_llm():
    """示例4: 使用自定义提示词调用LLM"""
    
    print("=" * 60)
    print("示例4: 使用自定义提示词调用LLM")
    print("=" * 60)
    print()
    
    # 加载配置
    config = ConfigManager()
    
    # 初始化LLM分析器
    llm_analyzer = LLMAnalyzer(
        api_key=config.get("llm.api_key"),
        provider=config.get("llm.provider"),
        model_name=config.get("llm.model_name")
    )
    
    # 自定义提示词
    custom_prompt = """你是一位市场情绪分析专家。

请根据以下数据判断市场情绪：
- 涨停数: 30
- 跌停数: 5
- 上涨家数: 2500
- 下跌家数: 1500

请以JSON格式返回：
{
  "sentiment": "情绪（乐观/中性/悲观）",
  "confidence": 0.85,
  "reasoning": "判定理由"
}
"""
    
    print("发送自定义提示词到LLM...")
    print()
    
    try:
        # 调用LLM
        response = llm_analyzer._call_llm(
            custom_prompt,
            temperature=0.7
        )
        
        print("LLM响应:")
        print("-" * 60)
        print(response)
        print()
        
    except Exception as e:
        print(f"❌ LLM调用失败: {e}")
        print("   请确保配置了有效的API密钥")
        print()


def main():
    """主函数"""
    
    print()
    print("🎨 自定义提示词示例")
    print()
    
    # 运行所有示例
    example_1_modify_existing_template()
    example_2_create_new_template()
    example_3_dynamic_prompt_building()
    
    # 示例4需要有效的API密钥，可选运行
    print("是否运行示例4（需要有效的LLM API密钥）？[y/N]: ", end="")
    choice = input().strip().lower()
    if choice == 'y':
        example_4_use_custom_prompt_with_llm()
    
    print("=" * 60)
    print("✅ 所有示例运行完成！")
    print("=" * 60)
    print()
    print("提示:")
    print("  - 自定义模板保存在 prompts/ 目录")
    print("  - 可以修改现有模板或创建新模板")
    print("  - 使用 PromptEngine 加载和渲染模板")
    print("  - 动态构建提示词适合临时分析需求")
    print()


if __name__ == "__main__":
    main()
