"""ASGI application wrapping the AdaptiveAgent control-plane engine."""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from .capabilities import CapabilityContext, CapabilityValidator, DEFAULT_SCOPE
from .config_loader import load_connectivity_config
from .engine import AdaptiveAgentEngine
from .program import dispatch_command


_connectivity = load_connectivity_config()
_engine = AdaptiveAgentEngine(_connectivity)
_validator = CapabilityValidator()


async def app(scope: Dict[str, Any], receive, send) -> None:
    if scope["type"] != "http":  # pragma: no cover - ASGI contract
        raise RuntimeError("AdaptiveAgent ASGI app only handles HTTP scopes")

    method = scope["method"].upper()
    path = scope["path"]
    headers = {key.decode("latin1"): value.decode("latin1") for key, value in scope["headers"]}

    if method == "GET" and path == "/healthz":
        payload = {"status": "ok", "heartbeat": _engine.heartbeat()}
        await _send_json(send, payload)
        return

    if method == "GET" and path == "/metrics":
        payload = {"status": "ok", "metrics": _engine.metrics_snapshot()}
        await _send_json(send, payload)
        return

    if method == "POST" and path in {"/commands", "/commands/dispatch"}:
        body = await _receive_json(receive)
        action = body.get("action", "")
        try:
            _validator.validate(headers, CapabilityContext(scope=DEFAULT_SCOPE, action=action))
            result = dispatch_command(_engine, body)
        except PermissionError as exc:
            await _send_json(send, {"status": "forbidden", "error": str(exc)}, status=403)
            return
        except Exception as exc:  # pragma: no cover - error mapping
            await _send_json(send, {"status": "error", "error": str(exc)}, status=400)
            return
        await _send_json(send, result)
        return

    await _send_json(send, {"status": "not_found", "error": "Endpoint not found"}, status=404)


async def _receive_json(receive) -> Dict[str, Any]:
    body = b""
    more_body = True
    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)
    if body:
        return json.loads(body.decode("utf-8"))
    return {}


async def _send_json(send, payload: Dict[str, Any], *, status: int = 200) -> None:
    body = json.dumps(payload).encode("utf-8")
    headers = [
        (b"content-type", b"application/json"),
        (b"content-length", str(len(body)).encode("latin1")),
    ]
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": headers,
    })
    await send({
        "type": "http.response.body",
        "body": body,
    })
