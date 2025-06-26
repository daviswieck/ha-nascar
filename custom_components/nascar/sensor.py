import logging
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class NascarSensor(CoordinatorEntity, SensorEntity):
    """Representation of a NASCAR race sensor."""

    def __init__(self, coordinator, favorite_driver_number):
        super().__init__(coordinator)
        self.favorite_driver_number = favorite_driver_number
        self._attr_name = "NASCAR Race Info"
        self._attr_unique_id = "nascar_race_info"

    @property
    def state(self):
        """Return the sensor state (time or lap number)."""
        data = self.coordinator.data
        if data:
            race_time_str = data.get("time_of_day_os")
            if race_time_str and self._is_before_race(race_time_str):
                return race_time_str
            return data.get("lap_number", "N/A")
        return "N/A"

    def _is_before_race(self, race_time_str):
        """Check if the race has not started yet."""
        try:
            race_time = datetime.fromisoformat(race_time_str.replace("Z", "+00:00"))
            now = dt_util.utcnow().astimezone(race_time.tzinfo)
            return now < race_time
        except Exception as e:
            _LOGGER.warning(f"Failed to parse race time: {race_time_str} - {e}")
            return False

    @property
    def extra_state_attributes(self):
        """Return additional race information."""
        data = self.coordinator.data
        if not data:
            return {}

        race_attributes = {
            "lap_number": data.get("lap_number"),
            "elapsed_time": data.get("elapsed_time"),
            "flag_state": data.get("flag_state"),
            "race_id": data.get("race_id"),
            "laps_in_race": data.get("laps_in_race"),
            "run_id": data.get("run_id"),
            "run_name": data.get("run_name"),
            "series_id": data.get("series_id"),
            "time_of_day": data.get("time_of_day"),
            "time_of_day_os": data.get("time_of_day_os"),
            "track_id": data.get("track_id"),
            "track_length": data.get("track_length"),
            "track_name": data.get("track_name"),
            "run_type": data.get("run_type"),
            "number_of_caution_segments": data.get("number_of_caution_segments"),
            "number_of_caution_laps": data.get("number_of_caution_laps"),
            "number_of_lead_changes": data.get("number_of_lead_changes"),
            "number_of_leaders": data.get("number_of_leaders"),
            "avg_diff_1to3": data.get("avg_diff_1to3"),
        }

        stage = data.get("stage", {})
        race_attributes["stage_num"] = stage.get("stage_num")
        race_attributes["finish_at_lap"] = stage.get("finish_at_lap")
        race_attributes["laps_in_stage"] = stage.get("laps_in_stage")

        # Top 5 vehicles
        running_order = [
            str(driver.get("vehicle_number"))
            for driver in data.get("vehicles", [])[:5]
            if driver.get("vehicle_number")
        ]
        race_attributes["running_order"] = running_order
        race_attributes["favorite_driver_position"] = self.get_favorite_driver_position(data)

        return race_attributes

    def get_favorite_driver_position(self, data):
        """Find the favorite driver's current position."""
        for position, driver in enumerate(data.get("vehicles", []), start=1):
            if str(driver.get("vehicle_number")) == str(self.favorite_driver_number):
                return position
        return "N/A"


class NascarVehicleSensor(CoordinatorEntity, SensorEntity):
    """Sensor for favorite driver's vehicle stats."""

    def __init__(self, coordinator, favorite_driver_number):
        super().__init__(coordinator)
        self.favorite_driver_number = favorite_driver_number
        self._attr_name = f"NASCAR Vehicle Info - {favorite_driver_number}"
        self._attr_unique_id = f"nascar_vehicle_info_{favorite_driver_number}"

    @property
    def state(self):
        """Return current running position of the favorite driver."""
        driver = self.get_driver_data()
        if driver:
            return driver.get("running_position", "N/A")
        return "N/A"

    @property
    def extra_state_attributes(self):
        """Return extended attributes for the favorite driver."""
        driver = self.get_driver_data()
        if not driver:
            return {}

        def get_or_default(key, default="N/A"):
            return driver.get(key, default)

        def get_driver_field(key, default="N/A"):
            return driver.get("driver", {}).get(key, default)

        laps_led = sum(
            led.get("end_lap", 0) - led.get("start_lap", 0)
            for led in driver.get("laps_led", [])
        )

        return {
            "vehicle_number": get_or_default("vehicle_number"),
            "driver_name": get_driver_field("full_name"),
            "vehicle_manufacturer": get_or_default("vehicle_manufacturer"),
            "average_restart_speed": get_or_default("average_restart_speed"),
            "average_running_position": get_or_default("average_running_position"),
            "average_speed": get_or_default("average_speed"),
            "best_lap": get_or_default("best_lap"),
            "best_lap_speed": get_or_default("best_lap_speed"),
            "best_lap_time": get_or_default("best_lap_time"),
            "vehicle_elapsed_time": get_or_default("vehicle_elapsed_time"),
            "fastest_laps_run": get_or_default("fastest_laps_run"),
            "laps_position_improved": get_or_default("laps_position_improved"),
            "laps_completed": get_or_default("laps_completed"),
            "laps_led": laps_led,
            "last_lap_speed": get_or_default("last_lap_speed"),
            "last_lap_time": get_or_default("last_lap_time"),
            "passes_made": get_or_default("passes_made"),
            "passing_differential": get_or_default("passing_differential"),
            "position_differential_last_10_percent": get_or_default("position_differential_last_10_percent"),
            "pit_stops": get_or_default("pit_stops"),
            "qualifying_status": get_or_default("qualifying_status"),
            "running_position": get_or_default("running_position"),
            "status": get_or_default("status"),
            "delta": get_or_default("delta"),
            "sponsor_name": get_or_default("sponsor_name"),
            "starting_position": get_or_default("starting_position"),
            "times_passed": get_or_default("times_passed"),
            "quality_passes": get_or_default("quality_passes"),
            "is_on_track": get_or_default("is_on_track"),
            "is_on_dvp": get_or_default("is_on_dvp"),
        }

    def get_driver_data(self):
        """Return the data dict for the favorite driver."""
        for driver in self.coordinator.data.get("vehicles", []):
            if str(driver.get("vehicle_number")) == str(self.favorite_driver_number):
                return driver
        return None


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up NASCAR sensors from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    favorite_driver_number = entry.data["driver_number"]

    sensors = [
        NascarSensor(coordinator, favorite_driver_number),
        NascarVehicleSensor(coordinator, favorite_driver_number),
    ]

    async_add_entities(sensors)
