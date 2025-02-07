import logging
from datetime import timedelta, datetime
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import aiohttp
import async_timeout

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL, BASE_URL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the NASCAR sensor from a config entry."""

    async def async_update_data():
        """Fetch data from the NASCAR API."""
        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    response = await session.get(BASE_URL)
                    raw_data = await response.json()
                    return raw_data
        except Exception as e:
            _LOGGER.error(f"Error fetching NASCAR data: {e}")
            raise UpdateFailed(f"Error fetching NASCAR data: {e}")

    async def determine_update_interval():
        """Determine the appropriate update interval dynamically."""
        try:
            data = await async_update_data()
            race_time_str = data.get("time_of_day_os")
            
            if race_time_str:
                try:
                    race_time = datetime.fromisoformat(race_time_str.replace("Z", "+00:00"))
                    now = datetime.now(race_time.tzinfo)
                    time_until_race = race_time - now

                    if 0 <= time_until_race.total_seconds() <= 900:  # 15 minutes
                        _LOGGER.debug("Switching to 5-second update interval.")
                        return timedelta(seconds=5)
                    elif time_until_race.total_seconds() < 0 and data.get("flag_state") != "Finished":
                        _LOGGER.debug("Race in progress, 5-second update interval.")
                        return timedelta(seconds=5)
                    else:
                        _LOGGER.debug("Using hourly update interval.")
                        return timedelta(hours=1)

                except ValueError as e:
                    _LOGGER.error(f"Error parsing race time: {e}. Raw string: {race_time_str}")
                    return timedelta(minutes=DEFAULT_UPDATE_INTERVAL)

            _LOGGER.warning("Race time not found in data. Using default interval.")
            return timedelta(minutes=DEFAULT_UPDATE_INTERVAL)

        except Exception as e:
            _LOGGER.error(f"Error determining update interval: {e}")
            return timedelta(minutes=DEFAULT_UPDATE_INTERVAL)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="nascar_data",
        update_method=async_update_data,
        update_interval=timedelta(minutes=DEFAULT_UPDATE_INTERVAL),  # Default update interval
    )

    async def update_interval_task():
        """Update the polling interval dynamically."""
        while True:
            new_interval = await determine_update_interval()
            if new_interval != coordinator.update_interval:
                _LOGGER.info(f"Updating polling interval to {new_interval}")
                coordinator.update_interval = new_interval
            await hass.async_add_executor_job(lambda: None)  # Sleep between interval updates
            await hass.async_create_task(hass.async_sleep(60))  # Check every 60 seconds

    hass.loop.create_task(update_interval_task())  # Start dynamic interval updates

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    return True
