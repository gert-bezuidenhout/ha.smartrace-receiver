"""Generate and display a dedicated local webhook."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.components import webhook
from homeassistant.helpers.network import NoURLAvailableError
from .const import DOMAIN


def url_details(hass, webhook_id, local_only=True):
    try:
        url = webhook.async_generate_url(hass, webhook_id, allow_internal=True,
            allow_external=not local_only, prefer_external=False)
    except NoURLAvailableError:
        return {"webhook_url": "Address unavailable", "url_note":
            "Set your Home Assistant local URL under Settings → System → Network, then reopen this dialog. Your webhook ID will remain unchanged."}
    return {"webhook_url": url, "url_note":
        "Copy the complete URL above into SmartRace. It already includes your Home Assistant address, port and webhook ID."}

def schema(local_only=True):
    return vol.Schema({vol.Required("local_only", default=local_only): bool})

class ReceiverConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if not hasattr(self, "webhook_id"):
            self.webhook_id = webhook.async_generate_id()
        if user_input is not None:
            return self.async_create_entry(title="SmartRace Receiver", data={"webhook_id": self.webhook_id, "local_only": user_input["local_only"]})
        return self.async_show_form(step_id="user", data_schema=schema(), description_placeholders=url_details(self.hass, self.webhook_id))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ReceiverOptionsFlow()

class ReceiverOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        entry = self.config_entry
        return self.async_show_form(step_id="init", data_schema=schema(entry.options.get("local_only", entry.data.get("local_only", True))), description_placeholders=url_details(self.hass, entry.data["webhook_id"], entry.options.get("local_only", entry.data.get("local_only", True))))
