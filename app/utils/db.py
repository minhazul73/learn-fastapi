"""Database-related helpers.

This project uses SQLAlchemy async with the asyncpg driver.

Supabase frequently sits behind PgBouncer (especially when using the
`pooler.supabase.com:6543` endpoint). In that mode, asyncpg's statement
cache / prepared statements can cause errors. We also need SSL for
Supabase-hosted Postgres.
"""

from __future__ import annotations

import ssl
import socket
from urllib.parse import urlparse


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

    # Supabase requires TLS for external connections.
    if "supabase.com" in host:
        connect_args["ssl"] = ssl.create_default_context()
        # Render commonly has no IPv6 route; Supabase DNS may return IPv6 first.
        # Force IPv4 to avoid `[Errno 101] Network is unreachable` during connect.
        connect_args["family"] = socket.AF_INET

    # Supabase's pooler endpoint uses PgBouncer; prepared statements can break.
    # Port 6543 is the common Supabase pooler port.
    if port == 6543 or host.endswith(".pooler.supabase.com"):
        connect_args["statement_cache_size"] = 0

    return connect_args
