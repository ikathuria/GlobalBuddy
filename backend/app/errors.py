from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from fastapi import Request, status
from fastapi.responses import JSONResponse


@dataclass
class ErrorEnvelope:
    code: str
    message: str
    trace_id: str

    def as_dict(self) -> dict:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "trace_id": self.trace_id,
            }
        }


class ApiError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        trace_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.trace_id = trace_id or str(uuid4())


def trace_id_from_request(request: Request) -> str:
    return getattr(request.state, "trace_id", str(uuid4()))


def api_error_response(
    code: str, message: str, trace_id: str, status_code: int
) -> JSONResponse:
    envelope = ErrorEnvelope(code=code, message=message, trace_id=trace_id)
    return JSONResponse(status_code=status_code, content=envelope.as_dict())
