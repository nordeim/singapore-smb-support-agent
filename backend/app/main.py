"""FastAPI main application for Singapore SMB Support Agent."""

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.api.routes import chat, auth
from app.models.schemas import HealthCheckResponse, ErrorResponse
from app.dependencies import engine
from app.models.database import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    try:
        await init_database()
        yield
    finally:
        await close_database()


async def init_database():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_database():
    """Close database connections."""
    await engine.dispose()


app = FastAPI(
    title="Singapore SMB Support Agent",
    description="AI-powered customer support agent for Singapore Small and Medium Enterprises",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """Handle request validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            detail="Validation error",
            error_code="VALIDATION_ERROR",
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    """Handle general exceptions."""
    if settings.DEBUG:
        import traceback

        traceback.print_exc()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail="Internal server error",
            error_code="INTERNAL_ERROR",
        ).model_dump(),
    )


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log HTTP requests and responses."""
    start_time = datetime.utcnow()

    response = await call_next(request)

    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000

    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = (
        request.state.request_id if hasattr(request.state, "request_id") else "unknown"
    )

    return response


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Add unique request ID to each request."""
    from uuid import uuid4

    request_id = str(uuid4())
    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "name": "Singapore SMB Support Agent",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs" if settings.DEBUG else None,
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        services={
            "api": "operational",
            "database": "operational",
            "redis": "operational",
            "qdrant": "operational",
        },
    )


app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )
