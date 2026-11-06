"""Expose the last transmitted brightness target."""

import asyncio
from datetime import timedelta
import logging
import math

from homeassistant.components.number import NumberMode, RestoreNumber
from homeassistant.const import PERCENTAGE, STATE_OFF, STATE_ON
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval

from .config_flow import DOMAIN
from .protocol import set_brightness
from .solar import END_ELEVATION, MIN_BRIGHTNESS, RETRY_TIMES, solar_step, solar_target

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([TB40Brightness(entry)])


class TB40Brightness(RestoreNumber):
    _attr_has_entity_name = True
    _attr_translation_key = "brightness"
    _attr_native_min_value = 1
    _attr_native_max_value = 100
    _attr_native_step = 0.1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER
    _attr_should_poll = False

    def __init__(self, entry):
        self._data = entry.data
        self._entry = entry
        self._relay = entry.options.get("relay")
        self._helper = entry.options.get("legacy_brightness")
        self._solar = entry.options.get("solar", False)
        self._night_limit = entry.options.get("night_limit", False)
        self._startup_task = None
        self._desired = None
        self._lock = asyncio.Lock()
        self._attr_unique_id = f"{entry.unique_id}_brightness"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            name="NovaStar TB40",
            manufacturer="NovaStar",
            model="TB40",
        )

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        if (last := await self.async_get_last_number_data()) is not None:
            self._attr_native_value = last.native_value
            self._desired = last.native_value
        if self._relay:
            self.async_on_remove(async_track_state_change_event(
                self.hass, [self._relay], self._relay_changed
            ))
            if self._solar:
                self.async_on_remove(async_track_time_interval(
                    self.hass, self._periodic_solar, timedelta(seconds=10)
                ))

    async def async_will_remove_from_hass(self):
        if self._startup_task is not None:
            self._startup_task.cancel()
            await asyncio.gather(self._startup_task, return_exceptions=True)
        await super().async_will_remove_from_hass()

    @callback
    def _relay_changed(self, event):
        old, new = event.data["old_state"], event.data["new_state"]
        if old is not None and new is not None and old.state == new.state:
            return
        if self._startup_task is not None:
            self._startup_task.cancel()
        if old is not None and old.state == STATE_OFF and new is not None and new.state == STATE_ON:
            self._startup_task = self._entry.async_create_background_task(
                self.hass, self._reapply_on_start(), "TB40 brightness startup"
            )

    def _elevation(self):
        sun = self.hass.states.get("sun.sun")
        value = sun.attributes.get("elevation") if sun else None
        return value if isinstance(value, (int, float)) and math.isfinite(value) else None

    def _target(self):
        if self._helper and (helper := self.hass.states.get(self._helper)) is not None:
            try:
                value = float(helper.state)
            except ValueError:
                pass
            else:
                if 1 <= value <= 100:
                    return value
        return self._desired

    async def _set_automatic_target(self, value):
        self._desired = value
        if self._helper and self._target() != value:
            await self.hass.services.async_call(
                "input_number", "set_value",
                {"entity_id": self._helper, "value": value}, blocking=True,
            )

    async def _reapply_on_start(self):
        loop = asyncio.get_running_loop()
        started = loop.time()
        async with self._lock:
            if not self.hass.states.is_state(self._relay, STATE_ON):
                return
            elevation = self._elevation()
            if elevation is not None:
                if self._solar:
                    await self._set_automatic_target(solar_target(elevation))
                    await self._send_automatic(self._target())
                elif self._night_limit and elevation <= END_ELEVATION:
                    target = self._target()
                    await self._set_automatic_target(
                        MIN_BRIGHTNESS if target is None else min(target, MIN_BRIGHTNESS)
                    )
        for elapsed in RETRY_TIMES:
            await asyncio.sleep(max(0, started + elapsed - loop.time()))
            async with self._lock:
                if not self.hass.states.is_state(self._relay, STATE_ON):
                    return
                if (target := self._target()) is not None:
                    await self._send_automatic(target)

    async def _periodic_solar(self, _now):
        async with self._lock:
            if not self.hass.states.is_state(self._relay, STATE_ON):
                return
            elevation, current = self._elevation(), self._target()
            if elevation is None or current is None:
                return
            if (value := solar_step(elevation, current)) is not None:
                await self._set_automatic_target(value)
                await self._send_automatic(value)

    async def _send_automatic(self, value):
        try:
            await self._send(value)
        except HomeAssistantError:
            _LOGGER.warning("Could not send the automatic brightness target to the TB40")

    async def async_set_native_value(self, value):
        async with self._lock:
            await self._send(value)
            await self._set_automatic_target(value)

    async def _send(self, value):
        try:
            await set_brightness(
                self._data["host"], self._data["serial"],
                self._data["username"], self._data["password"], value,
            )
        except (OSError, asyncio.TimeoutError, ValueError):
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="send_failed"
            ) from None
        self._attr_native_value = value
        self.async_write_ha_state()
