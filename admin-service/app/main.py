from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from app.api.routes import domain, application
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.events.consumers import domain_events, application_events
from app.events.kafka_client import KAFKA_ENABLED

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Admin Service API for ZCare Platform",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(domain.router, prefix=settings.API_V1_STR)
app.include_router(application.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to ZCare Admin Service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Event consumers startup and shutdown
@app.on_event("startup")
async def startup_event_consumers():
    print("Starting admin service startup process...")
    
    # Temporarily disable event consumers to test uvicorn startup
    print("Event consumers temporarily disabled for testing")
    app.state.event_consumers_running = False
    
    # Signal that the application has fully started
    print("Application startup complete - uvicorn should now start listening")
    print("Startup event handler finished")

@app.on_event("shutdown")
async def shutdown_event_consumers():
    # Cancel event consumer tasks
    try:
        if hasattr(app.state, 'event_consumers_running') and app.state.event_consumers_running:
            # Cancel the background tasks
            if hasattr(app.state, 'domain_consumer_task'):
                app.state.domain_consumer_task.cancel()
            if hasattr(app.state, 'application_consumer_task'):
                app.state.application_consumer_task.cancel()
            
            app.state.event_consumers_running = False
            print("Event consumer tasks cancelled")
    except Exception as e:
        print(f"Warning: Error during event consumer shutdown: {str(e)}")
        print("Application will continue to shut down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)