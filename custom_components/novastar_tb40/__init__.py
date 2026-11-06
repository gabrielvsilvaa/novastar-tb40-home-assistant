"""NovaStar TB40 integration."""

from homeassistant.const import Platform

PLATFORMS = [Platform.NUMBER]


async def async_setup_entry(hass, entry):
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)
