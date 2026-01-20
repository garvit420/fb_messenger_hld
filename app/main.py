"""FastAPI application entry point with SQLite backend."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.message_routes import router as message_router
from app.api.routes.conversation_routes import router as conversation_router
from app.api.routes.auth_routes import router as auth_router
from app.api.routes.user_routes import router as user_router
from app.db.sqlite_client import init_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Initializing application...")
    init_db()
    logger.info("SQLite database initialized")
    yield
    # Shutdown
    logger.info("Shutting down application...")
    close_db()


app = FastAPI(
    title="FB Messenger API",
    description="Backend API for FB Messenger implementation with SQLite and JWT authentication",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(message_router)
app.include_router(conversation_router)


@app.get("/")
async def root():
    """Root endpoint returning API status."""
    return {"message": "FB Messenger API is running with SQLite backend"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
