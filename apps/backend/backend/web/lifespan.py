from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.exc import IntegrityError

from backend.db.meta import meta
from backend.db.models import load_all_models
from backend.settings import settings


def _setup_db(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    Args:
        app: fastAPI application.
    """
    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory


async def _create_tables() -> None:  # pragma: no cover
    """Populates tables in the database."""
    load_all_models()
    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as connection:
        await connection.run_sync(meta.create_all)
    await engine.dispose()


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup global exception handlers for the application."""

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Database integrity error",
                "error": str(exc.orig),
            },
        )


@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    Args:
        app: the fastAPI application.

    Returns:
        Function that actually performs actions.
    """

    app.middleware_stack = None
    _setup_db(app)
    await _create_tables()

    if settings.environment == "prod" or settings.environment == "dev":
        # app.middleware_stack = app.build_middleware_stack()
        # elif settings.environment == "dev":
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],  # GET, POST, PUT, DELETE, OPTIONS
            allow_headers=["*"],  # Content-Type, Authorization itd.
        )

    yield
    await app.state.db_engine.dispose()
