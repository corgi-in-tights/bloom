from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from settings import DATABASE_URL, DEV
from .tables import create_tables


AsyncSessionLocal = async_sessionmaker(expire_on_commit=False)

def get_async_session():
    return AsyncSessionLocal()

async def connect_to_db():
    engine = create_async_engine(DATABASE_URL, echo=DEV)
    
    async with engine.begin() as conn:
        await conn.run_sync(create_tables)

    AsyncSessionLocal.configure(bind=engine)
