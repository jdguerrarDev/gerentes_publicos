from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg://postgres:101310@localhost:5432/gerentesPublicos"
    )

    class Config:
        env_file = ".env"


settings = Settings()

# Engine asincrónico
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
