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
    # Critical Template Calculations - Ported from packages
    SensorEntityDescription(
        key="p1_shot_duration_seconds",
        name="P1 Shot Duration",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        icon="mdi:timer-sand",
    ),
    SensorEntityDescription(
        key="p2_shot_duration_seconds",
        name="P2 Shot Duration",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        icon="mdi:timer-sand",
    ),
    SensorEntityDescription(
        key="p3_shot_duration_seconds",
        name="P3 Emergency Shot Duration",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        icon="mdi:timer-sand",
    ),
    SensorEntityDescription(
        key="ec_ratio",
        name="EC Ratio",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:division",
    ),
    SensorEntityDescription(
        key="p2_vwc_threshold_adjusted",
        name="P2 VWC Threshold Adjusted",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-alert",
    ),
    SensorEntityDescription(
        key="configured_avg_vwc",
        name="Average VWC All Zones",
        device_class=SensorDeviceClass.MOISTURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-percent",
    ),
    SensorEntityDescription(
        key="configured_avg_ec",
        name="Average EC All Zones",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="mS/cm",
        icon="mdi:flash",
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
        # Implement critical calculations ported from template entities
        if self.entity_description.key == "p1_shot_duration_seconds":
            return self._calculate_p1_shot_duration()
        elif self.entity_description.key == "p2_shot_duration_seconds":
            return self._calculate_p2_shot_duration()
        elif self.entity_description.key == "p3_shot_duration_seconds":
            return self._calculate_p3_shot_duration()
        elif self.entity_description.key == "ec_ratio":
            return self._calculate_ec_ratio()
        elif self.entity_description.key == "p2_vwc_threshold_adjusted":
            return self._calculate_adjusted_p2_threshold()
        elif self.entity_description.key == "configured_avg_vwc":
            return self._calculate_avg_vwc()
        elif self.entity_description.key == "configured_avg_ec":
            return self._calculate_avg_ec()
        else:
            # Other sensors return None (placeholder)
            return None
    
    def _calculate_p1_shot_duration(self) -> float:
        """Calculate P1 shot duration in seconds."""
        try:
            # Get configuration values
            dripper_flow = self._get_number_value("dripper_flow_rate")
            substrate_vol = self._get_number_value("substrate_volume") 
            shot_size = self._get_number_value("p1_initial_shot_size")  # Simplified for now
            
            if dripper_flow > 0:
                volume_to_add = substrate_vol * (shot_size / 100)
                duration_hours = volume_to_add / dripper_flow
                return round(duration_hours * 3600, 1)
            return 0.0
        except Exception:
            return 0.0
    
    def _calculate_p2_shot_duration(self) -> float:
        """Calculate P2 shot duration in seconds."""
        try:
            dripper_flow = self._get_number_value("dripper_flow_rate")
            substrate_vol = self._get_number_value("substrate_volume")
            shot_size = self._get_number_value("p2_shot_size")
            
            if dripper_flow > 0:
                volume_to_add = substrate_vol * (shot_size / 100)
                duration_hours = volume_to_add / dripper_flow
                return round(duration_hours * 3600, 1)
            return 0.0
        except Exception:
            return 0.0
    
    def _calculate_p3_shot_duration(self) -> float:
        """Calculate P3 emergency shot duration in seconds."""
        try:
            dripper_flow = self._get_number_value("dripper_flow_rate")
            substrate_vol = self._get_number_value("substrate_volume")
            shot_size = self._get_number_value("p3_emergency_shot_size")
            
            if dripper_flow > 0:
                volume_to_add = substrate_vol * (shot_size / 100)
                duration_hours = volume_to_add / dripper_flow
                return round(duration_hours * 3600, 1)
            return 0.0
        except Exception:
            return 0.0
    
    def _calculate_ec_ratio(self) -> float:
        """Calculate current EC ratio vs target."""
        try:
            current_ec = self._calculate_avg_ec()
            # Get current EC target based on phase and mode
            target_ec = self._get_current_ec_target()
            
            if target_ec > 0 and current_ec is not None:
                return round(current_ec / target_ec, 2)
            return 1.0
        except Exception:
            return 1.0
    
    def _calculate_adjusted_p2_threshold(self) -> float:
        """Calculate P2 VWC threshold adjusted for EC ratio."""
        try:
            base_threshold = self._get_number_value("p2_vwc_threshold")
            ec_ratio = self._calculate_ec_ratio()
            ec_high_threshold = self._get_number_value("p2_ec_high_threshold")
            ec_low_threshold = self._get_number_value("p2_ec_low_threshold")
            
            # Simplified adjustment logic (5% adjustment)
            if ec_ratio > ec_high_threshold:
                return round(base_threshold + 5.0, 2)  # Raise threshold when EC high
            elif ec_ratio < ec_low_threshold:
                return round(base_threshold - 5.0, 2)  # Lower threshold when EC low
            else:
                return round(base_threshold, 2)
        except Exception:
            return self._get_number_value("p2_vwc_threshold")
    
    def _calculate_avg_vwc(self) -> float | None:
        """Calculate average VWC from user's physical sensors."""
        try:
            # Use user's actual sensor entities from .env
            sensors = [
                "sensor.vwc_r1_front", "sensor.vwc_r1_back",
                "sensor.vwc_r2_front", "sensor.vwc_r2_back", 
                "sensor.vwc_r3_front", "sensor.vwc_r3_back"
            ]
            
            values = []
            for sensor_id in sensors:
                try:
                    state = self.hass.states.get(sensor_id)
                    if state and state.state not in ['unknown', 'unavailable']:
                        values.append(float(state.state))
                except (ValueError, TypeError):
                    continue
            
            if values:
                return round(sum(values) / len(values), 2)
            return None
        except Exception:
            return None
    
    def _calculate_avg_ec(self) -> float | None:
        """Calculate average EC from user's physical sensors."""
        try:
            # Use user's actual sensor entities from .env
            sensors = [
                "sensor.ec_r1_front", "sensor.ec_r1_back",
                "sensor.ec_r2_front", "sensor.ec_r2_back",
                "sensor.ec_r3_front", "sensor.ec_r3_back"
            ]
            
            values = []
            for sensor_id in sensors:
                try:
                    state = self.hass.states.get(sensor_id)
                    if state and state.state not in ['unknown', 'unavailable']:
                        values.append(float(state.state))
                except (ValueError, TypeError):
                    continue
            
            if values:
                return round(sum(values) / len(values), 2)
            return None
        except Exception:
            return None
    
    def _get_number_value(self, key: str) -> float:
        """Get value from integration number entity."""
        try:
            entity_id = f"number.crop_steering_{key}"
            state = self.hass.states.get(entity_id)
            if state and state.state not in ['unknown', 'unavailable']:
                return float(state.state)
            return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _get_current_ec_target(self) -> float:
        """Get current EC target based on phase and steering mode."""
        try:
            # Get current phase and mode
            phase_state = self.hass.states.get("select.crop_steering_irrigation_phase")
            mode_state = self.hass.states.get("select.crop_steering_steering_mode")
            
            if not phase_state or not mode_state:
                return 3.0  # Default fallback
            
            phase = phase_state.state
            mode = mode_state.state.lower()
            
            # Map to EC target entities
            if mode == "vegetative":
                if phase == "P0":
                    return self._get_number_value("ec_target_veg_p0")
                elif phase == "P1":
                    return self._get_number_value("ec_target_veg_p1")
                elif phase == "P2":
                    return self._get_number_value("ec_target_veg_p2")
                elif phase == "P3":
                    return self._get_number_value("ec_target_veg_p3")
            else:  # Generative
                if phase == "P0":
                    return self._get_number_value("ec_target_gen_p0")
                elif phase == "P1":
                    return self._get_number_value("ec_target_gen_p1")
                elif phase == "P2":
                    return self._get_number_value("ec_target_gen_p2")
                elif phase == "P3":
                    return self._get_number_value("ec_target_gen_p3")
            
            return 3.0  # Default fallback
        except Exception:
            return 3.0

    @property
    def available(self) -> bool:
        """Return if sensor is available."""
        return True