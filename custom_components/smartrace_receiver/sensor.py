"""Live model and convenient automation sensors."""
from datetime import datetime, timezone
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from .entity import DashboardEntity
from .race_data import EXTRA_KEYS, sensor_value, sensor_attributes, controller_attributes, lookup

async def async_setup_entry(hass, entry, async_add_entities):
    entities = [RaceSensor(entry.runtime_data, entry, key, name) for key, name in [("race_live", "Race live"), ("status", "Status"), ("weather", "Weather"), ("target_laps", "Target laps"), ("last_received", "Last received")]]
    entities += [RaceSensor(entry.runtime_data, entry, f"controller_{cid}_{field}", f"Controller {cid} {field.replace(chr(95), chr(32))}", str(cid), field) for cid in range(1,9) for field in ("lap", "fuel", "car_name")]
    entities += [RaceSensor(entry.runtime_data, entry, key, key.replace("_", " ").capitalize()) for key in EXTRA_KEYS]
    entities += [RaceSensor(entry.runtime_data, entry, f"controller_{cid}", f"Controller {cid}", str(cid), "summary") for cid in range(1,9)]
    async_add_entities(entities)

class RaceSensor(DashboardEntity, SensorEntity):
    platform_domain = "sensor"
    # The large live model is restored separately; avoid recorder attribute churn.
    _unrecorded_attributes = frozenset({"data", "event_data", "readings"})

    def __init__(self, coordinator, entry, key, name, controller=None, field=None):
        super().__init__(coordinator, entry, key, name)
        self.controller, self.field = controller, field
        if key == "last_received":
            self._attr_device_class = SensorDeviceClass.TIMESTAMP
        if field == "fuel":
            self._attr_native_unit_of_measurement = "%"

    @property
    def native_value(self):
        m = self.model
        if self.controller and self.field in ("summary", "car_name"):
            group = "driver_data" if self.field == "summary" else "car_data"
            value = lookup(m, ("readings", self.controller, "event_data", group, "name"))
            return value[:255] if isinstance(value, str) and value else None
        if self.controller:
            return m.get("readings", {}).get(self.controller, {}).get(self.field)
        if self.key == "race_live":
            return str(m.get("last_received", "waiting"))
        if self.key == "last_received":
            stamp = m.get("last_received")
            return datetime.fromtimestamp(stamp / 1000, timezone.utc) if stamp else None
        return sensor_value(m, self.key)

    @property
    def extra_state_attributes(self):
        if self.key == "race_live":
            return {"data": self.model}
        if self.field == "summary":
            return controller_attributes(self.model, self.controller)
        return sensor_attributes(self.model, self.key)
