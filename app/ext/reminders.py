import discord
import discord
from discord import app_commands
from discord.utils import format_dt
from discord.ext.commands import has_permissions
from datetime import datetime, timezone, timedelta

from configurable_cog import ConfigurableCog


default_settings = {
}

class Reminders(ConfigurableCog):
    def __init__(self, bot, **kwargs):
        super().__init__(bot, 'reminders', default_settings, **kwargs)
        self.start_time = datetime.now(self.bot.timezone)

    @app_commands.command(name="remind-me")
    async def remind_me(self, interaction: discord.Interaction, minutes: app_commands.Range[int, 1, None], message: str):
        """Remind you in DMs about anything after a certain amount of time."""
        time_to_expiration = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        await interaction.response.send_message(f"Okay! I'll remind you {format_dt(time_to_expiration, style='R')}.")


async def setup(bot):
    await bot.add_cog(Reminders(bot))