from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, timezone
import uuid


# --------------------
# User-related models
# --------------------

class UserCreate(BaseModel):
    """
    Data model for creating a new user.
    """
    user_name: Optional[str] = Field(default_factory=lambda: f"dear_guest_{str(uuid.uuid4())[:24]}")
    password: str
    email: Optional[EmailStr] = None


class UserRead(BaseModel):
    """
    Data model for reading user information.
    """
    id: str
    user_name: str
    email: Optional[EmailStr] = None

    # Optional personal info
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None


class UserUpdate(BaseModel):
    """
    Data model for updating user information.
    """
    user_name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None

    # Optional personal info
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None



# --------------------
# Conversation-related models
# --------------------




