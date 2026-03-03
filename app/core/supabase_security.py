"""Supabase JWT verification utilities.

Verifies Supabase-issued access tokens (JWT) using the Supabase JWKS (public keys).
Keys are cached in-memory with TTL to avoid fetching JWKS on every request.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx
from jose import JWTError, jwk, jwt

from app.config import get_settings
from app.core.exceptions import UnauthorizedException

settings = get_settings()

_JWKS_LOCK = asyncio.Lock()
_JWKS_CACHE: dict[str, Any] = {
    "jwks": None,
    "expires_at": 0.0,
}


async def _fetch_jwks() -> dict[str, Any]:
    if not settings.SUPABASE_JWKS_URL:
        raise UnauthorizedException("Supabase JWKS URL is not configured")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(settings.SUPABASE_JWKS_URL)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError:
        raise UnauthorizedException("Unable to fetch signing keys")

    if not isinstance(data, dict) or "keys" not in data:
        raise UnauthorizedException("Invalid Supabase JWKS response")
    return data


async def get_jwks(*, force_refresh: bool = False) -> dict[str, Any]:
    """Return JWKS dict, cached with TTL."""
    now = time.time()
    cached = _JWKS_CACHE.get("jwks")
    expires_at = float(_JWKS_CACHE.get("expires_at") or 0.0)

    if not force_refresh and cached is not None and now < expires_at:
        return cached

    async with _JWKS_LOCK:
        # Re-check after acquiring lock
        now = time.time()
        cached = _JWKS_CACHE.get("jwks")
        expires_at = float(_JWKS_CACHE.get("expires_at") or 0.0)
        if not force_refresh and cached is not None and now < expires_at:
            return cached

        jwks = await _fetch_jwks()
        _JWKS_CACHE["jwks"] = jwks
        _JWKS_CACHE["expires_at"] = now + max(30, int(settings.SUPABASE_JWKS_CACHE_TTL_SECONDS))
        return jwks


def _select_jwk(jwks: dict[str, Any], kid: str) -> dict[str, Any] | None:
    keys = jwks.get("keys")
    if not isinstance(keys, list):
        return None
    for key in keys:
        if isinstance(key, dict) and key.get("kid") == kid:
            return key
    return None


async def decode_supabase_jwt(token: str) -> dict[str, Any]:
    """Decode and validate a Supabase JWT.

    Validates:
    - Signature using JWKS
    - `iss` (if configured)
    - `aud` (always, defaults to "authenticated")
    - `exp` (handled by jose)
    - algorithm is in SUPABASE_ACCEPTED_ALGS

    Raises UnauthorizedException on any failure.
    """

    if not token:
        raise UnauthorizedException("Missing bearer token")

    try:
        header = jwt.get_unverified_header(token)
    except JWTError:
        raise UnauthorizedException("Invalid token header")

    kid = header.get("kid")
    alg = header.get("alg")

    if not kid or not isinstance(kid, str):
        raise UnauthorizedException("Token header missing kid")
    if not alg or not isinstance(alg, str):
        raise UnauthorizedException("Token header missing alg")
    if settings.SUPABASE_ACCEPTED_ALGS and alg not in settings.SUPABASE_ACCEPTED_ALGS:
        raise UnauthorizedException(f"Unsupported token algorithm: {alg}")

    jwks = await get_jwks(force_refresh=False)
    jwk_data = _select_jwk(jwks, kid)
    if jwk_data is None:
        jwks = await get_jwks(force_refresh=True)
        jwk_data = _select_jwk(jwks, kid)
    if jwk_data is None:
        raise UnauthorizedException("Signing key not found")

    try:
        key = jwk.construct(jwk_data, algorithm=alg)
        public_key_pem = key.to_pem()
        payload = jwt.decode(
            token,
            public_key_pem,
            algorithms=[alg],
            audience=settings.SUPABASE_AUDIENCE or None,
            # We validate issuer ourselves (tolerant to trailing slashes).
            issuer=None,
        )
    except httpx.HTTPError:
        raise UnauthorizedException("Unable to fetch signing keys")
    except JWTError:
        raise UnauthorizedException("Invalid or expired token")

    if not isinstance(payload, dict):
        raise UnauthorizedException("Invalid token payload")

    # Issuer validation (tolerant to trailing slashes)
    if settings.SUPABASE_ISSUER:
        expected_iss = settings.SUPABASE_ISSUER.rstrip("/")
        actual_iss = str(payload.get("iss") or "").rstrip("/")
        if not actual_iss or actual_iss != expected_iss:
            raise UnauthorizedException("Invalid token issuer")

    return payload
