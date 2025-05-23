"""
Main FastAPI application.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from rodrunner.models.config import AppConfig
from rodrunner.api.dependencies import get_app_config
from rodrunner.api.routers import metadata, workflows


def create_app(config: AppConfig) -> FastAPI:
    """
    Create the FastAPI application.
    
    Args:
        config: Application configuration
        
    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="iRODS Prefect API",
        description="API for Rodrunner",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(metadata.router)
    app.include_router(workflows.router)
    
    @app.get("/")
    async def root():
        return {"message": "Welcome to the iRODS Prefect API"}
    
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    return app


app = create_app(get_app_config())


if __name__ == "__main__":
    import uvicorn
    
    config = get_app_config()
    uvicorn.run(
        "rodrunner.api.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.debug
    )
