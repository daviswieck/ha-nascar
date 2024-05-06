"""Platform for sensor integration."""
import logging
import requests
from datetime import timedelta
import voluptuous as vol

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)

SENSOR_TYPES = {
    "lap_number": ["Lap Number", None, "laps"],
    "elapsed_time": ["Elapsed Time", None, "s"],
    "flag_state": ["Flag State", None, None],
    "laps_in_race": ["Laps in Race", None, "laps"],
    "laps_to_go": ["Laps to Go", None, "laps"],
    "number_of_caution_segments": ["Number of Caution Segments", None, "segments"],
    "number_of_caution_laps": ["Number of Caution Laps", None, "laps"],
    "number_of_lead_changes": ["Number of Lead Changes", None, "changes"],
    "number_of_leaders": ["Number of Leaders", None, "leaders"],
    "avg_diff_1to3": ["Average Difference 1 to 3", None, None],
    "stage": ["Stage", None, None],
    "vehicles": ["Vehicles", None, None]  # Assuming "vehicles" is an attribute
}

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend({})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    add_entities([NascarSensor()], True)

class NascarSensor(Entity):
    """Representation of a NASCAR sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._state = None
        self._attributes = {}
        self._available = False

    @property
    def name(self):
        """Return the name of the sensor."""
        return "NASCAR Sensor"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    def update(self):
        """Fetch data from NASCAR API."""
        try:
            response = requests.get("https://cf.nascar.com/live/feeds/live-feed.json")
            data = response.json()
            self._state = data["lap_number"]
            self._attributes = {key: data.get(key, "N/A") for key in SENSOR_TYPES.keys()}
            self._available = True
        except Exception as e:
            _LOGGER.error("Error fetching data: %s", e)
            self._available = False
