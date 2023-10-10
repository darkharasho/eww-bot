from config.imports import *
from discord.ext import commands
from src import settings
from src.bot_client import bot
from src.models.member import Member
from src.models.attendance import Attendance


def on_ready():
    with open('attendance.json', "r") as file:
        attendance_data = json.load(file)

    guild = discord.utils.get(bot.guilds, name=settings.GUILD)
    for key, value in attendance_data.items():
        db_member = Member.select().where(Member.discord_id == int(key)).first()
        if db_member:
            member = db_member
        else:
            member = Member.create(username=value["name"], discord_id=int(key), guild_id=settings.GUILD_ID)

        for date in value["dates"]:
            formatted_date = datetime.datetime.strptime(date["date"], "%m/%d/%y")
            Attendance.create(member=member, date=formatted_date, raid_type=date["day_type"])
    return


on_ready()
