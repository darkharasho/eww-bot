import pdb
import datetime

import discord
from peewee import *
from playhouse.sqlite_ext import *
from src import settings
from src import helpers
from src.models.base_model import BaseModel
from src.gw2_api_client import GW2ApiClient


class Member(BaseModel):
    username = CharField(unique=True)
    guild_id = IntegerField()
    discord_id = IntegerField(unique=True)
    gw2_api_key = CharField(null=True)
    gw2_stats = JSONField(null=True)
    gw2_username = CharField(null=True)
    created_at = DateTimeField()
    updated_at = DateTimeField(null=True)

    def total_count(self):
        return self.attendances.count()

    def weekly_kill_count(self):
        if not self.gw2_stats:
            return 0
        return self.gw2_stats["kills"]["this_week"] - self.gw2_stats["kills"]["last_week"]

    def weekly_capture_count(self):
        if not self.gw2_stats:
            return 0
        return self.gw2_stats["captures"]["this_week"] - self.gw2_stats["captures"]["last_week"]

    def weekly_ranks_count(self):
        if not self.gw2_stats:
            return 0
        return self.gw2_stats["wvw_ranks"]["this_week"] - self.gw2_stats["wvw_ranks"]["last_week"]

    def weekly_deaths_count(self):
        if not self.gw2_stats:
            return 0
        return self.gw2_stats["deaths"]["this_week"] - self.gw2_stats["deaths"]["last_week"]

    def weekly_kdr(self):
        return helpers.calculate_kd(self.weekly_kill_count(), self.weekly_deaths_count())

    def weekly_supply_spent(self):
        return self.gw2_stats["supply"]["this_week"] - self.gw2_stats["supply"]["last_week"]

    def weekly_yaks_escorted(self):
        return self.gw2_stats["yaks"]["this_week"] - self.gw2_stats["yaks"]["last_week"]

    def raid_day_count(self):
        from src.models.attendance import Attendance
        return self.attendances.where(Attendance.raid_type == "raid_day").count()

    def off_day_count(self):
        from src.models.attendance import Attendance
        return self.attendances.where(Attendance.raid_type == "off_day").count()

    def last_attended(self):
        from src.models.attendance import Attendance
        last_attendance = self.attendances.order_by(Attendance.date.desc()).limit(1).first()
        if last_attendance:
            return last_attendance.date
        else:
            return None

    def gw2_name(self):
        if self.gw2_username:
            return self.gw2_username
        elif self.gw2_api_key:
            gw2_username = GW2ApiClient(api_key=self.gw2_api_key).account()["name"]
            self.gw2_username = gw2_username
            self.save()
            return gw2_username
        else:
            return ""

    def legendary_spikes(self):
        items = GW2ApiClient(api_key=self.gw2_api_key).bank()
        legendary_spike_id = 81296
        count = 0
        for item in items:
            if item["id"] == legendary_spike_id:
                count += item["count"]
        return count

    def gifts_of_battle(self):
        items = GW2ApiClient(api_key=self.gw2_api_key).bank()
        gift_of_battle_id = 19678
        count = 0
        for item in items:
            if item["id"] == gift_of_battle_id:
                count += item["count"]
        return count

    def supply_spent(self):
        repairs = GW2ApiClient(api_key=self.gw2_api_key).account_achievements(name="Repair Master")
        return repairs[0]["current"]

    def yak_escorts(self):
        yaks = GW2ApiClient(api_key=self.gw2_api_key).account_achievements(name="A Pack Dolyak's Best Friend")
        return yaks[0]["current"]

    @staticmethod
    def find_or_create(member=discord.Member):
        db_member = Member.select().where(Member.discord_id == member.id).first()
        if db_member:
            return db_member
        else:
            return Member.create(
                username=member.name,
                discord_id=member.id,
                guild_id=settings.GUILD_ID,
                created_at=datetime.datetime.now()
            )
