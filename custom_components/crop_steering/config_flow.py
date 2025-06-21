"""Config flow for Crop Steering System integration."""
from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_NUM_ZONES,
    CONF_ENV_FILE_PATH,
    MIN_ZONES,
    MAX_ZONES,
    DEFAULT_NUM_ZONES,
)
from .zone_config import ZoneConfigParser

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="Crop Steering System"): str,
        vol.Required("installation_mode", default="auto"): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    {"value": "auto", "label": "Load from crop_steering.env (Recommended)"},
                    {"value": "manual", "label": "Manual Zone Configuration"},
                ]
            )
        ),
    }
)

def get_zone_schema(num_zones: int) -> vol.Schema:
    """Generate zone configuration schema based on number of zones."""
    schema_dict = {
        vol.Required("pump_switch"): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="switch")
        ),
        vol.Required("main_line_switch"): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="switch")
        ),
    }
    
    # Add zone switches based on configured number
    for i in range(1, num_zones + 1):
        schema_dict[vol.Optional(f"zone_{i}_switch")] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="switch")
        )
        
    return vol.Schema(schema_dict)


STEP_ZONE_COUNT_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_NUM_ZONES,
            default=DEFAULT_NUM_ZONES
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=MIN_ZONES,
                max=MAX_ZONES,
                mode="box",
                step=1
            )
        ),
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Crop Steering System."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data = {}
        self._zone_parser = None
        self._num_zones = DEFAULT_NUM_ZONES

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            self._data.update(user_input)
            
            if user_input["installation_mode"] == "auto":
                # Try to load from crop_steering.env
                self._zone_parser = ZoneConfigParser(self.hass.config.config_dir)
                if self._zone_parser.load_configuration():
                    # Validate entities exist
                    valid, missing = self._zone_parser.validate_entities(self.hass)
                    if not valid:
                        errors["base"] = "missing_entities"
                        errors["missing_entities"] = missing
                        return self.async_show_form(
                            step_id="user",
                            data_schema=STEP_USER_DATA_SCHEMA,
                            errors=errors,
                            description_placeholders={"missing": "\n".join(missing[:5])}
                        )
                    
                    # Create entry with zone configuration
                    zone_configs = self._zone_parser.zones
                    hardware_config = self._zone_parser.hardware_config
                    
                    data = {
                        "installation_mode": "auto",
                        "name": user_input[CONF_NAME],
                        CONF_NUM_ZONES: len(zone_configs),
                        "zones": zone_configs,
                        "hardware": hardware_config,
                    }
                    
                    await self._install_integration_files()
                    return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data=data,
                    )
                else:
                    errors["base"] = "env_file_not_found"
                    return self.async_show_form(
                        step_id="user",
                        data_schema=STEP_USER_DATA_SCHEMA,
                        errors=errors,
                    )
            else:
                # Go to manual configuration - first ask for number of zones
                return await self.async_step_zone_count()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_zone_count(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle zone count selection."""
        if user_input is not None:
            self._num_zones = int(user_input[CONF_NUM_ZONES])
            self._data[CONF_NUM_ZONES] = self._num_zones
            return await self.async_step_manual()

        return self.async_show_form(
            step_id="zone_count",
            data_schema=STEP_ZONE_COUNT_SCHEMA,
        )
        
    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual zone configuration."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Validate that switches exist
            for key, entity_id in user_input.items():
                if entity_id and not self.hass.states.get(entity_id):
                    errors[key] = "entity_not_found"
            
            if not errors:
                # Build zone configuration from user input
                zones = {}
                hardware = {
                    "pump_switch": user_input["pump_switch"],
                    "main_line_switch": user_input["main_line_switch"],
                }
                
                for i in range(1, self._num_zones + 1):
                    zone_switch = user_input.get(f"zone_{i}_switch")
                    if zone_switch:
                        zones[i] = {
                            "zone_number": i,
                            "zone_switch": zone_switch,
                            # Manual config doesn't include sensors
                            "vwc_front": "",
                            "vwc_back": "",
                            "ec_front": "",
                            "ec_back": "",
                        }
                
                # Install files and create entry
                await self._install_integration_files()
                
                self._data.update({
                    "installation_mode": "manual",
                    "zones": zones,
                    "hardware": hardware,
                })
                
                return self.async_create_entry(
                    title=self._data.get(CONF_NAME, "Crop Steering System"),
                    data=self._data,
                )

        # Generate schema for configured number of zones
        zone_schema = get_zone_schema(self._num_zones)
        
        return self.async_show_form(
            step_id="manual",
            data_schema=zone_schema,
            errors=errors,
        )

    async def _install_integration_files(self) -> None:
        """Install package files, AppDaemon, and configuration."""
        config_dir = self.hass.config.config_dir
        integration_dir = Path(__file__).parent
        
        # Install packages
        packages_dir = os.path.join(config_dir, "packages")
        os.makedirs(packages_dir, exist_ok=True)
        
        crop_steering_dir = os.path.join(packages_dir, "CropSteering")
        if not os.path.exists(crop_steering_dir):
            package_source = integration_dir / "packages" / "CropSteering"
            if package_source.exists():
                shutil.copytree(package_source, crop_steering_dir)
                _LOGGER.info("Installed package files")
        
        # Install AppDaemon files if AppDaemon exists
        appdaemon_dir = os.path.join(config_dir, "appdaemon")
        if os.path.exists(appdaemon_dir):
            appdaemon_source = integration_dir / "appdaemon"
            if appdaemon_source.exists():
                for item in appdaemon_source.iterdir():
                    dest = Path(appdaemon_dir) / item.name
                    if item.is_dir():
                        if not dest.exists():
                            shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)
                _LOGGER.info("Installed AppDaemon files")
        
        # Install configuration files
        env_source = integration_dir / "crop_steering.env"
        config_source = integration_dir / "configure_crop_steering.py"
        
        if env_source.exists():
            shutil.copy2(env_source, os.path.join(config_dir, "crop_steering.env.example"))
        
        if config_source.exists():
            shutil.copy2(config_source, os.path.join(config_dir, "configure_crop_steering.py"))
        
        _LOGGER.info("Integration files installed successfully")