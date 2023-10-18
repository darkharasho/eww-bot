from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from src.db_viewer import DBViewer


class DebugCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def check_creator(ctx):
        return ctx.message.author.id == 201537071804973056

    @commands.command()
    @commands.check(check_creator)
    async def debug(self, ctx, *, arg):
        dm_channel = await ctx.author.create_dm()
        await ctx.message.delete()
        if arg == "members":
            members = Member.select()
            for member in members:
                await member_hack(dm_channel, member)
        elif arg == "configs":
            configs = Config.select()
            for config in configs:
                await config_hack(dm_channel, config)
        elif "member" in arg:
            member = Member.select().where(Member.discord_id == int(re.sub(r'\D', '', arg))).first()
            await member_hack(dm_channel, member)
        elif "config" in arg:
            config = Config.select().where(Config.name == arg.split(" ")[-1]).first()
            await config_hack(dm_channel, config)


async def setup(bot):
    await bot.add_cog(DebugCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)


async def member_hack(dm_channel, member):
    member_data = DBViewer(return_string=True).member(member)
    await format_hacked_data(dm_channel, member_data)


async def config_hack(dm_channel, config):
    config_data = DBViewer(return_string=True).config(config)
    await format_hacked_data(dm_channel, config_data)


async def format_hacked_data(dm_channel, data):
    embed = discord.Embed(title=f"hack the planet - {settings.GUILD}", description="")
    for key, val in data.items():
        embed.add_field(name=key, value=f"```{val}```", inline=False)
    await dm_channel.send(embed=embed)
