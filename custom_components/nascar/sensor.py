import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ATTR_ATTRIBUTION
from .const import ATTRIBUTION, DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

class NascarSensor(SensorEntity):
    """Representation of a NASCAR sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_name = "NASCAR Sensor"  # Or make it dynamic, e.g., f"NASCAR {race_name}"
        self._attr_unique_id = "nascar_sensor" # Or make it dynamic, e.g., f"nascar_{race_id}"
        self._attr_attribution = ATTRIBUTION

    @property
    def state(self):
        """Return the state of the sensor."""
        # Access data from the coordinator
        data = self.coordinator.data
        if data:
            # Choose what you want the main state to be.  Example:
            return data.get("lap_number", "N/A")  # Or data.get("flag_state") or whatever you want
        return None  # Handle the case where data is not yet available

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        data = self.coordinator.data
        if data:
            return data  # Return all the data as attributes
        return {}

    @property
    def available(self):
        """Return True if the sensor is available."""
        return self.coordinator.data is not None

    async def async_update(self):
        """Update the sensor (called by Home Assistant)."""
        # The DataUpdateCoordinator handles the actual data fetching.
        # We just tell Home Assistant the sensor needs to be updated.
        await self.coordinator.async_request_refresh()


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the NASCAR sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]  # Get the coordinator

    async_add_entities([NascarSensor(coordinator)])  # Pass the coordinator to the sensor