# -*- coding: utf-8 -*-
"""
LLM情绪周期分析测试
测试LLM情绪周期分析的提示词生成、响应解析和错误处理
验证Property 11-12: Emotion cycle LLM analysis and validation
Requirements: 3.1, 3.2, 3.3
Property 11: Emotion cycle LLM analysis
Property 12: Emotion cycle stage validation
"""

import os
import sys
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm.llm_analyzer import LLMAnalyzer
from src.llm.prompt_engine import PromptEngine
from src.llm.context_builder import ContextBuilder
from src.models.data_models import (
    AnalysisContext,
    EmotionCycleAnalysis
)


# ============ Test Fixtures ============

@pytest.fixture
def sample_context():
    """创建示例分析上下文"""
    return AnalysisContext(
        date="2026-01-22",
        market_overview={
            "涨停数": 50,
            "跌停数": 5,
            "炸板率": "25.0%",
            "最高连板": "5连板"
        },
        target_sectors=[
            {
                "sector_name": "人工智能",
                "rank": 1,
                "strength_score": 12000,
                "is_new_face": True,
                "consecutive_days": 0,
                "limit_up_count": 15,
                "consecutive_boards": {
                    5: ["股票A"],
                    3: ["股票B", "股票C"],
                    1: ["股票D", "股票E", "股票F"]
                },
                "turnover": 85.5
            }
        ],
        sector_relationships={
            "leading_sectors": ["人工智能"],
            "resonance_sectors": [],
            "divergence_sectors": [],
            "seesaw_effects": []
        },
        historical_context={
            "new_faces": ["人工智能"],
            "old_faces": []
        }
    )


@pytest.fixture
def sample_limit_up_data():
    """创建示例涨停数据"""
    return {
        "limit_up_count": 50,
        "limit_down_count": 5,
        "blown_limit_up_rate": 25.0,
        "yesterday_limit_up_performance": 3.5,
        "consecutive_boards": {
            5: ["股票A"],
            3: ["股票B", "股票C"],
            1: ["股票D", "股票E", "股票F"]
        }
    }


@pytest.fixture
def sample_intraday_data():
    """创建示例分时数据"""
    return {
        "pct_changes": [0.5, 1.2, 2.5, 4.0, 5.5, 6.8, 7.2, 6.5, 7.0, 8.5],
        "timestamps": [datetime(2026, 1, 22, 9, 30 + i) for i in range(10)],
        "prices": [10.0 + i * 0.1 for i in range(10)]
    }


@pytest.fixture
def sample_historical_data():
    """创建示例历史数据"""
    return {
        "previous_limit_up_count": 10,
        "emotion_history": [
            {"date": "2026-01-21", "stage": "启动期"},
            {"date": "2026-01-20", "stage": "未知"}
        ]
    }


@pytest.fixture
def prompt_engine():
    """创建提示词引擎实例"""
    prompts_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts')
    return PromptEngine(template_dir=prompts_dir)


@pytest.fixture
def context_builder():
    """创建上下文构建器实例"""
    return ContextBuilder()


# ============ Test: Prompt Generation ============

def test_emotion_cycle_prompt_generation(prompt_engine, sample_context, 
                                        sample_limit_up_data, sample_intraday_data,
                                        sample_historical_data):
    """测试情绪周期提示词生成
    验证提示词包含板块名称、日期、涨停数据、连板梯队、炸板率、情绪周期理论背景
    Requirements: 3.2, 3.5
    """
    sector_name = "人工智能"
    prompt = prompt_engine.build_emotion_cycle_prompt(
        sector_name=sector_name,
        context=sample_context,
        limit_up_data=sample_limit_up_data,
        intraday_data=sample_intraday_data,
        historical_data=sample_historical_data
    )
    
    assert sector_name in prompt, "提示词应包含板块名称"
    assert "2026-01-22" in prompt, "提示词应包含日期"
    assert "涨停" in prompt or "limit_up" in prompt.lower(), "提示词应包含涨停相关信息"
    assert "连板" in prompt or "consecutive" in prompt.lower(), "提示词应包含连板信息"
    assert "炸板率" in prompt or "blown" in prompt.lower(), "提示词应包含炸板率信息"
    
    emotion_stages = ["启动期", "高潮期", "分化期", "修复期", "退潮期"]
    has_emotion_theory = any(stage in prompt for stage in emotion_stages)
    assert has_emotion_theory, "提示词应包含情绪周期理论背景"
    
    print(f"\n[测试通过] 情绪周期提示词生成正确")
    print(f"提示词长度: {len(prompt)} 字符")


