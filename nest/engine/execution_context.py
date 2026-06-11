from __future__ import annotations

from typing import Any, Optional


class HttpExecutionContext:
    def __init__(self, request: Any, response: Optional[Any] = None) -> None:
        self._request = request
        self._response = response

    def get_request(self) -> Any:
        return self._request

    def get_response(self) -> Optional[Any]:
        return self._response


class ExecutionContext:
    def __init__(self, request: Any, response: Optional[Any] = None) -> None:
        self._request = request
        self._response = response

    def switch_to_http(self) -> HttpExecutionContext:
        return HttpExecutionContext(self._request, self._response)

    def get_type(self) -> str:
        return "http"


__all__ = ["ExecutionContext", "HttpExecutionContext"]
