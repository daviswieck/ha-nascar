"""Config flow for ha_nascar integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class haNascarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ha_nascar."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # User confirmed, create the config entry
            return self.async_create_entry(
                title=DOMAIN, data={}
            )

        return self.async_show_form(
            step_id="user",
            errors=errors,
        )
