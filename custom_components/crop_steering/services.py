"""Crop Steering Services."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.util import dt as dt_util

from .const import DOMAIN, MIN_ZONES, MAX_ZONES

_LOGGER = logging.getLogger(__name__)

# Service schemas
PHASE_TRANSITION_SCHEMA = vol.Schema(
    {
        vol.Required("target_phase"): vol.In(["P0", "P1", "P2", "P3"]),
        vol.Optional("reason"): cv.string,
        vol.Optional("forced"): cv.boolean,
    }
)


def get_irrigation_shot_schema(hass: HomeAssistant) -> vol.Schema:
    """Get irrigation shot schema with dynamic zone validation."""
    # Get configured zones from the integration
    zones = []
    for entry_id in hass.data.get(DOMAIN, {}):
        config_data = hass.data[DOMAIN].get(entry_id, {})
        if "zones" in config_data:
            zones.extend(config_data["zones"].keys())

    # If no zones configured, use default range
    if not zones:
        zones = list(range(1, MAX_ZONES + 1))

    return vol.Schema(
        {
            vol.Required("zone"): vol.In(zones),
            vol.Required("duration_seconds"): vol.Range(min=1, max=3600),
            vol.Optional("shot_type"): vol.In(["P1", "P2", "P3_emergency", "manual"]),
        }
    )


MANUAL_OVERRIDE_SCHEMA = vol.Schema(
    {
        vol.Required("zone"): vol.Range(min=MIN_ZONES, max=MAX_ZONES),
        vol.Optional("timeout_minutes"): vol.Range(min=1, max=1440),  # Max 24 hours
        vol.Optional("enable"): cv.boolean,
    }
)

# LLM Service Schemas
LLM_API_KEY_TEST_SCHEMA = vol.Schema(
    {
        vol.Required("provider"): vol.In(["openai", "claude"]),
        vol.Required("api_key"): cv.string,
        vol.Optional("model"): cv.string,
    }
)

LLM_COST_ESTIMATE_SCHEMA = vol.Schema(
    {
        vol.Required("provider"): vol.In(["openai", "claude"]),
        vol.Required("model"): cv.string,
        vol.Optional("calls_per_day"): vol.Range(min=1, max=1000),
    }
)

LLM_CONFIG_GENERATE_SCHEMA = vol.Schema(
    {
        vol.Required("provider"): vol.In(["openai", "claude"]),
        vol.Required("model"): cv.string,
        vol.Optional("daily_budget"): vol.Range(min=0.1, max=100.0),
    }
)

SERVICES = {
    "transition_phase": {
        "schema": PHASE_TRANSITION_SCHEMA,
        "method": "async_transition_phase",
    },
    "execute_irrigation_shot": {
        "schema": None,  # Will be set dynamically
        "method": "async_execute_irrigation_shot",
        "dynamic_schema": True,
    },
    "check_transition_conditions": {
        "schema": vol.Schema({}),
        "method": "async_check_transition_conditions",
    },
    "set_manual_override": {
        "schema": MANUAL_OVERRIDE_SCHEMA,
        "method": "async_set_manual_override",
    },
    # LLM Services
    "test_llm_api_key": {
        "schema": LLM_API_KEY_TEST_SCHEMA,
        "method": "async_test_llm_api_key",
    },
    "estimate_llm_costs": {
        "schema": LLM_COST_ESTIMATE_SCHEMA,
        "method": "async_estimate_llm_costs",
    },
    "generate_llm_config": {
        "schema": LLM_CONFIG_GENERATE_SCHEMA,
        "method": "async_generate_llm_config",
    },
}


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for crop steering."""

    async def async_transition_phase(call: ServiceCall) -> None:
        """Service to transition between irrigation phases."""
        target_phase = call.data["target_phase"]
        reason = call.data.get("reason", "Manual transition")
        forced = call.data.get("forced", False)

        _LOGGER.info(f"Phase transition requested: {target_phase} - {reason}")

        # Update the phase select entity
        await hass.services.async_call(
            "select",
            "select_option",
            {
                "entity_id": "select.crop_steering_irrigation_phase",
                "option": target_phase,
            },
            blocking=True,
        )

        # Log the transition
        _LOGGER.info(f"Phase transitioned to {target_phase}: {reason}")

        # Fire event for automation/AppDaemon to handle
        hass.bus.async_fire(
            "crop_steering_phase_transition",
            {
                "target_phase": target_phase,
                "reason": reason,
                "forced": forced,
                "timestamp": dt_util.utcnow().isoformat(),
            },
        )

    async def async_execute_irrigation_shot(call: ServiceCall) -> None:
        """Service to execute an irrigation shot."""
        zone = call.data["zone"]
        duration = call.data["duration_seconds"]
        shot_type = call.data.get("shot_type", "manual")

        _LOGGER.info(
            f"Irrigation shot requested: Zone {zone}, {duration}s, type: {shot_type}"
        )

        # Fire event for hardware control (AppDaemon will handle the actual irrigation sequence)
        hass.bus.async_fire(
            "crop_steering_irrigation_shot",
            {
                "zone": zone,
                "duration_seconds": duration,
                "shot_type": shot_type,
                "timestamp": dt_util.utcnow().isoformat(),
            },
        )

        _LOGGER.info(f"Irrigation shot event fired for Zone {zone}")

    async def async_check_transition_conditions(call: ServiceCall) -> None:
        """Service to check if phase transition conditions are met."""
        try:
            # Get current state
            current_phase_state = hass.states.get(
                "select.crop_steering_irrigation_phase"
            )
            avg_vwc_state = hass.states.get("sensor.crop_steering_configured_avg_vwc")
            avg_ec_state = hass.states.get("sensor.crop_steering_configured_avg_ec")
            ec_ratio_state = hass.states.get("sensor.crop_steering_ec_ratio")

            if not all([current_phase_state, avg_vwc_state, avg_ec_state]):
                _LOGGER.warning(
                    "Cannot check transition conditions - missing sensor data"
                )
                return

            current_phase = current_phase_state.state
            avg_vwc = float(avg_vwc_state.state)
            avg_ec = float(avg_ec_state.state)
            ec_ratio = float(ec_ratio_state.state) if ec_ratio_state else 1.0

            # Get configuration values
            p1_target_vwc = float(
                hass.states.get("number.crop_steering_p1_target_vwc").state
            )
            float(hass.states.get("number.crop_steering_p2_vwc_threshold").state)
            ec_flush_target = float(
                hass.states.get("number.crop_steering_ec_target_flush").state
            )

            transition_reasons = []

            # Check P1 → P2 transition conditions
            if current_phase == "P1":
                if avg_vwc >= p1_target_vwc:
                    transition_reasons.append(
                        f"VWC target reached: {avg_vwc}% >= {p1_target_vwc}%"
                    )

                if avg_ec <= ec_flush_target and avg_vwc >= p1_target_vwc:
                    transition_reasons.append(
                        f"EC flush condition met: {avg_ec} <= {ec_flush_target} with VWC {avg_vwc}%"
                    )

            # Check P2 irrigation trigger
            elif current_phase == "P2":
                adjusted_threshold = hass.states.get(
                    "sensor.crop_steering_p2_vwc_threshold_adjusted"
                )
                if adjusted_threshold:
                    threshold = float(adjusted_threshold.state)
                    if avg_vwc <= threshold:
                        transition_reasons.append(
                            f"P2 irrigation needed: {avg_vwc}% <= {threshold}% (EC adjusted)"
                        )

            # Fire event with conditions
            hass.bus.async_fire(
                "crop_steering_transition_check",
                {
                    "current_phase": current_phase,
                    "avg_vwc": avg_vwc,
                    "avg_ec": avg_ec,
                    "ec_ratio": ec_ratio,
                    "transition_reasons": transition_reasons,
                    "conditions_met": len(transition_reasons) > 0,
                    "timestamp": dt_util.utcnow().isoformat(),
                },
            )

            _LOGGER.debug(
                f"Transition check: Phase {current_phase}, VWC {avg_vwc}%, EC {avg_ec}, Conditions: {len(transition_reasons)}"
            )

        except Exception as e:
            _LOGGER.error(f"Error checking transition conditions: {e}")

    async def async_set_manual_override(call: ServiceCall) -> None:
        """Service to set manual override for a zone with optional timeout."""
        zone = call.data["zone"]
        timeout_minutes = call.data.get("timeout_minutes", 60)  # Default 1 hour
        enable = call.data.get("enable", True)

        _LOGGER.info(
            f"Manual override requested: Zone {zone}, Enable: {enable}, Timeout: {timeout_minutes}min"
        )

        # Set the manual override switch
        override_entity = f"switch.crop_steering_zone_{zone}_manual_override"
        await hass.services.async_call(
            "switch",
            "turn_on" if enable else "turn_off",
            {"entity_id": override_entity},
            blocking=True,
        )

        # Fire event for AppDaemon to handle timeout logic
        if enable and timeout_minutes:
            hass.bus.async_fire(
                "crop_steering_manual_override",
                {
                    "zone": zone,
                    "action": "enable_with_timeout",
                    "timeout_minutes": timeout_minutes,
                    "timestamp": dt_util.utcnow().isoformat(),
                },
            )
        else:
            hass.bus.async_fire(
                "crop_steering_manual_override",
                {
                    "zone": zone,
                    "action": "disable" if not enable else "enable_permanent",
                    "timestamp": dt_util.utcnow().isoformat(),
                },
            )

    # LLM Testing Services
    async def async_test_llm_api_key(call: ServiceCall) -> None:
        """Service to test LLM API key configuration."""
        try:
            from .llm.setup_helper import LLMSetupHelper
            from .llm.client import LLMProvider
            
            provider_str = call.data["provider"]
            api_key = call.data["api_key"]
            model = call.data.get("model")
            
            # Validate provider
            try:
                provider = LLMProvider(provider_str)
            except ValueError:
                result = {
                    "success": False,
                    "message": f"Invalid provider: {provider_str}",
                    "recommendations": ["Use 'openai' or 'claude' as provider"]
                }
                hass.bus.async_fire("crop_steering_llm_test_result", result)
                return
            
            # Create setup helper and test
            setup_helper = LLMSetupHelper(hass)
            result = await setup_helper.validate_api_key(provider, api_key, model)
            
            # Fire event with results
            event_data = {
                "success": result.success,
                "message": result.message,
                "details": result.details,
                "recommendations": result.recommendations,
                "timestamp": dt_util.utcnow().isoformat(),
            }
            
            hass.bus.async_fire("crop_steering_llm_test_result", event_data)
            
            if result.success:
                _LOGGER.info("LLM API key test successful: %s", result.message)
            else:
                _LOGGER.warning("LLM API key test failed: %s", result.message)
                
        except Exception as e:
            _LOGGER.error("LLM API key test error: %s", e)
            hass.bus.async_fire("crop_steering_llm_test_result", {
                "success": False,
                "message": f"Test failed with error: {e}",
                "recommendations": ["Check configuration and try again"],
                "timestamp": dt_util.utcnow().isoformat(),
            })

    async def async_estimate_llm_costs(call: ServiceCall) -> None:
        """Service to estimate LLM usage costs."""
        try:
            from .llm.setup_helper import LLMSetupHelper
            from .llm.client import LLMProvider
            
            provider_str = call.data["provider"]
            model = call.data["model"]
            calls_per_day = call.data.get("calls_per_day", 100)
            
            # Validate provider
            try:
                provider = LLMProvider(provider_str)
            except ValueError:
                result = {
                    "error": f"Invalid provider: {provider_str}",
                    "recommendations": ["Use 'openai' or 'claude' as provider"]
                }
                hass.bus.async_fire("crop_steering_llm_cost_estimate", result)
                return
            
            # Create setup helper and estimate
            setup_helper = LLMSetupHelper(hass)
            result = await setup_helper.estimate_costs(provider, model, calls_per_day)
            
            # Add timestamp
            result["timestamp"] = dt_util.utcnow().isoformat()
            
            # Fire event with results
            hass.bus.async_fire("crop_steering_llm_cost_estimate", result)
            
            _LOGGER.info("LLM cost estimate completed for %s/%s", provider_str, model)
                
        except Exception as e:
            _LOGGER.error("LLM cost estimation error: %s", e)
            hass.bus.async_fire("crop_steering_llm_cost_estimate", {
                "error": f"Cost estimation failed: {e}",
                "recommendations": ["Check model name and try again"],
                "timestamp": dt_util.utcnow().isoformat(),
            })

    async def async_generate_llm_config(call: ServiceCall) -> None:
        """Service to generate LLM configuration template."""
        try:
            from .llm.setup_helper import LLMSetupHelper
            from .llm.client import LLMProvider
            
            provider_str = call.data["provider"]
            model = call.data["model"]
            daily_budget = call.data.get("daily_budget", 2.0)
            
            # Validate provider
            try:
                provider = LLMProvider(provider_str)
            except ValueError:
                result = {
                    "error": f"Invalid provider: {provider_str}",
                    "recommendations": ["Use 'openai' or 'claude' as provider"]
                }
                hass.bus.async_fire("crop_steering_llm_config_generated", result)
                return
            
            # Create setup helper and generate config
            setup_helper = LLMSetupHelper(hass)
            config_template = setup_helper.generate_config_template(provider, model, daily_budget)
            
            # Fire event with results
            result = {
                "success": True,
                "config_template": config_template,
                "provider": provider_str,
                "model": model,
                "daily_budget": daily_budget,
                "timestamp": dt_util.utcnow().isoformat(),
            }
            
            hass.bus.async_fire("crop_steering_llm_config_generated", result)
            
            _LOGGER.info("LLM config template generated for %s/%s", provider_str, model)
                
        except Exception as e:
            _LOGGER.error("LLM config generation error: %s", e)
            hass.bus.async_fire("crop_steering_llm_config_generated", {
                "error": f"Config generation failed: {e}",
                "recommendations": ["Check parameters and try again"],
                "timestamp": dt_util.utcnow().isoformat(),
            })

    # Register services
    for service_name, service_config in SERVICES.items():
        # Handle dynamic schema
        schema = service_config["schema"]
        if service_config.get("dynamic_schema"):
            schema = get_irrigation_shot_schema(hass)

        hass.services.async_register(
            DOMAIN,
            service_name,
            locals()[service_config["method"]],
            schema=schema,
        )

    _LOGGER.info("Crop steering services registered")


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services."""
    for service_name in SERVICES:
        hass.services.async_remove(DOMAIN, service_name)

    _LOGGER.info("Crop steering services unloaded")
