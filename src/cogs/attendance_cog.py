from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot

tree = bot.tree


class AttendanceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tree.command(
        name="attendance",
        description="Take raid attendance",
        guild=discord.Object(id=settings.GUILD_ID)
    )
    async def attendance(self, interaction, channel: discord.VoiceChannel):
        if await authorization.ensure_admin(interaction):
            await interaction.response.defer()

            # Escape if for any reason the channel wasn't found
            if channel is None:
                await interaction.response.send_message(
                    embed=discord.Embed(title="Error", description="Invalid channel selection.", color=0xff0000))
                return

            embeds = await attendance_core(channel)

            await interaction.followup.send(embeds=embeds)


async def setup(bot):
    await bot.add_cog(AttendanceCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)


def format_member_name(member: discord.Member):
    pattern = r'[^a-zA-Z0-9∴\s]'
    clean_name = helpers.strip_emojis(member.display_name)
    clean_name = re.sub(pattern, '', clean_name)

    member_name = f"{clean_name.title()} ({member.name.lower()})"[:30]

    return member_name


def format_attended_for_table(members: list):
    sorted_enriched_members = []
    for member in members:
        db_member = Member.select().where(Member.discord_id == member.id).first()

        sorted_enriched_members.append([
            f"{format_member_name(member)})"[:30],
            db_member.total_count(),
            f"({db_member.raid_day_count()}|{db_member.off_day_count()})"
        ])
    return sorted_enriched_members


def format_absent_for_table(members: list):
    sorted_enriched_absent_members = []
    for member in members:
        db_member = Member.select().where(Member.discord_id == member.id).first()
        last_date = db_member.attendances.order_by(Attendance.date.desc()).limit(1).first()
        if last_date:
            last_date = last_date.date.strftime("%m/%d/%y")
        else:
            last_date = "-"

        sorted_enriched_absent_members.append([
            f"{format_member_name(member)})"[:30],
            last_date
        ])
    return sorted_enriched_absent_members


async def attendance_core(channel):
    today = datetime.datetime.today().strftime("%m/%d/%y")
    current_day = datetime.datetime.now().weekday()
    raid_day = helpers.check_raid_time

    # Increment the attendance count for each member
    attended_current_raid = []
    attendance_check_data = []
    already_attended_current_raid = []
    members = channel.members
    guild = discord.utils.get(bot.guilds, name=settings.GUILD)
    total_members = []

    for member in guild.members:
        if helpers.check_guild_role(member=member):
            total_members.append(member)

    for member in members:
        if helpers.check_guild_role(member=member):
            db_member = Member.find_or_create(member=member)
            dates = [attendance.date.strftime("%m/%d/%y") for attendance in db_member.attendances]

            if today not in dates:
                if current_day in Config.raid_days():
                    Attendance.create(member=db_member, date=datetime.datetime.today(), raid_type="raid_day")
                else:
                    Attendance.create(member=db_member, date=datetime.datetime.today(), raid_type="off_day")
                attended_current_raid.append(member)
            else:
                already_attended_current_raid.append(member)
            attendance_check_data.append(member)
    sorted_attended_current_raid = sorted(
        attended_current_raid,
        key=lambda x: Member.select().where(Member.discord_id == x.id).first().total_count(),
        reverse=True
    )
    sorted_already_attended_current_raid = sorted(
        already_attended_current_raid,
        key=lambda x: Member.select().where(Member.discord_id == x.id).first().total_count(),
        reverse=True
    )

    body = f"**Total Attended:** {len(members)}/{len(total_members)}\n"
    body = body + f"**Taken in:** {channel.name[:46]} 🔊\n"
    if raid_day is True:
        body = body + f"**Raid Day:** Yes \n\n"
    else:
        body = body + f"**Raid Day:** No \n\n"

    # Absent
    absent_members = []
    for absent_member in total_members:
        if absent_member not in attendance_check_data:
            Member.find_or_create(member=absent_member)
            absent_members.append(absent_member)

    sorted_absent_members = sorted(
        absent_members,
        key=lambda x: Member.select().where(Member.discord_id == x.id).first().total_count(),
        reverse=True
    )

    sorted_enriched_attended_current_raid = format_attended_for_table(sorted_attended_current_raid)
    sorted_enriched_absent_members = format_absent_for_table(sorted_absent_members)
    sorted_enriched_already_attended_current_raid = format_attended_for_table(sorted_already_attended_current_raid)

    tablefmt = "heavy_outline"
    attended_headers = ["Name", "Total", "(Raid|Off)"]
    absent_headers = ["Name", "Last Attended"]

    attended_has_members = False
    already_attended_has_members = False
    absent_has_members = False

    if sorted_attended_current_raid:
        attended_has_members = True
    if sorted_already_attended_current_raid:
        already_attended_has_members = True
    if sorted_absent_members:
        absent_has_members = True

    attended_table = tabulate(sorted_enriched_attended_current_raid, attended_headers, tablefmt=tablefmt)
    absent_table = tabulate(sorted_enriched_absent_members, absent_headers, tablefmt=tablefmt)
    already_attended_table = tabulate(sorted_enriched_already_attended_current_raid, attended_headers, tablefmt)
    embeds = []
    group_size = 65
    max_size = 3961  # Largest supported size given the default information on every attendance (4096 - 135)

    if (len(attended_table) + len(absent_table) + len(already_attended_table)) > max_size:
        # Split the attended into embeds
        if attended_has_members:
            attended_embed_count = 1
            for i in range(0, len(sorted_enriched_attended_current_raid), group_size):
                group = sorted_enriched_attended_current_raid[i:i + group_size]
                shortened_table = tabulate(group, attended_headers, tablefmt=tablefmt)

                embeds.append(
                    discord.Embed(
                        title=f"{today} - Attendance {attended_embed_count}",
                        description=body + f"**✅ Attended**\n" + f"```elm\n{shortened_table}```\n",
                        color=0x0ff000)
                )
                attended_embed_count += 1

        if already_attended_has_members:
            already_attended_count = 1
            for i in range(0, len(sorted_enriched_already_attended_current_raid), group_size):
                group = sorted_enriched_already_attended_current_raid[i:i + group_size]
                shortened_table = tabulate(group, attended_headers, tablefmt=tablefmt)

                embeds.append(
                    discord.Embed(
                        title=f"{today} - Attendance {already_attended_count}",
                        description=body + "**⏭️ Already Attended**\n" + f"```elm\n{shortened_table}```",
                        color=0xfff000)
                )
                already_attended_count += 1

        if absent_has_members:
            absent_embed_count = 1
            for i in range(0, len(sorted_enriched_absent_members), group_size):
                group = sorted_enriched_absent_members[i:i + group_size]
                shortened_table = tabulate(group, absent_headers, tablefmt=tablefmt)

                embeds.append(
                    discord.Embed(
                        title=f"{today} - Attendance {absent_embed_count}",
                        description=body + "**❌ Absent**\n" + f"```elm\n{shortened_table}```",
                        color=0xff0000)
                )
                absent_embed_count += 1
    else:
        # Attended members
        if attended_has_members:
            body = body + f"**✅ Attended**\n"
            body = body + f"```elm\n{attended_table}```\n"
        if already_attended_has_members:
            body = body + f"**⏭️ Already Counted**\n"
            body = body + f"```elm\n{already_attended_table}```\n"
        if absent_has_members:
            body = body + "**❌ Absent**\n"
            body = body + f"```elm\n{absent_table}```"

        embeds.append(
            discord.Embed(title=f"{today} - Attendance", description=body, color=0x0ff000)
        )

    return embeds
