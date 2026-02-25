import logging
import time

logger = logging.getLogger("apps.monitoramento")


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started = time.perf_counter()
        response = self.get_response(request)
        duration_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "request_timing path=%s method=%s status=%s duration_ms=%.2f",
            request.path,
            request.method,
            response.status_code,
            duration_ms,
        )
        return response
