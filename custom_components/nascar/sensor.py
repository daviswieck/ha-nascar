import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ATTR_ATTRIBUTION
from .const import ATTRIBUTION, DOMAIN

_LOGGER = logging.getLogger(__name__)

class NascarSensor(SensorEntity):
    """Representation of a NASCAR driver sensor."""

    def __init__(self, coordinator, driver_number):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.driver_number = driver_number  # Store the entered driver number
        self._attr_name = f"NASCAR Driver {driver_number}"
        self._attr_unique_id = f"nascar_driver_{driver_number}"
        self._attr_attribution = ATTRIBUTION

    @property
    def state(self):
        """Return the state of the sensor (driver's position)."""
        data = self.coordinator.data
        if data and "vehicles" in data:
            for driver in data["vehicles"]:
                if str(driver.get("vehicle_number")) == str(self.driver_number):
                    return driver.get("running_position", "N/A")  # Set state to driver's position
        return "N/A"

    @property
    def extra_state_attributes(self):
        """Return extra attributes (full driver details)."""
        data = self.coordinator.data
        if data and "vehicles" in data:
            for driver in data["vehicles"]:
                if str(driver.get("vehicle_number")) == str(self.driver_number):
                    return driver  # Return all driver details as attributes
        return {}

    @property
    def available(self):
        """Return True if the sensor is available."""
        return self.coordinator.data is not None

    async def async_update(self):
        """Request an update from the coordinator."""
        await self.coordinator.async_request_refresh()


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the NASCAR sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]  # Get the coordinator
    driver_number = entry.data["driver_number"]  # Get driver number from config entry

    async_add_entities([NascarSensor(coordinator, driver_number)])  # Pass driver number
