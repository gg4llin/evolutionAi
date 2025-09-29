"""Minimal HTTP server exposing the AdaptiveAgent control-plane API."""
from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .capabilities import CapabilityContext, CapabilityValidator, DEFAULT_SCOPE
from .config_loader import load_connectivity_config
from .engine import AdaptiveAgentEngine
from .program import dispatch_command


class AdaptiveAgentRequestHandler(BaseHTTPRequestHandler):
    """Routes health, metric, and command requests to the engine."""

    engine: AdaptiveAgentEngine
    validator: CapabilityValidator

    def _send_json(self, payload: Dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8")) if raw else {}
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON payload") from exc

    # ------------------------------ routes ------------------------------
    def do_GET(self) -> None:  # noqa: N802 - HTTP verb
        if self.path == "/healthz":
            payload = self.engine.heartbeat()
            self._send_json({"status": "ok", "heartbeat": payload})
            return
        if self.path == "/metrics":
            self._send_json({"status": "ok", "metrics": self.engine.metrics_snapshot()})
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")

    def do_POST(self) -> None:  # noqa: N802 - HTTP verb
        if self.path not in {"/commands", "/commands/dispatch"}:
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return
        try:
            command = self._read_json()
            action = command.get("action", "")
            self.validator.validate(self.headers, CapabilityContext(scope=DEFAULT_SCOPE, action=action))
            result = dispatch_command(self.engine, command)
        except PermissionError as exc:
            self._send_json({"status": "forbidden", "error": str(exc)}, status=HTTPStatus.FORBIDDEN)
            return
        except Exception as exc:  # pragma: no cover - simple error mapping
            self._send_json({"status": "error", "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)


def build_server(host: str = "0.0.0.0", port: int = 8080, *, config_path: Optional[Path] = None) -> Tuple[ThreadingHTTPServer, AdaptiveAgentEngine]:
    """Instantiate the HTTP server and the attached engine."""
    cfg = load_connectivity_config(config_path)
    engine = AdaptiveAgentEngine(cfg)

    handler = AdaptiveAgentRequestHandler
    handler.engine = engine
    handler.validator = CapabilityValidator()

    server = ThreadingHTTPServer((host, port), handler)
    return server, engine


def serve_forever(host: str = "0.0.0.0", port: int = 8080, *, config_path: Optional[Path] = None) -> None:
    server, _ = build_server(host, port, config_path=config_path)
    try:
        server.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - graceful shutdown signal
        pass
    finally:
        server.server_close()
