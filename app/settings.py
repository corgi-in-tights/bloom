import os
from typing import Optional
from zoneinfo import ZoneInfo


# == App Settings == #
DEV: bool = True

TIMEZONE = ZoneInfo("America/New_York")


# == Bot Settings == #
BOT_PREFIXES: list[str] = ["bloom:"]

BOT_TOKEN: str = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise KeyError('No `BOT_TOKEN` environment variable provided!')

DISCORD_OWNER_ID: Optional[int] = int(os.getenv('DISCORD_OWNER_ID')) if 'DISCORD_OWNER_ID' in os.environ else None
TESTING_GUILD_ID: Optional[int] = int(os.getenv('TESTING_GUILD_ID')) if 'TESTING_GUILD_ID' in os.environ else None


# == Extensions == #
ENABLED_EXTENSIONS = ['ext.utils', 'ext.mathmatize', 'ext.reminders']
if DEV:
    ENABLED_EXTENSIONS.append('ext.development')

EXTENSION_SETTINGS: dict = {    
    'utils': {
        'pong_message': 'bong'
    }
}


