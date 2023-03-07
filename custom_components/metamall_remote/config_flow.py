from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason='already_configured')

        if user_input is not None:
            res = requests.post('https://app.metamall.hk/api/register', json=data)
            if res.status_code == 200:
                return self.async_create_entry(title="configuration", data=res.json)
            else:
                return self.async_abort(reason='auth_failed')

        return self.async_show_form(
            step_id='user',
            data_schema=vol.Schema({
                vol.Required('code', 'Registration Code'): str
                vol.Required('hass_name', 'Box Name'): str
            })
        )
