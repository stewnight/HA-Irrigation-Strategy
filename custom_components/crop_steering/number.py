"""Crop Steering System number entities."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

NUMBER_DESCRIPTIONS = [
    NumberEntityDescription(
        key="substrate_volume",
        name="Substrate Volume",
        icon="mdi:cube-outline",
        native_min_value=1.0,
        native_max_value=100.0,
        native_step=0.1,
        native_unit_of_measurement=UnitOfVolume.LITERS,
    ),
    NumberEntityDescription(
        key="dripper_flow_rate",
        name="Dripper Flow Rate",
        icon="mdi:water-pump",
        native_min_value=0.1,
        native_max_value=20.0,
        native_step=0.1,
        native_unit_of_measurement="L/hr",
    ),
    NumberEntityDescription(
        key="field_capacity",
        name="Field Capacity",
        icon="mdi:water-percent",
        native_min_value=30.0,
        native_max_value=90.0,
        native_step=1.0,
        native_unit_of_measurement=PERCENTAGE,
    ),
    NumberEntityDescription(
        key="max_ec",
        name="Maximum EC",
        icon="mdi:lightning-bolt",
        native_min_value=3.0,
        native_max_value=12.0,
        native_step=0.1,
        native_unit_of_measurement="mS/cm",
    ),
    NumberEntityDescription(
        key="veg_dryback_target",
        name="Vegetative Dryback Target",
        icon="mdi:water-minus",
        native_min_value=40.0,
        native_max_value=65.0,
        native_step=1.0,
        native_unit_of_measurement=PERCENTAGE,
    ),
    NumberEntityDescription(
        key="gen_dryback_target",
        name="Generative Dryback Target", 
        icon="mdi:water-minus",
        native_min_value=35.0,
        native_max_value=55.0,
        native_step=1.0,
        native_unit_of_measurement=PERCENTAGE,
    ),
    NumberEntityDescription(
        key="p1_target_vwc",
        name="P1 Target VWC",
        icon="mdi:target",
        native_min_value=50.0,
        native_max_value=80.0,
        native_step=1.0,
        native_unit_of_measurement=PERCENTAGE,
    ),
    NumberEntityDescription(
        key="p2_vwc_threshold",
        name="P2 VWC Threshold",
        icon="mdi:water-alert",
        native_min_value=45.0,
        native_max_value=70.0,
        native_step=1.0,
        native_unit_of_measurement=PERCENTAGE,
    ),
    # P0 Phase Parameters
    NumberEntityDescription(
        key="p0_min_wait_time",
        name="P0 Minimum Wait Time",
        icon="mdi:timer",
        native_min_value=15.0,
        native_max_value=120.0,
        native_step=5.0,
        native_unit_of_measurement=UnitOfTime.MINUTES,
    ),
    NumberEntityDescription(
        key="p0_max_wait_time",
        name="P0 Maximum Wait Time",
        icon="mdi:timer-alert",
        native_min_value=60.0,
        native_max_value=300.0,
        native_step=15.0,
        native_unit_of_measurement=UnitOfTime.MINUTES,
    ),
    NumberEntityDescription(
        key="p0_dryback_drop_percent",
        name="P0 Dryback Drop Percent",
        icon="mdi:water-minus",
        native_min_value=5.0,
        native_max_value=25.0,
        native_step=1.0,
        native_unit_of_measurement=PERCENTAGE,
    ),
    # P1 Phase Parameters
    NumberEntityDescription(
        key="p1_initial_shot_size",
        name="P1 Initial Shot Size",
        icon="mdi:water-pump",
        native_min_value=0.5,
        native_max_value=5.0,
        native_step=0.1,
        native_unit_of_measurement=PERCENTAGE,
    ),
    NumberEntityDescription(
        key="p1_shot_increment",
        name="P1 Shot Size Increment",
        icon="mdi:plus",
        native_min_value=0.1,
        native_max_value=2.0,
        native_step=0.1,
        native_unit_of_measurement=PERCENTAGE,
    ),
    NumberEntityDescription(
        key="p1_max_shot_size",
        name="P1 Maximum Shot Size",
        icon="mdi:water-pump-off",
        native_min_value=5.0,
        native_max_value=20.0,
        native_step=0.5,
        native_unit_of_measurement=PERCENTAGE,
    ),
    NumberEntityDescription(
        key="p1_time_between_shots",
        name="P1 Time Between Shots",
        icon="mdi:timer-outline",
        native_min_value=5.0,
        native_max_value=30.0,
        native_step=1.0,
        native_unit_of_measurement=UnitOfTime.MINUTES,
    ),
    NumberEntityDescription(
        key="p1_max_shots",
        name="P1 Maximum Shots",
        icon="mdi:counter",
        native_min_value=3.0,
        native_max_value=15.0,
        native_step=1.0,
    ),
    NumberEntityDescription(
        key="p1_min_shots",
        name="P1 Minimum Shots",
        icon="mdi:counter",
        native_min_value=1.0,
        native_max_value=8.0,
        native_step=1.0,
    ),
    # P2 Phase Parameters
    NumberEntityDescription(
        key="p2_shot_size",
        name="P2 Shot Size",
        icon="mdi:water-pump",
        native_min_value=2.0,
        native_max_value=15.0,
        native_step=0.5,
        native_unit_of_measurement=PERCENTAGE,
    ),
    NumberEntityDescription(
        key="p2_ec_high_threshold",
        name="P2 EC High Threshold",
        icon="mdi:arrow-up-bold",
        native_min_value=1.05,
        native_max_value=1.50,
        native_step=0.05,
    ),
    NumberEntityDescription(
        key="p2_ec_low_threshold",
        name="P2 EC Low Threshold",
        icon="mdi:arrow-down-bold",
        native_min_value=0.50,
        native_max_value=0.95,
        native_step=0.05,
    ),
    # P3 Phase Parameters
    NumberEntityDescription(
        key="p3_veg_last_irrigation",
        name="P3 Veg Last Irrigation",
        icon="mdi:timer-sand",
        native_min_value=30.0,
        native_max_value=180.0,
        native_step=15.0,
        native_unit_of_measurement=UnitOfTime.MINUTES,
    ),
    NumberEntityDescription(
        key="p3_gen_last_irrigation",
        name="P3 Gen Last Irrigation",
        icon="mdi:timer-sand",
        native_min_value=60.0,
        native_max_value=300.0,
        native_step=15.0,
        native_unit_of_measurement=UnitOfTime.MINUTES,
    ),
    NumberEntityDescription(
        key="p3_emergency_vwc_threshold",
        name="P3 Emergency VWC Threshold",
        icon="mdi:alert",
        native_min_value=35.0,
        native_max_value=50.0,
        native_step=1.0,
        native_unit_of_measurement=PERCENTAGE,
    ),
    NumberEntityDescription(
        key="p3_emergency_shot_size",
        name="P3 Emergency Shot Size",
        icon="mdi:water-alert",
        native_min_value=0.5,
        native_max_value=5.0,
        native_step=0.1,
        native_unit_of_measurement=PERCENTAGE,
    ),
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Crop Steering number entities."""
    numbers = []
    
    for description in NUMBER_DESCRIPTIONS:
        numbers.append(CropSteeringNumber(entry, description))
    
    async_add_entities(numbers)

