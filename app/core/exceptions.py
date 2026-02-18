"""
Centralised exception handling.
All HTTP errors returned in a consistent JSON shape.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.utils.response import error_response

logger = logging.getLogger(__name__)


# ── Custom exceptions ─────────────────────────────────────
class AppException(Exception):
    """Base for all application-level errors."""

    def __init__(self, status_code: int = 400, detail: str = "Bad request"):
        self.status_code = status_code
        self.detail = detail


class NotFoundException(AppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(status_code=404, detail=f"{resource} not found")


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(status_code=403, detail=detail)


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=409, detail=detail)


# ── Register handlers on the app ─────────────────────────
def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                message=exc.detail,
                response_code=exc.status_code,
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content=error_response(
                message="Internal server error",
                response_code=500,
            ),
        )
