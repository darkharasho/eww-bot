import tabulate

from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src.gw2_api_client import GW2ApiClient
from src.bot_client import bot

tabulate.PRESERVE_WHITESPACE = True
tree = bot.tree


async def calculate_leaderboard(name, data):
    members = Member.select().where(Member.gw2_api_key.is_null(False))
    leaderboard = []
    for member in members:
        leaderboard.append([member.username, member.gw2_name(), getattr(member, data)()])
    sorted_leaderboard = sorted(leaderboard, key=lambda x: x[2], reverse=True)
    index = [i for i in range(1, len(sorted_leaderboard[:settings.MAX_LEADERBOARD_MEMBERS]) + 1)]

    tablefmt = "simple"
    headers = ["Name", "GW2 Username", f"{name}"]
    table = tabulate(
        sorted_leaderboard[:settings.MAX_LEADERBOARD_MEMBERS],
        headers,
        tablefmt=tablefmt,
        showindex=index,
        maxcolwidths=[23, 23, None]
    )

    return table


class FunderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = SqliteDatabase('eww_bot.db')
        self.guild = bot.get_guild(settings.GUILD_ID)

    @tree.command(
        name="funderboard",
        description="Fun Leaderboard Stats",
        guild=discord.Object(id=settings.GUILD_ID)
    )
    async def funderboard(self, interaction):
        await interaction.response.defer()
        spike_table =  await calculate_leaderboard("Spikes", "legendary_spikes")
        supply_table = await calculate_leaderboard("Supply", "weekly_supply_spent")
        yak_table =    await calculate_leaderboard("Yaks", "weekly_yaks_escorted")

        embed = discord.Embed(
            title="🎉 Funderboard",
            description=f"**🏆 Legendary Spikes:**```{spike_table}```\n"
                        f"**📦 Weekly Repair Masters:**```{supply_table}```\n"
                        f"**🐄 Weekly Yak Escorts:**```{yak_table}```\n"
        )

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(FunderboardCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
