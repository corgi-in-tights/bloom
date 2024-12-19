from database import Base, get_async_session
from sqlalchemy import BigInteger, Column, String
from sqlalchemy.future import select


class SnipeTable(Base):
    __tablename__ = "ext_snipe"

    channel_id = Column(BigInteger, primary_key=True)
    username = Column(String(255))
    message_content = Column(String(1027), nullable=False)


async def set_recent_snipe(channel_id, username, content):
    async with get_async_session() as session:
        stmt = select(SnipeTable).where(SnipeTable.channel_id == channel_id).limit(1)
        result = (await session.execute(stmt)).scalars().first()

        if result:
            result.username = username
            result.message_content = content
        else:
            new = SnipeTable(channel_id=channel_id, username=username, message_content=content)
            session.add(new)

        await session.commit()


async def fetch_snipe_content(channel_id):
    async with get_async_session() as session:
        stmt = select(SnipeTable).where(SnipeTable.channel_id == channel_id).limit(1)
        result = (await session.execute(stmt)).scalars().first()

        return result.message_content if result else None
