from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Mapping
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.const import CONF_BODY, CONF_HEADERS, CONF_METHOD, CONF_TIMEOUT, CONF_URL
from homeassistant.core import HomeAssistant, SupportsResponse, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

CONF_BODY = "body"

DOMAIN = "http_ha"
SERVICE_REQUEST = "request"

_LOGGER = logging.getLogger(__name__)

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): cv.string,
        vol.Optional(CONF_METHOD, default="GET"): vol.In(
            ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
        ),
        vol.Optional(CONF_HEADERS, default={}): object,
        vol.Optional(CONF_BODY): object,
        vol.Optional(CONF_TIMEOUT, default=10): vol.Coerce(int),
    }
)


def _coerce_headers(value: Any) -> dict[str, str]:
    if value is None:
        return {}

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return {}
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as err:
            raise HomeAssistantError("Headers must be a valid JSON object") from err
        if not isinstance(parsed, dict):
            raise HomeAssistantError("Headers must be a JSON object")
        return {str(k): str(v) for k, v in parsed.items()}

    if isinstance(value, Mapping):
        return {str(k): str(v) for k, v in value.items()}

    raise HomeAssistantError("Headers must be a JSON object")


def _coerce_body(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return value

    return value


async def _request_http(
    method: str,
    url: str,
    headers: dict[str, str],
    body: Any,
    timeout: int,
) -> dict[str, Any]:
    timeout_config = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=timeout_config) as session:
        request_kwargs: dict[str, Any] = {"headers": headers}

        if body is not None:
            if method in {"GET", "HEAD"}:
                request_kwargs["data"] = json.dumps(body) if isinstance(body, (dict, list)) else str(body)
            else:
                request_kwargs["json"] = body

        async with session.request(method, url, **request_kwargs) as response:
            raw_text = await response.text()
            content_type = response.headers.get("Content-Type", "")
            parsed_body: Any

            if "json" in content_type.lower():
                try:
                    parsed_body = json.loads(raw_text)
                except json.JSONDecodeError:
                    parsed_body = raw_text
            else:
                parsed_body = raw_text

            return {
                "status": response.status,
                "headers": dict(response.headers),
                "content_type": content_type,
                "body": parsed_body,
            }


async def async_handle_request(call: ServiceCall) -> dict[str, Any]:
    method = call.data[CONF_METHOD].upper()
    url = call.data[CONF_URL]
    headers = _coerce_headers(call.data.get(CONF_HEADERS, {}))
    body = _coerce_body(call.data.get(CONF_BODY))
    timeout = call.data.get(CONF_TIMEOUT, 10)

    try:
        return await _request_http(method, url, headers, body, timeout)
    except asyncio.TimeoutError as err:
        raise HomeAssistantError(f"Request timeout after {timeout} seconds") from err
    except aiohttp.ClientError as err:
        raise HomeAssistantError(f"HTTP request failed: {err}") from err


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    if not hass.services.has_service(DOMAIN, SERVICE_REQUEST):
        hass.services.async_register(
            DOMAIN,
            SERVICE_REQUEST,
            async_handle_request,
            schema=SERVICE_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: Any) -> bool:
    await async_setup(hass, {})
    return True


async def async_unload_entry(hass: HomeAssistant, entry: Any) -> bool:
    return True
