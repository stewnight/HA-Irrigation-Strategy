"""Crop Steering System sensors."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfTime,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="current_phase",
        name="Current Phase",
        icon="mdi:water-circle",
    ),
    SensorEntityDescription(
        key="vwc_zone_1",
        name="Zone 1 VWC",
        device_class=SensorDeviceClass.MOISTURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-percent",
    ),
    SensorEntityDescription(
        key="ec_zone_1", 
        name="Zone 1 EC",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="mS/cm",
        icon="mdi:lightning-bolt",
    ),
    SensorEntityDescription(
        key="irrigation_efficiency",
        name="Irrigation Efficiency",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-check",
    ),
    SensorEntityDescription(
        key="water_usage_daily",
        name="Daily Water Usage",
        device_class=SensorDeviceClass.VOLUME,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        icon="mdi:water",
    ),
    SensorEntityDescription(
        key="dryback_percentage",
        name="Dryback Percentage",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-minus",
    ),
    SensorEntityDescription(
        key="next_irrigation_time",
        name="Next Irrigation Time",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-outline",
    ),
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Crop Steering sensors."""
    sensors = []
    
    for description in SENSOR_DESCRIPTIONS:
        sensors.append(CropSteeringSensor(entry, description))
    
    async_add_entities(sensors)

class CropSteeringSensor(SensorEntity):
    """Crop Steering sensor."""

    def __init__(
        self,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{description.key}"
        self._attr_name = f"Crop Steering {description.name}"

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

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        # Template sensors will be created via YAML packages
        # This provides the entity structure for the integration
        return None

    @property
    def available(self) -> bool:
        """Return if sensor is available."""
        return True