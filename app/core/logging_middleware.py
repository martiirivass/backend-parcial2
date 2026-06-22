import logging
import time
import uuid

logger = logging.getLogger(__name__)

SENSITIVE_HEADERS = frozenset({"authorization", "cookie", "x-api-key", "set-cookie"})


class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        method = scope["method"]
        path = scope["path"]
        query = scope["query_string"]
        client = scope.get("client")
        client_ip = f"{client[0]}:{client[1]}" if client else "unknown"

        raw_headers = dict(scope.get("headers", []))
        user_agent = raw_headers.get(b"user-agent", b"").decode("latin-1", errors="replace") or "-"
        request_id = raw_headers.get(b"x-request-id", b"").decode("ascii", errors="ignore") or str(uuid.uuid4())

        status_code = [None]
        logged = [False]

        async def wrapped_send(message):
            if message["type"] == "http.response.start":
                status_code[0] = message["status"]
            await send(message)
            is_last = message["type"] == "http.response.body" and not message.get("more_body", True)
            if is_last:
                self._log(method, path, query, client_ip, user_agent, request_id, start, status_code[0])
                logged[0] = True

        response = await self.app(scope, receive, wrapped_send)

        if not logged[0]:
            self._log(method, path, query, client_ip, user_agent, request_id, start, status_code[0] or 500)

        return response

    def _log(self, method, path, query, client_ip, user_agent, request_id, start, status):
        duration = (time.perf_counter() - start) * 1000
        qs = f"?{query.decode('latin-1')}" if query else ""
        level = logging.ERROR if status >= 500 else logging.WARNING if status >= 400 else logging.INFO
        logger.log(
            level,
            "%d %s %s%s %.1fms %s %s %s",
            status, method, path, qs, duration, client_ip, user_agent, request_id,
        )
