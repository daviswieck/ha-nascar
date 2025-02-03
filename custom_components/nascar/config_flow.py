import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL  # Import DOMAIN

class NASCARSensorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # Use the DOMAIN constant
    """Config flow for NASCAR Live Feed sensor."""

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        if user_input is not None:
            return self.async_create_entry(
                title="NASCAR Live Feed",  # Or make it dynamic, e.g., from API data
                data=user_input,  # Store any initial config data here if needed
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),  # Initial form is empty (for now)
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return NASCARSensorOptionsFlowHandler(config_entry)


class NASCARSensorOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle the options flow for the NASCAR sensor."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options for the integration."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "update_interval",
                    default=self.config_entry.options.get(
                        "update_interval", DEFAULT_UPDATE_INTERVAL
                    ),
                ): int,
            }),
        )