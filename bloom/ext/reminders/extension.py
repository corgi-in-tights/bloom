import discord
import asyncio
from discord import app_commands
from discord.utils import format_dt
from discord.ext.commands import has_permissions
from discord.ext.tasks import loop
from discord.errors import HTTPException, NotFound
from datetime import datetime, timedelta

from configurable_cog import ConfigurableCog
from helper import user_dms_open, round_datetime_minutes

from .data import add_reminder, query_outdated_reminders, remove_reminders

default_settings = {}


class Reminders(ConfigurableCog):
    def __init__(self, bot, **kwargs):
        super().__init__(bot, 'reminders', default_settings, **kwargs)
        self.check_for_reminders.start()

    def cog_unload(self):
        self.check_for_reminders.cancel()

    @loop(minutes=1)
    async def check_for_reminders(self):
        self.logger.debug("Running remainder loop check...")
        current_date = datetime.now(self.bot.timezone)

        user_ids = []

        results = await query_outdated_reminders(current_date)
        for r in results:
            try:
                user = await self.bot.fetch_user(r.user_id)
                self.logger.debug(f"Found {r.user_id} for reminder {
                    r.id}: {r.message}")
                await user.send(f"Your reminder for {format_dt(r.target_date, style='F')}: {r.message}")
                user_ids.append(r.id)

            except NotFound as e:
                self.logger.info(f"Could not find user 
                    {r.user_id}, deleting reminder {r.id} due to {e}")
                user_ids.append(r.id)

            except HTTPException:
                self.logger.info(f"Could not find user {r.user_id} for 
                    {r.id} due to {e}, ignoring.")

            if len(user_ids) > 0:
                self.logger.debug(f"Removing reminders {', '.join(
                    [str(n) for n in user_ids])} as they were processed.")
                await remove_reminders(*user_ids)

    @check_for_reminders.before_loop
    async def before_check_for_reminders(self):
        self.logger.debug("Waiting for bot to get ready to start loop...")
        await self.bot.wait_until_ready()

    @app_commands.command(name="remind-me")
    async def remind_me(self, interaction: discord.Interaction, minutes: app_commands.Range[int, 1, None], message: str):
        """Remind you in DMs about anything after a certain amount of time."""

        if not await user_dms_open(interaction.user):
            await interaction.response.send_message(f"Your DMs are not open! Please ensure the bot is able to message you privately.", ephemeral=True)
            return

        await interaction.response.defer(thinking=True, ephemeral=True)

        try:
            time_to_expiration = round_datetime_minutes(
                datetime.now(self.bot.timezone) + timedelta(minutes=minutes))
            await add_reminder(interaction.guild_id, interaction.user.id, time_to_expiration, message.strip())
            self.logger.info(f"Created new reminder for {interaction.user.id} for message '{
                             message}' at {time_to_expiration.strftime('%Y-%m-%d %H:%M:%S')}")
            await interaction.edit_original_response(content=f"Okay! I'll remind you at {format_dt(time_to_expiration, style='F')} about {message} in DMs.")

        except Exception as e:
            await interaction.edit_original_response(content=f"Sorry, there was an error!")
            self.logger.warning(e)
