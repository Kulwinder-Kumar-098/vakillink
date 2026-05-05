"""
app/middleware/error_handler.py
================================
Global exception middleware for VakeelLink.

Catches every unhandled exception that escapes route handlers and returns
a consistent JSON error envelope instead of a raw 500 HTML page or a
stack-trace leak.

Error envelope schema
---------------------
{
    "error":   true,
    "status":  <http_status_code>,
    "message": "<human-readable message>",
    "detail":  "<extra context — only present in non-production>",
    "path":    "<request path>"
}
"""

import logging
import traceback
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("vakeellink.errors")


# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────

def _env_is_production() -> bool:
    """Suppress stack traces in production."""
    import os
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def _error_response(
    status_code: int,
    message: str,
    detail: str | None = None,
    path: str = "",
) -> JSONResponse:
    body: dict = {
        "error":   True,
        "status":  status_code,
        "message": message,
        "path":    path,
    }
    if detail and not _env_is_production():
        body["detail"] = detail
    return JSONResponse(status_code=status_code, content=body)


# ─────────────────────────────────────────────────────────────────────────────
# Registration helper — call this from main.py
# ─────────────────────────────────────────────────────────────────────────────

def register_error_handlers(app: FastAPI) -> None:
    """
    Attach all exception handlers to the FastAPI app.
    Call BEFORE including routers so handlers are in place early.
    """

    # ── 1. FastAPI / Starlette HTTP exceptions (e.g. HTTPException(404)) ─────
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(
            "HTTP %s | %s %s | %s",
            exc.status_code, request.method, request.url.path, exc.detail
        )
        return _error_response(
            status_code=exc.status_code,
            message=_status_message(exc.status_code),
            detail=str(exc.detail),
            path=request.url.path,
        )

    # ── 2. Pydantic validation errors (422 Unprocessable Entity) ─────────────
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Flatten Pydantic's nested error list into a readable string
        errors = "; ".join(
            f"{'.'.join(str(l) for l in e['loc'])}: {e['msg']}"
            for e in exc.errors()
        )
        logger.warning(
            "Validation error | %s %s | %s",
            request.method, request.url.path, errors
        )
        return _error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Request validation failed. Check your request body or query parameters.",
            detail=errors,
            path=request.url.path,
        )

    # ── 3. Catch-all for unhandled Python exceptions ──────────────────────────
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        tb = traceback.format_exc()
        logger.error(
            "Unhandled exception | %s %s\n%s",
            request.method, request.url.path, tb
        )
        return _error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred. Our team has been notified.",
            detail=tb if not _env_is_production() else None,
            path=request.url.path,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Human-readable status messages
# ─────────────────────────────────────────────────────────────────────────────

def _status_message(code: int) -> str:
    return {
        400: "Bad request. Please check the data you sent.",
        401: "Authentication required. Please log in.",
        403: "You do not have permission to perform this action.",
        404: "The requested resource was not found.",
        405: "HTTP method not allowed on this endpoint.",
        409: "A conflict occurred. The resource may already exist.",
        422: "The request data failed validation.",
        429: "Too many requests. Please slow down.",
        500: "Internal server error.",
        502: "Bad gateway. Upstream service error.",
        503: "Service temporarily unavailable. Please try again shortly.",
    }.get(code, f"HTTP error {code}")
