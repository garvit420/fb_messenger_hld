"""User controller for profile management operations."""

from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.sqlite_models import User
from app.schemas.user import UserUpdate, UserStatusUpdate, UserResponse, UserProfileResponse


class UserController:
    """Controller for user profile operations."""

    async def get_current_user_profile(self, user: User) -> UserProfileResponse:
        """Get the current authenticated user's profile."""
        return UserProfileResponse.model_validate(user)

    async def update_current_user_profile(
        self, db: Session, user: User, update_data: UserUpdate
    ) -> UserProfileResponse:
        """Update the current user's profile."""
        if update_data.display_name is not None:
            user.display_name = update_data.display_name
        if update_data.avatar_url is not None:
            user.avatar_url = update_data.avatar_url

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return UserProfileResponse.model_validate(user)

    async def update_user_status(
        self, db: Session, user: User, status_data: UserStatusUpdate
    ) -> UserProfileResponse:
        """Update the current user's online status."""
        user.is_online = status_data.is_online
        user.last_seen_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(user)

        return UserProfileResponse.model_validate(user)

    async def get_user_by_id(self, db: Session, user_id: int) -> UserResponse:
        """Get a user by their ID."""
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return UserResponse.model_validate(user)
