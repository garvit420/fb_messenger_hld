"""Authentication controller for user registration and login."""
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.sqlite_models import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token


class AuthController:
    """Controller for authentication operations."""

    async def register(self, db: Session, user_data: UserCreate) -> UserResponse:
        """Register a new user."""
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Check if username already exists
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password,
            display_name=user_data.display_name or user_data.username,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserResponse.model_validate(new_user)

    async def login(self, db: Session, login_data: UserLogin) -> TokenResponse:
        """Authenticate user and return JWT token."""
        # Find user by username
        user = db.query(User).filter(User.username == login_data.username).first()

        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last seen
        user.last_seen_at = datetime.utcnow()
        user.is_online = True
        db.commit()

        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})

        return TokenResponse(access_token=access_token)
