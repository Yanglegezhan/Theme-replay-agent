# -*- coding: utf-8 -*-
"""
LLM分析引擎

负责调用大模型进行深度分析
"""

import json
import logging
import time
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..models.data_models import (
    AnalysisContext,
    MarketIntentAnalysis,
    EmotionCycleAnalysis,
    SustainabilityEvaluation,
    TradingAdvice
)
from .prompt_engine import PromptEngine
from .context_builder import ContextBuilder


logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """LLM分析引擎，负责调用大模型进行深度分析"""
    
    # 支持的LLM提供商
    SUPPORTED_PROVIDERS = {
        'openai': 'https://api.openai.com/v1/chat/completions',
        'zhipu': 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
        'qwen': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
        'deepseek': 'https://api.deepseek.com/v1/chat/completions',
        'minimax': 'https://api.minimaxi.com/v1/chat/completions'  # 修正为 .com
    }
    
    def __init__(
        self,
        api_key: str,
        provider: str = "openai",
        model_name: str = "gpt-4",
        prompt_engine: Optional[PromptEngine] = None,
        context_builder: Optional[ContextBuilder] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        request_delay: float = 2.0  # 新增：请求之间的延迟（秒）
    ):
        """初始化LLM分析器
        
        Args:
            api_key: LLM API密钥
            provider: LLM提供商（openai/zhipu/qwen/deepseek）
            model_name: 模型名称
            prompt_engine: 提示词引擎（可选）
            context_builder: 上下文构建器（可选）
            temperature: 温度参数
            max_tokens: 最大token数（None表示不限制）
            timeout: 超时时间（秒，None表示不限制）
            request_delay: 请求之间的延迟（秒，防止达到速率限制）
        """
        self.api_key = api_key
        self.provider = provider.lower()
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.request_delay = request_delay  # 新增：保存延迟设置
        self._last_request_time = 0  # 新增：记录上次请求时间
        
        # 验证提供商
        if self.provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported: {list(self.SUPPORTED_PROVIDERS.keys())}"
            )
        
        self.api_url = self.SUPPORTED_PROVIDERS[self.provider]
        
        print(f"[DEBUG] LLM初始化: provider={self.provider}, api_url={self.api_url}")
        
        # 初始化提示词引擎和上下文构建器
        self.prompt_engine = prompt_engine or PromptEngine()
        self.context_builder = context_builder or ContextBuilder()
        
        # 配置HTTP会话（不重试）
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """创建HTTP会话（不重试，MiniMax禁用SSL验证）

        Returns:
            配置好的Session对象
        """
        session = requests.Session()

        # MiniMax 需要禁用 SSL 验证
        if self.provider == 'minimax':
            session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # 不配置重试策略，直接返回
        return session
    
    def analyze_market_intent(self, context: AnalysisContext) -> MarketIntentAnalysis:
        """分析市场资金意图
        
        Args:
            context: 分析上下文（包含所有数据）
            
        Returns:
            资金意图分析结果：
            - main_capital_flow: 主力资金流向
            - sector_rotation: 板块轮动分析
            - market_sentiment: 市场情绪判断
            - key_drivers: 关键驱动因素
        """
        try:
            # 构建提示词
            prompt = self.prompt_engine.build_market_intent_prompt(context)
            
            # 调用LLM
            response_text = self._call_llm(prompt)
            
            # 解析响应
            result = self._parse_json_response(response_text)
            
            # 构建分析结果
            return MarketIntentAnalysis(
                main_capital_flow=result.get('main_capital_flow', ''),
                sector_rotation=result.get('sector_rotation', ''),
                market_sentiment=result.get('market_sentiment', ''),
                key_drivers=result.get('key_drivers', []),
                confidence=float(result.get('confidence', 0.5))
            )
        
        except Exception as e:
            logger.error(f"Market intent analysis failed: {e}")
            # 返回默认值
            return MarketIntentAnalysis(
                main_capital_flow="分析失败",
                sector_rotation="分析失败",
                market_sentiment="未知",
                key_drivers=[],
                confidence=0.0
            )
    
    def analyze_emotion_cycle(
        self,
        sector_name: str,
        context: AnalysisContext,
        limit_up_data: Optional[Dict[str, Any]] = None,
        intraday_data: Optional[Dict[str, Any]] = None,
        historical_data: Optional[Dict[str, Any]] = None
    ) -> EmotionCycleAnalysis:
        """分析板块情绪周期
        
        Args:
            sector_name: 板块名称
            context: 分析上下文（包含涨停数据、连板梯队、炸板率、分时走势等）
            limit_up_data: 涨停数据（可选，包含全市场炸板率、昨日涨停今日表现等）
            intraday_data: 分时数据（可选，用于分析分时走势特征）
            historical_data: 历史数据（可选，包含历史情绪周期信息）
            
        Returns:
            情绪周期分析结果：
            - stage: 周期阶段（启动期/高潮期/分化期/修复期/退潮期）
            - confidence: 判定置信度（0-1）
            - reasoning: 判定理由
            - key_indicators: 关键指标说明
            - risk_level: 风险等级（Low/Medium/High）
            - opportunity_level: 机会等级（Low/Medium/High）
        """
        try:
            # 构建提示词（传递额外的数据参数）
            prompt = self.prompt_engine.build_emotion_cycle_prompt(
                sector_name=sector_name,
                context=context,
                limit_up_data=limit_up_data,
                intraday_data=intraday_data,
                historical_data=historical_data
            )
            
            # 调用LLM
            response_text = self._call_llm(prompt)
            
            # 解析响应
            result = self._parse_json_response(response_text)

            # 验证阶段标签（支持中英文字段名）
            valid_stages = ['启动期', '高潮期', '分化期', '修复期', '退潮期']
            stage = result.get('stage') or result.get('周期阶段') or '未知'
            if stage not in valid_stages:
                logger.warning(f"Invalid emotion cycle stage: {stage}")
                stage = '未知'

            # 置信度（支持中英文字段名）
            confidence = result.get('confidence') or result.get('判定置信度') or 0.5

            # 判定理由（支持中英文字段名）
            reasoning = result.get('reasoning') or result.get('判定理由') or ''

            # 关键指标（支持中英文字段名）
            key_indicators = result.get('key_indicators') or result.get('关键指标') or []

            # 风险等级和机会等级（支持中英文字段名）
            risk_level = result.get('risk_level') or result.get('风险等级') or 'Medium'
            opportunity_level = result.get('opportunity_level') or result.get('机会等级') or 'Medium'

            # 标准化风险等级和机会等级（处理中文输入）
            risk_level_map = {
                '高': 'High', '高风险': 'High', 'high': 'High',
                '中': 'Medium', '中等风险': 'Medium', 'medium': 'Medium',
                '低': 'Low', '低风险': 'Low', 'low': 'Low'
            }
            opportunity_level_map = {
                '高': 'High', '高机会': 'High', 'high': 'High',
                '中': 'Medium', '中等机会': 'Medium', 'medium': 'Medium',
                '低': 'Low', '低机会': 'Low', 'low': 'Low'
            }
            risk_level = risk_level_map.get(str(risk_level).lower(), risk_level)
            opportunity_level = opportunity_level_map.get(str(opportunity_level).lower(), opportunity_level)

            # 构建分析结果
            return EmotionCycleAnalysis(
                stage=stage,
                confidence=float(confidence),
                reasoning=reasoning,
                key_indicators=key_indicators if isinstance(key_indicators, list) else [key_indicators],
                risk_level=risk_level,
                opportunity_level=opportunity_level
            )
        
        except Exception as e:
            logger.error(f"Emotion cycle analysis failed for {sector_name}: {e}")
            # 返回默认值
            return EmotionCycleAnalysis(
                stage='未知',
                confidence=0.0,
                reasoning='分析失败',
                key_indicators=[],
                risk_level='High',
                opportunity_level='Low'
            )
    
    def evaluate_sustainability(
        self,
        sector_name: str,
        context: AnalysisContext,
        emotion_cycle: Optional[Any] = None,
        capacity_profile: Optional[Any] = None
    ) -> SustainabilityEvaluation:
        """评估题材持续性
        
        Args:
            sector_name: 板块名称
            context: 分析上下文
            
        Returns:
            持续性评估：
            - sustainability_score: 持续性评分（0-100）
            - time_horizon: 预期持续时间
            - risk_factors: 风险因素
            - support_factors: 支撑因素
        """
        try:
            # 构建提示词
            prompt = self.prompt_engine.build_sustainability_prompt(
                sector_name,
                context,
                emotion_cycle,
                capacity_profile
            )
            
            # 调用LLM
            response_text = self._call_llm(prompt)
            
            # 解析响应
            result = self._parse_json_response(response_text)

            # 构建评估结果（支持中英文字段名）
            # 持续性评分：优先使用中文字段名，其次英文字段名，默认50
            sustainability_score = result.get('持续性评分')
            if sustainability_score is None:
                sustainability_score = result.get('sustainability_score', 50)

            # 预期持续时间：优先使用中文字段名
            time_horizon = result.get('预期持续时间')
            if time_horizon is None:
                time_horizon = result.get('time_horizon', '未知')

            # 风险因素和支撑因素
            risk_factors = result.get('风险因素') or result.get('risk_factors') or []
            support_factors = result.get('支撑因素') or result.get('support_factors') or []

            # 评估理由
            reasoning = result.get('评估理由') or result.get('reasoning', '')

            return SustainabilityEvaluation(
                sustainability_score=float(sustainability_score),
                time_horizon=time_horizon,
                risk_factors=risk_factors if isinstance(risk_factors, list) else [risk_factors],
                support_factors=support_factors if isinstance(support_factors, list) else [support_factors],
                reasoning=reasoning
            )
        
        except Exception as e:
            logger.error(f"Sustainability evaluation failed for {sector_name}: {e}")
            # 返回默认值
            return SustainabilityEvaluation(
                sustainability_score=50.0,
                time_horizon='未知',
                risk_factors=['分析失败'],
                support_factors=[],
                reasoning='分析失败'
            )
    
    def generate_trading_advice(
        self,
        sector_name: str,
        context: AnalysisContext
    ) -> TradingAdvice:
        """生成操作建议
        
        Args:
            sector_name: 板块名称
            context: 分析上下文
            
        Returns:
            操作建议：
            - action: 操作方向（观望/低吸/追涨/减仓）
            - entry_timing: 入场时机
            - exit_strategy: 出场策略
            - position_sizing: 仓位建议
            - risk_warning: 风险提示
        """
        try:
            # 构建提示词
            prompt = self.prompt_engine.build_trading_advice_prompt(sector_name, context)
            
            # 调用LLM
            response_text = self._call_llm(prompt)
            
            # 解析响应
            result = self._parse_json_response(response_text)
            
            # 构建操作建议
            return TradingAdvice(
                action=result.get('action', '观望'),
                entry_timing=result.get('entry_timing', ''),
                exit_strategy=result.get('exit_strategy', ''),
                position_sizing=result.get('position_sizing', '轻仓'),
                risk_warning=result.get('risk_warning', ''),
                reasoning=result.get('reasoning', '')
            )
        
        except Exception as e:
            logger.error(f"Trading advice generation failed for {sector_name}: {e}")
            # 返回默认值
            return TradingAdvice(
                action='观望',
                entry_timing='分析失败',
                exit_strategy='分析失败',
                position_sizing='空仓',
                risk_warning='分析失败，建议观望',
                reasoning='分析失败'
            )
    
    def _call_llm(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """调用LLM API
        
        Args:
            prompt: 提示词
            temperature: 温度参数（可选，使用默认值）
            max_tokens: 最大token数（可选，使用默认值）
            
        Returns:
            LLM响应文本
            
        Raises:
            Exception: API调用失败
        """
        # 添加请求延迟，防止达到速率限制
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        
        if time_since_last_request < self.request_delay:
            sleep_time = self.request_delay - time_since_last_request
            logger.info(f"等待 {sleep_time:.1f} 秒以避免速率限制...")
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
        
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        # 根据提供商构建请求
        if self.provider in ['openai', 'zhipu', 'deepseek', 'minimax']:
            return self._call_openai_compatible(prompt, temp, max_tok)
        elif self.provider == 'qwen':
            return self._call_qwen(prompt, temp, max_tok)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _call_openai_compatible(
        self,
        prompt: str,
        temperature: float,
        max_tokens: Optional[int]
    ) -> str:
        """调用OpenAI兼容的API
        
        Args:
            prompt: 提示词
            temperature: 温度参数
            max_tokens: 最大token数（None表示不限制）
            
        Returns:
            LLM响应文本
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        payload = {
            'model': self.model_name,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': temperature
        }
        
        # 只在max_tokens不为None时才添加
        if max_tokens is not None:
            payload['max_tokens'] = max_tokens
        
        print(f"[DEBUG] 调用API: {self.api_url}")
        print(f"[DEBUG] 模型: {self.model_name}")
        print(f"[DEBUG] 超时设置: {self.timeout}")
        
        try:
            # 如果timeout为None，则不设置超时
            # 对于MiniMax，禁用SSL验证
            verify_ssl = self.provider != 'minimax'

            response = self.session.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout if self.timeout is not None else None,
                verify=verify_ssl
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 提取响应内容
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"\n[LLM原始输出]\n{content}\n")
                return content
            else:
                raise ValueError("Invalid API response format")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API call failed: {e}")
            raise
    
    def _call_qwen(
        self,
        prompt: str,
        temperature: float,
        max_tokens: Optional[int]
    ) -> str:
        """调用通义千问API
        
        Args:
            prompt: 提示词
            temperature: 温度参数
            max_tokens: 最大token数（None表示不限制）
            
        Returns:
            LLM响应文本
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        parameters = {
            'temperature': temperature
        }
        
        # 只在max_tokens不为None时才添加
        if max_tokens is not None:
            parameters['max_tokens'] = max_tokens
        
        payload = {
            'model': self.model_name,
            'input': {
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            },
            'parameters': parameters
        }
        
        try:
            response = self.session.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout if self.timeout is not None else None
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 提取响应内容
            if 'output' in result and 'text' in result['output']:
                return result['output']['text']
            else:
                raise ValueError("Invalid API response format")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API call failed: {e}")
            raise
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """解析LLM返回的JSON响应
        
        Args:
            response_text: LLM响应文本
            
        Returns:
            解析后的字典
            
        Raises:
            ValueError: JSON解析失败
        """
        try:
            # 尝试直接解析
            return json.loads(response_text)
        except json.JSONDecodeError:
            # 尝试提取JSON代码块
            if '```json' in response_text:
                # 提取```json ... ```之间的内容
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                json_str = response_text[start:end].strip()
                return json.loads(json_str)
            elif '```' in response_text:
                # 提取``` ... ```之间的内容
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                json_str = response_text[start:end].strip()
                return json.loads(json_str)
            else:
                # 尝试查找第一个{和最后一个}
                start = response_text.find('{')
                end = response_text.rfind('}')
                if start != -1 and end != -1:
                    json_str = response_text[start:end+1]
                    return json.loads(json_str)
                else:
                    raise ValueError("No valid JSON found in response")
