"""Capability token validation aligned with security_authentication_framework."""
from __future__ import annotations

import base64
import hmac
import os
import time
from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping

CAPABILITY_SECRET_ENV = "ADAPTIVE_CAPABILITY_SECRET"
TIMESTAMP_HEADER = "X-Timestamp"
TOKEN_HEADER = "X-Capability-Token"
DEFAULT_SCOPE = "control_plane"
ALLOWED_SKEW_SECONDS = 300


@dataclass(frozen=True)
class CapabilityContext:
    scope: str
    action: str


class CapabilityValidator:
    """Validates scoped_macaroon-style capability tokens using an HMAC envelope."""

    def __init__(self, secret: str | None = None) -> None:
        self._secret = (secret or os.getenv(CAPABILITY_SECRET_ENV, "")).encode("utf-8")
        if not self._secret:
            raise RuntimeError(
                "Capability secret is undefined. Export ADAPTIVE_CAPABILITY_SECRET before serving the API."
            )

    def validate(self, headers: Mapping[str, str], context: CapabilityContext) -> None:
        token = headers.get(TOKEN_HEADER)
        timestamp_raw = headers.get(TIMESTAMP_HEADER)
        if not token or not timestamp_raw:
            raise PermissionError("Missing capability token or timestamp header.")

        try:
            timestamp = float(timestamp_raw)
        except ValueError as exc:  # pragma: no cover - defensive programming
            raise PermissionError("Invalid timestamp header.") from exc

        now = time.time()
        if abs(now - timestamp) > ALLOWED_SKEW_SECONDS:
            raise PermissionError("Timestamp outside allowed skew window.")

        message = f"{context.scope}:{context.action}:{timestamp_raw}".encode("utf-8")
        expected = base64.urlsafe_b64encode(hmac.new(self._secret, message, sha256).digest()).decode("utf-8")
        if not hmac.compare_digest(expected, token):
            raise PermissionError("Invalid capability token.")

    @staticmethod
    def build_token(secret: str, timestamp: float, action: str, scope: str = DEFAULT_SCOPE) -> str:
        message = f"{scope}:{action}:{timestamp}".encode("utf-8")
        return base64.urlsafe_b64encode(hmac.new(secret.encode("utf-8"), message, sha256).digest()).decode(
            "utf-8"
        )
