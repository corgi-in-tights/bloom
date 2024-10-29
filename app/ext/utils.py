import discord
from discord import app_commands
from discord.ext.commands import has_permissions
from datetime import datetime, timezone

from configurable_cog import ConfigurableCog

default_settings = {
    'pong_message': 'pong'
}

class Utils(ConfigurableCog):
    def __init__(self, bot, **kwargs):
        super().__init__(bot, 'utils', default_settings, **kwargs)
        self.start_time = datetime.now(self.bot.timezone)
        
    @app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        """Latency/bot-uptime command"""
        time_passed = datetime.now(self.bot.timezone) - self.start_time
        await interaction.response.send_message(f'{self.settings.pong_message}, took {round(self.bot.latency*1000)}ms. \
                        \nbot has been up for {round(time_passed.seconds)} seconds.')

    @app_commands.command()
    @has_permissions(administrator=True)   
    async def purge(self, interaction: discord.Interaction, message_count: app_commands.Range[int, 1, 200]):
        """Purge channel"""
        await interaction.followup.send(f"Purging {message_count} messages..", ephemeral=True)

        await interaction.channel.purge(limit=message_count)
        await interaction.response.send_message(f'Successfully purged {message_count} messages, executed by {interaction.user.mention}!')


async def setup(bot):
    await bot.add_cog(Utils(bot))