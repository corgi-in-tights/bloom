import asyncio
import logging
import logging.handlers
import signal
import zoneinfo

import discord
import settings
from database.setup import connect_to_db
from discord.ext import commands

discord.VoiceClient.warn_nacl = False  # annoying pop-up warning
default_timezone = zoneinfo.ZoneInfo("America/New_York")

class KeyboardInterruptHandler:
    def __init__(self, bot):
        self.bot = bot
        self._task = None

    def __call__(self):
        if self._task:
            raise KeyboardInterrupt
        self._task = asyncio.create_task(self.bot.close())

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


def setup_bot_logging():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter("[{asctime}] [{levelname}] {name}: {message}", dt_fmt, style="{")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


async def main():
    setup_bot_logging()

    intents = discord.Intents.all()

    async with BloomBot(
        command_prefix=commands.when_mentioned_or(*settings.BOT_PREFIXES),
        intents=intents,
        initial_extensions=settings.ENABLED_EXTENSIONS,
        extension_settings=settings.EXTENSION_SETTINGS,
        testing_guild_id=settings.TESTING_GUILD_ID,
        owner_id=settings.DISCORD_OWNER_ID,
        timezone=settings.TIMEZONE,
    ) as bot:
        bot.loop.add_signal_handler(signal.SIGINT, KeyboardInterruptHandler(bot))
        await bot.start(settings.BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
