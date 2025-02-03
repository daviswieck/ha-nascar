import logging
from datetime import timedelta, datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from.const import DOMAIN, DEFAULT_UPDATE_INTERVAL, BASE_URL  # Import BASE_URL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the NASCAR sensor from a config entry."""

    async def async_update_data():
        """Fetch data from the NASCAR API."""
        try:
            async with aiohttp.ClientSession() as session:  # Use aiohttp here
                with async_timeout.timeout(10):
                    response = await session.get(BASE_URL) # Use BASE_URL
                    raw_data = await response.json()
                    return raw_data  # Return the fetched JSON data
        except Exception as e:
            _LOGGER.error(f"Error fetching NASCAR data: {e}")
            raise  # Re-raise the exception so the coordinator knows the update failed

    async def determine_update_interval():
        """Determine the appropriate update interval."""
        try:
            data = await async_update_data()  # Fetch data to check race time
            race_time_str = data.get("time_of_day") # Example key, Adjust as needed
            if race_time_str:
                race_time = datetime.strptime(race_time_str, "%Y-%m-%dT%H:%M:%S%z") # Example format, Adjust as needed
                now = datetime.now(race_time.tzinfo) # Be timezone aware
                time_until_race = race_time - now

                if 0 <= time_until_race <= timedelta(minutes=15):
                    _LOGGER.debug("Switching to 5-second update interval.")
                    return timedelta(seconds=5)
                elif time_until_race < timedelta(0) and data.get("flag_state")!= "Finished": #Example finished state, adjust as needed
                    _LOGGER.debug("Race in progress, 5-second update interval")
                    return timedelta(seconds=5)
                else:
                    _LOGGER.debug("Using hourly update interval.")
                    return timedelta(hours=1)
            else:
                _LOGGER.warning("Race time not found in data. Using default interval.")
                return timedelta(minutes=DEFAULT_UPDATE_INTERVAL)

        except Exception as e:
            _LOGGER.error(f"Error determining update interval: {e}")
            return timedelta(minutes=DEFAULT_UPDATE_INTERVAL)  # Fallback


    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="nascar_data",
        update_method=async_update_data,
        update_interval=determine_update_interval,  # Use the function here
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setup(entry, "sensor")
    return True

#... (async_unload