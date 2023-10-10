from config.imports import *
from discord.ext import commands, tasks
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from src.views import class_select_view
if Config.raid_reminder():
    time = datetime.time(
        hour=Config.raid_reminder(nested_cfg=["time", "hour"]),
        minute=Config.raid_reminder(nested_cfg=["time", "minute"]),
        tzinfo=datetime.timezone.utc
    )
else:
    time = datetime.time()


class RaidReminderTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.raid_reminder.start()
        self.guild = self.bot.get_guild(settings.GUILD_ID)

    def cog_unload(self):
        self.raid_reminder.cancel()

    # @tasks.loop(seconds=60000)
    @tasks.loop(time=time)
    async def raid_reminder(self):
        today = datetime.datetime.today().weekday()
        if Config.raid_reminder() and today in Config.raid_days():
            channel = self.guild.get_channel(Config.raid_reminder(nested_cfg=["channel_id"]))

            ping_body = ""
            for role_id in Config.raid_reminder(nested_cfg=["role_ids"]):
                role = self.guild.get_role(role_id)
                ping_body += f"{role.mention} "

            embed = discord.Embed(
                title="",
                description="# ⚔️ 📢 RAID REMINDER 📢 ⚔️\n⬇️ Please select the class you plan on bringing below ⬇️",
                color=0x6b1709
            )
            embed.set_author(name=settings.GUILD, icon_url=self.guild.icon.url)

            msg = await channel.send(ping_body, embed=embed)
            view = class_select_view.ClassSelectView(embed, msg)
            await msg.edit(embed=embed, view=view)

        else:
            pass


async def setup(bot):
    await bot.add_cog(RaidReminderTask(bot), guild=settings.GUILD_ID, override=True)
