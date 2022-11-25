from homeassistant import config_entries
import voluptuous as vol
from config.custom_components.metamall_remote.const import DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason='already_configured')

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id='user',
            data_schema=vol.Schema({
                # vol.Required('username', 'Username'): str,
                # vol.Required('password'): str,
                vol.Required('token'): str
            })
        )


    # async def async_login(self, data):
    #     res = requests.post('https://metamall.vatxx.com/api/login', json=data)
    #     if res.status_code == 200:
    #         pass