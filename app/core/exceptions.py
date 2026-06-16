from http import HTTPStatus

from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse

_STATUS_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    422: "validation_error",
    429: "too_many_requests",
    500: "internal_error",
}


def rfc7807_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    field = None

    if isinstance(detail, dict):
        field = detail.get("field")
        detail = detail.get("msg", detail)

    body = {
        "type": f"https://httpstatuses.org/{exc.status_code}",
        "title": HTTPStatus(exc.status_code).phrase,
        "status": exc.status_code,
        "detail": detail,
        "code": _STATUS_CODES.get(exc.status_code, "unknown"),
    }

    if field:
        body["field"] = field

    return JSONResponse(
        status_code=exc.status_code,
        content=body,
        media_type="application/problem+json",
    )
