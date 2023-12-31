# main.py
import importlib
import os
import uvicorn
import random

from config.imports import *
from discord.ext import commands
from src import settings
from src import authorization
from src import helpers
from src.bot_client import bot
from src.db_migrate import DBMigrate
from src.catfact import CatFact
from fastapi import FastAPI, HTTPException
from src.open_ai import conversation_client

global guild
tree = bot.tree
app = FastAPI()


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=settings.GUILD)
    await load_db()
    await load_cogs(cog_type="cogs")
    await load_cogs(cog_type="tasks")
    await load_cogs(cog_type="cmds")
    await load_views()
    print("--------------------------------------------")
    print(f"[CONNECTED]".ljust(20) + f"🟢 {guild.name}(id: {guild.id})")
    await tree.sync(guild=discord.Object(id=settings.GUILD_ID))
    print("[FINISH]".ljust(20) + f"♾️ All Commands Loaded")


async def load_db():
    db = SqliteDatabase('eww_bot.db')
    try:
        db.connect()
        db.create_tables([Config, Member, Attendance, ArcDPS, Feed, ApiKey])
        print("[DATABASE]".ljust(20) + f"🟢 DB Connected")
        migrations = DBMigrate().migrate()
        for migrate in migrations:
            print(f"[MIGRATION]".ljust(20) + f"{migrate[0]} {migrate[1]} - {migrate[2]}")
        print("[DATABASE]".ljust(20) + f"🟢 DB Ready")
    except Exception as e:
        print("[DATABASE]".ljust(20) + f"🔴 FAILED")
        if os.getenv('LOG_LEVEL') == "debug":
            raise e
        else:
            print(" ".ljust(23) + f"[ERR] {e}")
            pass


async def load_cogs(cog_type=None):
    if not cog_type:
        raise "Cog Type required"
    print("--------------------------------------------")
    # Load Cog Extensions
    for f in os.listdir(f"./src/{cog_type}"):
        cog = f[:-3]
        if f.endswith(".py"):
            cmd = re.sub(r'_', '-', cog[:-4])
            try:
                await bot.load_extension(f"src.{cog_type}." + cog)
                if cmd in Config.disabled_modules():
                    tree.remove_command(cmd, guild=discord.Object(id=settings.GUILD_ID))
                    print(f"[DISABLED]".ljust(20) + f"🟡 {cog_type}." + cog)
                else:
                    print(f"[{cog_type.upper()} LOADED]".ljust(20) + f"🟢 {cog_type}." + cog)
            except Exception as e:
                print(f"[{cog_type.upper()} FAILED]".ljust(20) + f"🔴 {cog_type}." + cog)
                if os.getenv('LOG_LEVEL') == "debug":
                    raise e
                else:
                    print(" ".ljust(23) + f"[ERR] {e}")


async def load_views():
    print("--------------------------------------------")
    for f in os.listdir("./src/views"):
        view = f[:-3]
        if f.endswith(".py"):
            try:
                print("[VIEW LOADED]".ljust(20) + f"🟢 views." + view)
            except Exception as e:
                print("[VIEW FAILED]".ljust(20) + f"🔴 views." + view)
                if os.getenv('LOG_LEVEL') == "debug":
                    raise e
                else:
                    print(" ".ljust(23) + f"[ERR] {e}")


@bot.event
async def on_message(message):
    if await authorization.ensure_allowed_channel(message, "chat_channel_ids"):
        percentage_chance = random.randint(1, 100)
        if bot.user.mentioned_in(message) and "@everyone" not in message.content:
            if settings.OPEN_AI_KEY:
                if Config.bot_chat_channel_ids():
                    if message.channel.id in Config.bot_chat_channel_ids():
                        if "fleas" in message.author.name and random.randint(1, 100) <= percentage_chance:
                            await CatFact.catfact(message.channel)
                        else:
                            await conversation_client.chunked_converse(message.author, message)
                else:
                    if "fleas" in message.author.name and random.randint(1, 100) <= percentage_chance:
                        await CatFact.catfact(message.channel)
                    else:
                        await conversation_client.chunked_converse(message.author, message)
            else:
                await message.channel.send("I'm sorry Dave, I can't let you do that.")
        await bot.process_commands(message)


@app.get("/modules")
async def modules():
    return settings.MODULES


@app.get("/config_options")
async def config_options():
    return settings.CONFIG_OPTIONS


@app.post("/reload_tasks/{command}")
async def reload_tasks_named(command):
    print("[Info]".ljust(20) + f"♾️ Task Reload Triggered")
    cmd = re.sub(r'-', '_', command)
    await bot.reload_extension("src.tasks." + cmd + "_task")
    print("[ENABLED]".ljust(20) + f"🟢 cogs." + command)
    print("[FINISH]".ljust(20) + f"♾️ Task Reloaded")
    return True


@app.post("/reload_commands")
async def reload_commands():
    print("[Info]".ljust(20) + f"♾️ Command Reload Triggered")

    for module in settings.MODULES:
        if module in Config.disabled_modules():
            tree.remove_command(module, guild=discord.Object(id=settings.GUILD_ID))
            print("[DISABLED]".ljust(20) + f"🟡 cogs." + module)
        else:
            cog = bot.get_cog(helpers.command_to_cog(module))
            cmd = cog.get_app_commands()[0]
            tree.add_command(cmd, guild=discord.Object(id=settings.GUILD_ID))
            print("[ENABLED]".ljust(20) + f"🟢 cogs." + module)
    await tree.sync(guild=discord.Object(id=settings.GUILD_ID))
    print("[FINISH]".ljust(20) + f"♾️ All Commands Loaded")

    return True


async def run():
    try:
        await bot.start(settings.TOKEN)
    except KeyboardInterrupt:
        await bot.logout()


if os.environ.get("BOT_ONLY", False):
    bot.run(settings.TOKEN)
else:
    asyncio.create_task(run())
