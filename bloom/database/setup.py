from settings import DATABASE_URL, DEV
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .tables import create_tables

AsyncSessionLocal = async_sessionmaker(expire_on_commit=False)


def get_async_session():
    return AsyncSessionLocal()


async def connect_to_db():
    engine = create_async_engine(DATABASE_URL, echo=DEV)

    async with engine.begin() as conn:
        await conn.run_sync(create_tables, engine)

    AsyncSessionLocal.configure(bind=engine)