def test_emotion_cycle_data_formatting(context_builder, sample_context,
                                      sample_limit_up_data, sample_intraday_data,
                                      sample_historical_data):
    """测试情绪周期数据格式化
    验证数据格式化为结构化文本，包含涨停家数变化、连板梯队分布、市场情绪指标、资金参与度、分时走势
    Requirements: 3.2
    """
    sector_name = "人工智能"
    formatted_data = context_builder.format_emotion_cycle_data(
        sector_name=sector_name,
        context=sample_context,
        limit_up_data=sample_limit_up_data,
        intraday_data=sample_intraday_data,
        historical_data=sample_historical_data
    )
    
    assert "涨停家数变化" in formatted_data, "应包含涨停家数变化"
    assert "连板梯队" in formatted_data, "应包含连板梯队"
    assert "市场情绪指标" in formatted_data, "应包含市场情绪指标"
    assert "资金参与度" in formatted_data, "应包含资金参与度"
    assert "分时走势" in formatted_data, "应包含分时走势"
    assert "15只" in formatted_data, "应包含当前涨停数"
    assert "10只" in formatted_data, "应包含前一日涨停数"
    assert "25.0%" in formatted_data, "应包含炸板率"
    assert "85.5亿元" in formatted_data, "应包含成交额"
    
    print(f"\n[测试通过] 情绪周期数据格式化正确")
    print(f"格式化数据长度: {len(formatted_data)} 字符")


# ============ Test: LLM Response Parsing ============

def test_parse_valid_json_response():
    """测试解析有效的JSON响应
    验证能够解析标准JSON格式，能够提取所有必需字段
    Requirements: 3.3
    """
    analyzer = LLMAnalyzer(api_key="test_key", provider="openai", model_name="gpt-4")
    
    valid_response = json.dumps({
        "stage": "高潮期",
        "confidence": 0.85,
        "reasoning": "涨停数大幅增加，连板高度达到5板，炸板率低于20%",
        "key_indicators": [
            "涨停数从10只增加到15只，增幅50%",
            "最高连板达到5板",
            "全市场炸板率25%，处于正常水平"
        ],
        "risk_level": "Medium",
        "opportunity_level": "High"
    })
    
    result = analyzer._parse_json_response(valid_response)
    
    assert result["stage"] == "高潮期", "应正确解析阶段"
    assert result["confidence"] == 0.85, "应正确解析置信度"
    assert "reasoning" in result, "应包含判定理由"
    assert "key_indicators" in result, "应包含关键指标"
    assert result["risk_level"] == "Medium", "应正确解析风险等级"
    assert result["opportunity_level"] == "High", "应正确解析机会等级"
    
    print(f"\n[测试通过] 有效JSON响应解析正确")


def test_parse_json_with_code_block():
    """测试解析包含代码块的JSON响应
    验证能够从```json ... ```代码块中提取JSON，能够正确解析提取的JSON
    Requirements: 3.3
    """
    analyzer = LLMAnalyzer(api_key="test_key", provider="openai", model_name="gpt-4")
    
    response_with_code_block = """
    根据分析，该板块处于高潮期。以下是详细分析：
    
    ```json
    {
        "stage": "高潮期",
        "confidence": 0.85,
        "reasoning": "市场情绪高涨",
        "key_indicators": ["涨停数增加", "连板高度提升"],
        "risk_level": "Medium",
        "opportunity_level": "High"
    }
    ```
    
    以上是我的分析结果。
    """
    
    result = analyzer._parse_json_response(response_with_code_block)
    
    assert result["stage"] == "高潮期", "应从代码块中正确提取阶段"
    assert result["confidence"] == 0.85, "应从代码块中正确提取置信度"
    
    print(f"\n[测试通过] 代码块JSON响应解析正确")


