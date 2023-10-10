from config.imports import *
from discord.ext import commands
from src.bot_client import bot
from src import settings
from src.cogs.stats_cog import StatsCog


class CheckMemberCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def check_member(self, interaction, member: discord.Member):
        await StatsCog(self.bot).get_stats(interaction, member)


async def setup(bot):
    await bot.add_cog(CheckMemberCog(bot), guild=settings.GUILD_ID, override=True)
