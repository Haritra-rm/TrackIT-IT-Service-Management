import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        request_id = str(uuid.uuid4())[:8]

        # Attach correlation ID to request state
        request.state.request_id = request_id

        client_host = request.client.host if request.client else "unknown"
        logger.info(f"[{request_id}] --> {request.method} {request.url.path} (from {client_host})")

        response = await call_next(request)

        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"[{request_id}] <-- {request.method} {request.url.path} - Status: {response.status_code} ({duration_ms}ms)")

        response.headers["X-Request-ID"] = request_id
        return response
