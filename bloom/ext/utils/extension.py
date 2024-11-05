from datetime import datetime

import discord
from configurable_cog import ConfigurableCog
from discord import app_commands
from discord.ext.commands import has_permissions

default_settings = {"pong_message": "pong"}


class Utils(ConfigurableCog):
    def __init__(self, bot, **kwargs):
        super().__init__(bot, "utils", default_settings, **kwargs)

    @app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        """Latency/bot-uptime command."""
        time_passed = datetime.now(self.bot.timezone) - self.start_time
        await interaction.response.send_message(
            f"{self.settings.pong_message}, took {round(self.bot.latency*1000)}ms.\n"
            f"bot has been up for {round(time_passed.seconds)} seconds.",
            ephemeral=True,
        )

    @app_commands.command()
    @app_commands.describe(
        message_count="The amount of messages to purge, max 200.",
    )
    @has_permissions(administrator=True)
    async def purge(self, interaction: discord.Interaction, message_count: app_commands.Range[int, 1, 200]):
        """Purge channel."""
        await interaction.followup.send(f"Purging {message_count} messages..", ephemeral=True)

        await interaction.channel.purge(limit=message_count)
        await interaction.response.send_message(
            f"Successfully purged {message_count} messages, executed by {interaction.user.mention}!",
        )
