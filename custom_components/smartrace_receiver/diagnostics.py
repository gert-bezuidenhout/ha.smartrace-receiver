"""Report counters only; omit driver names, car metadata and captured payloads."""
async def async_get_config_entry_diagnostics(hass, entry):
    c = entry.runtime_data
    m = c.data or {}
    return {"version": "1.1.0", "status": m.get("status"), "received_events": m.get("received_count", 0), "rejected_events": c.rejected_events, "active_controllers": sorted(m.get("readings", {})), "has_results": bool(m.get("result")), "lap_gap_count": len(m.get("lap_gaps", []))}
