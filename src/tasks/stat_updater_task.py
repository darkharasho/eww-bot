import requests

from config.imports import *
from discord.ext import commands, tasks
from src import settings
from src.bot_client import bot
from src.gw2_api_client import GW2ApiClient

tree = bot.tree


class StatUpdaterTask(commands.Cog):
    def __init__(self, bot, api_key=None):
        self.bot = bot
        self.update_stats.start()
        self.guild = self.bot.get_guild(settings.GUILD_ID)
        self.api_client = GW2ApiClient(api_key=api_key)

    def cog_unload(self):
        self.update_stats.cancel()

    # @tasks.loop(seconds=60000)
    @tasks.loop(minutes=45.0)
    async def update_stats(self):
        await self.bulk_update()

    async def bulk_update(self):
        print("[GW2 SYNC]".ljust(20) + f"🟢 STARTED")
        members = Member.select().where(Member.gw2_api_key.is_null(False))

        # for i in tqdm(range(len(members)), desc="[GW2 SYNC]     "):
        for index, member in enumerate(members, start=1):
            try:
                start_time = datetime.datetime.now()
                self.api_client = GW2ApiClient(api_key=member.gw2_api_key)
                await self.update_kill_count(member)
                await self.update_capture_count(member)
                await self.update_rank_count(member)
                await self.update_deaths_count(member)
                await self.update_supply_spent(member)
                await self.update_yaks_escorted(member)
                print(f"[GW2 SYNC]".ljust(20) + f"🟢 ({index}/{len(members)}) {member.username}: {datetime.datetime.now() - start_time}")
            except Exception as e:
                print(f"[GW2 SYNC]".ljust(20) + f"🔴 ({index}/{len(members)}) {member.username}: {datetime.datetime.now() - start_time}")
                print(" ".ljust(23) + f"[ERR] {e}")

        print("[GW2 SYNC]".ljust(20) + f"🟢 DONE")

    async def update_kill_count(self, member):
        member = Member.get(Member.id == member.id)
        avenger_stats = await self.api_client.aio_account_achievements(name="Emblem of the Avenger")
        kills = avenger_stats[0]["current"] + (avenger_stats[0]["repeated"] * 100)
        await self.update(member=member, stat_name="kills", stat=kills)

    async def update_capture_count(self, member):
        member = Member.get(Member.id == member.id)
        conqueror = await self.api_client.aio_account_achievements(name="Emblem of the Conqueror")
        captures = conqueror[0]["current"] + (conqueror[0]["repeated"] * 100)
        await self.update(member=member, stat_name="captures", stat=captures)

    async def update_rank_count(self, member):
        member = Member.get(Member.id == member.id)
        account = await self.api_client.aio_account()
        wvw_ranks = account["wvw_rank"]
        await self.update(member=member, stat_name="wvw_ranks", stat=wvw_ranks)

    async def update_deaths_count(self, member):
        member = Member.get(Member.id == member.id)
        characters = await self.api_client.aio_characters(ids="all")
        deaths = 0
        for character in characters:
            deaths += character["deaths"]
        await self.update(member=member, stat_name="deaths", stat=deaths)

    async def update_supply_spent(self, member):
        member = Member.get(Member.id == member.id)
        repair_master = await self.api_client.aio_account_achievements(name="Repair Master")
        supply = repair_master[0]["current"]
        await self.update(member=member, stat_name="supply", stat=supply)

    async def update_yaks_escorted(self, member):
        member = Member.get(Member.id == member.id)
        yak_escorts = await self.api_client.aio_account_achievements(name="A Pack Dolyak's Best Friend")
        yaks = yak_escorts[0]["current"]
        await self.update(member=member, stat_name="yaks", stat=yaks)

    @staticmethod
    async def update(member=Member, stat_name=None, stat=None):
        if member.gw2_stats and member.gw2_stats.get(stat_name, None):
            stats = member.gw2_stats
            stats[stat_name]["this_week"] = stat

            # Check if it's reset to update "last_week" data
            current_time_utc = datetime.datetime.utcnow()
            current_time_utc_minus_7 = current_time_utc - datetime.timedelta(hours=7)
            if current_time_utc_minus_7.weekday() == 4 and current_time_utc_minus_7.hour == 17:
                stats[stat_name]["last_week"] = stat
        else:
            stats = member.gw2_stats or {}
            stats[stat_name] = {
                "last_week": stat,
                "this_week": stat
            }
        try:
            Member.update(gw2_stats=stats, updated_at=datetime.datetime.now()).where(Member.id == member.id).execute()
        except:
            sleep(3)
            Member.update(gw2_stats=stats, updated_at=datetime.datetime.now()).where(Member.id == member.id).execute()


async def setup(bot):
    await bot.add_cog(StatUpdaterTask(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
