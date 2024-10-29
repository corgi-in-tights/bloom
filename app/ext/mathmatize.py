import discord
import discord
from discord import app_commands
from discord.utils import format_dt
from discord.ext.commands import has_permissions
from datetime import datetime, timezone, timedelta

from configurable_cog import ConfigurableCog

default_settings = {
    'expiration_delta': timedelta(days=7),
    'max_monitors': 3,
    'proxies': [],
}

class MathMatize(ConfigurableCog):
    def __init__(self, bot, **kwargs):
        super().__init__(bot, 'mathmatize', default_settings, **kwargs)
        self.start_time = datetime.now(self.bot.timezone)

    @app_commands.command(name="setup-profile")
    async def setup_profile(self, interaction: discord.Interaction):
        """Initialize a temporarily MathMatize profile."""
        time_to_expiration = datetime.now(self.bot.timezone) + self.settings.expiration_delta
        await interaction.response.send_message(f"Your MathMatize profile is valid until {format_dt(time_to_expiration, 'F')}. Please remember to `/setup-profile` after that time period passes.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MathMatize(bot))