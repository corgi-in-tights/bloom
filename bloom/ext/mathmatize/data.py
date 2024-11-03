from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy import delete, Column, Integer, DateTime, BigInteger, String

from database import Base, get_async_session


class MathMatizeRestrictions(Base):
    __tablename__ = 'ext_mathmatize'

    user_id = Column(BigInteger, primary_key=True)
    release_date = Column(DateTime)


async def set_time_restriction(user_id, release_date):
    async with get_async_session() as session:
        r = MathMatizeRestrictions(user_id=user_id, release_date=release_date)
        session.add(r)
        await session.commit()


async def check_time_restriction(session, user_id, current_date):
    async with get_async_session() as session:
        result = await session.query(MathMatizeRestrictions).filter(
            MathMatizeRestrictions.user_id == user_id
        ).limit(1).first()

        if result is not None:
            # check if it should be refreshed
            if current_date >= result.release_date:
                await reset_time_restriction(session, user_id)
                await session.commit()
                return True

        return False


async def get_time_remaining(user_id, start_time, default_time, refresh_hours):
    async with get_async_session() as session:
        result = await session.query(MathMatizeRestrictions).filter(
            MathMatizeRestrictions.user_id == user_id
        ).limit(1).first()

        if result is None:
            set_time_restriction(user_id, start_time, default_time)

        return result


async def reset_time_restriction(session, user_id):
    await session.query(MathMatizeRestrictions).filter(
        MathMatizeRestrictions.user_id == user_id
    ).delete(synchronize_session=False)
