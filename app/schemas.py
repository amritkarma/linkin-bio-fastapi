from pydantic import BaseModel, EmailStr, ConfigDict, validator
from typing import List, Optional
import re

# 🔐 Auth Models

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator("password")
    def validate_password_strength(cls, value):
        """
        Enforces the following password rules:
        - At least 8 characters
        - At least one number
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one special character
        """
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"\d", value):
            raise ValueError("Password must include at least one number.")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must include at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must include at least one lowercase letter.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must include at least one special character.")
        return value

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# 🔗 Link Models

class LinkCreate(BaseModel):
    title: str
    url: str

class LinkUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None

class LinkOut(BaseModel):
    id: int
    title: str
    url: str

    model_config = ConfigDict(from_attributes=True)

# 👤 User Models

class UserOut(BaseModel):
    username: str
    email: EmailStr
    bio: Optional[str] = ""
    avatar_url: Optional[str] = ""
    links: List[LinkOut] = []

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    bio: Optional[str] = ""
    avatar_url: Optional[str] = ""

class ProfileOut(BaseModel):
    username: str
    bio: Optional[str] = ""
    avatar_url: Optional[str] = ""
    links: List[LinkOut] = []

    model_config = ConfigDict(from_attributes=True)
