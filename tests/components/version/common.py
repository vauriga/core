"""Fixtures for version integration."""
from __future__ import annotations

from typing import Any, Final
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.components.version.const import (
    DEFAULT_CONFIGURATION,
    DEFAULT_NAME_CURRENT,
    DOMAIN,
    UPDATE_COORDINATOR_UPDATE_INTERVAL,
    VERSION_SOURCE_LOCAL,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util import dt

from tests.common import MockConfigEntry, async_fire_time_changed

MOCK_VERSION: Final = "1970.1.0"
MOCK_VERSION_DATA: Final = {"source": "local", "channel": "stable"}


MOCK_VERSION_CONFIG_ENTRY_DATA: Final[dict[str, Any]] = {
    "domain": DOMAIN,
    "title": VERSION_SOURCE_LOCAL,
    "data": DEFAULT_CONFIGURATION,
    "source": config_entries.SOURCE_USER,
}

TEST_DEFAULT_IMPORT_CONFIG: Final = {
    **DEFAULT_CONFIGURATION,
    CONF_NAME: DEFAULT_NAME_CURRENT,
}


async def mock_get_version_update(
    hass: HomeAssistant,
    version: str = MOCK_VERSION,
    data: dict[str, Any] = MOCK_VERSION_DATA,
    side_effect: Exception = None,
) -> None:
    """Mock getting version."""
    with patch(
        "pyhaversion.HaVersion.get_version",
        return_value=(version, data),
        side_effect=side_effect,
    ):

        async_fire_time_changed(hass, dt.utcnow() + UPDATE_COORDINATOR_UPDATE_INTERVAL)
        await hass.async_block_till_done()


async def setup_version_integration(hass: HomeAssistant) -> MockConfigEntry:
    """Set up the Version integration."""
    await async_setup_component(hass, "persistent_notification", {})
    mock_entry = MockConfigEntry(**MOCK_VERSION_CONFIG_ENTRY_DATA)
    mock_entry.add_to_hass(hass)

    with patch(
        "pyhaversion.HaVersion.get_version",
        return_value=(MOCK_VERSION, MOCK_VERSION_DATA),
    ):

        assert await hass.config_entries.async_setup(mock_entry.entry_id)
        await hass.async_block_till_done()

    assert hass.states.get("sensor.local_installation").state == MOCK_VERSION
    assert mock_entry.state == config_entries.ConfigEntryState.LOADED

    return mock_entry
