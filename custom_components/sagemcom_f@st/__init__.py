"""The Sagemcom integration."""
import asyncio
import logging

import voluptuous as vol

from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_HOST, HTTP_BAD_REQUEST
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    config_validation as cv,
    device_registry as dr,
    discovery,
)

from .const import DOMAIN, CONF_ENCRYPTION_METHOD

from sagemcom_api import SagemcomClient, EncryptionMethod

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)
_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["device_tracker"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Sagemcom component."""

    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Sagemcom from a config entry."""

    host = entry.data[CONF_HOST]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    encryption_method = data[CONF_ENCRYPTION_METHOD]

    sagemcom = SagemcomClient(host, username, password, encryption_method)

    try:
        device = await sagemcom.get_device_info()
        _LOGGER.info(device["DeviceInfo"])
    except:
        _LOGGER.error("ERROR")

    # Create router device
    device_info = device["DeviceInfo"]
    device_registry = await dr.async_get_registry(hass)

    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        connections={(dr.CONNECTION_NETWORK_MAC, device_info["MACAddress"])},
        identifiers={(DOMAIN, device_info["SerialNumber"])},
        manufacturer=device_info["Manufacturer"],
        name=f'{device_info["Manufacturer"]} {device_info["ModelNumber"]}',
        model=device_info["ModelName"],
        sw_version=device_info["SoftwareVersion"],
    )

    # Register components
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True

    async def async_livebox_reboot(call):
        """Handle reboot service call."""
        await print("Reboot")

    hass.services.async_register(DOMAIN, "reboot", async_livebox_reboot)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok