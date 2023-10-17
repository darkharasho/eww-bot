import feedparser
import requests

from config.imports import *
from discord.ext import commands, tasks
from src import settings
from src import helpers
from src.bot_client import bot
from bs4 import BeautifulSoup

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

    async def parse_feed(self, feed_name=None, db_feed_name=None, feed_url=None):
        db_feed = Feed.select().where(Feed.name == db_feed_name).first()
        if db_feed:
            first_time = False
            post = feedparser.parse(feed_url, modified=db_feed.modified)
            db_feed.modified = post['headers']['date']
            db_feed.save()
        else:
            first_time = True
            post = feedparser.parse(feed_url)
            db_feed = Feed.create(name=db_feed_name, modified=post.modified, guild_id=settings.GUILD_ID)
        entries = post.entries

        if entries:
            updated_entries = []
            if first_time:
                updated_entries = [entries[0]]
            else:
                for entry in entries:
                    entry_published = datetime.datetime.strptime(entry.published.replace(" +0000", ""),
                                                                 '%a, %d %b %Y %H:%M:%S')
                    db_modified = datetime.datetime.strptime(db_feed.modified.replace(" GMT", ""),
                                                             '%a, %d %b %Y %H:%M:%S')
                    if entry_published > db_modified:
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

                summary = re.sub(r'\n+', '\n', entry.summary)
                if len(summary) > 4096:
                    summary = summary.split("\n")[0]

                embed = discord.Embed(
                    title=entry.title,
                    url=entry.link,
                    description=re.sub(r'\n+', '\n', summary),
                    color=0xd6a24a)
                embed.set_author(name=feed_name, icon_url=self.guild.icon.url)
                # Convert the timestamp to a datetime object
                datetime_obj = datetime.datetime.strptime(entry.published.replace(" +0000", ""), '%a, %d %b %Y %H:%M:%S')

                # Format the datetime object as a 12-hour timestamp with AM/PM
                formatted_timestamp = datetime_obj.strftime('%a, %d %b %Y %I:%M:%S %p')
                embed.set_footer(text=f"Eww Bot • {formatted_timestamp}")

                file_name = helpers.select_icon("Secrets_of_the_Obscure_logo")
                file = discord.File(file_name)
                embed.set_thumbnail(url=f"attachment://{file.filename}")

                channel = self.guild.get_channel(Config.game_updates(nested_cfg=["channel_id"]))
                await channel.send(embed=embed, file=file)


async def setup(bot):
    await bot.add_cog(GameUpdatesTask(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
