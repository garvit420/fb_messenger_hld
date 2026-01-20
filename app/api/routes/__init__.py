"""API routes package."""
from app.api.routes.message_routes import router as message_router
from app.api.routes.conversation_routes import router as conversation_router
from app.api.routes.auth_routes import router as auth_router
from app.api.routes.user_routes import router as user_router

__all__ = ["message_router", "conversation_router", "auth_router", "user_router"]
