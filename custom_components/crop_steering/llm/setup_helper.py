"""LLM Setup Helper for Crop Steering System.

Provides user-friendly setup validation, API key testing, and configuration assistance
to make LLM integration more accessible to end users.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Any

from homeassistant.core import HomeAssistant

from .client import LLMProvider, LLMConfig, LLMClientFactory

_LOGGER = logging.getLogger(__name__)


@dataclass
class SetupResult:
    """Result of setup validation."""
    
    success: bool
    message: str
    details: Dict[str, Any]
    recommendations: List[str]


class LLMSetupHelper:
    """Helper class for LLM setup and validation."""
    
    def __init__(self, hass: HomeAssistant):
        """Initialize setup helper."""
        self._hass = hass
        
    async def validate_api_key(
        self, 
        provider: LLMProvider, 
        api_key: str, 
        model: str = None
    ) -> SetupResult:
        """Validate API key by making a test request."""
        try:
            # Set default models for testing
            test_models = {
                LLMProvider.OPENAI: model or "gpt-4o-mini",
                LLMProvider.CLAUDE: model or "claude-3-haiku-20240307",
            }
            
            test_model = test_models.get(provider)
            if not test_model:
                return SetupResult(
                    success=False,
                    message=f"Unsupported provider: {provider}",
                    details={},
                    recommendations=["Use 'openai' or 'claude' as provider"]
                )
            
            # Create test configuration
            config = LLMConfig(
                provider=provider,
                api_key=api_key,
                model=test_model,
                timeout=10,
                max_retries=1,
            )
            
            # Create client and test
            client = LLMClientFactory.create_client(self._hass, config)
            
            # Send a simple test message
            test_messages = [
                {"role": "user", "content": "Reply with just 'OK' if you can read this."}
            ]
            
            response = await client.complete(test_messages)
            
            # Validate response
            if response and response.content:
                return SetupResult(
                    success=True,
                    message=f"✅ API key valid! Model: {test_model}",
                    details={
                        "provider": provider.value,
                        "model": test_model,
                        "response_tokens": response.tokens_used,
                        "estimated_cost": response.cost_estimate,
                    },
                    recommendations=[
                        f"Your {provider.value} API key is working correctly",
                        f"Test cost: ${response.cost_estimate:.6f}",
                        "You can now enable LLM features"
                    ]
                )
            else:
                return SetupResult(
                    success=False,
                    message="❌ API key test failed - no response received",
                    details={"provider": provider.value, "model": test_model},
                    recommendations=[
                        "Check your API key is correct",
                        "Verify your account has credits/billing enabled",
                        f"Ensure {test_model} is available on your account"
                    ]
                )
                
        except Exception as e:
            error_msg = str(e)
            recommendations = ["Check your API key is correct"]
            
            # Provide specific help based on error
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                recommendations.extend([
                    "Your API key appears to be invalid",
                    "Double-check you copied the full key correctly",
                    "Make sure the key hasn't expired"
                ])
            elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
                recommendations.extend([
                    "Your account may have exceeded quota or billing issues",
                    "Check your account balance and billing settings",
                    "Consider using a cheaper model for testing"
                ])
            elif "timeout" in error_msg.lower():
                recommendations.extend([
                    "Request timed out - this might be temporary",
                    "Check your internet connection",
                    "Try again in a few minutes"
                ])
            else:
                recommendations.append(f"Technical error: {error_msg}")
            
            return SetupResult(
                success=False,
                message=f"❌ API key test failed: {error_msg}",
                details={"provider": provider.value, "error": error_msg},
                recommendations=recommendations
            )
    
    async def estimate_costs(
        self, 
        provider: LLMProvider, 
        model: str,
        calls_per_day: int = 100
    ) -> Dict[str, Any]:
        """Estimate daily/monthly costs for given usage."""
        try:
            # Create test config to get pricing info
            config = LLMConfig(
                provider=provider,
                api_key="test",  # Won't be used for estimation
                model=model,
            )
            
            client = LLMClientFactory.create_client(self._hass, config)
            
            # Estimate typical usage
            avg_input_tokens = 800  # Typical irrigation decision prompt
            avg_output_tokens = 150  # Typical response length
            
            # Calculate costs
            cost_per_call = client.estimate_cost(avg_input_tokens, avg_output_tokens)
            daily_cost = cost_per_call * calls_per_day
            monthly_cost = daily_cost * 30
            
            return {
                "model": model,
                "calls_per_day": calls_per_day,
                "cost_per_call": cost_per_call,
                "daily_cost": daily_cost,
                "monthly_cost": monthly_cost,
                "avg_input_tokens": avg_input_tokens,
                "avg_output_tokens": avg_output_tokens,
                "recommendations": self._get_cost_recommendations(daily_cost, monthly_cost)
            }
            
        except Exception as e:
            _LOGGER.error("Failed to estimate costs: %s", e)
            return {
                "error": str(e),
                "recommendations": ["Unable to estimate costs - check model name"]
            }
    
    def _get_cost_recommendations(self, daily_cost: float, monthly_cost: float) -> List[str]:
        """Get cost recommendations based on estimated usage."""
        recommendations = []
        
        if daily_cost < 0.50:
            recommendations.append("💚 Very economical - great for testing and learning")
        elif daily_cost < 2.00:
            recommendations.append("💛 Reasonable cost - good for regular home use")
        elif daily_cost < 5.00:
            recommendations.append("🧡 Moderate cost - consider budget limits")
        else:
            recommendations.append("🔴 High cost - set strict budget limits")
        
        if monthly_cost > 50:
            recommendations.append("⚠️  Monthly cost may exceed $50 - consider cheaper models")
        
        # Model-specific recommendations
        recommendations.append("💡 Use caching to reduce costs by 70-90%")
        recommendations.append("📊 Monitor usage with built-in cost tracking")
        
        return recommendations
    
    def get_recommended_models(self) -> Dict[str, Any]:
        """Get recommended models for different use cases."""
        return {
            "beginner": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "description": "Most cost-effective for learning ($0.15-0.60 per 1M tokens)",
                "daily_budget": 1.0,
                "best_for": "Testing, learning, low-volume usage"
            },
            "balanced": {
                "provider": "claude", 
                "model": "claude-3-haiku-20240307",
                "description": "Fast and capable for regular use ($0.25-1.25 per 1M tokens)",
                "daily_budget": 3.0,
                "best_for": "Daily automation, good balance of speed and intelligence"
            },
            "premium": {
                "provider": "openai",
                "model": "gpt-4o",
                "description": "High quality for important decisions ($5-15 per 1M tokens)",
                "daily_budget": 5.0,
                "best_for": "Critical decisions, complex analysis, research"
            }
        }
    
    def generate_config_template(
        self, 
        provider: LLMProvider, 
        model: str,
        daily_budget: float = 2.0
    ) -> str:
        """Generate a ready-to-use configuration template."""
        
        provider_key_hints = {
            LLMProvider.OPENAI: "# Get your API key from: https://platform.openai.com/api-keys",
            LLMProvider.CLAUDE: "# Get your API key from: https://console.anthropic.com/",
        }
        
        config = f"""# LLM Enhanced Crop Steering Configuration
