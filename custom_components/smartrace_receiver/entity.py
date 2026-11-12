"""Shared entity identity."""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN

class DashboardEntity(CoordinatorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator, entry, key, name):
        super().__init__(coordinator)
        self.key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self.entity_id = f"{self.platform_domain}.smartrace_receiver_{key}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name="SmartRace Receiver", manufacturer="Gert Bezuidenhout", model="SmartRace Receiver", sw_version="1.1.5")

    @property
    def model(self):
        return self.coordinator.data or {}
