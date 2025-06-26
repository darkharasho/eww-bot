import feedparser
import requests
import peewee

from config.imports import *
from discord.ext import commands, tasks
from src import settings
from src import helpers
from src.bot_client import bot
from bs4 import BeautifulSoup
from src.open_ai import ChatGPT

tree = bot.tree


class GameUpdatesTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_updates.start()
        self.guild = self.bot.get_guild(settings.GUILD_ID)

    def cog_unload(self):
        self.game_updates.cancel()

    # @tasks.loop(seconds=60000)
    @tasks.loop(minutes=15.0)
    async def game_updates(self):
        if Config.game_updates() and Config.game_updates(nested_cfg=["enabled"]):
            wvw_feed_url = "https://en-forum.guildwars2.com/discover/80.xml/?member=223901&key=5376b0f04ed61ab7e54bf44bb64b5e0e"
            game_feed_url = "https://en-forum.guildwars2.com/discover/79.xml/?member=223901&key=5376b0f04ed61ab7e54bf44bb64b5e0e"
            studio_feed_url = "https://www.guildwars2.com/en/feed/"
            await self.parse_feed(
                feed_name="Dev Tracker - Game Update Notes",
                db_feed_name="game_updates",
                feed_url=game_feed_url
            )
            await self.parse_feed(
                feed_name="Dev Tracker - WvW Updates",
                db_feed_name="wvw_updates",
                feed_url=wvw_feed_url
            )
            # await self.parse_feed(
            #     feed_name="Dev Tracker - Studio Updates",
            #     db_feed_name="studio_updates",
            #     feed_url=studio_feed_url
            # )

    async def parse_feed(self, feed_name=None, db_feed_name=None, feed_url=None):
        db_feed = Feed.select().where(Feed.name == db_feed_name).first()
        date_format = "%a, %d %b %Y %H:%M:%S %Z"
        if db_feed:
            first_time = False
            post = feedparser.parse(feed_url, modified=db_feed.modified)
            prev_modified = db_feed.modified  # Store so we can check for new items
            db_feed.modified = datetime.datetime.strptime(post['headers']['date'], date_format)
            db_feed.save()
        else:
            first_time = True
            post = feedparser.parse(feed_url)
            if db_feed_name == "studio_updates":
                modified = datetime.datetime.strptime(post['headers']['date'], date_format)
            else:
                modified = datetime.datetime.strptime(post.modified, date_format)
            db_feed = Feed.create(name=db_feed_name, modified=modified, guild_id=settings.GUILD_ID)
        entries = post.entries

        if entries:
            updated_entries = []
            if first_time:
                if db_feed_name == "studio_updates":
                    for entry in entries:
                        if "Studio Update:" in entry.title:
                            updated_entries = [entry]
                else:
                    updated_entries = [entries[0]]
            else:
                for entry in entries:
                    entry_published = datetime.datetime.strptime(entry.published.replace(" +0000", ""),
                                                                 '%a, %d %b %Y %H:%M:%S')
                    if entry_published > prev_modified:
                        updated_entries.append(entry)
            for entry in updated_entries:
                if db_feed_name == "wvw_updates":
                    response = requests.get(entry.link)
                    parsed_html = BeautifulSoup(response.text, features="html.parser")
                    tags = parsed_html.body.find(id='elPostFeed').find_all('a')
                    filtered_tags = []
                    for tag in tags:
                        if "comment-" in tag.get('id', ''):
                            filtered_tags.append(tag['id'].split("-")[-1])
                    if entry.link.split("=")[-1] != filtered_tags[0]:
                        return

                if db_feed_name == "studio_updates":
                    if [item for item in ["Studio Update", "Live Now"] if item in entry.title]:
                        cleantext = BeautifulSoup(entry.content[0]["value"], "html.parser").text
                    else:
                        pdb.set_trace()
                        continue
                else:
                    cleantext = entry.summary

                summary = re.sub(r'\n+', '\n', cleantext)
                if len(summary) > 4096:
                    if settings.OPEN_AI_KEY:
                        summary = ChatGPT().summarize(summary)
                    else:
                        summary = summary.split("\n")[0]

                embed = discord.Embed(
                    title=entry.title,
                    url=entry.link,
                    description=re.sub(r'\n+', '\n', summary),
                    color=0x458bb7)
                embed.set_author(name=feed_name, icon_url=self.guild.icon.url)
                # Convert the timestamp to a datetime object
                datetime_obj = datetime.datetime.strptime(entry.published.replace(" +0000", ""), '%a, %d %b %Y %H:%M:%S')

                # Format the datetime object as a 12-hour timestamp with AM/PM
                formatted_timestamp = datetime_obj.strftime('%a, %d %b %Y %I:%M:%S %p')
                embed.set_footer(text=f"Eww Bot • {formatted_timestamp}")

                file_name = helpers.select_icon("Janthir_Wilds_logo.png")
                file = discord.File(file_name)
                embed.set_thumbnail(url=f"attachment://{file.filename}")

                channel = self.guild.get_channel(Config.game_updates(nested_cfg=["channel_id"]))
                print(f"[GAME UPDATES]".ljust(20) + f"📰 {feed_name} ❗ Found Updates -  {db_feed.modified}")
                await channel.send(embed=embed, file=file)
        else:
            print(f"[GAME UPDATES]".ljust(20) + f"📰 {feed_name} - {db_feed.modified}")


async def setup(bot):
    await bot.add_cog(GameUpdatesTask(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
