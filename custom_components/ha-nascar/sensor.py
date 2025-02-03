import logging
import asyncio
import aiohttp
import datetime
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

URL = "https://cf.nascar.com/live/feeds/live-feed.json"

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = NASCARDataUpdateCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([NASCARSensor(coordinator)], True)

class NASCARDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass):
        self.hass = hass
        super().__init__(
            hass,
            _LOGGER,
            name="NASCAR Data",
            update_interval=datetime.timedelta(hours=1),
        )

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(URL) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Error fetching data: {response.status}")
                    data = await response.json()
                    
                    # Extract race start time
                    race_start = data.get("time_of_day_os")
                    if race_start:
                        race_start_dt = datetime.datetime.fromisoformat(race_start)
                        now = datetime.datetime.now().astimezone()
                        time_to_race = (race_start_dt - now).total_seconds()
                        
                        # Adjust polling interval
                        if time_to_race > 3600:
                            self.update_interval = datetime.timedelta(hours=1)
                        elif 0 < time_to_race <= 3600:
                            self.update_interval = datetime.timedelta(minutes=10)
                        else:
                            self.update_interval = datetime.timedelta(seconds=5)

                        _LOGGER.debug(f"Polling interval adjusted: {self.update_interval}")

                    return data
        except Exception as err:
            raise UpdateFailed(f"Update failed: {err}")

class NASCARSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "NASCAR Live Data"
        self._attr_unique_id = "nascar_live_data"

    @property
    def extra_state_attributes(self):
        return self.coordinator.data if self.coordinator.data else {}

    @property
    def state(self):
        return self.coordinator.data.get("flag_state", "Unknown")

    async def async_update(self):
        await self.coordinator.async_request_refresh()
