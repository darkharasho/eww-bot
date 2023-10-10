from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot


class ShowAttendanceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def show_attendance(self, interaction):
        guild = discord.utils.get(bot.guilds, name=settings.GUILD)
        role = discord.utils.get(guild.roles, id=Config.guild_member_role_id())

        members_body = []
        for member in role.members:
            members_body.append(attended_member_formatter(member))
        sorted_body = sorted(members_body, key=lambda x: x[1], reverse=True)

        tablefmt = "heavy_outline"
        headers = ["Name", "Total", "(R|O)", "Last"]
        table = tabulate(sorted_body, headers, tablefmt=tablefmt)
        embeds = []
        group_size = 65
        max_size = 4096

        if len(table) > max_size:
            sheet_count = 1
            for i in range(0, len(sorted_body), group_size):
                group = sorted_body[i:i + group_size]
                shortened_table = tabulate(group, headers, tablefmt=tablefmt)

                embeds.append(
                    discord.Embed(
                        title=f"📋 Attendance Sheet {sheet_count}",
                        description=f"```elm\n{shortened_table}```",
                        color=0x0ff000)
                )
                sheet_count += 1
        else:
            embeds.append(
                discord.Embed(title="📋 Attendance Sheet", description=f"```elm\n{table}```", color=0x0ff000)
            )

        await interaction.response.send_message(embeds=embeds)


async def setup(bot):
    await bot.add_cog(ShowAttendanceCog(bot), guild=settings.GUILD_ID, override=True)


def attended_member_formatter(member: discord.Member):
    pattern = r'[^a-zA-Z0-9∴\s]'
    clean_name = helpers.strip_emojis(member.display_name)
    clean_name = re.sub(pattern, '', clean_name)
    name = f"{clean_name.title()} ({member.name})"[:25]
    db_member = Member.find_or_create(member=member)

    raid = helpers.format_number(db_member.raid_day_count())
    off = helpers.format_number(db_member.off_day_count())
    total = helpers.format_number(db_member.total_count())
    last = db_member.attendances.order_by(Attendance.date.desc()).limit(1).first()
    if last:
        last = last.date.strftime("%m/%d/%y")

    return [name, total, f"({raid}|{off})", last]
