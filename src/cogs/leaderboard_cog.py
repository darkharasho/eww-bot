import tabulate

from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.gw2_api_client import GW2ApiClient
from src.bot_client import bot
tabulate.PRESERVE_WHITESPACE = True
tree = bot.tree


async def calculate_leaderboard(name, data):
    members = list(set([api_key.member for api_key in ApiKey.select()]))
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
        showindex=index
    )

    return table


class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = SqliteDatabase('eww_bot.db')
        self.guild = bot.get_guild(settings.GUILD_ID)

    @tree.command(
        name="leaderboard",
        description="Leaderboards for GW2 stats",
        guild=discord.Object(id=settings.GUILD_ID)
    )
    async def leaderboard(self, interaction):
        if await authorization.ensure_allowed_channel(interaction, "leaderboard_channel_ids"):
            await interaction.response.defer()
            kill_table = await calculate_leaderboard("Kills", "weekly_kill_count")
            kdr_table = await calculate_leaderboard("KDR", "weekly_kdr")
            capture_table = await calculate_leaderboard("Captures", "weekly_capture_count")

            embed = discord.Embed(
                title="📊 Weekly Leaderboard",
                description=f"〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️"
                            f"\n**⚔️ Kills: **```{kill_table}```"
                            f"\n**🧿 KDR:**```{kdr_table}```"
                            f"\n**🏰 Captures:**```{capture_table}```"
            )

            await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LeaderboardCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
