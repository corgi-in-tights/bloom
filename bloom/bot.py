import asyncio
import logging
import logging.handlers
import zoneinfo

import discord
import settings
from database.setup import connect_to_db
from discord.ext import commands

default_timezone = zoneinfo.ZoneInfo("America/New_York")


class BloomBot(commands.Bot):
    def __init__(
        self,
        *args,
        initial_extensions: list[str] | None = None,
        extension_settings: dict | None = None,
        testing_guild_id: int | None = None,
        timezone=default_timezone,
        **kwargs,
    ):
        if initial_extensions is None:
            initial_extensions = []
        if extension_settings is None:
            extension_settings = {}

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

        # connect to database after loading extensions
        await connect_to_db()

    async def refresh_testing_guild(self):
        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)


def setup_logging():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{")
    handler.setFormatter(formatter)
    logger.addHandler(logging.StreamHandler())
    return logger


async def main():
    setup_logging()

    intents = discord.Intents.all()

    async with BloomBot(
        command_prefix=commands.when_mentioned,
        intents=intents,
        initial_extensions=settings.ENABLED_EXTENSIONS,
        extension_settings=settings.EXTENSION_SETTINGS,
        testing_guild_id=settings.TESTING_GUILD_ID,
        owner_id=settings.DISCORD_OWNER_ID,
        timezone=settings.TIMEZONE,
    ) as bot:
        await bot.start(settings.BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
