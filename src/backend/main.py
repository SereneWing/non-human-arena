"""Main application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import (
    history_router,
    roles_router,
    rules_router,
    sessions_router,
    templates_router,
    ws_router,
)
from core import EventBus, LocalEventBus
from events import register_handlers
from infrastructure import DatabaseManager, get_config
from utils import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    setup_logging()
    logger.info("Starting NonHumanArena...")
    
    config = get_config()
    
    db_manager = DatabaseManager(config.database.url)
    await db_manager.initialize()
    await db_manager.create_tables()
    
    event_bus: EventBus = LocalEventBus()
    await event_bus.start()
    register_handlers(event_bus)
    
    app.state.db_manager = db_manager
    app.state.event_bus = event_bus
    
    logger.info("NonHumanArena started successfully")
    
    yield
    
    logger.info("Shutting down NonHumanArena...")
    await event_bus.stop()
    await db_manager.close()
    logger.info("NonHumanArena shutdown complete")


def create_app() -> FastAPI:
    """Create FastAPI application."""
    config = get_config()
    
    app = FastAPI(
        title="NonHumanArena API",
        description="AI-driven multi-agent debate and discussion platform",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    api_prefix = config.api_prefix
    app.include_router(roles_router, prefix=api_prefix)
    app.include_router(rules_router, prefix=api_prefix)
    app.include_router(sessions_router, prefix=api_prefix)
    app.include_router(templates_router, prefix=api_prefix)
    app.include_router(history_router, prefix=api_prefix)
    app.include_router(ws_router)
    
    @app.get("/")
    async def root():
        return {"message": "Welcome to NonHumanArena API"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
