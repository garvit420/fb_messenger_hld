"""Authentication API routes."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.sqlite_client import get_db
from app.controllers.auth_controller import AuthController
from app.schemas.user import UserCreate, UserResponse, TokenResponse, UserLogin

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def get_auth_controller() -> AuthController:
    """Dependency to get AuthController instance."""
    return AuthController()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    controller: AuthController = Depends(get_auth_controller),
):
    """Register a new user account."""
    return await controller.register(db, user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    controller: AuthController = Depends(get_auth_controller),
):
    """Login and get JWT access token."""
    login_data = UserLogin(username=form_data.username, password=form_data.password)
    return await controller.login(db, login_data)
