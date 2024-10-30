import discord
import uuid
import re

async def user_dms_open(user) -> bool:
    try:
        await user.send()
    except discord.HTTPException as e:
        if e.code == 50006:  # cannot send an empty message
            return True
        elif e.code == 50007:  # cannot send messages to this user
            return False
        else:
            raise


def is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


# https://stackoverflow.com/a/62414348
def escape_mentions(text, user_mentions=True):
    if user_mentions:
        return re.sub(r'@(everyone|here|[!&]?[0-9]{17,21})', '@\u200b\\1', text)
    else:
        return re.sub(r'@(everyone|here)', '@\u200b\\1', text)
