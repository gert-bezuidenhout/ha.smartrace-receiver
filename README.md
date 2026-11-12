# SmartRace Receiver 1.1.5

SmartRace Receiver by Gert Bezuidenhout is a self-contained Home Assistant integration for race data. No webhook automation, template-sensor YAML, helpers or scripts are required for receiving and processing the data. The dashboard and SmartRace Connect remain separate.

## New installation

1. Copy the single `custom_components/smartrace_receiver` folder into `/config/custom_components/` and restart Home Assistant.
2. Open Settings → Devices & services → Add integration → SmartRace Receiver.
3. Copy the complete webhook URL shown in the setup dialog into SmartRace and submit the form. Keep local-network-only enabled for a phone on your home network.
4. Run a short race. The integration automatically creates its sensors and retains their data across restarts.

That is the entire receiver setup. Do not install the old receiver automation or any of the old SmartRace template files for a new installation.

This release is distributed as a ZIP, so copying the integration folder is still necessary. It is not yet published through HACS. A future repository/release can simplify installation and updates; no HACS repository URL has been created or assumed here.

## Upgrade your current receiver

Replace `/config/custom_components/smartrace_receiver` with the folder from this archive, then restart Home Assistant. Keep the existing integration entry. Its webhook ID, existing receiver entity IDs and saved race state are retained. Additional sensors appear automatically. Event-detail sensors receive their first values as new events arrive; old snapshots cannot be reconstructed from data that was never saved.

No dashboard package update is required if it already reads `sensor.smartrace_receiver_race_live`.

## Native sensors

The integration now supplies 65 sensors and 3 diagnostic binary sensors:

- Existing live race model, status, weather, target laps and last-received timestamp.
- Individual lap and fuel values for controllers 1–8.
- Controller 1–8 summary sensors with driver/car identity, crossing time and best-lap attributes.
- Latest lap details: driver, car, car laps, controller, time and sectors 1–3.
- Lap, race, weather, VSC, penalty, damage, fuel, pit/tyre, miscellaneous and sector event details.
- Previous/new status and a race-status alias.
- VSC status and a weather-state sensor that resets to dry when a race ends.
- Combined fuel, damage and pit readings, and official race results.
- Data-stale, missing-results and lap-gap indicators.

All 33 sensor definitions in the pasted legacy template file have native counterparts. See MIGRATION.md for their IDs. The receiver no longer requires that file. Some additional fields are held in sensor attributes, just as in the templates.

`weather` preserves the race model's last weather value. `weather_state` reproduces the separate dry-at-race-end behaviour. Event details are bounded snapshots of the latest accepted event in each category, not a growing log. They clear when a new race resets the model; stale/out-of-order events do not replace them. Controller summary readable timestamps use UTC ISO format. Early identity can appear before a completed lap.

## One-time cleanup of an existing YAML installation

The old templates may still be used by your own automations even though the receiver does not need them. They are not silently deleted or edited by this update.

1. Keep the old receiver automation disabled and ensure SmartRace uses the integration's URL.
2. Verify the new sensors during a short race.
3. Switch any consumers of old sensor IDs to the new IDs listed in MIGRATION.md. Automations built in the Home Assistant editor can be changed there. Existing handwritten YAML consumers require a one-time edit.
4. Remove the old SmartRace template definitions/include only when those consumers have been migrated. Do not remove unrelated template entries.

Fresh installations do not have this cleanup step. Existing old templates can remain temporarily: the receiver still publishes `smartrace_data_received` for recorders and automations. Publishing that event does not mean the receiver depends on those templates.

## Scope

Included: webhook reception, race-data processing, automatic entities, persistence and diagnostics.

Separate: dashboard cards/images, track lights, sound effects, custom notifications, recording scripts and SmartRace Connect race-control commands. These are not installed by this receiver.

## Behaviour and limits

Actual sector durations are supplied by the captured lap-update events, not the captured sector-crossing events. Sector indicators and metadata update earlier; the receiver does not invent durations. Inactive controllers may remain Unknown. Final results and detailed driver/car data remain available in the live sensor's `data` attribute.

The webhook accepts JSON POST requests and uses a generated secret URL. The Configure dialog shows the complete URL again. The established event envelope is still published for existing consumers. Events missed while Home Assistant is offline cannot be recovered. Saved race state includes driver/car metadata; diagnostics omit payloads and the webhook secret.

## Validation

Replayed 3,455 events from four recorded sessions. Existing race-model fields matched 1.0.4 throughout. Every native sensor's state and attributes were checked on every event, and all 33 legacy sensor definitions were checked for native coverage. Additional checks cover VSC, penalties, stale updates, weather-at-end, reset and restoration. Python/JSON syntax checks passed.

Home Assistant itself is not installed in the test environment. Entity checks used minimal API substitutes; live entity registration and UI verification still need checking after installation. This is a custom integration release, not an official Home Assistant integration.

## Controller names
Main controller sensors now show the driver's name, with existing detailed attributes retained. Separate car-name, lap and fuel sensors remain. Missing driver names show unknown, including after a race reset until identity arrives.
The eight redundant driver_name entities from v1.1.1 are removed automatically from this integration's entity registry entries on setup. Controller IDs and unique IDs are preserved. Any custom automation that read the main controller state as a lap count must use controller_N_lap instead.
Upgrade: replace custom_components/smartrace_receiver and restart Home Assistant. Keep the existing integration entry and webhook URL.

Manual scripts: use smartrace_receiver.manual_update to update receiver data and publish one marked manual event. No command is sent to SmartRace.

## Optional test buttons
Ten Test buttons are registered on the Receiver device and disabled by default: prepare_for_start, starting, running, ended, VSC deployed/retracted, About to rain, Wet, About to dry up, and Dry.
After replacing the integration folder and restarting Home Assistant, open Settings > Devices & services > Entities, filter by SmartRace Receiver and disabled entities, and enable the buttons you want. They can then be pressed from the device page or added to a dashboard. Keep your existing integration entry and webhook URL.
Buttons use the same manual_update action as the scripts. They update Home Assistant only, can trigger lighting/sound automations, and are recorded with source: manual. Prepare race clears current readings. End race does not fabricate results and may activate Missing results.
The eight equivalent event scripts are optional once you use buttons. Keep scripts if existing dashboard controls or automations call them. Light and Car Approaching scripts are not replaced.

Version 1.1.5 migrates default button IDs test_prepare_race to test_prepare_for_start and test_end_race to test_ended while retaining enabled settings. User-customized IDs are preserved. Update any external references to renamed IDs.
