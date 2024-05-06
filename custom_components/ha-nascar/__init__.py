"""Custom integration for NASCAR data."""
import logging

from homeassistant.helpers import discovery

_LOGGER = logging.getLogger(__name__)

DOMAIN = "nascar"

async def async_setup(hass, config):
    """Set up the NASCAR component."""
    _LOGGER.info("Setting up NASCAR component")
    
    # Load the platforms
    for platform in ["sensor"]:
        hass.async_create_task(
            discovery.async_load_platform(hass, platform, DOMAIN, {}, config)
        )

    return True
