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
from datetime import datetime
from datetime import timedelta

import pytz
from homeassistant.components.calendar import CalendarEntity
from homeassistant.components.calendar import CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .const import CONF_USERNAME
from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    coordinator = entry.runtime_data.coordinator
    await coordinator.async_config_entry_first_refresh()

    async_add_devices([MedisafeCalendarEntity(coordinator, entry)])


class MedisafeCalendarEntity(CoordinatorEntity, CalendarEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:pill"

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_unique_id = f"medisafe_calendar_{self.config_entry.entry_id}"

    def event_from_appointment(self, appointment):
        dt = datetime.utcfromtimestamp(appointment["date"]).replace(tzinfo=pytz.utc)
        doctor = self.coordinator.get_doctor(appointment["doctorId"])
        event = CalendarEvent(
            start=dt, end=dt + timedelta(hours=1), summary=appointment["title"]
        )
        description = ""
        if appointment["notes"]:
            description += appointment["notes"] + "\n\n"

        if doctor is not None:
            description += "Doctor:\n"
            description += doctor["firstName"] + " " + doctor["lastName"]
            if "speciality" in doctor and doctor["speciality"]:
                description += " (" + doctor["speciality"] + ")"
            description += "\n"

            if "email" in doctor and doctor["email"]:
                description += "Email: " + doctor["email"] + "\n"

            if "address" in doctor and doctor["address"]:
                description += "Address: " + doctor["address"] + "\n"

            if "phone1" in doctor and doctor["phone1"] and doctor["phone1Type"]:
                description += doctor["phone1Type"] + ": " + doctor["phone1"] + "\n"

            if "phone2" in doctor and doctor["phone2"] and doctor["phone2Type"]:
                description += doctor["phone2Type"] + ": " + doctor["phone2"] + "\n"

            if "phone3" in doctor and doctor["phone3"] and doctor["phone3Type"]:
                description += doctor["phone3Type"] + ": " + doctor["phone3"] + "\n"

            description += "\n"

        event.description = description
        if "address" in appointment and appointment["address"]:
            event.location = appointment["address"]
        elif doctor is not None and "address" in doctor and doctor["address"]:
            event.location = doctor["address"]
        event.uid = appointment["id"]
        return event

    @property
    def event(self):
        now = datetime.utcnow().replace(tzinfo=pytz.utc)

        if (
            self.coordinator.data is not None
            and "appointments" in self.coordinator.data
        ):
            for appointment in reversed(self.coordinator.data["appointments"]):
                if appointment["active"] is True:
                    if (
                        datetime.utcfromtimestamp(appointment["date"]).replace(
                            tzinfo=pytz.utc
                        )
                        >= now
                    ):
                        return self.event_from_appointment(appointment)

        return None

    async def async_get_events(self, hass, start_date, end_date) -> list[CalendarEvent]:
        events = []

        if (
            self.coordinator.data is not None
            and "appointments" in self.coordinator.data
        ):
            for appointment in self.coordinator.data["appointments"]:
                if appointment["active"] is True:
                    dt = datetime.utcfromtimestamp(appointment["date"]).replace(
                        tzinfo=pytz.utc
                    )
                    if dt >= start_date and dt <= end_date:
                        events.append(self.event_from_appointment(appointment))

        return events

    @property
    def name(self):
        return "Medisafe"

    @property
    def available(self):
        return "appointments" in self.coordinator.data

    @property
    def extra_state_attributes(self):
        return {
            "account": self.config_entry.data.get(CONF_USERNAME),
            "attribution": ATTRIBUTION,
            "integration": DOMAIN,
        }
