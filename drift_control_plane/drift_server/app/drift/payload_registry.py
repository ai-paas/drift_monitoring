from __future__ import annotations

from typing import Any, Callable

from drift_server.app.payload_adapter import PayloadBindingError
from drift_server.app.payload_adapter import build_payload as build_bound_payload
from drift_server.app.payload_adapters.adwin_mean_stream_to_chart_stream_001 import build_payload


class PayloadAdapterNotFound(KeyError):
    pass


PayloadAdapter = Callable[[dict[str, Any]], dict[str, Any]]

PAYLOAD_ADAPTERS: dict[str, PayloadAdapter] = {
    "adwin_mean_stream_to_chart_stream_001": build_payload,
}


# @managed-contract contract_id=drift.payload_registry.get_payload_adapter level=P0
def get_payload_adapter(key: str) -> PayloadAdapter:
    try:
        return PAYLOAD_ADAPTERS[key]
    except KeyError as exc:
        def _generic_bound_payload(context: dict[str, Any]) -> dict[str, Any]:
            try:
                return build_bound_payload(context, key)
            except PayloadBindingError as binding_exc:
                raise PayloadAdapterNotFound(key) from binding_exc

        return _generic_bound_payload
