import logging
from datetime import datetime

import discord
from configurable_cog import ConfigurableCog
from discord import app_commands
from discord.ext import commands

from .data import fetch_snipe_content, set_recent_snipe

default_settings = {}


class Snipe(ConfigurableCog):
    def __init__(self, bot, **kwargs):
        super().__init__(bot, "snipe", default_settings, **kwargs)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        await set_recent_snipe(message.channel.id, message.author.display_name, message.content)
        logging.debug("Added snipe for channel %s as %s", message.channel.id, message.content)

    @app_commands.command(name="snipe")
    async def snipe(self, interaction: discord.Interaction):
        """Snipe the most recently deleted message."""
        snipe_content = await fetch_snipe_content(interaction.channel.id)

        if snipe_content:
            embed = discord.Embed(title="Snipe!", description=snipe_content, color=0xee4b57)
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
            embed.set_footer(text=datetime.now(self.bot.timezone).strftime("%Y-%m-%d %H:%M:%S"))
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("There is no message to snipe!", ephemeral=True)
