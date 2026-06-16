from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse


def http_error(
    status_code: int,
    detail: str,
    code: str,
    field: str | None = None,
) -> HTTPException:
    """Lanza HTTPException con formato RFC 7807."""
    content = {
        "detail": detail,
        "code": code,
    }
    if field:
        content["field"] = field
    return HTTPException(status_code=status_code, detail=content)


async def rfc7807_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """Global exception handler que serializa HTTPException en formato RFC 7807."""
    detail = exc.detail
    if not isinstance(detail, dict):
        detail = {"detail": detail, "code": "UNKNOWN_ERROR"}
    return JSONResponse(
        status_code=exc.status_code,
        content=detail,
        headers=getattr(exc, "headers", None) or {},
    )
