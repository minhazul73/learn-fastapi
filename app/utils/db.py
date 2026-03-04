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

    connect_args: dict = {}

    is_supabase_host = (
        host.endswith(".supabase.com")
        or host.endswith(".supabase.co")
        or ".supabase." in host
    )

    # Supabase requires TLS for external connections.
    #
    # SSL mode can be overridden via env var to match common Postgres SSL modes:
    # - DB_SSLMODE=verify-full (default): verify cert chain + hostname
    # - DB_SSLMODE=require: encrypt, but DO NOT verify cert chain (less secure)
    # - DB_SSLMODE=disable: no TLS
    if is_supabase_host:
        sslmode = (os.getenv("DB_SSLMODE") or "verify-full").strip().lower()

        if sslmode != "disable":
            if sslmode == "require":
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                connect_args["ssl"] = ctx
            else:
                # Use certifi's CA bundle for consistent verification in containers.
                ctx = ssl.create_default_context(cafile=certifi.where())
                connect_args["ssl"] = ctx

    # Supabase's pooler endpoint uses PgBouncer; prepared statements can break.
    # Port 6543 is the common Supabase pooler port.
    if port == 6543 or host.endswith(".pooler.supabase.com"):
        connect_args["statement_cache_size"] = 0

    return connect_args
