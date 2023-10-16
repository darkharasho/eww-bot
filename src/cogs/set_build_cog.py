from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from src.views import set_build_view

tree = bot.tree


class SetBuildCog(commands.Cog):
    def __init__(self, passed_bot):
        self.passed_bot = passed_bot

    @tree.command(
        name="set-build",
        description="Set a new build. Required: Class Name, Link, Delete old build, whether to post in updates",
        guild=discord.Object(id=settings.GUILD_ID)
    )
    async def set_build(self, interaction, class_name: str, announce: bool):
        if await authorization.ensure_build_manager(interaction):
            modal = set_build_view.SetBuildView(class_name=class_name, announce=announce)
            await interaction.response.send_modal(modal)


async def setup(bot):
    await bot.add_cog(SetBuildCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
