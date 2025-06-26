import logging
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DRIVER_NUMBER = "driver_number"

class NascarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the NASCAR integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the user enters a driver number."""
        errors = {}

        if user_input is not None:
            driver_number = user_input.get(DRIVER_NUMBER, "").strip()

            if not driver_number.isdigit():
                errors[DRIVER_NUMBER] = "invalid_number"

            if not errors:
                _LOGGER.debug(f"Creating entry for NASCAR driver {driver_number}")
                return self.async_create_entry(
                    title=f"NASCAR Driver {driver_number}",
                    data={DRIVER_NUMBER: driver_number},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(DRIVER_NUMBER): str
            }),
            errors=errors,
        )
