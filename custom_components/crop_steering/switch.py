"""Crop Steering System switches."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SWITCH_DESCRIPTIONS = [
    SwitchEntityDescription(
        key="zone_1_enabled",
        name="Zone 1 Enabled",
        icon="mdi:water-pump",
    ),
    SwitchEntityDescription(
        key="zone_2_enabled",
        name="Zone 2 Enabled", 
        icon="mdi:water-pump",
    ),
    SwitchEntityDescription(
        key="zone_3_enabled",
        name="Zone 3 Enabled",
        icon="mdi:water-pump",
    ),
    SwitchEntityDescription(
        key="ec_stacking_enabled",
        name="EC Stacking Enabled",
        icon="mdi:chemistry-bottle",
    ),
    SwitchEntityDescription(
        key="system_enabled",
        name="System Enabled",
        icon="mdi:power",
    ),
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Crop Steering switches."""
    switches = []
    
    for description in SWITCH_DESCRIPTIONS:
        switches.append(CropSteeringSwitch(entry, description))
    
    async_add_entities(switches)

class CropSteeringSwitch(SwitchEntity):
    """Crop Steering switch."""

    def __init__(
        self,
        entry: ConfigEntry,
        description: SwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{description.key}"
        self._attr_name = f"Crop Steering {description.name}"
        self._attr_is_on = False

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Crop Steering System",
            manufacturer="Home Assistant Community", 
            model="Professional Irrigation Controller",
            sw_version="2.0.0",
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self._attr_is_on = False
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return if switch is available."""
        return True