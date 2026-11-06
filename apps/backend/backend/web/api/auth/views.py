from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pwdlib import PasswordHash
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from backend.db.repositories.users_repository import (
    get_user_by_email,
    create_new_user_record,
)
from backend.schemas.auth import UserCreate, UserRead, TokenData, Token
from backend.web.api.auth.services import (
    verify_password,
    create_access_token,
    get_current_user,
)
from backend.db.dependencies import get_db_session


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=201, response_model=Token)
async def signup_user(
    response: Response,
    payload: UserCreate,
    db_session: AsyncSession = Depends(get_db_session),
) -> Token:
    """Create and authorize a new user."""

    user = await get_user_by_email(db_session, payload.email)
    if user:
        raise HTTPException(
            status_code=409,
            detail="User with this email already exist",
        )

    password_hasher = PasswordHash.recommended()

    user = await create_new_user_record(
        db_session,
        UserCreate(
            name=payload.name,
            last_name=payload.last_name,
            email=payload.email,
            password=password_hasher.hash(payload.password),
        ),
    )

    claims = TokenData(
        sub=user.id, email=user.email, name=user.name, last_name=user.last_name
    )

    return Token(access_token=create_access_token(claims), token_type="bearer")  # noqa: S106


@router.post("/login", status_code=200, response_model=Token)
async def login_user(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: AsyncSession = Depends(get_db_session),
) -> Token:
    """Authorize a user and return an access token and refresh token."""

    user = await get_user_by_email(db_session, form_data.username)

    if not user or not verify_password(
        plain_password=form_data.password,
        hashed_password=user.password,
    ):
        raise HTTPException(
            status_code=404,
            detail="Invalid credentials",
        )

    claims = TokenData(
        sub=user.id, email=user.email, name=user.name, last_name=user.last_name
    )

    return Token(access_token=create_access_token(claims), token_type="bearer")  # noqa: S106


@router.get("/me", status_code=200, response_model=UserRead)
async def get_me(
    current_user: UserRead = Depends(get_current_user),
) -> UserRead:
    """Get the current authorized user."""
    return current_user
