from pydantic import BaseModel, Field
from enum import StrEnum


class Token(BaseModel):
    """Schema for JWT token."""

    access_token: str
    token_type: str


class TokenType(StrEnum):
    """Enum for JWT token type."""

    ACCESS = "access"
    REFRESH = "refresh"


class TokenData(BaseModel):
    """Schema for data stored in JWT token."""

    sub: str
    email: str
    name: str
    last_name: str
    exp: int | None = None
    token_type: TokenType | None = None


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    name: str = Field(..., description="User name")
    last_name: str = Field(..., description="User last name")
    email: str = Field(..., description="User e-mail address")
    password: str = Field(..., description="User password")


class UserRead(BaseModel):
    """Schema for reading a user record."""

    id: str = Field(..., description="ID of the user")
    name: str = Field(..., description="User name")
    last_name: str = Field(..., description="User last name")
    email: str = Field(..., description="User e-mail address")
