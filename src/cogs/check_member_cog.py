from config.imports import *
from discord.ext import commands
from src.bot_client import bot
from src import settings

tree = bot.tree


class CheckMemberCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tree.command(
        name="check-member",
        description="Leaderboards for GW2 stats",
        guild=discord.Object(id=settings.GUILD_ID)
    )
    async def check_member(self, interaction, member: discord.Member):
        if await authorization.ensure_admin(interaction):
            from src.cogs.stats_cog import StatsCog
            await StatsCog(self.bot).get_stats(interaction, member)


async def setup(bot):
    await bot.add_cog(CheckMemberCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
