import logging
from datetime import datetime
from types import SimpleNamespace

from discord.ext import commands


class ConfigurableCog(commands.Cog):
    def __init__(self, bot, cog_id, default_settings):
        self.bot: commands.Bot = bot
        self.cog_id = cog_id
        self._default_settings = default_settings

        self.logger = self._create_logger()

    def cog_load(self):
        self.logger.info("Reloading cog %s", self.cog_id)
        self.start_time = datetime.now(self.bot.timezone)
        self.settings = self._load_settings()

    def _create_logger(self):
        logger = logging.getLogger("bloom.%s", self.cog_id)
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{")
        handler.setFormatter(formatter)
        logger.addHandler(logging.StreamHandler())

        return logger

    def _load_settings(self):
        # use default settings
        if self.cog_id not in self.bot.extension_settings:
            return SimpleNamespace(**self._default_settings)

        provided_settings = self.bot.extension_settings[self.cog_id]
        _merged = provided_settings.copy()

        # copy over any missing keys from the default settings
        for k, v in self._default_settings.items():
            if k not in _merged:
                _merged[k] = v

        # verify types
        for k in _merged:
            # if its a default setting key and an incorrect value, bitch about it
            if k in self._default_settings and not isinstance(v, type(self._default_settings[k])):
                msg = (
                    f"Invalid types {k}: {v} passed for \
                                {self.cog_id}, was expecting {type(self._default_settings[k])}"
                )
                raise TypeError(msg)

        return SimpleNamespace(**_merged)
