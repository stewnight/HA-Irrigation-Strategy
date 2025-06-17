"""Crop Steering System select entities."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SELECT_DESCRIPTIONS = [
    SelectEntityDescription(
        key="crop_type",
        name="Crop Type",
        icon="mdi:sprout",
        options=[
            "Cannabis_Athena",
            "Cannabis_Hybrid", 
            "Cannabis_Indica",
            "Cannabis_Sativa",
            "Tomato",
            "Lettuce",
            "Basil",
            "Custom"
        ],
    ),
    SelectEntityDescription(
        key="steering_mode",
        name="Steering Mode",
        icon="mdi:steering",
        options=["Vegetative", "Generative"],
    ),
    SelectEntityDescription(
        key="irrigation_phase",
        name="Irrigation Phase",
        icon="mdi:water-circle",
        options=["P0", "P1", "P2", "P3", "Manual"],
    ),
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Crop Steering select entities."""
    selects = []
    
    for description in SELECT_DESCRIPTIONS:
        selects.append(CropSteeringSelect(entry, description))
    
    async_add_entities(selects)

class CropSteeringSelect(SelectEntity):
    """Crop Steering select entity."""

    def __init__(
        self,
        entry: ConfigEntry,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{description.key}"
        self._attr_name = f"Crop Steering {description.name}"
        self._attr_current_option = description.options[0] if description.options else None
        self._attr_options = description.options

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

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option in self.options:
            self._attr_current_option = option
            self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return if select is available."""
        return True