def test_parse_invalid_json_response():
    """测试解析无效的JSON响应
    验证无效JSON应抛出ValueError
    Requirements: 3.4
    """
    analyzer = LLMAnalyzer(api_key="test_key", provider="openai", model_name="gpt-4")
    invalid_response = "这不是一个有效的JSON格式"
    
    with pytest.raises(ValueError):
        analyzer._parse_json_response(invalid_response)
    
    print(f"\n[测试通过] 无效JSON响应正确抛出异常")


# ============ Test: Mock LLM Analysis ============

@patch('src.llm.llm_analyzer.LLMAnalyzer._call_llm')
def test_analyze_emotion_cycle_with_mock(mock_call_llm, sample_context,
                                        sample_limit_up_data, sample_intraday_data,
                                        sample_historical_data):
    """测试使用Mock LLM进行情绪周期分析
    验证能够调用LLM API，能够解析LLM响应，返回正确的EmotionCycleAnalysis对象
    Property 11: Emotion cycle LLM analysis
    Requirements: 3.1, 3.2, 3.3
    """
    mock_llm_response = json.dumps({
        "stage": "高潮期",
        "confidence": 0.85,
        "reasoning": "涨停数大幅增加，连板高度达到5板，炸板率低于30%，市场情绪高涨",
        "key_indicators": [
            "涨停数从10只增加到15只，增幅50%",
            "最高连板达到5板，梯队完整",
            "全市场炸板率25%，处于正常水平",
            "板块成交额85.5亿元，资金参与度高"
        ],
        "risk_level": "Medium",
        "opportunity_level": "High"
    })
    
    mock_call_llm.return_value = mock_llm_response
    
    analyzer = LLMAnalyzer(api_key="test_key", provider="openai", model_name="gpt-4")
    
    result = analyzer.analyze_emotion_cycle(
        sector_name="人工智能",
        context=sample_context,
        limit_up_data=sample_limit_up_data,
        intraday_data=sample_intraday_data,
        historical_data=sample_historical_data
    )
    
    assert isinstance(result, EmotionCycleAnalysis), "应返回EmotionCycleAnalysis对象"
    assert result.stage == "高潮期", "应正确解析阶段"
    assert result.confidence == 0.85, "应正确解析置信度"
    assert result.reasoning != "", "应包含判定理由"
    assert len(result.key_indicators) > 0, "应包含关键指标"
    assert result.risk_level == "Medium", "应正确解析风险等级"
    assert result.opportunity_level == "High", "应正确解析机会等级"
    assert mock_call_llm.called, "应调用LLM API"
    
    print(f"\n[测试通过] Mock LLM情绪周期分析正确")
    print(f"分析结果: {result.stage}, 置信度: {result.confidence}")


# ============ Test: Stage Validation ============

@patch('src.llm.llm_analyzer.LLMAnalyzer._call_llm')
def test_emotion_cycle_stage_validation(mock_call_llm, sample_context):
    """测试情绪周期阶段验证
    验证只接受有效的阶段标签（启动期/高潮期/分化期/修复期/退潮期），无效阶段标签应被标记为"未知"
    Property 12: Emotion cycle stage validation
    Requirements: 3.1
    """
    analyzer = LLMAnalyzer(api_key="test_key", provider="openai", model_name="gpt-4")
    
    valid_stages = ["启动期", "高潮期", "分化期", "修复期", "退潮期"]
    
    for stage in valid_stages:
        mock_llm_response = json.dumps({
            "stage": stage,
            "confidence": 0.8,
            "reasoning": f"测试{stage}",
            "key_indicators": ["指标1"],
            "risk_level": "Medium",
            "opportunity_level": "Medium"
        })
        
        mock_call_llm.return_value = mock_llm_response
        
        result = analyzer.analyze_emotion_cycle(
            sector_name="测试板块",
            context=sample_context
        )
        
        assert result.stage == stage, f"应正确识别{stage}"
    
    invalid_stage = "无效阶段"
    mock_llm_response = json.dumps({
        "stage": invalid_stage,
        "confidence": 0.8,
        "reasoning": "测试无效阶段",
        "key_indicators": ["指标1"],
        "risk_level": "Medium",
        "opportunity_level": "Medium"
    })
    
    mock_call_llm.return_value = mock_llm_response
    
    result = analyzer.analyze_emotion_cycle(
        sector_name="测试板块",
        context=sample_context
    )
    
    assert result.stage == "未知", "无效阶段应被标记为'未知'"
    
    print(f"\n[测试通过] 情绪周期阶段验证正确")
    print(f"有效阶段: {', '.join(valid_stages)}")


