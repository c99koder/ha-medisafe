[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

View your medication from [Medisafe Cloud](https://www.medisafe.com/) in Home Assistant.  
This integration adds sensors for today's upcoming, taken, skipped, and missed doses, plus sensors for each medication's remaining pills.

![example][exampleimg]

{% if not installed %}

## Installation

1. Click install.
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Medisafe".

{% endif %}

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

## Credits

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[commits-shield]: https://img.shields.io/github/commit-activity/y/c99koder/ha-medisafe.svg?style=for-the-badge
[commits]: https://github.com/c99koder/ha-medisafe/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[exampleimg]: example.png
[license]: https://github.com/c99koder/ha-medisafe/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/c99koder/ha-medisafe.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40c99koder-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/c99koder/ha-medisafe.svg?style=for-the-badge
[releases]: https://github.com/c99koder/ha-medisafe/releases
[user_profile]: https://github.com/c99koder
