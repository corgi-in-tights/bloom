from .extension import Utils


async def setup(bot):
    await bot.add_cog(Utils(bot))
