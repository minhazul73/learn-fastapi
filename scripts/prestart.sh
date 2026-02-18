#!/usr/bin/env bash
# scripts/prestart.sh – Run before the app starts (migrations, seeding, etc.)
set -e

echo "==> Waiting for database..."
# Simple retry loop – no extra deps needed
for i in $(seq 1 30); do
    if python -c "
import asyncio, asyncpg, os
async def check():
    url = os.environ.get('DATABASE_URL', '').replace('+asyncpg', '')
    url = url.replace('postgresql://', 'postgresql://')  # strip driver
    conn = await asyncpg.connect(url.replace('postgresql+asyncpg', 'postgresql'))
    await conn.close()
asyncio.run(check())
" 2>/dev/null; then
        echo "==> Database is ready."
        break
    fi
    echo "    Waiting for database... ($i/30)"
    sleep 2
done

echo "==> Applying migrations..."
alembic upgrade head

echo "==> Pre-start complete."
