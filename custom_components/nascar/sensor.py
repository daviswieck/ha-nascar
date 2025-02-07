import logging
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class NascarSensor(SensorEntity):
    """Representation of a NASCAR race sensor."""

    def __init__(self, coordinator, favorite_driver_number):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.favorite_driver_number = favorite_driver_number
        self._attr_name = "NASCAR Race Info"
        self._attr_unique_id = "nascar_race_info"

    @property
    def state(self):
        """Return the state of the sensor (time of day or lap number)."""
        data = self.coordinator.data
        if data:
            # Show "time_of_day_os" before the race
            race_time_str = data.get("time_of_day_os")
            if race_time_str and self._is_before_race(data):
                return race_time_str
            # Show lap number after the race has started
            return data.get("lap_number", "N/A")
        return "N/A"

    def _is_before_race(self, data):
        """Check if the race is before starting (based on time)."""
        race_time_str = data.get("time_of_day_os")
        if race_time_str:
            race_time = race_time_str.split("T")[-1]
            race_hour, race_minute = map(int, race_time.split(":")[:2])
            current_time = self.coordinator.hass.helpers.dt_util.utcnow().hour * 60 + self.coordinator.hass.helpers.dt_util.utcnow().minute
            return (race_hour * 60 + race_minute) > current_time
        return False

    @property
    def extra_state_attributes(self):
        """Return race attributes, excluding vehicles."""
        data = self.coordinator.data
        if not data:
            return {}

        # Extract all race details except "vehicles"
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
            "stage_num": data.get("stage", {}).get("stage_num"),
            "finish_at_lap": data.get("stage", {}).get("finish_at_lap"),
            "laps_in_stage": data.get("stage", {}).get("laps_in_stage"),
        }

        # Get the top 5 driver numbers as an array
        running_order = []
        if "vehicles" in data:
            for driver in data["vehicles"][:5]:  # Limit to top 5 drivers
                driver_number = driver.get("vehicle_number")
                if driver_number:
                    running_order.append(str(driver_number))

        # Add the running_order and favorite driver's position to the attributes
        race_attributes["running_order"] = running_order
        race_attributes["favorite_driver_position"] = self.get_favorite_driver_position(data)

        return race_attributes

    def get_favorite_driver_position(self, data):
        """Return the position of the user's favorite driver."""
        if "vehicles" in data:
            for position, driver in enumerate(data["vehicles"], start=1):
                if str(driver.get("vehicle_number")) == str(self.favorite_driver_number):
                    return position
        return "N/A"  # If the favorite driver is not found

class NascarVehicleSensor(SensorEntity):
    """Representation of a NASCAR vehicle sensor for the favorite driver."""

    def __init__(self, coordinator, favorite_driver_number):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.favorite_driver_number = favorite_driver_number
        self._attr_name = f"NASCAR Vehicle Info - {favorite_driver_number}"
        self._attr_unique_id = f"nascar_vehicle_info_{favorite_driver_number}"

    @property
    def state(self):
        """Return the state of the sensor (vehicle's running position)."""
        data = self.coordinator.data
        if data and "vehicles" in data:
            for driver in data["vehicles"]:
                if str(driver.get("vehicle_number")) == str(self.favorite_driver_number):
                    return driver.get("running_position", "N/A")
        return "N/A"

    @property
    def extra_state_attributes(self):
        """Return all vehicle information for the favorite driver."""
        data = self.coordinator.data
        if data and "vehicles" in data:
            for driver in data["vehicles"]:
                if str(driver.get("vehicle_number")) == str(self.favorite_driver_number):
                    # Extract the full vehicle details for the favorite driver
                    return {
                        "vehicle_number": driver.get("vehicle_number", "N/A"),
                        "driver_name": driver["driver"].get("full_name", "N/A"),
                        "vehicle_manufacturer": driver.get("vehicle_manufacturer", "N/A"),
                        "average_restart_speed": driver.get("average_restart_speed", "N/A"),
                        "average_running_position": driver.get("average_running_position", "N/A"),
                        "average_speed": driver.get("average_speed", "N/A"),
                        "best_lap": driver.get("best_lap", "N/A"),
                        "best_lap_speed": driver.get("best_lap_speed", "N/A"),
                        "best_lap_time": driver.get("best_lap_time", "N/A"),
                        "vehicle_elapsed_time": driver.get("vehicle_elapsed_time", "N/A"),
                        "fastest_laps_run": driver.get("fastest_laps_run", "N/A"),
                        "laps_position_improved": driver.get("laps_position_improved", "N/A"),
                        "laps_completed": driver.get("laps_completed", "N/A"),
                        "laps_led": sum(led["end_lap"] - led["start_lap"] for led in driver.get("laps_led", [])),
                        "last_lap_speed": driver.get("last_lap_speed", "N/A"),
                        "last_lap_time": driver.get("last_lap_time", "N/A"),
                        "passes_made": driver.get("passes_made", "N/A"),
                        "passing_differential": driver.get("passing_differential", "N/A"),
                        "position_differential_last_10_percent": driver.get("position_differential_last_10_percent", "N/A"),
                        "pit_stops": driver.get("pit_stops", "N/A"),
                        "qualifying_status": driver.get("qualifying_status", "N/A"),
                        "running_position": driver.get("running_position", "N/A"),
                        "status": driver.get("status", "N/A"),
                        "delta": driver.get("delta", "N/A"),
                        "sponsor_name": driver.get("sponsor_name", "N/A"),
                        "starting_position": driver.get("starting_position", "N/A"),
                        "times_passed": driver.get("times_passed", "N/A"),
                        "quality_passes": driver.get("quality_passes", "N/A"),
                        "is_on_track": driver.get("is_on_track", "N/A"),
                        "is_on_dvp": driver.get("is_on_dvp", "N/A"),
                    }
        return {}

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the NASCAR sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    favorite_driver_number = entry.data["driver_number"]

    async_add_entities([NascarSensor(coordinator, favorite_driver_number), NascarVehicleSensor(coordinator, favorite_driver_number)])
