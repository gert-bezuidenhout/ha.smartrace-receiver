"""Race-feed health indicators."""
from datetime import datetime, timezone
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from .entity import DashboardEntity

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([RaceProblem(entry.runtime_data, entry, key, name) for key, name in [("data_stale", "Data stale"), ("missing_results", "Missing results"), ("lap_gaps", "Lap gaps")]])

class RaceProblem(DashboardEntity, BinarySensorEntity):
    platform_domain = "binary_sensor"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self):
        m = self.model
        now = datetime.now(timezone.utc).timestamp() * 1000
        if self.key == "data_stale":
            return m.get("status") == "running" and now - m.get("last_received", 0) > 30000
        if self.key == "missing_results":
            return m.get("status") == "ended" and not m.get("result") and now - m.get("ended_at", 0) > 10000
        return bool(m.get("lap_gaps"))
