from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import src.model as model_module
from src.config import Settings
from src.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    model_module.load_model(settings)
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Flatten pydantic errors into a single message string
    messages = "; ".join(
        f"{' -> '.join(str(l) for l in e['loc'])}: {e['msg']}"
        for e in exc.errors()
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "message": messages,
                "type": "invalid_request_error",
                "code": "invalid_request",
            }
        },
    )


app.include_router(router, prefix="/v1")
