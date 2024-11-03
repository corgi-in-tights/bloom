import os
import json
from dotenv import load_dotenv
from typing import Optional
from zoneinfo import ZoneInfo

load_dotenv()

# == App Settings == #
DEV = True

TIMEZONE = ZoneInfo("America/New_York")

if DEV:
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
else:
    DATABASE_URL = os.getenv("DATABASE_URL")


# == Bot Settings == #
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise KeyError('No `BOT_TOKEN` environment variable provided!')

DISCORD_OWNER_ID = int(os.getenv('DISCORD_OWNER_ID')) if 'DISCORD_OWNER_ID' in os.environ else None
TESTING_GUILD_ID = int(os.getenv('TESTING_GUILD_ID')) if 'TESTING_GUILD_ID' in os.environ else None


# == Extensions == #
ENABLED_EXTENSIONS = ['ext.utils', 'ext.mathmatize', 'ext.reminders']
if DEV:
    ENABLED_EXTENSIONS.append('ext.development')

_mm_proxy_list_fp = os.getenv("MATHMATIZE_PROXY_LIST_PATH", "/proxies.json")
_mm_proxies = []
if os.path.exists(_mm_proxy_list_fp):
    with open(_mm_proxy_list_fp, 'r') as fp:
        _mm_proxies = json.load(fp)
    
EXTENSION_SETTINGS: dict = {    
    'utils': {
        'pong_message': 'bong'
    },
    'mathmatize': {
        'proxies': _mm_proxies
    }
}


