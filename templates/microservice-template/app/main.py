from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import router as api_router
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

# Create database tables
Base.metadata.create_all(bind=engine)

def create_application() -> FastAPI:
    """Factory function to create and configure the FastAPI application"""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    # Set CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add GZip compression
    application.add_middleware(GZipMiddleware, minimum_size=1000)

    # Setup OpenTelemetry instrumentation
    FastAPIInstrumentor.instrument_app(application, tracer_provider=settings.TRACER_PROVIDER)

    # Setup Prometheus metrics
    Instrumentator().instrument(application).expose(application)

    # Include API routers
    application.include_router(api_router, prefix=settings.API_V1_STR)

    # Health check endpoint
    @application.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return application


app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)