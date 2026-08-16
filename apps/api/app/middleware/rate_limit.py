import re
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

DOWNLOAD_PATH_PATTERN = re.compile(r"^/api/resources/\d+/download$")
WINDOW_SECONDS = 60


class DownloadRateLimitMiddleware(BaseHTTPMiddleware):
    """Fine-grained per-IP fixed-window limiter for the download endpoint.

    nginx already applies coarse per-IP limiting in front of this app; this is
    the application layer that enforces the exact per-minute download budget.
    State is in-memory, so it is per-process and resets on restart.
    """

    def __init__(self, app, limit_per_minute: int):
        super().__init__(app)
        self.limit = limit_per_minute
        # ip -> (window_start_epoch, request_count)
        self._hits: dict[str, tuple[int, int]] = {}

    async def dispatch(self, request: Request, call_next):
        if not DOWNLOAD_PATH_PATTERN.match(request.url.path):
            return await call_next(request)

        client_ip = self._client_ip(request)
        window = int(time.time() // WINDOW_SECONDS)
        window_start, count = self._hits.get(client_ip, (window, 0))
        if window_start != window:
            count = 0
        count += 1
        self._hits[client_ip] = (window, count)

        if count > self.limit:
            return JSONResponse(
                status_code=429, content={"detail": "Download rate limit exceeded"}
            )
        return await call_next(request)

    @staticmethod
    def _client_ip(request: Request) -> str:
        # Behind nginx reverse proxy the real client IP arrives via X-Forwarded-For.
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
