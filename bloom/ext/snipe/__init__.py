from .extension import Snipe


async def setup(bot):
    await bot.add_cog(Snipe(bot))
