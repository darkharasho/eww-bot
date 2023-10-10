from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from src.views import set_build_view


class SetBuildCog(commands.Cog):
    def __init__(self, passed_bot):
        self.passed_bot = passed_bot

    @commands.command(pass_context=True)
    async def set_build(self, interaction, class_name: str, announce: bool):
        modal = set_build_view.SetBuildView(class_name=class_name, announce=announce)
        await interaction.response.send_modal(modal)


async def setup(passed_bot):
    await passed_bot.add_cog(SetBuildCog(passed_bot), guild=settings.GUILD_ID, override=True)
