# MyApp API

Production-ready FastAPI backend for a mobile app, optimised for **Oracle Cloud free tier** (1 OCPU / 1 GB RAM).

## Architecture

```
app/
├── main.py                 # FastAPI app factory + lifespan
├── config.py               # Pydantic-settings (env-based config)
├── database.py             # Async SQLAlchemy engine + session
├── api/
│   ├── deps.py             # Shared deps (get_current_user, etc.)
│   └── v1/
│       ├── router.py       # v1 aggregate router
│       └── endpoints/
│           ├── health.py   # Health check (Docker + LB)
│           ├── auth.py     # Register / Login / Refresh / Me
│           └── items.py    # CRUD example
├── models/                 # SQLAlchemy ORM models
│   ├── base.py             # DeclarativeBase + TimestampMixin
│   ├── item.py
│   └── user.py
├── schemas/                # Pydantic request/response schemas
│   ├── base.py             # MessageResponse, PaginatedResponse
│   ├── item.py
│   └── auth.py
├── services/               # Business logic layer
│   ├── item.py
│   └── auth.py
├── core/
│   ├── security.py         # JWT + bcrypt utilities
│   └── exceptions.py       # Custom exceptions + global handlers
└── utils/
    └── n8n.py              # n8n webhook helper (future use)

alembic/                    # Database migrations (async-aware)
scripts/                    # start.sh, prestart.sh
docker-compose*.yml         # Dev / Stage / Prod compose files
Dockerfile                  # Multi-stage, ~120 MB final image
Makefile                    # Common commands
```

## Key Design Decisions

| Area | Choice | Why |
|------|--------|-----|
| Async | SQLAlchemy 2.0 + asyncpg | Non-blocking I/O; fewer workers = less RAM |
| Workers | 1 gunicorn + uvicorn worker | Oracle free tier has 1 OCPU / 1 GB |
| DB Pool | 5 connections, 0 overflow | Bounded memory |
| Auth | JWT (access + refresh tokens) | Stateless; ideal for mobile apps |
| API versioning | `/api/v1/` prefix | Backward compatibility for shipped apps |
| Migrations | Alembic (async) | Schema versioning without downtime |
| Config | pydantic-settings + `.env` | Same code, different env files per stage |
| Docker | Multi-stage slim build | ~120 MB vs ~1 GB |
| Docs | Auto-disabled in prod | No Swagger exposure in production |

## Quick Start

### 1. Local Development (no Docker)

```bash
# Clone & enter project
cd learn-fastapi

# Create virtualenv
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

# Install deps
pip install -r requirements.txt

# Copy & edit env
cp .env.example .env

# Make sure Postgres is running, then:
alembic upgrade head        # apply migrations
uvicorn app.main:app --reload
```

### 2. Docker Development

```bash
# Start app + Postgres
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# (Optional) include pgAdmin
docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile debug up
```

### 3. Production: Render (Recommended - No Credit Card Required)

**Deploy with automatic GitHub integration, managed PostgreSQL, and free HTTPS.**

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for step-by-step instructions.

Quick summary:
- Create PostgreSQL service (free tier available)
- Connect GitHub repo to Web Service
- Set environment variables in Render dashboard
- Done! Auto-deploys on every `git push`

**Why Render over Oracle?**
- No credit card required
- Simpler setup (no container management)
- Managed database with automatic backups
- Auto-scaling & HTTPS included

### 4. Production: Oracle Free Tier

```bash
# On the server
cp .env.example .env
# Edit .env: set ENVIRONMENT=prod, strong SECRET_KEY, real DB creds

docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

This repo includes an Nginx reverse proxy and a Certbot renewer in
`docker-compose.prod.yml` plus a sample config in `nginx/conf.d/app.conf`.

**Prereqs**

- Point your domain A record to the VM public IP
- Open inbound ports 80 and 443 in Oracle security list

**One-time cert issuance**

1) Temporarily comment out the HTTPS server block in `nginx/conf.d/app.conf`
     so Nginx can start without existing certs.
2) Start app + db + Nginx (HTTP only):

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx app db
```

3) Issue the cert (replace domain/email if needed):

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot -w /var/www/certbot \
    -d api.learn-fastapi.com \
    -m minhazul73@gmail.com \
    --agree-tos --no-eff-email
```

4) Restore the HTTPS server block and restart Nginx:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart nginx
```

**Renewals**

The `certbot` service runs `certbot renew` every 12 hours.

## Environment Files

| File | Purpose |
|------|---------|
| `.env.example` | Template – commit to git |
| `.env` | Active config – **never commit** |

Switch environments by changing `ENVIRONMENT=dev|stage|prod` in `.env`.

## Database Migrations

```bash
# Generate migration after model changes
alembic revision --autogenerate -m "add xyz table"

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/health` | No | Health check |
| POST | `/api/v1/auth/register` | No | Create account |
| POST | `/api/v1/auth/login` | No | Get tokens |
| POST | `/api/v1/auth/refresh` | No | Refresh access token |
| GET | `/api/v1/auth/me` | Yes | Current user |
| GET | `/api/v1/items` | No | List items |
| GET | `/api/v1/items/{id}` | No | Get item |
| POST | `/api/v1/items` | Yes | Create item |
| PUT | `/api/v1/items/{id}` | Yes | Update item |
| DELETE | `/api/v1/items/{id}` | Yes | Delete item |

## n8n Integration (Future)

Set `N8N_WEBHOOK_URL` and `N8N_API_KEY` in `.env`, then call from any service:

```python
from app.utils.n8n import trigger_webhook

await trigger_webhook("on-new-order", {"order_id": 123, "total": 49.99})
```

## Oracle Free Tier Deployment Notes

- **1 OCPU / 1 GB RAM** – keep workers at 1, pool at 3-5
- Use `docker-compose.prod.yml` which sets memory limits (256 MB each for app + DB)
- Postgres tuned with `shared_buffers=64MB`, `max_connections=30`
- Enable swap on the VM: `sudo fallocate -l 1G /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile`
- Use Nginx reverse proxy with free Let's Encrypt TLS (see HTTPS section above)
