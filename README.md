# Medisafe

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

View your medication from [Medisafe Cloud](https://www.medisafe.com/) in [Home Assistant](https://www.home-assistant.io/).  
This integration adds sensors for today's upcoming, taken, skipped, and missed doses, plus sensors for each medication's remaining pills.

![example][exampleimg]

## Installation

### Install with HACS (recommended)
1. Add `https://github.com/c99koder/ha-medisafe` as a custom repository as Type: `Integration`
2. Click install under "Medisafe" in the Integration tab
3. Restart Home Assistant
4. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Medisafe"

### Install manually
1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `medisafe`.
4. Download _all_ the files from the `custom_components/medisafe/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Medisafe"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/medisafe/sensor.py
custom_components/medisafe/__init__.py
custom_components/medisafe/api.py
custom_components/medisafe/manifest.json
custom_components/medisafe/translations
custom_components/medisafe/translations/en.json
custom_components/medisafe/const.py
custom_components/medisafe/config_flow.py
```

## Configuration is done in the UI

Data is updated every 15 minutes, which can be adjusted by changing `SCAN_INTERVAL` in `__init__.py`.

The sample card above was built using [template-entity-row](https://github.com/thomasloven/lovelace-template-entity-row) and [auto-entities](https://github.com/thomasloven/lovelace-auto-entities):

```yaml
type: horizontal-stack
cards:
  - type: entity
    entity: sensor.medication_taken
    name: Taken
  - type: entity
    entity: sensor.medication_missed
    name: Missed
  - type: entity
    entity: sensor.medication_dismissed
    name: Skipped
```

```yaml
type: custom:auto-entities
filter:
  include:
    - attributes:
        integration: medisafe
      options:
        type: custom:template-entity-row
        state: "{{ states(config.entity) }} {{ state_attr(config.entity, 'unit_of_measurement') }}"
        secondary: "{{ state_attr(config.entity, 'dose') }}"
  exclude:
    - entity_id: sensor.medication_*
sort:
  method: state
  numeric: true
card:
  type: entities
  title: Remaining Medication
```

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Credits

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template

## License

Copyright (C) 2022 Sam Steele. Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/c99koder/ha-medisafe.svg?style=for-the-badge
[commits]: https://github.com/c99koder/ha-medisafe/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[exampleimg]: example.png
[license-shield]: https://img.shields.io/github/license/c99koder/ha-medisafe.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40c99koder-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/c99koder/ha-medisafe.svg?style=for-the-badge
[releases]: https://github.com/c99koder/ha-medisafe/releases
[user_profile]: https://github.com/c99koder
