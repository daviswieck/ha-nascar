import aiohttp
import async_timeout
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ATTR_ATTRIBUTION
import homeassistant.util.dt as dt_util
from .const import BASE_URL, DEFAULT_UPDATE_INTERVAL

ATTRIBUTION = "Data provided by NASCAR"

class NascarSensor(SensorEntity):
    """Representation of a NASCAR sensor."""

    def __init__(self, update_interval):
        """Initialize the sensor."""
        self._update_interval = update_interval
        self._state = None
        self._attr_name = "NASCAR Sensor"
        self._attr_unique_id = "nascar_sensor"
        self._attributes = {}
        self._next_update = None

    async def async_update(self):
        """Fetch and parse NASCAR data."""
        if self._next_update and dt_util.utcnow() < self._next_update:
            return  # Skip update if not time yet

        await self._fetch_nascar_data()
        self._next_update = dt_util.utcnow() + timedelta(minutes=self._update_interval)

    async def _fetch_nascar_data(self):
        """Helper method to fetch and parse NASCAR live feed data."""
        url = BASE_URL  # Assuming BASE_URL contains the NASCAR live feed URL
        async with aiohttp.ClientSession() as session:
            try:
                with async_timeout.timeout(10):
                    response = await session.get(url)
                    raw_data = await response.json()

                    # Extract relevant NASCAR data from the JSON feed
                    self._attributes = {
                        "lap_number": raw_data.get("lap_number", "N/A"),
                        "elapsed_time": raw_data.get("elapsed_time", "N/A"),
                        "flag_state": raw_data.get("flag_state", "N/A"),
                        "race_id": raw_data.get("race_id", "N/A"),
                        "laps_in_race": raw_data.get("laps_in_race", "N/A"),
                        "laps_to_go": raw_data.get("laps_to_go", "N/A"),
                        "vehicles": raw_data.get("vehicles", "N/A"),
                        "run_id": raw_data.get("run_id", "N/A"),
                        "run_name": raw_data.get("run_name", "N/A"),
                        "series_id": raw_data.get("series_id", "N/A"),
                        "time_of_day": raw_data.get("time_of_day", "N/A"),
                        "time_of_day_os": raw_data.get("time_of_day_os", "N/A"),
                        "track_id": raw_data.get("track_id", "N/A"),
                        "track_length": raw_data.get("track_length", "N/A"),
                        "track_name": raw_data.get("track_name", "N/A"),
                        "run_type": raw_data.get("run_type", "N/A"),
                        "number_of_caution_segments": raw_data.get("number_of_caution_segments", "N/A"),
                        "number_of_caution_laps": raw_data.get("number_of_caution_laps", "N/A"),
                        "number_of_lead_changes": raw_data.get("number_of_lead_changes", "N/A"),
                        "number_of_leaders": raw_data.get("number_of_leaders", "N/A"),
                        "avg_diff_1to3": raw_data.get("avg_diff_1to3", "N/A"),
                        "stage": raw_data.get("stage", "N/A"),
                    }
                    # Set the state to something relevant, for example, lap number
                    self._state = raw_data.get("lap_number", "N/A")
            except Exception as e:
                self._state = f"Error: {e}"
                self._attributes = {"error": str(e)}

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the NASCAR sensor platform."""
    update_interval = entry.options.get("update_interval", DEFAULT_UPDATE_INTERVAL)

    async_add_entities([NascarSensor(update_interval)])
