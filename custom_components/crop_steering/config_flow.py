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

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="Crop Steering System"): str,
        vol.Required("installation_mode", default="auto"): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    {"value": "auto", "label": "Automatic Setup (Recommended)"},
                    {"value": "manual", "label": "Manual Configuration"},
                ]
            )
        ),
    }
)

STEP_MANUAL_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("pump_switch"): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="switch")
        ),
        vol.Required("main_line_switch"): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="switch")
        ),
        vol.Optional("zone_1_switch"): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="switch")
        ),
        vol.Optional("zone_2_switch"): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="switch")
        ),
        vol.Optional("zone_3_switch"): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="switch")
        ),
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Crop Steering System."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            self._data.update(user_input)
            
            if user_input["installation_mode"] == "auto":
                # Install files and create entry
                await self._install_integration_files()
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={"installation_mode": "auto", "name": user_input[CONF_NAME]},
                )
            else:
                # Go to manual configuration
                return await self.async_step_manual()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual configuration."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Validate that switches exist
            for key, entity_id in user_input.items():
                if entity_id and not self.hass.states.get(entity_id):
                    errors[key] = "entity_not_found"
            
            if not errors:
                # Install files and create entry
                await self._install_integration_files()
                
                self._data.update(user_input)
                return self.async_create_entry(
                    title=self._data.get(CONF_NAME, "Crop Steering System"),
                    data=self._data,
                )

        return self.async_show_form(
            step_id="manual",
            data_schema=STEP_MANUAL_DATA_SCHEMA,
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