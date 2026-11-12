"""Normalize raw SmartRace JSON and the established receiver envelope."""
import math

def normalize(body):
    if not isinstance(body, dict):
        raise ValueError("JSON object required")
    payload = body.get("payload", body)
    if not isinstance(payload, dict):
        raise ValueError("Payload object required")
    kind = payload.get("event_type", body.get("event_type"))
    if not isinstance(kind, str) or not kind or len(kind) > 128:
        raise ValueError("Event type required")
    if "event_data" not in payload:
        raise ValueError("Event data required")
    stamp = payload.get("time")
    if isinstance(stamp, bool) or not isinstance(stamp, (int, float)) or not math.isfinite(stamp) or stamp < 0:
        raise ValueError("Producer time must be milliseconds")
    # Copy rather than modifying the request. Keep event-specific metadata intact.
    return {"event_type": kind, "payload": dict(payload, event_type=kind)}
