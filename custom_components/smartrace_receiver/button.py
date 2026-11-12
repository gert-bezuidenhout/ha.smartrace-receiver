"""Optional manual-event test buttons."""
from homeassistant.components.button import ButtonEntity
from .entity import DashboardEntity
from .const import DOMAIN

TEST_BUTTONS = (
    ("starting", "starting", "event.change_status", {"new": "starting"}, "mdi:flag"),
    ("running", "running", "event.change_status", {"new": "running"}, "mdi:flag"),
    ("prepare_for_start", "prepare_for_start", "event.change_status", {"new": "prepare_for_start"}, "mdi:flag"),
    ("ended", "ended", "event.change_status", {"new": "ended"}, "mdi:flag-checkered"),
    ("vsc_deployed", "VSC vsc_deployed", "race.vsc_deployed", {}, "mdi:car-emergency"),
    ("vsc_retracted", "VSC vsc_retracted", "race.vsc_retracted", {}, "mdi:car-emergency"),
    ("about_to_rain", "Weather about_to_rain", "events.weather_update", "about_to_rain", "mdi:weather-lightning"),
    ("wet", "Weather wet", "events.weather_change", "wet", "mdi:weather-lightning-rainy"),
    ("about_to_dry_up", "Weather about_to_dry_up", "events.weather_update", "about_to_dry_up", "mdi:weather-partly-lightning"),
    ("dry", "Weather dry", "events.weather_change", "dry", "mdi:weather-sunny"),
)

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([RaceTestButton(entry.runtime_data, entry, *definition) for definition in TEST_BUTTONS])

class RaceTestButton(DashboardEntity, ButtonEntity):
    platform_domain = "button"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator, entry, key, name, event_type, event_data, icon):
        super().__init__(coordinator, entry, "test_" + key, "Test: " + name)
        self.event_type = event_type
        self.event_data = event_data
        self._attr_icon = icon

    async def async_press(self):
        data = dict(self.event_data) if isinstance(self.event_data, dict) else self.event_data
        await self.hass.services.async_call(
            DOMAIN, "manual_update", {"event_type": self.event_type, "event_data": data},
            blocking=True, context=self._context,
        )
