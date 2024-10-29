import re
import discord
from discord import app_commands
from discord.app_commands import Range
from discord.utils import format_dt
from discord.ext.commands import has_permissions
from datetime import datetime, timezone, timedelta

from configurable_cog import ConfigurableCog
from helper import user_dms_open

from .monitor import create_monitor

default_settings = {
    'expiration_delta': timedelta(days=7),
    'max_monitors': 3,
    'proxies': [],
    'frequency': 5,
    'frequency_range': 3
}


class MathMatize(ConfigurableCog):
    def __init__(self, bot, **kwargs):
        super().__init__(bot, 'mathmatize', default_settings, **kwargs)
        self.start_time = datetime.now(self.bot.timezone)
        self.monitors = []

    @app_commands.command(name="mm-monitor")
    async def mm_monitor(self, interaction: discord.Interaction, poll_uuid: str, duration: Range[int, 5, 180] = 120):
        """Start monitoring MathMatize for polls."""

        if await user_dms_open(interaction.user):
            if await create_monitor(poll_uuid, duration, self.settings.frequency, self.settings.frequency_range):
                time_to_expiration = datetime.now(
                    self.bot.timezone) + timedelta(minutes=duration)
                await interaction.user.send(f'Poll https://www.mathmatize.com/polls/{poll_uuid}/ will now send you an update *here* until \
                                            you use `/mm-stop`, the activity closes or the duration runs \
                                            out {format_dt(time_to_expiration, 'F')}.')
                await interaction.response.send_message(f"You should have been messaged on how to proceed next, \
                                                        please check your DMs.", ephemeral=True)

            else:
                await interaction.response.send_message(f"There was an error creating your poll monitor, \
                                                        please contact an administrator.", ephemeral=True)

        else:
            await interaction.response.send_message(f"Your DMs are not open! Please ensure the bot is able \
                                                    to message you privately.", ephemeral=True)
