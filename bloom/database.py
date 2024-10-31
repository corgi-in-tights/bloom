from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, DateTime, BigInteger, String, delete
from datetime import datetime
import asyncio

from settings import DATABASE_URL, DEV

Base = declarative_base()

class Reminders(Base):
    __tablename__ = 'ext_reminders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger)
    user_id = Column(BigInteger)
    target_date = Column(DateTime)
    message = Column(String(1027), nullable=False)

class MathMatizeRestrictions(Base):
    __tablename__ = 'ext_mathmatize'

    user_id = Column(BigInteger, primary_key=True)
    time = Column(DateTime)




AsyncSessionLocal = async_sessionmaker(expire_on_commit=False)

def get_async_session():
    return AsyncSessionLocal()


async def add_reminder(guild_id, user_id, target_date, message):
    async with get_async_session() as session:
        r = Reminders(guild_id=guild_id, user_id=user_id, target_date=target_date, message=message)
        session.add(r)
        await session.commit()


async def query_reminders(session: AsyncSession, condition):
    stmt = select(Reminders).where(condition)
    result = await session.execute(stmt)
    return result.scalars().all()


async def query_reminders_by_user_id(session: AsyncSession, user_id: int):
    return await query_reminders(session, Reminders.user_id == user_id)

async def query_outdated_reminders(session: AsyncSession, target_date: datetime):
    return await query_reminders(session, Reminders.target_date <= target_date)


async def remove_reminders(session: AsyncSession, *pks):
    stmt = delete(Reminders).where(Reminders.id.in_(pks))
    await session.execute(stmt)
    await session.commit()




async def setup_database():
    engine = create_async_engine(DATABASE_URL, echo=DEV)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal.configure(bind=engine)
