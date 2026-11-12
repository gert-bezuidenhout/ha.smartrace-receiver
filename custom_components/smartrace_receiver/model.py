"""Run the established race reducer without Home Assistant dependencies.

The bundled template is application code, not a user-supplied template. Keeping
the reducer intact preserves the existing race, pit and warning semantics.
"""
from datetime import datetime
from jinja2 import StrictUndefined
from jinja2.nativetypes import NativeEnvironment
from .race_data import extend_model

class RaceModel:
    def __init__(self, source, state=None):
        env = NativeEnvironment(undefined=StrictUndefined)
        env.globals["as_timestamp"] = lambda value: (value if isinstance(value, datetime) else datetime.fromisoformat(value)).timestamp()
        self.template = env.from_string(source)
        self.state = state or {}

    def apply(self, data, received):
        if not isinstance(data, dict) or not isinstance(data.get("payload"), dict):
            raise ValueError("Expected a SmartRace event envelope with a payload mapping")
        result = self.template.render(trigger={"event": {"data": data, "time_fired": received}}, this={"attributes": {"data": self.state}})
        if not isinstance(result, dict):
            raise ValueError("Race model did not return a mapping")
        result = extend_model(self.state, result, data)
        self.state = result
        return result
