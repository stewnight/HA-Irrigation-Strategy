"""Modern LLM Configuration and Integration for Crop Steering System.

Implements current LLM features with cost optimization and intelligent 
model selection for Claude and OpenAI models.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Any, Tuple

_LOGGER = logging.getLogger(__name__)


class LLMModel(Enum):
    """Current LLM model variants with 2024 pricing."""

    # OpenAI Models
    GPT4O_MINI = "gpt-4o-mini"  # $0.15/1M input, $0.60/1M output - Best value
    GPT4O = "gpt-4o"  # $5.00/1M input, $15.00/1M output - High quality
    GPT4_TURBO = "gpt-4-turbo"  # $10.00/1M input, $30.00/1M output - Premium
    
    # Claude Models  
    CLAUDE_HAIKU = "claude-3-haiku-20240307"  # $0.25/1M input, $1.25/1M output - Fastest
    CLAUDE_SONNET = "claude-3-5-sonnet-20241022"  # $3.00/1M input, $15.00/1M output - Balanced


class ReasoningEffort(Enum):
    """GPT-5 reasoning effort levels."""

    MINIMAL = "minimal"  # Fast, basic logic
    LOW = "low"  # Standard analysis
    MEDIUM = "medium"  # Deeper thinking
    HIGH = "high"  # Maximum intelligence


class Verbosity(Enum):
    """GPT-5 verbosity control."""

    LOW = "low"  # Concise responses
    MEDIUM = "medium"  # Include explanations
    HIGH = "high"  # Detailed analysis


@dataclass
class LLMConfig:
    """Modern LLM configuration."""

    # Model selection - Use real models with good value
    default_model: LLMModel = LLMModel.GPT4O_MINI  # Best cost/performance
    enhanced_model: LLMModel = LLMModel.CLAUDE_HAIKU  # Fast and capable
    emergency_model: LLMModel = LLMModel.GPT4O  # High quality when needed

    # Reasoning configuration
    default_reasoning: ReasoningEffort = ReasoningEffort.MINIMAL
    enhanced_reasoning: ReasoningEffort = ReasoningEffort.MEDIUM
    emergency_reasoning: ReasoningEffort = ReasoningEffort.HIGH

    # Verbosity configuration
    default_verbosity: Verbosity = Verbosity.LOW
    enhanced_verbosity: Verbosity = Verbosity.MEDIUM
    emergency_verbosity: Verbosity = Verbosity.HIGH

    # Context window management
    max_input_tokens: int = 8000  # Well under 272K limit
    max_output_tokens: int = 2000  # Well under 128K limit

    # Temperature settings
    default_temperature: float = 0.1  # Consistent decisions
    enhanced_temperature: float = 0.3  # Some creativity
    emergency_temperature: float = 0.5  # More exploration

    # Caching configuration (90% discount!)
    enable_caching: bool = True
    cache_ttl_minutes: int = 1440  # 24 hours
    similarity_threshold: float = 0.95

    # Custom tools (GPT-5 feature)
    enable_plaintext_tools: bool = True
    tool_grammar: Optional[str] = None


class LLMCostCalculator:
    """Calculate costs for current LLM models."""

    # December 2024 Pricing (per million tokens)
    PRICING = {
        LLMModel.GPT4O_MINI: {"input": 0.15, "output": 0.60},
        LLMModel.GPT4O: {"input": 5.00, "output": 15.00},
        LLMModel.GPT4_TURBO: {"input": 10.00, "output": 30.00},
        LLMModel.CLAUDE_HAIKU: {"input": 0.25, "output": 1.25},
        LLMModel.CLAUDE_SONNET: {"input": 3.00, "output": 15.00},
    }

    @classmethod
    def calculate_cost(
        cls,
        model: LLMModel,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
    ) -> float:
        """Calculate cost for a GPT-5 API call.

        Args:
            model: GPT-5 model variant
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cached_tokens: Number of cached input tokens

        Returns:
            Total cost in USD
        """
        pricing = cls.PRICING[model]

        # Calculate input cost with caching discount
        uncached_tokens = input_tokens - cached_tokens
        input_cost = uncached_tokens * pricing["input"] / 1_000_000

        # Add cached token cost (90% discount)
        if cached_tokens > 0:
            cached_cost = cached_tokens * pricing["input"] * 0.1 / 1_000_000
            input_cost += cached_cost

        # Calculate output cost
        output_cost = output_tokens * pricing["output"] / 1_000_000

        return input_cost + output_cost

    @classmethod
    def estimate_daily_cost(
        cls,
        model: LLMModel,
        calls_per_day: int,
        avg_input_tokens: int = 1000,
        avg_output_tokens: int = 200,
        cache_hit_rate: float = 0.5,
    ) -> float:
        """Estimate daily cost for GPT-5 usage.

        Args:
            model: GPT-5 model variant
            calls_per_day: Number of API calls per day
            avg_input_tokens: Average input tokens per call
            avg_output_tokens: Average output tokens per call
            cache_hit_rate: Percentage of calls hitting cache

        Returns:
            Estimated daily cost in USD
        """
        cached_calls = int(calls_per_day * cache_hit_rate)
        uncached_calls = calls_per_day - cached_calls

        # Calculate uncached cost
        uncached_cost = uncached_calls * cls.calculate_cost(
            model, avg_input_tokens, avg_output_tokens, 0
        )

        # Calculate cached cost (90% discount on input)
        cached_cost = cached_calls * cls.calculate_cost(
            model, avg_input_tokens, avg_output_tokens, avg_input_tokens
        )

        return uncached_cost + cached_cost


class LLMDecisionRouter:
    """Route decisions to appropriate LLM models based on urgency."""

    def __init__(self, config: LLMConfig):
        """Initialize the decision router.

        Args:
            config: LLM configuration
        """
        self.config = config

    def select_model(
        self,
        urgency: str = "normal",
        vwc: float = None,
        ec: float = None,
        confidence_required: float = 0.7,
    ) -> Tuple[LLMModel, ReasoningEffort, Verbosity]:
        """Select appropriate model based on conditions.

        Args:
            urgency: Decision urgency level
            vwc: Current VWC percentage
            ec: Current EC value
            confidence_required: Required confidence level

        Returns:
            Tuple of (model, reasoning_effort, verbosity)
        """
        # Emergency conditions - use best model
        if self._is_emergency(vwc, ec):
            return (
                self.config.emergency_model,
                self.config.emergency_reasoning,
                self.config.emergency_verbosity,
            )

        # Enhanced conditions - use mid-tier model
        if urgency in ["high", "complex"] or confidence_required > 0.8:
            return (
                self.config.enhanced_model,
                self.config.enhanced_reasoning,
                self.config.enhanced_verbosity,
            )

        # Default conditions - use nano model
        return (
            self.config.default_model,
            self.config.default_reasoning,
            self.config.default_verbosity,
        )

    def _is_emergency(self, vwc: float = None, ec: float = None) -> bool:
        """Check if conditions warrant emergency response.

        Args:
            vwc: Current VWC percentage
            ec: Current EC value

        Returns:
            True if emergency conditions detected
        """
        if vwc is not None:
            if vwc < 35 or vwc > 85:  # Critical moisture levels
                return True

        if ec is not None:
            if ec > 6.0:  # Dangerous salt levels
                return True

        return False


def create_llm_prompt(
    context: Dict[str, Any],
    model: LLMModel,
    reasoning: ReasoningEffort,
    verbosity: Verbosity,
) -> str:
    """Create optimized prompt for current LLM models.

    Args:
        context: Irrigation context data
        model: LLM model being used
        reasoning: Reasoning effort level
        verbosity: Response verbosity level

    Returns:
        Formatted prompt string
    """
    # Adjust prompt based on model capabilities
    if model == LLMModel.GPT4O_MINI:
        # Simple, direct prompt for mini model
        prompt = f"""
