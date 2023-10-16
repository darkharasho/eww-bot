import requests

from config.imports import *
from discord.ext import commands, tasks
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from bs4 import BeautifulSoup

tree = bot.tree


class ArcDpsCheckTask(commands.Cog):
    def __init__(self, bot):
        self.url = "https://www.deltaconnected.com/arcdps/x64/"
        self.bot = bot
        self.arcdps_check.start()
        self.guild = self.bot.get_guild(settings.GUILD_ID)

    def cog_unload(self):
        self.arcdps_check.cancel()

    # @tasks.loop(seconds=60000)
    @tasks.loop(minutes=15.0)
    async def arcdps_check(self):
        if Config.arcdps_updates() and Config.arcdps_updates(nested_cfg=["enabled"]):
            response = requests.get(self.url)
            parsed_html = BeautifulSoup(response.text, features="html.parser")
            last_updated_at_str = (parsed_html.body.find('tr', attrs={'class': 'odd'}).
                                   find('td', attrs={'class': 'indexcollastmod'}).text)
            last_updated_at = datetime.datetime.strptime(last_updated_at_str.strip(), "%Y-%m-%d %H:%M")
            db_arcdps = ArcDPS.get_last_updated()

            if db_arcdps:
                if last_updated_at > db_arcdps.last_updated_at:
                    ArcDPS.update(last_updated_at=last_updated_at).where(ArcDPS.id == db_arcdps.id).execute()

                    body = f"Latest ArcDPS update: **<t:{int(time.mktime(last_updated_at.timetuple()))}:f>**\n\n"
                    body += f"**⚔️ Download:** [arcdps](https://www.deltaconnected.com/arcdps/x64/)"

                    embed = discord.Embed(
                        title="ArcDPS Update",
                        description=body,
                        color=0xff6723)
                    embed.set_author(name=f"{settings.GUILD} - ArcDPS Releases", icon_url=self.guild.icon.url)

                    file_name = helpers.select_icon("Abacus-Flat-icon")
                    file = discord.File(file_name)
                    embed.set_thumbnail(url=f"attachment://{file.filename}")

                    channel = self.guild.get_channel(Config.arcdps_updates(nested_cfg=["channel_id"]))
                    await channel.send(embed=embed, file=file)
            else:
                ArcDPS.create(last_updated_at=last_updated_at)


async def setup(bot):
    await bot.add_cog(ArcDpsCheckTask(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)

