# Deploying to Render

This guide covers deploying the FastAPI app with PostgreSQL on Render's free tier.

## Why Render?

- **No credit card required** for the free tier
- **Managed PostgreSQL** with automatic backups
- **Auto-scaling** & built-in HTTPS
- **Simple GitHub integration** – deploys on every push

## Prerequisites

1. **GitHub account** with this repo pushed to it
2. **Render account** (free signup at https://render.com)
3. **Generate a strong SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

## Deployment Steps

### Step 1: Create the PostgreSQL Database

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **PostgreSQL**
3. Fill in:
   - **Name**: `myapp-db`
   - **Database**: `myapp`
   - **User**: `myappuser` (Render doesn't allow `postgres`)
   - **Region**: Choose closest to your users
   - **Plan**: Free
4. Click **Create Database**
5. **Copy the connection string** (you'll need it in Step 3)

### Step 2: Create the Web Service

1. Click **New +** → **Web Service**
2. **Connect your GitHub repo**:
   - Click "Connect account" if needed
   - Search for your repo
   - Click **Connect**
3. Fill in:
   - **Name**: `myapp`
   - **Region**: Same as database (Step 1)
   - **Branch**: `main` (or your default branch)
   - **Runtime**: `Python 3`
   - **Build Command**: Leave empty (Render reads from `render.yaml`)
   - **Start Command**: Leave empty (Render reads from `render.yaml`)
   - **Plan**: Free or Starter ($7/month for 24/7 uptime)
4. Click **Create Web Service**

### Step 3: Set Environment Variables

Render dashboard → Your Web Service → **Environment**:

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | Paste from Step 1 | Update `postgresql://` to `postgresql+asyncpg://` |
| `ENVIRONMENT` | `prod` | |
| `DEBUG` | `false` | |
| `SECRET_KEY` | *(generated in Prerequisites)* | **Keep this secret!** |
| `CORS_ORIGINS` | `["https://yourdomain.com"]` | Update to your frontend domain |

### Step 4: Deploy

1. Back in the Web Service page, click **Manual Deploy** → **Deploy latest commit**
   - Or just push to GitHub; Render auto-deploys
2. Watch the **Deploy Logs** for build/migration output
3. Once live, click the service URL to test the health endpoint:
   ```
   https://myapp-onrender.com/api/v1/health
   ```

## Updating the App

Just push to GitHub:
```bash
git add .
git commit -m "your change"
git push origin main
```

Render automatically rebuilds and deploys within ~2–3 minutes.

## Common Issues

### Cold Starts (Free Tier Only)

- Render spins down free services after 15 min of inactivity
- First request takes ~30 seconds to wake up
- **Solution**: Upgrade to **Starter** plan ($7/month) for 24/7 uptime

### Migrations Fail on Deploy

Check the **Build Logs**:
```
alembic upgrade head
```

If you see an async error, ensure `alembic/env.py` has:
```python
from app.config import get_settings

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

✓ *This is already configured in your project.*

### Database Connection Error

Verify in **Environment** that `DATABASE_URL` is:
- From Postgres service creation (Step 1)
- Updated to use `postgresql+asyncpg://` (not just `postgresql://`)
- Copied exactly without typos

### Secrets Exposed?

If you accidentally commit a real `SECRET_KEY` or `DATABASE_URL`:
1. Regenerate the Postgres password in Render dashboard
2. Rotate the `SECRET_KEY` immediately
3. Never commit `.env` files; use `.env.example` only

## Custom Domain (Optional)

1. In Web Service → **Settings** → **Custom Domains**
2. Add your domain (e.g., `api.myapp.com`)
3. Update your domain registrar DNS to point to Render
4. Render provisions free HTTPS with Let's Encrypt ✓

## Scaling Beyond Free Tier

| Tier | Cost | Purpose |
|------|------|---------|
| **Free** | $0 | Testing, hobby projects |
| **Starter** | $7/mo | Production, always-on |
| **Standard** | $12/mo | Higher CPU/memory |
| **Pro** | $19/mo | Team features, SLA |

To upgrade: Web Service → **Settings** → **Plan** → Select tier

## Database Backups

Render's PostgreSQL automatically backs up daily. To restore:
1. Postgres service → **Settings** → **Backups**
2. Choose a backup point
3. Click **Restore**

## Next Steps

1. Add custom domain (optional)
2. Configure CORS for your frontend domain
3. Test all endpoints: `/api/v1/health`, `/api/v1/auth/register`, etc.
4. Monitor logs in Render dashboard

For more info: https://docs.render.com
