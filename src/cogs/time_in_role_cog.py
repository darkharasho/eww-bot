from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot

tree = bot.tree


class TimeInRoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tree.command(
        name="time-in-role",
        description="Get specific attendance data on a user",
        guild=discord.Object(id=settings.GUILD_ID)
    )
    async def time_in_role(self, interaction, member: discord.Member):
        if await authorization.ensure_admin(interaction):
            tmp_guild = discord.utils.get(self.bot.guilds, name=settings.GUILD)
            roles = []

            await interaction.response.defer()

            # Fetch the audit logs for the guild
            async for entry in tmp_guild.audit_logs(action=discord.AuditLogAction.member_role_update):
                if entry.target.id == member.id:
                    for role in member.roles:
                        if any(role.id == r.id for r in entry.after.roles):
                            roles.append([role.name, entry.created_at])

            table_data = []
            for role in roles:
                current_datetime = datetime.datetime.now().date()
                role_date = role[1].date()
                days_ago = (current_datetime - role_date).days
                table_data.append([role[0][:25], role[1].strftime('%m/%d/%y'), f"{str(days_ago)} days"])

            tablefmt = "heavy_outline"
            headers = ["Role", "Given", "Time"]
            table = tabulate(table_data, headers, tablefmt=tablefmt)

            embed = discord.Embed(title=f"{member.display_name} ({member.name})", description=f"```{table}```",
                                  color=member.top_role.color)
            embed.set_thumbnail(url=member.display_avatar.url)
            if member.top_role.display_icon:
                embed.set_author(name=member.top_role.name, icon_url=member.top_role.display_icon.url)
            else:
                embed.set_author(name=member.top_role.name)
            embed.set_footer(text="⚠️ Warning: Data only goes back 90 days")

            await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(TimeInRoleCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
