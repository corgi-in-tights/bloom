import logging
import random
import re
from datetime import datetime, timedelta

import discord
import validators
from configurable_cog import ConfigurableCog
from discord import app_commands
from discord.app_commands import Range
from discord.utils import format_dt
from helper import is_valid_uuid, user_dms_open

from .monitor import can_create_instance, create_monitor, stop_monitor, user_has_instance

default_settings = {"max_monitors": 3, "proxies": [], "frequency": 15, "frequency_range": 5}


class MathMatize(ConfigurableCog):
    def __init__(self, bot, **kwargs):
        super().__init__(bot, "mathmatize", default_settings, logger_level=logging.DEBUG, **kwargs)
        self.monitors = []

    def cog_load(self):
        super().cog_load()
        self.logger.info("Loaded %s proxies.", len(self.settings.proxies))

    async def on_poll_change(self, user_id, activity_url, event_date):
        try:
            self.logger.debug("Running poll change event for %s at %s", user_id, event_date)
            user = await self.bot.fetch_user(user_id)
            if event_date:
                desc = f"{activity_url} recieved an update at {format_dt(event_date, 'S')}"
            else:
                desc = f"{activity_url} recieved an update"
            embed = discord.Embed(
                title="Poll Update",
                url=activity_url,
                description=desc,
                color=0x45FF9A,
            )
            embed.set_author(name="MathMatize")
            await user.send(embed=embed)
        except discord.errors.HTTPException as e:
            self.logger.warning("Failed poll change due to HTTP exception %s", e)
        except discord.errors.NotFound:
            self.logger.warning("Failed poll change as user was not found.")

    async def on_poll_end(self, user_id, activity_url, reason, event_date=None):
        self.logger.debug("End poll event at %s for %s", activity_url, user_id)
        try:
            user = await self.bot.fetch_user(user_id)

            if event_date:
                desc = f'{activity_url} was stopped due to "{reason}" at {format_dt(event_date, 'S')}'
            else:
                desc = f'{activity_url} was stopped due to "{reason}"'
            embed = discord.Embed(
                title="Poll Ended",
                url=activity_url,
                description=desc,
                color=0xFB6B45,
            )
            embed.set_author(name="MathMatize")
            await user.send(embed=embed)
        except discord.errors.HTTPException as e:
            self.logger.warning("Failed poll change due to HTTP exception %s", e)
        except discord.errors.NotFound:
            self.logger.warning("Failed poll change as user was not found.")

    @app_commands.command(name="mm-monitor")
    @app_commands.describe(
        activity_url="URL of the MathMatize activity to monitor.",
        duration="Duration of the monitor in minutes, max 3 hours.",
    )
    async def mm_monitor(self, interaction: discord.Interaction, activity_url: str, duration: Range[int, 5, 180] = 120):
        """Start monitoring MathMatize for poll updates."""
        if not validators.url(activity_url):
            await interaction.response.send_message(f"Passed URL {activity_url} is invalid!", ephemeral=True)
            return

        # check if passed string has a UUID
        uuid_pattern = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
        _match = re.search(uuid_pattern, activity_url)
        if not _match:
            await interaction.response.send_message(
                f"Could not obtain UUID match from url {activity_url}.",
                ephemeral=True,
            )
            return
        activity_uuid = _match.group(0)
        if not is_valid_uuid(activity_uuid):
            await interaction.response.send_message(f"Provided UUID {activity_uuid} is invalid.", ephemeral=True)
            return

        # check if bot can DM user
        if not await user_dms_open(interaction.user):
            await interaction.response.send_message(
                "Your DMs are not open! Please ensure the bot is able to message you privately.",
                ephemeral=True,
            )
            return

        # has not exceeded instance limit
        if not can_create_instance(max(1, self.settings.max_monitors)):
            await interaction.response.send_message("There are too many monitors running currently.", ephemeral=True)
            return

        # user isnt being a greedy pig
        user_id = interaction.user.id
        if user_has_instance(user_id):
            await interaction.response.send_message(
                "You already have a poll monitor instance running!",
                ephemeral=True,
            )
            return

        monitor_expiration_date = datetime.now(self.bot.timezone) + timedelta(minutes=duration)

        await interaction.response.send_message(
            "You should have been messaged on how to proceed next, please check your DMs.",
            ephemeral=True,
        )

        embed = discord.Embed(
            title="Created Poll Monitor!",
            url=activity_url,
            description=
            f"Poll {activity_url} will now send you an update *here* until you use `/mm-monitor-stop`,"
            f" the activity closes, or the monitor ends at {format_dt(monitor_expiration_date, 'F')}.",
            color=0x0FB4E9,
        )
        embed.set_author(name="MathMatize")
        embed.set_footer(
            text=f"May be delayed by up-to {round(self.settings.frequency + self.settings.frequency_range)} seconds.",
        )
        await interaction.user.send(embed=embed)

        # pick a random proxy if ava.
        proxy = random.choice(self.settings.proxies) if len(self.settings.proxies) > 0 else None

        await create_monitor(
            user_id=user_id,
            activity_url=activity_url,
            end_date=monitor_expiration_date,
            on_poll_change=self.on_poll_change,
            on_poll_end=self.on_poll_end,
            frequency=self.settings.frequency,
            frange=self.settings.frequency_range,
            proxy=proxy,
            tzone=self.bot.timezone,
        )

    @app_commands.command(name="mm-monitor-stop")
    async def mm_monitor_stop(self, interaction: discord.Interaction):
        """Stop your current poll monitor, if you have one."""
        if await stop_monitor(interaction.user.id, self.on_poll_end):
            await interaction.response.send_message(
                "Gracefully stopping your linked instance.. you should receive a confirmation.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message("You do not have any current poll monitors!", ephemeral=True)
