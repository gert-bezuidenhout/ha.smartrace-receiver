# Repository files

Only `custom_components/smartrace_receiver/` is installed as integration runtime code. The remaining files support installation, documentation and development.

| File or folder | Purpose |
| --- | --- |
| `custom_components/smartrace_receiver/` | Integration implementation loaded by Home Assistant. |
| `manifest.json` inside that folder | Integration identity, version, dependencies and support links. |
| `__init__.py` | Setup, reload and shutdown lifecycle. |
| `config_flow.py` | Setup/settings forms in Home Assistant. |
| `sensor.py`, `binary_sensor.py`, `button.py` | Sensors, diagnostic/connection indicators and buttons. |
| `strings.json`, `translations/en.json` | User-facing form text. |
| `brand/` | Integration icon and logo. |
| `hacs.json` | HACS repository metadata. |
| `README.md` | Installation, features and troubleshooting. |
| `MIGRATION.md` | Guidance for users upgrading older setups; unnecessary for fresh installations. |
| `LICENSE` | MIT licence for the project code. |
| `.gitignore` | Keeps local caches, logs and secrets out of future commits. |
| `.github/workflows/validate.yaml` | Automated HACS and Hassfest checks. |
| `docs/HACS_SUBMISSION.md` | Maintainer checklist for later Marketplace submission. |
| `const.py`, `entity.py` | Shared definitions and entity behaviour. |
| `model.py`, `payload.py`, `race_data.py`, `race_model.jinja` | Event processing, stored race model and sensor values. The Jinja file is internal implementation, not a template users must install. |
| `diagnostics.py` | Redacted diagnostic download. |
| `services.yaml` | Description of the manual update action. |
| `sensor-mapping.json` | Legacy-to-native sensor reference; not a configuration file to copy. |

