from .extension import Development


async def setup(bot):
    await bot.add_cog(Development(bot))
