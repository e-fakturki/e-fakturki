from pwdlib import PasswordHash
import jwt
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pydantic import ValidationError, SecretStr
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer

from backend.schemas.auth import UserRead
from backend.db.models.users import UsersTable
from fastapi import Depends, HTTPException, status
from backend.schemas.auth import TokenData, TokenType
from backend.db.dependencies import get_db_session
from backend.settings import settings


SECRET_KEY: SecretStr = settings.JWT_SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", scheme_name="JWT")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    password_hasher = PasswordHash.recommended()
    return password_hasher.verify(plain_password, hashed_password)


def create_access_token(data: TokenData, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token with the given data and expiration."""
    to_encode = data.model_dump()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "token_type": TokenType.ACCESS})

    return jwt.encode(to_encode, SECRET_KEY.get_secret_value(), algorithm=ALGORITHM)


# def create_refresh_token(
#     data: TokenData, expires_delta: timedelta | None = None
# ) -> str:
#     """Create a JWT refresh token with the given data and expiration."""
#     to_encode = data.model_dump()

#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(
#             minutes=REFRESH_TOKEN_EXPIRE_DAYS
#         )

#     to_encode.update({"exp": expire, "token_type": TokenType.REFRESH})

#     return jwt.encode(to_encode, SECRET_KEY.get_secret_value(), algorithm=ALGORITHM)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db_session: AsyncSession = Depends(get_db_session),
) -> UserRead:
    """Get the current user from the JWT token."""

    try:
        payload = jwt.decode(
            token, SECRET_KEY.get_secret_value(), algorithms=[ALGORITHM]
        )

        token_data = TokenData.model_validate(payload)

    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user: UsersTable = await db_session.get(UsersTable, token_data.sub)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserRead(
        id=user.id,
        name=user.name,
        last_name=user.last_name,
        email=user.email,
    )
