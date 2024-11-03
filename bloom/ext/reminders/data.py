from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy import delete, Column, Integer, DateTime, BigInteger, String

from database import Base, get_async_session


class Reminders(Base):
    __tablename__ = 'ext_reminders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger)
    user_id = Column(BigInteger)
    target_date = Column(DateTime)
    message = Column(String(1027), nullable=False)


async def add_reminder(guild_id, user_id, target_date, message):
    async with get_async_session() as session:
        r = Reminders(guild_id=guild_id, user_id=user_id,
                      target_date=target_date, message=message)
        session.add(r)
        await session.commit()


async def query_reminders(session, condition):
    stmt = select(Reminders).where(condition)
    result = await session.execute(stmt)
    return result.scalars().all()


async def query_reminders_by_user_id(user_id: int):
    async with get_async_session() as session:
        return await query_reminders(session, Reminders.user_id == user_id)


async def query_outdated_reminders(target_date: datetime):
    async with get_async_session() as session:
        return await query_reminders(session, Reminders.target_date <= target_date)


async def remove_reminders(*pks):
    async with get_async_session() as session:
        stmt = delete(Reminders).where(Reminders.id.in_(pks))
        await session.execute(stmt)
        await session.commit()
