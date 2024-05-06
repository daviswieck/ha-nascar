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
        if self._async_current_entries():
            # If there's already an entry, no need to configure again
            return self.async_abort(reason="single_instance_allowed")

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={"domain": DOMAIN},
        )

    async def async_step_confirm(self, user_input=None):
        """Handle user confirmation."""
        if user_input is not None:
            # User confirmed, create the config entry
            return self.async_create_entry(
                title=DOMAIN, data={}
            )

        # User did not confirm, show confirmation form again
        return self.async_show_form(
            step_id="confirm",
            description_placeholders={"domain": DOMAIN},
        )
