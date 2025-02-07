import logging
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class NascarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NASCAR integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the user enters a driver number."""
        errors = {}

        if user_input is not None:
            driver_number = user_input["driver_number"]
            
            # Validate driver number (must be numeric)
            if not driver_number.isdigit():
                errors["driver_number"] = "invalid_number"

            if not errors:
                return self.async_create_entry(
                    title=f"NASCAR Driver {driver_number}",
                    data={"driver_number": driver_number},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("driver_number"): str}),
            errors=errors,
        )
