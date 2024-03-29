from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN
import requests
from datetime import timedelta

import logging

logger = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            return await self.async_register_hass(user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("code", description="Registration Code"): str,
                    vol.Required("hass_name", description="Hass Name"): str,
                }
            ),
        )

    async def async_register_hass(self, user_input):
        users = await self.hass.auth.async_get_users()

        refresh_token = await self.hass.auth.async_create_refresh_token(
            user=users[0],
            client_name="metamall",
            token_type="system",
            access_token_expiration=timedelta(days=36500),
        )

        access_token = self.hass.auth.async_create_access_token(refresh_token)
        if access_token is None or access_token == "":
            return self.async_abort(reason="generate_token_failed")

        user_input["access_token"] = access_token

        res = await self.hass.async_add_executor_job(self.register, user_input)
        if res.status_code == 200:
            return self.async_create_entry(title="Remote", data=res.json())
        else:
            return self.async_abort(reason="auth_failed")

    def register(self, data):
        return requests.post(
            "https://app.metamall.hk/api/hass/register",
            json=data,
            headers={"Accept": "application/json"},
        )
