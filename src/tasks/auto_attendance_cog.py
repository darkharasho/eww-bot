from config.imports import *
from discord.ext import commands, tasks
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from src.cogs.attendance_cog import attendance_core

if Config.auto_attendance():
    time = datetime.time(
        hour=Config.auto_attendance(nested_cfg=["time", "hour"]),
        minute=Config.auto_attendance(nested_cfg=["time", "minute"]),
        tzinfo=datetime.timezone.utc
    )
else:
    time = datetime.time()


class AutoAttendanceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_attendance.start()
        self.guild = self.bot.get_guild(settings.GUILD_ID)

    def cog_unload(self):
        self.auto_attendance.cancel()

    # @tasks.loop(seconds=60000)
    @tasks.loop(time=time)
    async def auto_attendance(self):
        if Config.auto_attendance() and Config.auto_attendance(nested_cfg=["enabled"]):
            highest_voice_channel_count = 0
            predictive_voice_channel = discord.VoiceChannel
            today = datetime.datetime.today().weekday()
            if today in Config.raid_days():
                for vc in self.guild.voice_channels:
                    if len(vc.members) > highest_voice_channel_count:
                        highest_voice_channel_count = len(vc.members)
                        predictive_voice_channel = vc
                if highest_voice_channel_count == 0:
                    return

                output_channel = bot.get_channel(Config.auto_attendance(nested_cfg=["channel_id"]))
                embeds = await attendance_core(predictive_voice_channel)

                await output_channel.send(embeds=embeds)


async def setup(bot):
    await bot.add_cog(AutoAttendanceCog(bot), guild=settings.GUILD_ID, override=True)