# Generated by Setup Helper

llm_enhanced_crop_steering:
  module: crop_steering.llm.llm_enhanced_app
  class: LLMEnhancedCropSteering

  # Basic Configuration
  zones: [1, 2, 3]  # ADJUST: Your active zones
  enable_llm: true

  # LLM Provider Configuration
  llm_config:
    provider: "{provider.value}"
    model: "{model}"
    {provider_key_hints.get(provider, "# Add your API key here")}
    api_key: !secret {provider.value}_api_key
    timeout: 30
    max_retries: 3

  # Budget Control
  budget_config:
    daily_limit: {daily_budget:.1f}
    cost_tier: "standard"
    enable_alerts: true

  # Decision Thresholds
  llm_confidence_threshold: 70.0
  enable_llm_phase_transitions: true

  # Safety Limits
  safety_thresholds:
    min_confidence: 70.0
    max_vwc_critical: 80.0
    min_vwc_critical: 40.0
    emergency_response_time: 300

---
# Add this to your secrets.yaml:
# {provider.value}_api_key: "your-actual-api-key-here"
"""
        
        return config
    
    async def test_full_setup(self, config_dict: Dict[str, Any]) -> SetupResult:
        """Test a complete LLM configuration."""
        try:
            # Extract LLM config
            llm_config = config_dict.get("llm_config", {})
            provider_str = llm_config.get("provider", "")
            model = llm_config.get("model", "")
            api_key = llm_config.get("api_key", "")
            
            if not all([provider_str, model, api_key]):
                return SetupResult(
                    success=False,
                    message="❌ Incomplete configuration",
                    details={},
                    recommendations=[
                        "Ensure provider, model, and api_key are all specified",
                        "Check your secrets.yaml file for API key"
                    ]
                )
            
            # Validate provider
            try:
                provider = LLMProvider(provider_str)
            except ValueError:
                return SetupResult(
                    success=False,
                    message=f"❌ Invalid provider: {provider_str}",
                    details={},
                    recommendations=["Use 'openai' or 'claude' as provider"]
                )
            
            # Test API key
            api_result = await self.validate_api_key(provider, api_key, model)
            
            if api_result.success:
                # Estimate costs
                budget = config_dict.get("budget_config", {}).get("daily_limit", 5.0)
                cost_info = await self.estimate_costs(provider, model, calls_per_day=50)
                
                recommendations = [
                    "✅ Configuration looks good!",
                    "✅ API connection successful",
                    f"📊 Estimated daily cost: ${cost_info.get('daily_cost', 0):.3f}",
                    f"💰 Daily budget: ${budget:.2f}",
                ]
                
                if cost_info.get('daily_cost', 0) > budget:
                    recommendations.append("⚠️ Estimated cost may exceed budget - consider adjustment")
                
                return SetupResult(
                    success=True,
                    message="✅ LLM setup validation successful!",
                    details={
                        "provider": provider.value,
                        "model": model,
                        "budget": budget,
                        "cost_estimate": cost_info,
                    },
                    recommendations=recommendations
                )
            else:
                return api_result
                
        except Exception as e:
            return SetupResult(
                success=False,
                message=f"❌ Setup validation failed: {e}",
                details={"error": str(e)},
                recommendations=[
                    "Check your configuration file syntax",
                    "Verify all required fields are present",
                    "Review the generated template for reference"
                ]
            )