"""API module initialization."""
from api.roles import router as roles_router
from api.rules import router as rules_router
from api.sessions import router as sessions_router
from api.templates import router as templates_router
from api.history import router as history_router
from api.ws import router as ws_router

__all__ = [
    "roles_router",
    "rules_router",
    "sessions_router",
    "templates_router",
    "history_router",
    "ws_router",
]
