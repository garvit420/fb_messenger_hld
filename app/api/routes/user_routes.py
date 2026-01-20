"""User profile API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.sqlite_client import get_db
from app.core.dependencies import get_current_user
from app.controllers.user_controller import UserController
from app.models.sqlite_models import User
from app.schemas.user import UserUpdate, UserStatusUpdate, UserResponse, UserProfileResponse

router = APIRouter(prefix="/api/users", tags=["Users"])


def get_user_controller() -> UserController:
    """Dependency to get UserController instance."""
    return UserController()


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
):
    """Get the current authenticated user's profile."""
    return await controller.get_current_user_profile(current_user)


@router.put("/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
):
    """Update the current user's profile (display name, avatar)."""
    return await controller.update_current_user_profile(db, current_user, update_data)


@router.put("/me/status", response_model=UserProfileResponse)
async def update_user_status(
    status_data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
):
    """Update the current user's online status."""
    return await controller.update_user_status(db, current_user, status_data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
):
    """Get a user by their ID."""
    return await controller.get_user_by_id(db, user_id)
