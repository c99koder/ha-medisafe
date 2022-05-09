#  Copyright (C) 2022 Sam Steele
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
from datetime import date

from homeassistant.components.sensor import SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .const import CONF_USERNAME
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_devices):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_config_entry_first_refresh()

    entities = []

    for idx, ent in enumerate(coordinator.data["medications"]):
        if ent["treatmentStatus"] == 1:
            entities.append(MedisafeMedicationEntity(coordinator, entry, idx))

    entities.append(MedisafeStatusCountEntity(coordinator, entry, "taken"))
    entities.append(MedisafeStatusCountEntity(coordinator, entry, "missed"))
    entities.append(MedisafeStatusCountEntity(coordinator, entry, "dismissed"))
    entities.append(MedisafeStatusCountEntity(coordinator, entry, "pending"))

    async_add_devices(entities)


class MedisafeStatusCountEntity(CoordinatorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_unit_of_measurement = "doses"
    _attr_icon = "mdi:pill"

    def __init__(self, coordinator, config_entry, status):
        super().__init__(coordinator)
        self.status = status
        self.config_entry = config_entry
        self._attr_unique_id = f"medication_{self.config_entry.entry_id}_{status}"
        self._attr_name = f"medication {status}".title()

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
    _attr_device_class = "medication"
    _attr_unit_of_measurement = "pills"
    _attr_icon = "mdi:pill"

    def __init__(self, coordinator, config_entry, idx):
        super().__init__(coordinator)
        self.idx = idx
        self.config_entry = config_entry
        self._attr_unique_id = f"medication_{self.config_entry.entry_id}_{self.coordinator.data['medications'][self.idx]['uuid']}"
        self._attr_name = self.coordinator.data["medications"][self.idx]["name"]

    @property
    def state(self):
        if "pillsLeft" in self.coordinator.data["medications"][self.idx]:
            return self.coordinator.data["medications"][self.idx]["pillsLeft"]
        else:
            return None

    @property
    def available(self):
        return (
            "medications" in self.coordinator.data
            and "pillsLeft" in self.coordinator.data["medications"][self.idx]
        )

    @property
    def extra_state_attributes(self):
        if "dose" in self.coordinator.data["medications"][self.idx]:
            return {
                "account": self.config_entry.data.get(CONF_USERNAME),
                "attribution": ATTRIBUTION,
                "integration": DOMAIN,
                "dose": self.coordinator.data["medications"][self.idx]["dose"],
            }
        else:
            return {
                "account": self.config_entry.data.get(CONF_USERNAME),
                "attribution": ATTRIBUTION,
                "integration": DOMAIN,
            }

    @property
    def entity_picture(self):
        med = self.coordinator.data["medications"][self.idx]
        if med is None or med["shape"] == "capsule":
            return None
        else:
            return f"https://web.medisafe.com/medication-icons/pill_{med['shape']}_{med['color']}.png"
