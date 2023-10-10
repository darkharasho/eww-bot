from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot


class CheckAttendanceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def check_attendance(self, interaction, member: discord.Member):
        if type(member) is not discord.Member:
            await interaction.response.send_message(
                embed=discord.Embed(title="Error", description="Not a valid user.", color=0xff0000))
            return

        db_member = Member.find_or_create(member=member)
        raid_dates = [attendance.date.strftime("%m/%d/%y") for attendance in
                      db_member.attendances.where(Attendance.raid_type == "raid_day")]
        off_dates = [attendance.date.strftime("%m/%d/%y") for attendance in
                     db_member.attendances.where(Attendance.raid_type == "off_day")]

        raid = db_member.raid_day_count()
        off = db_member.off_day_count()
        total = db_member.total_count()

        tablefmt = "heavy_outline"

        top_headers = ["Total Attendance", "Raid Days", "Off Dates"]
        top_data = [[total, raid, off]]
        top_table = tabulate(top_data, top_headers, tablefmt=tablefmt)
        body = f"📊 **Totals**\n" + f"```elm\n{top_table}```\n"

        headers = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]
        raid_days_table = tabulate(format_dates_for_table(raid_dates), headers, tablefmt=tablefmt)
        off_days_table = tabulate(format_dates_for_table(off_dates), headers, tablefmt=tablefmt)
        body += f"⚔️ **Raid Dates**\n" + f"```elm\n{raid_days_table}```\n"
        body += f"🌑 **Off Dates**\n" + f"```elm\n{off_days_table}```"

        embed = discord.Embed(
            title="",
            description=body,
            color=member.top_role.color
        )

        if member.top_role.display_icon:
            embed.set_footer(text=member.top_role.name, icon_url=member.top_role.display_icon.url)
        else:
            embed.set_author(name=member.name)
        if member.display_avatar:
            embed.set_author(name=f"{member.display_name} ({member.name})", icon_url=member.display_avatar.url)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(CheckAttendanceCog(bot), guild=settings.GUILD_ID, override=True)


def print_dates(date_list):
    if date_list == ["-"]:
        return date_list[0]

    # Define a custom sorting key function
    def custom_sort_key(date_str):
        # Convert the date string to a datetime object
        date_obj = datetime.datetime.strptime(date_str, "%m/%d/%y")
        # Sort by day in descending order
        return -date_obj.day

    # Sort the list of dates using the custom key function
    sorted_dates = sorted(date_list, key=custom_sort_key)

    # Split the sorted dates into groups of three
    grouped_dates = [sorted_dates[i:i + 5] for i in range(0, len(sorted_dates), 5)]

    return "\n".join([' '.join(group) for group in grouped_dates])


def separate_dates_by_day_of_week(week_dates):
    # Create a dictionary to group dates by day of the week
    grouped_dates = {
        'Monday': [],
        'Tuesday': [],
        'Wednesday': [],
        'Thursday': [],
        'Friday': [],
        'Saturday': [],
        'Sunday': [],
    }

    # Convert the date strings to datetime objects and group them
    for date_str in week_dates:
        date_obj = date_str
        day_of_week = date_obj.strftime('%A')  # Get the day of the week as a string
        grouped_dates[day_of_week].append(str(date_str.strftime("%m/%d")))

    # Ensure that each day of the week has at least one date
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if not grouped_dates[day]:
            grouped_dates[day].append("")

    # Create a list of dates sorted by day of the week
    sorted_dates = []
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        sorted_dates.extend(grouped_dates[day])

    return sorted_dates


def separate_dates_by_week(dates):
    # Sort the dates in ascending order
    dates.sort(key=lambda x: datetime.datetime.strptime(x, "%m/%d/%y"))

    weeks = []
    current_week = []

    for date_str in dates:
        date = datetime.datetime.strptime(date_str, "%m/%d/%y")
        if not current_week:
            current_week.append(date)
        elif (date - current_week[0]).days <= 6:
            current_week.append(date)
        else:
            weeks.append(current_week)
            current_week = [date]

    if current_week:
        weeks.append(current_week)

    return weeks


def format_dates_for_table(dates):
    weeks = separate_dates_by_week(list(set(dates)))

    table_formatted = []
    for week in weeks:
        table_formatted.append(separate_dates_by_day_of_week(week))

    formatted_timeline = []
    for week in table_formatted:
        formatted_week = []
        for day in week:
            formatted_week.append(day[:5])
        formatted_timeline.append(formatted_week)

    return formatted_timeline
