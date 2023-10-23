from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src.gw2_api_client import GW2ApiClient
from src.bot_client import bot

tree = bot.tree


class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = SqliteDatabase('eww_bot.db')
        self.guild = bot.get_guild(settings.GUILD_ID)

    @tree.command(
        name="stats",
        description="See stats about yourself",
        guild=discord.Object(id=settings.GUILD_ID)
    )
    async def stats(self, interaction):
        await self.get_stats(interaction, interaction.user)

    async def get_stats(self, interaction, member):
        await interaction.response.defer(ephemeral=True)
        db_member = Member.find_or_create(member)

        if db_member.api_key:
            api_client = GW2ApiClient(api_key=db_member.api_key)
            gw2_account_info = api_client.account()

            embed = discord.Embed(
                title="Guild Wars 2 - Weekly Stats",
                description=f"",
                color=member.top_role.color)
            embed.set_thumbnail(url=member.display_avatar.url)

            if Config.review_forum_channel_id():
                review_channel = self.bot.get_channel(Config.review_forum_channel_id())
                reviewed_count = 0
                unreviewed_count = 0
                last_reviewed_date = None
                for thread in review_channel.threads:
                    if thread.owner_id == member.id:
                        if "Reviewed" in [forum_tag.name for forum_tag in thread.applied_tags]:
                            reviewed_count += 1
                            if last_reviewed_date:
                                if last_reviewed_date < thread.created_at:
                                    last_reviewed_date = thread.created_at
                            else:
                                last_reviewed_date = thread.created_at
                        else:
                            unreviewed_count += 1
            embed.add_field(name="Current Role", value=member.top_role.mention, inline=True)
            embed.add_field(name="GW2 Name", value=gw2_account_info["name"], inline=True)
            if "attendance" not in Config.disabled_modules():
                embed.add_field(name="", value=f"", inline=False)
                embed.add_field(
                    name="Attendance",
                    value=f"```Raid: {db_member.raid_day_count()} | Off: {db_member.off_day_count()}```",
                    inline=True
                )
                last_attended = db_member.last_attended()
                if last_attended:
                    embed.add_field(name="Last Attended",
                                    value=f"```" + db_member.last_attended().strftime("%m/%d/%y") + "```", inline=True)
                else:
                    embed.add_field(name="Last Attended",
                                    value=f"```-```", inline=True)
            if Config.review_forum_channel_id():
                embed.add_field(name="", value=f"", inline=False)
                embed.add_field(name="Reviewed", value=f"```{reviewed_count}```", inline=True)
                embed.add_field(name="Unreviewed", value=f"```{unreviewed_count}```", inline=True)
                if last_reviewed_date:
                    embed.add_field(name="Last Reviewed",
                                    value=f"```" + last_reviewed_date.strftime("%m/%d/%y") + "```",
                                    inline=True)
                else:
                    embed.add_field(name="Last Reviewed",
                                    value=f"```-```",
                                    inline=True)
            embed.add_field(name="", value="```----- Guild Wars 2 Stats -----```", inline=False)
            embed.add_field(name="WvW Rank", value=f"```" + str(gw2_account_info["wvw_rank"]) + "```")
            embed.add_field(name="Legendary Spikes", value=f"```" + str(db_member.legendary_spikes()) + "```")
            embed.add_field(name="Weekly Ranks", value=f"```" + str(db_member.weekly_ranks_count()) + "```")
            embed.add_field(name="Weekly Kills", value=f"```" + str(db_member.weekly_kill_count()) + "```")
            embed.add_field(name="Weekly Deaths", value=f"```" + str(db_member.weekly_deaths_count()) + "```")
            embed.add_field(name="Weekly KDR", value=f"```" + str(db_member.weekly_kdr()) + "```")
            embed.add_field(name="Weekly Captures", value=f"```" + str(db_member.weekly_capture_count()) + "```")
            embed.add_field(name="", value=f"")
            embed.add_field(name="", value=f"")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="No API Key Found",
                    description=f"A GW2 API key is required to use this command. Register one with `/set-key`",
                    color=0xff0000
                )
            )


async def setup(bot):
    await bot.add_cog(StatsCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
