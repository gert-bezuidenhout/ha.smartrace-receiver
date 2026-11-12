# Legacy template migration

These are new native entities, not aliases that silently take ownership of old template IDs. Existing receiver IDs are preserved. Confirm the actual IDs in Home Assistant if you previously renamed entities.

| Old template sensor | New native entity |
| --- | --- |
| `sensor.smartrace_lap_event_type` | `sensor.smartrace_receiver_lap_event_type` |
| `sensor.smartrace_lap` | `sensor.smartrace_receiver_lap` |
| `sensor.smartrace_lap_driver_name` | `sensor.smartrace_receiver_lap_driver_name` |
| `sensor.smartrace_lap_car_name` | `sensor.smartrace_receiver_lap_car_name` |
| `sensor.smartrace_lap_car_laps` | `sensor.smartrace_receiver_lap_car_laps` |
| `sensor.smartrace_lap_controller_id` | `sensor.smartrace_receiver_lap_controller_id` |
| `sensor.smartrace_lap_time` | `sensor.smartrace_receiver_lap_time` |
| `sensor.smartrace_lap_sector_1` | `sensor.smartrace_receiver_lap_sector_1` |
| `sensor.smartrace_lap_sector_2` | `sensor.smartrace_receiver_lap_sector_2` |
| `sensor.smartrace_lap_sector_3` | `sensor.smartrace_receiver_lap_sector_3` |
| `sensor.smartrace_event_event_type` | `sensor.smartrace_receiver_event_event_type` |
| `sensor.smartrace_event_old` | `sensor.smartrace_receiver_event_old` |
| `sensor.smartrace_event_new` | `sensor.smartrace_receiver_event_new` |
| `sensor.smartrace_weather_event_type` | `sensor.smartrace_receiver_weather_event_type` |
| `sensor.smartrace_weather_state` | `sensor.smartrace_receiver_weather_state` |
| `sensor.smartrace_vsc_event_type` | `sensor.smartrace_receiver_vsc_event_type` |
| `sensor.smartrace_penalty_event_type` | `sensor.smartrace_receiver_penalty_event_type` |
| `sensor.smartrace_damage_event_type` | `sensor.smartrace_receiver_damage_event_type` |
| `sensor.smartrace_fuel_event_type` | `sensor.smartrace_receiver_fuel_event_type` |
| `sensor.smartrace_pitstops_event_type` | `sensor.smartrace_receiver_pitstops_event_type` |
| `sensor.smartrace_miscellaneous_event_type` | `sensor.smartrace_receiver_miscellaneous_event_type` |
| `sensor.smartrace_controller_1` | `sensor.smartrace_receiver_controller_1` |
| `sensor.smartrace_controller_2` | `sensor.smartrace_receiver_controller_2` |
| `sensor.smartrace_controller_3` | `sensor.smartrace_receiver_controller_3` |
| `sensor.smartrace_controller_4` | `sensor.smartrace_receiver_controller_4` |
| `sensor.smartrace_controller_5` | `sensor.smartrace_receiver_controller_5` |
| `sensor.smartrace_controller_6` | `sensor.smartrace_receiver_controller_6` |
| `sensor.smartrace_controller_7` | `sensor.smartrace_receiver_controller_7` |
| `sensor.smartrace_controller_8` | `sensor.smartrace_receiver_controller_8` |
| `sensor.smartrace_fuel_levels` | `sensor.smartrace_receiver_fuel_levels` |
| `sensor.smartrace_damage_levels` | `sensor.smartrace_receiver_damage_levels` |
| `sensor.smartrace_pit_levels` | `sensor.smartrace_receiver_pit_levels` |
| `sensor.smartrace_race_results` | `sensor.smartrace_receiver_race_results` |

The integration also provides `sensor.smartrace_receiver_event` as a status alias, and `sensor.smartrace_receiver_vsc_status` with deployed/retracted values.

For the newer race-model template package, point `sensor.smartrace_race_live` consumers to `sensor.smartrace_receiver_race_live`, effective-status consumers to `sensor.smartrace_receiver_status`, and effective-weather consumers to `sensor.smartrace_receiver_weather`. The `data` model remains compatible. Use the native last-received sensor for a timestamp.

Do not delete legacy templates until their consumers are migrated. No receiver template YAML is required on a fresh install.
