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
from datetime import timedelta
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from .api import MedisafeApiClient
from .const import CONF_PASSWORD
from .const import CONF_USERNAME
from .const import DOMAIN
from .const import PLATFORMS
from .const import STARTUP_MESSAGE

SCAN_INTERVAL = timedelta(minutes=15)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    coordinator = MedisafeDataUpdateCoordinator(hass)

    entry.runtime_data = MedisafeData(
        client=MedisafeApiClient(
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            session=async_get_clientsession(hass),
        ),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


class MedisafeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_data()
        except Exception as exception:
            raise UpdateFailed() from exception

    def get_medication(self, uuid):
        if "medications" not in self.data:
            _LOGGER.error("Medisafe has no data yet")
            return None
        else:
            for medication in self.data["medications"]:
                if medication["uuid"] == uuid:
                    return medication

        _LOGGER.error(f"Medication not found for UUID: {uuid}")

        return None


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


@dataclass
class MedisafeData:
    """Data for the Medisafe integration."""

    client: MedisafeApiClient
    coordinator: MedisafeDataUpdateCoordinator
