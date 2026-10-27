"""Signed, expiring bearer sessions for authenticated API requests."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time


SESSION_TTL_SECONDS = 12 * 60 * 60
# Configure SESSION_SECRET in deployment for stable tokens across process restarts.
# The random fallback is safer than a checked-in development secret.
_configured_secret = os.environ.get("SESSION_SECRET", "").encode("utf-8")
if _configured_secret and len(_configured_secret) < 32:
    raise RuntimeError("SESSION_SECRET must contain at least 32 bytes.")
_SESSION_SECRET = _configured_secret or secrets.token_bytes(32)


def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def create_session_token(customer_id: int) -> str:
    """Create an HMAC-SHA256 token that binds a customer id to an expiry."""
    payload = json.dumps(
        {"sub": customer_id, "exp": int(time.time()) + SESSION_TTL_SECONDS},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    encoded_payload = _encode(payload)
    signature = hmac.new(
        _SESSION_SECRET, encoded_payload.encode("ascii"), hashlib.sha256
    ).digest()
    return f"{encoded_payload}.{_encode(signature)}"


def verify_session_token(token: str) -> int:
    """Return the signed customer id, rejecting malformed, forged, or expired tokens."""
    try:
        encoded_payload, encoded_signature = token.split(".", maxsplit=1)
        if not re.fullmatch(r"[A-Za-z0-9_-]+", encoded_payload) or not re.fullmatch(
            r"[A-Za-z0-9_-]+", encoded_signature
        ):
            raise ValueError
        supplied_signature = base64.urlsafe_b64decode(
            encoded_signature + "=" * (-len(encoded_signature) % 4)
        )
        expected_signature = hmac.new(
            _SESSION_SECRET, encoded_payload.encode("ascii"), hashlib.sha256
        ).digest()
        if not hmac.compare_digest(supplied_signature, expected_signature):
            raise ValueError
        payload_bytes = base64.urlsafe_b64decode(
            encoded_payload + "=" * (-len(encoded_payload) % 4)
        )
        payload = json.loads(payload_bytes)
        customer_id = payload["sub"]
        expires_at = payload["exp"]
        if (
            not isinstance(customer_id, int)
            or isinstance(customer_id, bool)
            or customer_id < 1
            or not isinstance(expires_at, int)
            or expires_at <= int(time.time())
        ):
            raise ValueError
        return customer_id
    except (ValueError, TypeError, KeyError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("Session token is invalid or expired.") from error
