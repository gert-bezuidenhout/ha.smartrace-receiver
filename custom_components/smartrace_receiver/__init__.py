"""Receive SmartRace webhooks, maintain race sensors, and publish legacy events."""
from pathlib import Path
import logging
from datetime import timedelta
from types import SimpleNamespace
from aiohttp import web
from homeassistant.core import callback
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import ServiceValidationError
import voluptuous as vol
from homeassistant.components import webhook
from homeassistant.helpers.storage import Store
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util
from jinja2 import TemplateError
from .const import DOMAIN, EVENT_TYPE, PLATFORMS
from .model import RaceModel
from .payload import normalize

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    async def manual_update(call):
        entries = [entry for entry in hass.config_entries.async_entries(DOMAIN)
                   if entry.state == ConfigEntryState.LOADED]
        if len(entries) != 1:
            raise ServiceValidationError("Exactly one loaded SmartRace Receiver is required")
        coordinator = entries[0].runtime_data
        kind = call.data["event_type"]
        data = call.data["event_data"]
        if kind == "event.change_status":
            if not isinstance(data, dict) or data.get("new") not in ("ended", "prepare_for_start", "starting", "running"):
                raise ServiceValidationError("Choose prepare_for_start, starting, running or ended")
            data = {"old": coordinator.data.get("status", "unknown"), "new": data["new"]}
        elif kind in ("events.weather_update", "events.weather_change"):
            if data not in ("dry", "wet", "about_to_rain", "about_to_dry_up"):
                raise ServiceValidationError("Invalid weather value")
        elif not isinstance(data, dict) or data:
            raise ServiceValidationError("VSC event data must be an empty object")
        now = dt_util.utcnow()
        stamp = max(int(now.timestamp() * 1000), int(coordinator.data.get("last_source_time", 0)) + 1)
        envelope = normalize({"event_type": kind, "time": stamp, "event_data": data})
        envelope["source"] = "manual"
        if not coordinator.receive(SimpleNamespace(data=envelope, time_fired=now)):
            raise ServiceValidationError("Manual update could not be processed")
        hass.bus.async_fire(EVENT_TYPE, envelope, context=call.context)
    hass.services.async_register(DOMAIN, "manual_update", manual_update, schema=vol.Schema({
        vol.Required("event_type"): vol.In(["event.change_status", "events.weather_update", "events.weather_change", "race.vsc_deployed", "race.vsc_retracted"]),
        vol.Required("event_data"): vol.Any(dict, str),
    }))
    return True

class RaceCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, engine, store):
        super().__init__(hass, _LOGGER, name=DOMAIN, config_entry=entry)
        self.engine, self.store = engine, store
        self.rejected_events = 0
        self.async_set_updated_data(engine.state)

    @callback
    def receive(self, event):
        try:
            model = self.engine.apply(dict(event.data), event.time_fired)
        except (TemplateError, ValueError, TypeError, AttributeError, OverflowError):
            self.rejected_events += 1
            return False
        self.async_set_updated_data(model)
        self.store.async_delay_save(lambda: self.engine.state, 10)
        return True

    @callback
    def tick(self, now):
        self.async_update_listeners()

def make_handler(coordinator):
    async def handle(hass, webhook_id, request):
        try:
            envelope = normalize(await request.json())
        except (ValueError, TypeError, UnicodeError):
            coordinator.rejected_events += 1
            return web.Response(status=400, text="Invalid SmartRace JSON")
        if not coordinator.receive(SimpleNamespace(data=envelope, time_fired=dt_util.utcnow())):
            return web.Response(status=400, text="Invalid SmartRace event")
        # Process only here. Do not also listen to this event, which would duplicate data.
        hass.bus.async_fire(EVENT_TYPE, envelope)
        return web.Response(status=200, text="OK")
    return handle

async def async_setup_entry(hass, entry):
    # Remove only obsolete driver-name entities owned by this config entry.
    registry = er.async_get(hass)
    for old_key, new_key in (("prepare_race", "prepare_for_start"), ("end_race", "ended")):
        old_id = registry.async_get_entity_id("button", DOMAIN, f"{entry.entry_id}_test_{old_key}")
        registered = registry.async_get(old_id) if old_id else None
        if registered and registered.config_entry_id == entry.entry_id:
            new_id = f"button.smartrace_receiver_test_{new_key}"
            changes = {"new_unique_id": f"{entry.entry_id}_test_{new_key}"}
            if old_id == f"button.smartrace_receiver_test_{old_key}" and not registry.async_get(new_id):
                changes["new_entity_id"] = new_id
            registry.async_update_entity(old_id, **changes)
    for cid in range(1, 9):
        entity_id = registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_controller_{cid}_driver_name")
        registered = registry.async_get(entity_id) if entity_id else None
        if registered and registered.config_entry_id == entry.entry_id:
            registry.async_remove(entity_id)
    store = Store(hass, 1, f"{DOMAIN}.{entry.entry_id}")
    restored = await store.async_load()
    source = await hass.async_add_executor_job((Path(__file__).parent / "race_model.jinja").read_text, "utf-8")
    engine = await hass.async_add_executor_job(RaceModel, source, restored if isinstance(restored, dict) else {})
    coordinator = RaceCoordinator(hass, entry, engine, store)
    entry.runtime_data = coordinator
    hook = entry.data["webhook_id"]
    webhook.async_register(hass, DOMAIN, "SmartRace Receiver", hook, make_handler(coordinator), local_only=entry.options.get("local_only", entry.data.get("local_only", True)), allowed_methods=["POST"])
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        webhook.async_unregister(hass, hook)
        raise
    entry.async_on_unload(lambda: webhook.async_unregister(hass, hook))
    entry.async_on_unload(async_track_time_interval(hass, coordinator.tick, timedelta(seconds=5)))
    entry.async_on_unload(entry.add_update_listener(async_options_updated))
    return True

async def async_options_updated(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    webhook.async_unregister(hass, entry.data["webhook_id"])
    await entry.runtime_data.store.async_save(entry.runtime_data.engine.state)
    return True

async def async_remove_entry(hass, entry):
    await Store(hass, 1, f"{DOMAIN}.{entry.entry_id}").async_remove()
