#  Copyright (C) 2024 Sam Steele
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import logging

from datetime import date

from homeassistant.components.sensor import SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .const import CONF_USERNAME
from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    coordinator = entry.runtime_data.coordinator
    await coordinator.async_config_entry_first_refresh()

    entities = []

    if coordinator.data is not None and "medications" in coordinator.data:
        _LOGGER.info(f"Got {len(coordinator.data['medications'])} medications")
        for ent in coordinator.data["medications"]:
            if "pillsLeft" not in ent:
                _LOGGER.debug(f"Missing pillsLeft: {ent['name']} with UUID {ent['uuid']}")
            elif ent["treatmentStatus"] != 1:
                _LOGGER.debug(f"Inactive medication: {ent['name']} with UUID {ent['uuid']}")
            else:
                _LOGGER.debug(f"Adding: {ent['name']} with UUID {ent['uuid']}")
                entities.append(MedisafeMedicationEntity(coordinator, entry, ent["uuid"]))

    entities.append(MedisafeStatusCountEntity(coordinator, entry, "taken"))
    entities.append(MedisafeStatusCountEntity(coordinator, entry, "missed"))
    entities.append(MedisafeStatusCountEntity(coordinator, entry, "dismissed"))
    entities.append(MedisafeStatusCountEntity(coordinator, entry, "pending"))

    _LOGGER.info(f"Setting up {len(entities)} entities")
    async_add_devices(entities)


class MedisafeStatusCountEntity(CoordinatorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_unit_of_measurement = "doses"
    _attr_icon = "mdi:pill"
    _attr_suggested_display_precision = 0
    _attr_has_entity_name = True

    def __init__(self, coordinator, config_entry, status):
        super().__init__(coordinator)
        self.status = status
        self.config_entry = config_entry
        self._attr_unique_id = f"medication_{self.config_entry.entry_id}_{status}"

    @property
    def name(self):
        return f"medication {self.status}".title()

    @property
    def available(self):
        return "items" in self.coordinator.data

    @property
    def state(self):
        count = 0
        for item in self.coordinator.data["items"]:
            if (
                item["status"] == self.status
                and date.fromtimestamp(item["date"]) == date.today()
            ):
                count = count + 1
        return count

    @property
    def extra_state_attributes(self):
        return {
            "account": self.config_entry.data.get(CONF_USERNAME),
            "attribution": ATTRIBUTION,
            "integration": DOMAIN,
        }


class MedisafeMedicationEntity(CoordinatorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_unit_of_measurement = "pills"
    _attr_icon = "mdi:pill"
    _attr_suggested_display_precision = 0
    _attr_has_entity_name = True

    def __init__(self, coordinator, config_entry, uuid):
        super().__init__(coordinator)
        self.uuid = uuid
        self.config_entry = config_entry
        self._attr_unique_id = f"medication_{self.config_entry.entry_id}_{uuid}"

    @property
    def name(self):
        return self.coordinator.get_medication(self.uuid)["name"]

    @property
    def state(self):
        medication = self.coordinator.get_medication(self.uuid)

        if "pillsLeft" in medication:
            return medication["pillsLeft"]
        else:
            return None

    @property
    def available(self):
        medication = self.coordinator.get_medication(self.uuid)

        return (medication is not None and "pillsLeft" in medication)

    @property
    def extra_state_attributes(self):
        medication = self.coordinator.get_medication(self.uuid)

        if "dose" in medication:
            return {
                "account": self.config_entry.data.get(CONF_USERNAME),
                "attribution": ATTRIBUTION,
                "integration": DOMAIN,
                "dose": medication["dose"],
            }
        else:
            return {
                "account": self.config_entry.data.get(CONF_USERNAME),
                "attribution": ATTRIBUTION,
                "integration": DOMAIN,
            }

    @property
    def entity_picture(self):
        medication = self.coordinator.get_medication(self.uuid)

        if medication is None or medication["shape"] == "capsule":
            return None
        else:
            return f"https://web.medisafe.com/medication-icons/pill_{medication['shape']}_{medication['color']}.png"
