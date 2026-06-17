from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.users import UsersTable
from backend.schemas.auth import UserCreate


async def get_user_by_email(db: AsyncSession, email: str) -> UsersTable | None:
    """Fetch a user by email."""
    result = await db.execute(select(UsersTable).where(UsersTable.email == email))
    return result.scalars().first()


async def create_new_user_record(
    db: AsyncSession, payload: UserCreate
) -> UsersTable | None:
    """Create a new user record in the database."""
    user = UsersTable(
        name=payload.name,
        last_name=payload.last_name,
        email=payload.email,
        password=payload.password,
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return user
