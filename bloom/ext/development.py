from discord.ext import commands
from configurable_cog import ConfigurableCog


class Development(ConfigurableCog):
    def __init__(self, bot, **kwargs):
        super().__init__(bot, 'development', {}, **kwargs)

    @commands.command(name="reload-ext")
    @commands.is_owner()
    async def reload_extension(self, ctx: commands.Context, extension_id: str):
        """Owner only - Reload an extension"""
        try:
            await self.bot.refresh_testing_guild()
            await self.bot.reload_extension('ext.' + extension_id)
            await ctx.send(f'Safely reloaded extension `ext.{extension_id}`.')
            self.logger.info(f"Reloaded extension {extension_id}")
        except Exception as e:
            await ctx.send(f'There was an error while reloading extension `ext.{extension_id}`:', e)

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown(self, ctx: commands.Context):
        """Owner only - Shutdown bot"""
        self.logger.info("Shutting down gracefully...")
        await ctx.send("Shutting down gracefully...")
        await self.bot.close()


async def setup(bot):
    await bot.add_cog(Development(bot))
