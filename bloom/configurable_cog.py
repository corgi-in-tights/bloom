import logging
from datetime import datetime
from types import SimpleNamespace

from discord.ext import commands


class ConfigurableCog(commands.Cog):
    """A cog that can be configured with settings from the bot's settings, includes a logger with `self.logger`."""

    def __init__(self, bot, cog_id, default_settings, logger_level=logging.INFO):
        self.bot: commands.Bot = bot
        self.cog_id = cog_id
        self._default_settings = default_settings

        self.logger = self._setup_logger(logger_level)

    def cog_load(self):
        self.logger.info("Reloading cog %s", self.cog_id)
        self.start_time = datetime.now(self.bot.timezone)
        self.settings = self._load_settings()

    def _setup_logger(self, logger_level):
        logger = logging.getLogger("bloom." + self.cog_id)
        logger.setLevel(logger_level)
        return logger

    def _load_settings(self):
        # use default settings
        if self.cog_id not in self.bot.extension_settings:
            return SimpleNamespace(**self._default_settings)

        provided_settings = self.bot.extension_settings[self.cog_id]
        _merged = provided_settings.copy()

        # copy over any missing keys from the default settings
        for k in self._default_settings:
            if k not in _merged:
                _merged[k] = self._default_settings[k]

        # verify types
        for mk in _merged:
            # if its a default setting key and an incorrect value, bitch about it
            if mk in self._default_settings and not isinstance(_merged[mk], type(self._default_settings[mk])):
                msg = (
                    f"Invalid types {mk}: {_merged[mk]} passed for"
                    f" {self.cog_id}, was expecting {type(self._default_settings[k])}"
                )
                raise TypeError(msg)

        return SimpleNamespace(**_merged)
