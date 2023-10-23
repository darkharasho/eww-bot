import discord.ui

from config.imports import *
from discord.ext import commands
from src import settings
from src.gw2_api_client import GW2ApiClient
from src.bot_client import bot
from src.tasks.stat_updater_task import StatUpdaterTask

tree = bot.tree


class KeysCog(commands.Cog):
    def __init__(self, option):
        self.option = option
        self.db = SqliteDatabase('eww_bot.db')
        self.guild = bot.get_guild(settings.GUILD_ID)

    @tree.command(
        name="keys",
        description="Check your GW2 API Keys",
        guild=discord.Object(id=settings.GUILD_ID)
    )
    async def keys(self, interaction):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(
            title="Guild Wars 2 API Keys",
            description=f"",
            color=0x0ff000)
        member = Member.select().where(Member.discord_id == interaction.user.id).first()
        for api_key in member.api_keys:
            value = f"""
            **Server**: {api_key.api_client().world()["name"]}
            **Rank**: {api_key.api_client().account()["wvw_rank"]}
            **Key**: 
            ```{api_key.value}```
            """
            embed.add_field(name=f"{api_key.name} {'🟢' if api_key.primary else ''}", value=value, inline=False)

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(KeysCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
