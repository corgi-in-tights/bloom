import discord
import discord
from discord import app_commands
from discord.utils import format_dt
from discord.ext.commands import has_permissions
from datetime import datetime, timezone, timedelta

from configurable_cog import ConfigurableCog
from helper import user_dms_open

default_settings = {
}

class Reminders(ConfigurableCog):
    def __init__(self, bot, **kwargs):
        super().__init__(bot, 'reminders', default_settings, **kwargs)

    @app_commands.command(name="remind-me")
    async def remind_me(self, interaction: discord.Interaction, minutes: app_commands.Range[int, 1, None], message: str):
        """Remind you in DMs about anything after a certain amount of time."""
        time_to_expiration = datetime.now(self.bot.timezone) + timedelta(minutes=minutes)

        if not await user_dms_open(interaction.user):
            await interaction.response.send_message(f"Your DMs are not open! Please ensure the bot is able to message you privately.", ephemeral=True)
            return
        
        self.logger.info(f"Created new reminder for {interaction.user.id} for {message} at {time_to_expiration.strftime('%Y-%m-%d %H:%M:%S')}")
        await interaction.response.send_meessage(f"Okay! I'll remind you {format_dt(time_to_expiration, style='R')} about {message} in DMs.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Reminders(bot))