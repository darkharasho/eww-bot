import discord

from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from src.db_viewer import DBViewer
from src.open_ai import ChatGPT


class WikiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wiki(self, ctx, *, arg):
        if settings.OPEN_AI_KEY:
            await ChatGPT().chunked_wiki(ctx.message)
        else:
            await ctx.message.channel.send("I'm sorry Dave, I can't let you do that.")


async def setup(bot):
    await bot.add_cog(WikiCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
