"""Native sensor projections and bounded event snapshots, independent of HA."""
from datetime import datetime, timezone

EVENT_GROUPS = {
    "lap_event_type": ("ui.lap_update",),
    "event_event_type": ("event.start", "event.end", "event.change_status"),
    "weather_event_type": ("events.weather_update", "events.weather_change"),
    "vsc_event_type": ("race.vsc_deployed", "race.vsc_retracted"),
    "penalty_event_type": ("race.penalty_update",),
    "damage_event_type": ("race.damage_update",),
    "fuel_event_type": ("util.fuel_update",),
    "pitstops_event_type": ("events.tire_change", "event.pit.enter", "event.pit.leave"),
    "miscellaneous_event_type": ("util.set_active_track", "ui.reset", "ui.remove_car_from_session", "cu.send_esc_command"),
    "sector_event_type": ("ui.sector_for_car",),
}
LAP_FIELDS = {
    "lap": ("lap",), "lap_driver_name": ("driver_data", "name"),
    "lap_car_name": ("car_data", "name"), "lap_car_laps": ("car_data", "laps"),
    "lap_controller_id": ("controller_id",), "lap_time": ("laptime",),
    "lap_sector_1": ("sector_1",), "lap_sector_2": ("sector_2",),
    "lap_sector_3": ("sector_3",),
}
EXTRA_KEYS = tuple(EVENT_GROUPS) + tuple(LAP_FIELDS) + (
    "event_old", "event_new", "event", "weather_state", "vsc_status",
    "fuel_levels", "damage_levels", "pit_levels", "race_results",
)

def extend_model(old, model, envelope):
    """Keep event details only when the existing reducer accepted their timestamp.

    Snapshots are bounded by the fixed event groups, not an accumulating event log.
    All extension data resets with the race; weather_state also resets at the end.
    """
    p = envelope["payload"]
    kind = envelope.get("event_type", p.get("event_type"))
    raw = p.get("event_data")
    d = raw if isinstance(raw, dict) else {}
    key = f"{kind}:{d.get('controller_id', '')}"
    before = old.get("event_times", {}).get(key, 0)
    after = model.get("event_times", {}).get(key, 0)
    if after <= before:
        return model
    snapshots = dict(model.get("event_snapshots", {}))
    for group, types in EVENT_GROUPS.items():
        if kind in types:
            snapshots[group] = {"time": p.get("time"), "event_type": kind,
                                "event_data": raw, "event_id": d.get("event_id", p.get("event_id"))}
    model["event_snapshots"] = snapshots
    if kind == "event.change_status":
        model["event_old"] = d.get("old")
        model["event_new"] = d.get("new")
    if kind in EVENT_GROUPS["weather_event_type"] and raw in ("dry", "wet", "about_to_rain", "about_to_dry_up"):
        model["weather_state"] = raw
    if kind == "event.end" or (kind == "event.change_status" and d.get("new") in ("ended", "prepare_for_start")):
        model["weather_state"] = "dry"
    if kind == "race.vsc_deployed":
        model["vsc_status"] = "deployed"
    elif kind == "race.vsc_retracted":
        model["vsc_status"] = "retracted"
    return model

def lookup(value, path):
    for part in path:
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value

def sensor_value(model, key):
    if key in EVENT_GROUPS:
        return model.get("event_snapshots", {}).get(key, {}).get("event_type")
    if key in LAP_FIELDS:
        return lookup(model.get("event_snapshots", {}).get("lap_event_type", {}).get("event_data"), LAP_FIELDS[key])
    if key == "event":
        return model.get("status")
    if key == "weather_state":
        return model.get("weather_state", "dry" if model.get("status") == "ended" else model.get("weather"))
    if key == "race_results":
        return "event.end" if model.get("result") else "waiting"
    if key in ("fuel_levels", "damage_levels", "pit_levels"):
        return str(model.get("last_received", 0))
    return model.get(key)

def sensor_attributes(model, key):
    if key in EVENT_GROUPS:
        return model.get("event_snapshots", {}).get(key, {})
    if key == "race_results":
        return {"event_type": "event.end" if model.get("result") else "race.reset",
                "time": model.get("result_time", 0), "event_id": model.get("event_id"),
                "event_data": {"type": "race", "result": model.get("result", {})},
                "reset_time": model.get("reset_time", 0)}
    readings = model.get("readings", {})
    if key in ("fuel_levels", "damage_levels", "pit_levels"):
        out = {}
        for cid, r in readings.items():
            if key == "fuel_levels" and "fuel" in r:
                out[cid] = {"fuel": r["fuel"], "time": r.get("fuel_time")}
            elif key == "damage_levels" and "damage" in r:
                data = r.get("event_data", {})
                out[cid] = {"damage": r["damage"], "time": r.get("damage_time"),
                    "event_id": data.get("event_id"), "driver_id": lookup(data, ("driver_data", "id")),
                    "car_id": lookup(data, ("car_data", "id"))}
            elif key == "pit_levels":
                out[cid] = {"in_pit": r.get("in_pit", False), "tire": r.get("tire", "dry"),
                           "time": max(r.get("pit_time", 0), r.get("tire_time", 0))}
        return {"readings": out, "reset_time": model.get("reset_time", 0)}
    return None

def controller_attributes(model, cid):
    r = model.get("readings", {}).get(cid, {})
    reset = model.get("reset_time", 0)
    stamp = r.get("event_time", 0)
    def iso(ms):
        return datetime.fromtimestamp(ms / 1000, timezone.utc).isoformat() if ms else None
    return {"controller_id": cid, "race_reset_time": reset,
            "race_prepared_at": iso(reset), "event_type": "ui.lap_update" if r.get("lap", 0) else "race.reset",
            "event_id": model.get("event_id"), "event_time": stamp or None,
            "best_laptime_raw": r.get("best_laptime_raw"), "event_time_readable": iso(stamp),
            "event_data": r.get("event_data", {})}
