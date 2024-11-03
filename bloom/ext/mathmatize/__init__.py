from .extension import MathMatize


async def setup(bot):
    await bot.add_cog(MathMatize(bot))
