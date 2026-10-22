from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import AIRuntimeException


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AIRuntimeException)
    async def ai_runtime_exception_handler(request: Request, exc: AIRuntimeException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
