from datetime import datetime

import discord
from configurable_cog import ConfigurableCog
from discord import app_commands
from discord.ext.commands import has_permissions
from settings import TESTING_ADMIN_CHANNEL_ID

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
            f"bot has been up for {round(time_passed.seconds)} seconds\n"
            f"running on version {self.bot.version}.",
            ephemeral=True,
        )

    @app_commands.command()
    @has_permissions(administrator=True)
    @app_commands.describe(
        message_count="The amount of messages to purge, max 200.",
    )
    async def purge(self, interaction: discord.Interaction, message_count: app_commands.Range[int, 1, 200]):
        """Purge channel."""
        await interaction.followup.send(f"Purging {message_count} messages..", ephemeral=True)

        await interaction.channel.purge(limit=message_count)
        await interaction.response.send_message(
            f"Successfully purged {message_count} messages, executed by {interaction.user.mention}!",
        )

    @app_commands.command(name="purge-request")
    @app_commands.describe(
        reason="Short description of why you think it should be erased >.>",
        message_count="How many messages you think should be purged.",
    )
    async def purge_request(
        self,
        interaction: discord.Interaction,
        reason: str,
        message_count: app_commands.Range[int, 1, 50],
    ):
        """Sometimes you just need to clean up the chat, if approved, the purge will go through."""
        admin_channel = self.bot.get_channel(TESTING_ADMIN_CHANNEL_ID)
        if not admin_channel:
            await interaction.response.send_message(
                "Admin channel not found, please contact the bot owner.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Request sent to admin channel.",
            ephemeral=True,
        )

        # get latest message to provide context
        messages = [message async for message in interaction.channel.history(limit=1)]
        url = messages[0].jump_url if messages and len(messages) > 0 else interaction.channel.mention

        await admin_channel.send(
            content=f"{interaction.user.mention} has requested to purge {message_count} messages "
            f"at {url} with the reason: {reason}",
        )