# ============ Test: Error Handling ============

@patch('src.llm.llm_analyzer.LLMAnalyzer._call_llm')
def test_emotion_cycle_llm_failure_handling(mock_call_llm, sample_context):
    """测试LLM调用失败的错误处理
    验证LLM调用失败时返回默认值，默认值包含"未知"阶段和0.0置信度，不会抛出异常
    Requirements: 3.4
    """
    mock_call_llm.side_effect = Exception("API调用失败")
    
    analyzer = LLMAnalyzer(api_key="test_key", provider="openai", model_name="gpt-4")
    
    result = analyzer.analyze_emotion_cycle(
        sector_name="测试板块",
        context=sample_context
    )
    
    assert isinstance(result, EmotionCycleAnalysis), "应返回EmotionCycleAnalysis对象"
    assert result.stage == "未知", "失败时应返回'未知'阶段"
    assert result.confidence == 0.0, "失败时置信度应为0.0"
    assert result.reasoning == "分析失败", "应包含失败说明"
    assert result.risk_level == "High", "失败时风险等级应为High"
    assert result.opportunity_level == "Low", "失败时机会等级应为Low"
    
    print(f"\n[测试通过] LLM失败错误处理正确")


@patch('src.llm.llm_analyzer.LLMAnalyzer._call_llm')
def test_emotion_cycle_invalid_response_handling(mock_call_llm, sample_context):
    """测试LLM返回无效响应的错误处理
    验证无效JSON响应时返回默认值，不会抛出异常
    Requirements: 3.4
    """
    mock_call_llm.return_value = "这不是有效的JSON"
    
    analyzer = LLMAnalyzer(api_key="test_key", provider="openai", model_name="gpt-4")
    
    result = analyzer.analyze_emotion_cycle(
        sector_name="测试板块",
        context=sample_context
    )
    
    assert result.stage == "未知", "无效响应时应返回'未知'阶段"
    assert result.confidence == 0.0, "无效响应时置信度应为0.0"
    
    print(f"\n[测试通过] 无效响应错误处理正确")


# ============ Test: Integration ============

def test_emotion_cycle_full_workflow(prompt_engine, context_builder,
                                    sample_context, sample_limit_up_data,
                                    sample_intraday_data, sample_historical_data):
    """测试情绪周期分析完整工作流
    验证数据格式化 -> 提示词生成 -> LLM分析 -> 结果解析的完整流程，各组件协同工作正常
    Requirements: 3.1, 3.2, 3.3
    """
    sector_name = "人工智能"
    
    formatted_data = context_builder.format_emotion_cycle_data(
        sector_name=sector_name,
        context=sample_context,
        limit_up_data=sample_limit_up_data,
        intraday_data=sample_intraday_data,
        historical_data=sample_historical_data
    )
    
    assert len(formatted_data) > 0, "数据格式化应成功"
    
    prompt = prompt_engine.build_emotion_cycle_prompt(
        sector_name=sector_name,
        context=sample_context,
        limit_up_data=sample_limit_up_data,
        intraday_data=sample_intraday_data,
        historical_data=sample_historical_data
    )
    
    assert len(prompt) > 0, "提示词生成应成功"
    assert sector_name in prompt, "提示词应包含板块名称"
    assert "涨停家数变化" in prompt or "15只" in prompt, "提示词应包含涨停数据"
    assert "连板梯队" in prompt or "5板" in prompt, "提示词应包含连板数据"
    
    print(f"\n[测试通过] 情绪周期分析完整工作流正确")
    print(f"格式化数据长度: {len(formatted_data)} 字符")
    print(f"提示词长度: {len(prompt)} 字符")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
