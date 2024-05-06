"""Custom integration for NASCAR data."""
import logging

from homeassistant.helpers import discovery

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ha_nascar"

async def async_setup(hass, config):
    """Set up the ha_nascar component."""
    _LOGGER.info("Setting up ha_nascar component")
    
    # Load the platforms
    for platform in ["sensor"]:
        hass.async_create_task(
            discovery.async_load_platform(hass, platform, DOMAIN, {}, config)
        )

    return True
