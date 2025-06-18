"""The Crop Steering System integration."""
from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .services import async_setup_services, async_unload_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.SELECT, Platform.NUMBER]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Crop Steering System from a config entry."""
    _LOGGER.info("Setting up Crop Steering System")
    
    # Set up the integration data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Install package files if they don't exist
    await _install_package_files(hass)
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Set up services
    await async_setup_services(hass)
    
    return True

async def _install_package_files(hass: HomeAssistant) -> None:
    """Install package files to the correct location."""
    config_dir = hass.config.config_dir
    packages_dir = os.path.join(config_dir, "packages")
    crop_steering_dir = os.path.join(packages_dir, "CropSteering")
    
    # Create packages directory if it doesn't exist
    os.makedirs(packages_dir, exist_ok=True)
    
    # Check if crop steering package already exists
    if os.path.exists(crop_steering_dir):
        _LOGGER.info("Crop Steering package already exists")
        return
    
    # Get the path to our integration directory
    integration_dir = Path(__file__).parent
    package_source = integration_dir / "packages" / "CropSteering"
    
    if package_source.exists():
        _LOGGER.info("Installing Crop Steering package files")
        shutil.copytree(package_source, crop_steering_dir)
        _LOGGER.info("Package files installed successfully")
    else:
        _LOGGER.warning("Package source files not found in integration")

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        
    # Unload services
    await async_unload_services(hass)
    
    return unload_ok