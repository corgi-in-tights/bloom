import random
import discord
from discord import app_commands
from discord.app_commands import Range
from discord.utils import format_dt
from discord.ext.commands import has_permissions
from datetime import datetime, timezone, timedelta

from configurable_cog import ConfigurableCog
from helper import user_dms_open, is_valid_uuid

from .monitor import user_has_instance, create_monitor, stop_monitor

default_settings = {
    'expiration_delta': timedelta(days=7),
    'max_monitors': 3,
    'proxies': [],
    'frequency': 15,
    'frequency_range': 5
}



class MathMatize(ConfigurableCog):
    def __init__(self, bot, **kwargs):
        super().__init__(bot, 'mathmatize', default_settings, **kwargs)
        self.start_time = datetime.now(self.bot.timezone)
        self.monitors = []

    @app_commands.command(name="mm-monitor")
    async def mm_monitor(self, interaction: discord.Interaction, poll_uuid: str, duration: Range[int, 5, 180] = 120):
        """Start monitoring MathMatize for polls."""

        # check if passed string is actually a UUID
        if not is_valid_uuid(poll_uuid):
            await interaction.response.send_message(f"Provided UUID {poll_uuid} is invalid.", ephemeral=True)
            return
        
        # check if bot can DM user
        if not await user_dms_open(interaction.user):
            await interaction.response.send_message(f"Your DMs are not open! Please ensure the bot is able to message you privately.", ephemeral=True)
            return
        
        if user_has_instance(interaction.user.id):
            await interaction.response.send_message(f"You already have a poll monitor instance running!", ephemeral=True)
            return
                
        # pick a random proxy if ava.
        if len(self.settings.proxies) > 0:
            proxy = random.choice(self.settings.proxies)
        else:
            proxy = None

        # define trigger event
        async def trigger_event(bot, user_id, url, last_result, result):
            try:
                user = await bot.fetch_user(user_id)
                await user.send(f'Update recieved at: {url}')
            except Exception as e:
                print(f'MM; Failed to trigger event for {user_id}: {url} due to {e}')
        
        time_to_expiration = datetime.now(self.bot.timezone) + timedelta(minutes=duration)
        await interaction.user.send(f'Poll https://www.mathmatize.com/polls/{poll_uuid}/ will now send you an update *here* until 
                                    you use `/mm-monitor-stop` or the duration runs out at {format_dt(time_to_expiration, 'F')}.')
        await interaction.response.send_message(f"You should have been messaged on how to proceed next, 
                                                please check your DMs.", ephemeral=True)
        

        await create_monitor(self.bot, interaction.user.id, poll_uuid, duration, trigger_event, self.settings.frequency, self.settings.frequency_range, proxy=proxy)


    @app_commands.command(name="mm-monitor-stop")
    async def mm_monitor_stop(self, interaction: discord.Interaction):
        if await stop_monitor(interaction.user.id):
            await interaction.response.send_message(f"Gracefully stopping your linked instance..", ephemeral=True)
        else:
            await interaction.response.send_message(f"You do not have any current poll monitors!", ephemeral=True)