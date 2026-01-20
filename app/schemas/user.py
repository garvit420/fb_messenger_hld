"""Pydantic schemas for user-related operations."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=6)
    display_name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserStatusUpdate(BaseModel):
    """Schema for updating user online status."""
    is_online: bool


class UserResponse(BaseModel):
    """Schema for user response (public info)."""
    id: int
    email: EmailStr
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_online: bool
    last_seen_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfileResponse(UserResponse):
    """Schema for detailed user profile response."""
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""
    user_id: Optional[int] = None
