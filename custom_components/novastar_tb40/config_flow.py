"""Set up the TB40 with an optional, non-writing connectivity check."""

import asyncio
from ipaddress import IPv4Address

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .protocol import async_check_connection

DOMAIN = "novastar_tb40"


class TB40ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return await self._async_connection_form("user", user_input)

    async def async_step_reconfigure(self, user_input=None):
        return await self._async_connection_form(
            "reconfigure", user_input, self._get_reconfigure_entry()
        )

    async def _async_connection_form(self, step_id, user_input, entry=None):
        errors = {}
        suggested = {}
        if entry is not None:
            suggested = {key: entry.data[key] for key in ("host", "username")}

        if user_input is not None:
            data = {key: value.strip() for key, value in user_input.items()
                    if key in ("host", "serial", "username")}
            for key, value in data.items():
                if not value:
                    errors[key] = "required"
            try:
                IPv4Address(data["host"])
            except ValueError:
                if entry is None or data["host"] != entry.data["host"]:
                    errors["host"] = "invalid_ip"

            password = user_input.get("password", "")
            if not password and entry is None:
                errors["password"] = "required"
            data["password"] = password or (entry.data["password"] if entry else "")

            if not errors and user_input.get("check_connection", True):
                try:
                    await async_check_connection(data["host"])
                except (OSError, asyncio.TimeoutError):
                    errors["base"] = "cannot_connect"

            if not errors:
                if entry is not None:
                    return self.async_update_and_abort(entry, data_updates=data)
                await self.async_set_unique_id(data["serial"].casefold())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="NovaStar TB40", data=data)

            suggested.update({key: value for key, value in user_input.items() if key != "password"})

        fields = {vol.Required("host"): str}
        if entry is None:
            fields[vol.Required("serial")] = str
        password_field = vol.Optional if entry is not None else vol.Required
        fields.update({
            vol.Required("username", default="admin"): str,
            password_field("password"): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
            ),
            vol.Optional("check_connection", default=True): bool,
        })
        return self.async_show_form(
            step_id=step_id,
            data_schema=self.add_suggested_values_to_schema(vol.Schema(fields), suggested),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return TB40OptionsFlow()


class TB40OptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            if (user_input.get("solar") or user_input.get("night_limit")) and not user_input.get("relay"):
                errors["base"] = "relay_required"
            else:
                return self.async_create_entry(data=user_input)

        options = self.config_entry.options
        schema = vol.Schema({
            vol.Optional("relay"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="switch")
            ),
            vol.Optional("solar", default=False): bool,
            vol.Optional("night_limit", default=False): bool,
            vol.Optional("legacy_brightness"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="input_number")
            ),
        })
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(schema, user_input or options),
            errors=errors,
        )
