import asyncio
import logging
import logging.handlers
import zoneinfo
from typing import Optional

import discord
from discord.ext import commands

import settings

class CustomBot(commands.Bot):
    def __init__(
        self,
        *args,
        initial_extensions: list[str] = [],
        extension_settings: dict = {},
        testing_guild_id: Optional[int] = None,
        timezone = zoneinfo.ZoneInfo("America/New_York"),
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.initial_extensions = initial_extensions
        self.extension_settings = extension_settings
        
        self.testing_guild_id = testing_guild_id
        self.timezone = timezone

    async def setup_hook(self) -> None:
        # setup extensions & sync commands for test guild
        for extension in self.initial_extensions:
            await self.load_extension(extension)
        await self.refresh_testing_guild()
        
    async def refresh_testing_guild(self):
        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)



def setup_logging():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='logs/discord.log',
        encoding='utf-8',
        maxBytes=16 * 1024 * 1024,  # 16 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.addHandler(logging.StreamHandler())



async def main():
    setup_logging()

    intents = discord.Intents.default()
    intents.message_content = True

    async with CustomBot(
        command_prefix=commands.when_mentioned_or(*settings.BOT_PREFIXES),
        initial_extensions = settings.ENABLED_EXTENSIONS,
        extension_settings = settings.EXTENSION_SETTINGS,
        intents = intents,
        testing_guild_id = settings.TESTING_GUILD_ID,
        owner_id = settings.DISCORD_OWNER_ID,
        timezone=settings.TIMEZONE
    ) as bot:
        await bot.start(settings.BOT_TOKEN)


asyncio.run(main())