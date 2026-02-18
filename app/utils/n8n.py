"""
n8n webhook integration helper.
Call n8n workflows from your FastAPI backend.

Usage:
    from app.utils.n8n import trigger_webhook

    result = await trigger_webhook("on-new-order", {"order_id": 123})
"""

import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def trigger_webhook(
    webhook_path: str,
    payload: dict,
    *,
    timeout: float = 10.0,
) -> dict | None:
    """
    POST to an n8n webhook workflow.

    Args:
        webhook_path: The path segment after the base webhook URL
                      (e.g. "on-new-order").
        payload:      JSON-serialisable dict sent as the request body.
        timeout:      HTTP timeout in seconds.

    Returns:
        Parsed JSON response from n8n, or None if n8n is not configured.
    """
    if not settings.N8N_WEBHOOK_URL:
        logger.debug("n8n not configured – skipping webhook %s", webhook_path)
        return None

    url = f"{settings.N8N_WEBHOOK_URL.rstrip('/')}/{webhook_path}"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if settings.N8N_API_KEY:
        headers["Authorization"] = f"Bearer {settings.N8N_API_KEY}"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url, json=payload, headers=headers, timeout=timeout
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as exc:
        logger.error("n8n webhook %s failed: %s", webhook_path, exc)
        return None
