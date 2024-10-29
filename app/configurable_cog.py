from discord.ext import commands
from types import SimpleNamespace

class ConfigurableCog(commands.Cog):
    def __init__(self, bot, cog_id, default_settings):
        self.bot: commands.Bot = bot
        self.cog_id = cog_id
        self._default_settings = default_settings

    def cog_load(self):
        print(f'Loading cog {self.cog_id}')
        self._create_settings()

    def _create_settings(self):
        if self.cog_id in self.bot.extension_settings:
            provided_settings = self.bot.extension_settings[self.cog_id]

            _merged = provided_settings.copy()

            # copy over any missing keys from the default settings
            for k, v in self._default_settings.items():
                if k not in _merged:
                    _merged[k] = v

            # verify types
            for k in _merged.keys():
                # if its a default setting key and an incorrect value, bitch about it
                if k in self._default_settings and not isinstance(v, type(self._default_settings[k])):
                    raise TypeError(f'Invalid types {k}: {v} passed for {self.cog_id}, was expecting {type(self._default_settings[k])}')

            self.settings = SimpleNamespace(**_merged)
        else:
            self.settings = SimpleNamespace(**self._default_settings)
    
