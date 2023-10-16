import discord.ui

from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from src.views import proposal_view

tree = bot.tree


class SyncLeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tree.command(
        name="sync-leaderboard",
        description="Leaderboards for GW2 stats",
        guild=discord.Object(id=settings.GUILD_ID)
    )
    async def sync_leaderboard(self, interaction):
        if await authorization.ensure_admin(interaction):
            await interaction.response.defer(ephemeral=True)
            cog = bot.get_cog('StatUpdaterTask')
            await cog.update_stats()
            await interaction.followup.send(embed=discord.Embed(title="Sync Complete", description="", color=0x0ff000))


async def setup(bot):
    await bot.add_cog(SyncLeaderboardCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
