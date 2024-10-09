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
        self._attr_unique_id = f"medication_refills_{self.config_entry.entry_id}"

    @property
    def todo_items(self) -> list[TodoItem]:
        todo_list = []

        if self.coordinator.data is not None and "groups" in self.coordinator.data:
            for group in self.coordinator.data["groups"]:
                if "refill" in group and "refillReminder" in group["refill"] and "status" in group:
                    if group["status"] == "ACTIVE" and group["refill"]["currentNumberOfPills"] <= group["refill"]["refillReminder"]["pills"]:
                        item = TodoItem()
                        item.summary = group["medicine"]["name"]
                        item.uid = group["uuid"]
                        item.status = TodoItemStatus.NEEDS_ACTION
                        if group["refill"]["currentNumberOfPills"].is_integer():
                            item.description = f"{int(group['refill']['currentNumberOfPills'])} pills remaining"
                        else:
                            item.description = f"{group['refill']['currentNumberOfPills']} pills remaining"
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
