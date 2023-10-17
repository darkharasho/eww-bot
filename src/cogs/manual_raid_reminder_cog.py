import discord.ui

from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from src.views import proposal_view

tree = bot.tree


class ManualRaidReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tree.command(
        name="manual-raid-reminder",
        description="Kick off the raid reminder... again",
        guild=discord.Object(id=settings.GUILD_ID)
    )
    async def manual_raid_reminder(self, interaction):
        if await authorization.ensure_admin(interaction):
            await interaction.response.defer(ephemeral=True)
            cog = bot.get_cog('RaidReminderTask')
            await cog.raid_reminder()
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Raid reminder manually posted",
                    description="",
                    color=0x0ff000
                )
            )


async def setup(bot):
    await bot.add_cog(ManualRaidReminderCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