class CropSteeringNumber(NumberEntity):
    """Crop Steering number entity."""

    def __init__(
        self,
        entry: ConfigEntry,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{description.key}"
        self._attr_name = f"Crop Steering {description.name}"
        
        # Set default values based on Athena methodology
        default_values = {
            "substrate_volume": 10.0,
            "dripper_flow_rate": 2.0,
            "field_capacity": 70.0,
            "max_ec": 9.0,
            "veg_dryback_target": 50.0,
            "gen_dryback_target": 40.0,
            "p1_target_vwc": 65.0,
            "p2_vwc_threshold": 60.0,
            # P0 Phase Defaults
            "p0_min_wait_time": 30.0,
            "p0_max_wait_time": 120.0,
            "p0_dryback_drop_percent": 15.0,
            # P1 Phase Defaults
            "p1_initial_shot_size": 2.0,
            "p1_shot_increment": 0.5,
            "p1_max_shot_size": 10.0,
            "p1_time_between_shots": 15.0,
            "p1_max_shots": 6.0,
            "p1_min_shots": 3.0,
            # P2 Phase Defaults
            "p2_shot_size": 5.0,
            "p2_ec_high_threshold": 1.2,
            "p2_ec_low_threshold": 0.8,
            # P3 Phase Defaults
            "p3_veg_last_irrigation": 120.0,
            "p3_gen_last_irrigation": 180.0,
            "p3_emergency_vwc_threshold": 40.0,
            "p3_emergency_shot_size": 2.0,
        }
        
        self._attr_native_value = default_values.get(description.key, description.native_min_value)

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

    async def async_set_native_value(self, value: float) -> None:
        """Update the value."""
        self._attr_native_value = value
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return if number is available."""
        return True