import re
import uuid
from datetime import datetime, timedelta

import discord

EMPTY_MESSAGE_ERROR_CODE = 50006
UNABLE_TO_SEND_MESSAGES_ERROR_CODE = 50007


async def user_dms_open(user) -> bool:
    try:
        await user.send()
    except discord.HTTPException as e:
        if e.code == EMPTY_MESSAGE_ERROR_CODE:
            return True
        if e.code == UNABLE_TO_SEND_MESSAGES_ERROR_CODE:
            return False
        raise  # otherwise be a shit about it


def is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(str(val))
    except ValueError:
        return False
    return True


# https://stackoverflow.com/a/62414348
def escape_mentions(text):
    return re.sub(r"@(everyone|here|[!&]?[0-9]{17,21})", "@\u200b\\1", text)


def round_datetime_minutes(date: datetime):
    date += timedelta(seconds=30)
    return date.replace(second=0, microsecond=0)
