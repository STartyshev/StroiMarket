from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config import settings

async_engine = create_async_engine(settings.ASYNCPG_DATABASE_URL)
async_session_maker = async_sessionmaker(async_engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass
