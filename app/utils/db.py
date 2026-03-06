"""Database-related helpers.

This project uses SQLAlchemy async with the asyncpg driver.

Supabase frequently sits behind PgBouncer (especially when using the
`pooler.supabase.com:6543` endpoint). In that mode, asyncpg's statement
cache / prepared statements can cause errors. We also need SSL for
Supabase-hosted Postgres.
"""

from __future__ import annotations

import os
import ssl
from urllib.parse import parse_qs
from urllib.parse import urlparse

import certifi


def get_asyncpg_connect_args(database_url: str) -> dict:
    """Return `connect_args` suitable for SQLAlchemy+asyncpg.

    - Enables SSL automatically for Supabase hosts.
    - Disables asyncpg statement caching when using Supabase pooler (PgBouncer)
      to avoid prepared-statement errors.
    """

    parsed = urlparse(database_url)
    host = (parsed.hostname or "").lower()
    port = parsed.port
    query = parse_qs(parsed.query)

    connect_args: dict = {}

    is_supabase_host = (
        host.endswith(".supabase.com")
        or host.endswith(".supabase.co")
        or ".supabase." in host
    )

    is_localish_host = host in {"", "localhost", "127.0.0.1", "::1", "db"}
    env_sslmode = (os.getenv("DB_SSLMODE") or "").strip().lower()

    # Many managed Postgres providers (including Render) provide connection
    # strings with `?sslmode=require` or similar. asyncpg doesn't interpret
    # `sslmode` itself, so we translate it into an SSLContext.
    sslmode_from_url = (query.get("sslmode", [""])[0] or "").strip().lower()

    # SSL mode handling
    # - Prefer sslmode in the URL query string (common on managed DBs).
    # - Fall back to DB_SSLMODE env var for non-local hosts.
    # Supported values: disable | require | verify-ca | verify-full
    sslmode: str | None = None
    if sslmode_from_url:
        sslmode = sslmode_from_url
    elif env_sslmode and not is_localish_host:
        sslmode = env_sslmode
    elif is_supabase_host:
        sslmode = "verify-full"

    if sslmode and sslmode != "disable":
        if sslmode == "require":
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ctx
        elif sslmode == "verify-ca":
            ctx = ssl.create_default_context(cafile=certifi.where())
            ctx.check_hostname = False
            connect_args["ssl"] = ctx
        else:
            # Default to verify-full.
            ctx = ssl.create_default_context(cafile=certifi.where())
            connect_args["ssl"] = ctx

    # Optional: shorter fail-fast connect timeout (seconds)
    # Note: asyncpg's `timeout` applies to establishing the connection.
    connect_timeout = (os.getenv("DB_CONNECT_TIMEOUT_SECONDS") or "").strip()
    if connect_timeout:
        try:
            connect_args["timeout"] = float(connect_timeout)
        except ValueError:
            pass

    # Supabase's pooler endpoint uses PgBouncer; prepared statements can break.
    # Port 6543 is the common Supabase pooler port.
    if port == 6543 or host.endswith(".pooler.supabase.com"):
        connect_args["statement_cache_size"] = 0

    return connect_args
