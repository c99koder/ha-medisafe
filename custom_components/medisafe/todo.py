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

from homeassistant.components.todo import TodoListEntity, TodoItem, TodoItemStatus
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .const import CONF_USERNAME
from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    coordinator = entry.runtime_data.coordinator
    await coordinator.async_config_entry_first_refresh()

    async_add_devices([MedisafeTodoListEntity(coordinator, entry)])


class MedisafeTodoListEntity(CoordinatorEntity, TodoListEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:pill"

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_unique_id = "medication_refills"

    @property
    def todo_items(self) -> list[TodoItem]:
        todo_list = []

        if self.coordinator.data is not None and "medications" in self.coordinator.data:
            for medication in self.coordinator.data["medications"]:
                if "pillsLeft" in medication and "pillsReminder" in medication and "treatmentStatus" in medication:
                    if medication["treatmentStatus"] == 1 and medication["pillsLeft"] <= medication["pillsReminder"]:
                        item = TodoItem()
                        item.summary = medication["name"]
                        item.uid = medication["uuid"]
                        item.status = TodoItemStatus.NEEDS_ACTION
                        if medication['pillsLeft'].is_integer():
                            item.description = f"{int(medication['pillsLeft'])} pills remaining"
                        else:
                            item.description = f"{medication['pillsLeft']} pills remaining"
                        todo_list.append(item)

        return todo_list

    @property
    def name(self):
        return "Medication Refills"

    @property
    def available(self):
        return "medications" in self.coordinator.data

    @property
    def extra_state_attributes(self):
        return {
            "account": self.config_entry.data.get(CONF_USERNAME),
            "attribution": ATTRIBUTION,
            "integration": DOMAIN,
        }