Irrigation Decision (Quick Analysis):
VWC: {context.get('vwc', 0)}%
EC: {context.get('ec', 0)} mS/cm
Phase: {context.get('phase', 'Unknown')}

Should irrigate? Reply: YES/NO, duration (seconds), confidence (0-1)
"""

    elif model in [LLMModel.CLAUDE_HAIKU, LLMModel.GPT4O]:
        # More detailed prompt for mid-tier models
        prompt = f"""
Crop Steering Irrigation Analysis:

Current Conditions:
- VWC: {context.get('vwc', 0)}% (target: {context.get('vwc_target', 60)}%)
- EC: {context.get('ec', 0)} mS/cm (target: {context.get('ec_target', 2.0)})
- Phase: {context.get('phase', 'Unknown')}
- Growth Stage: {context.get('growth_stage', 'Unknown')}

Recent Trends:
- VWC trend: {context.get('vwc_trend', 'stable')}
- Last irrigation: {context.get('last_irrigation', 'Unknown')}

Provide irrigation decision with reasoning.
Format: Decision (YES/NO), Duration (seconds), Reasoning (1-2 sentences), Confidence (0-1)
"""

    else:  # Premium models (GPT4_TURBO, CLAUDE_SONNET)
        # Comprehensive prompt for premium models
        prompt = f"""
Expert Crop Steering Irrigation Analysis

Complete Context:
{json.dumps(context, indent=2)}

Analyze all factors and provide:
1. Irrigation decision (YES/NO)
2. Optimal duration (seconds)
3. Scientific reasoning (2-3 sentences)
4. Risk assessment
5. Confidence level (0-1)
6. Alternative recommendations

Consider plant physiology, environmental conditions, and optimization goals.
"""

    # Add reasoning and verbosity hints
    prompt += f"\n[Reasoning: {reasoning.value}, Verbosity: {verbosity.value}]"

    return prompt


# Example usage configuration
DEFAULT_LLM_CONFIG = LLMConfig(
    default_model=LLMModel.GPT4O_MINI,  # Best value for routine decisions
    enhanced_model=LLMModel.CLAUDE_HAIKU,  # Fast and capable
    emergency_model=LLMModel.GPT4O,  # High quality when needed
    max_input_tokens=8000,
    enable_caching=True,
    cache_ttl_minutes=1440,  # 24 hours
)
