import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

# == App Settings == #
DEV = True

TIMEZONE = ZoneInfo("America/New_York")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")


# == Bot Settings == #
BOT_PREFIXES = ["&"]

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    msg = "No `BOT_TOKEN` environment variable provided!"
    raise KeyError(msg)

DISCORD_OWNER_ID = int(os.getenv("DISCORD_OWNER_ID")) if "DISCORD_OWNER_ID" in os.environ else None
TESTING_GUILD_ID = int(os.getenv("TESTING_GUILD_ID")) if "TESTING_GUILD_ID" in os.environ else None


# == Extensions == #
ENABLED_EXTENSIONS = ["ext.utils", "ext.mathmatize", "ext.reminders"]
if DEV:
    ENABLED_EXTENSIONS.append("ext.development")


if MATHMATIZE_PROXY_LIST_PATH := os.getenv("MATHMATIZE_PROXY_LIST_PATH"):
    _mm_proxy_list_path = Path(MATHMATIZE_PROXY_LIST_PATH)
    with _mm_proxy_list_path.open() as fp:
        _mm_proxies = json.load(fp)
else:
    _mm_proxies = []


EXTENSION_SETTINGS: dict = {"utils": {"pong_message": "bong"}, "mathmatize": {"proxies": _mm_proxies}}
