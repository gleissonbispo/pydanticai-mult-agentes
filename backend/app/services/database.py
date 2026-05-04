from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings


# Engine: a "conexão principal" com o banco
engine = create_async_engine(
    settings.database_url.get_secret_value(),
    echo=False,  # True = imprime todo SQL no console (útil pra debug)
    pool_size=5,
    max_overflow=10,
)

# Factory de sessões
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_db() -> AsyncIterator[AsyncSession]:
    """Context manager que dá uma sessão de banco e fecha no final."""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()