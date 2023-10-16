# main.py
import importlib
import os
import uvicorn
from config.imports import *
from discord.ext import commands
from src import settings
from src import authorization
from src import helpers
from src.bot_client import bot
from src.db_migrate import DBMigrate
from fastapi import FastAPI, HTTPException

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
    print(f'[CONNECTED]    🟢 {guild.name}(id: {guild.id})')
    await tree.sync(guild=discord.Object(id=settings.GUILD_ID))
    print("[FINISH]       ♾️ All Commands Loaded")


async def load_db():
    db = SqliteDatabase('eww_bot.db')
    try:
        db.connect()
        db.create_tables([Config, Member, Attendance, ArcDPS, Feed])
        print(textwrap.fill("[DATABASE]     🟢 DB Connected", width=80))
        migrations = DBMigrate().migrate()
        for migrate in migrations:
            print(f"[MIGRATION]    {migrate[0]} {migrate[1]} - {migrate[2]}")
    except Exception as e:
        print("[DATABASE]     🔴 FAILED")
        if os.getenv('LOG_LEVEL') == "debug":
            raise e
        else:
            print(f"    [ERR] {e}")
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
                    print(f"[DISABLED]     🟡 {cog_type}." + cog)
                else:
                    print(f"[COG LOADED]   🟢 {cog_type}." + cog)
            except Exception as e:
                print(f"[COG FAILED]   🔴 {cog_type}." + cog)
                if os.getenv('LOG_LEVEL') == "debug":
                    raise e
                else:
                    print(f"    [ERR] {e}")


async def load_views():
    print("--------------------------------------------")
    for f in os.listdir("./src/views"):
        view = f[:-3]
        if f.endswith(".py"):
            try:
                print("[VIEW LOADED]  🟢 views." + view)
            except Exception as e:
                print("[COG FAILED]   🔴 views." + view)
                if os.getenv('LOG_LEVEL') == "debug":
                    raise e
                else:
                    print(f"    [ERR] {e}")


@app.get("/modules")
async def modules():
    return settings.MODULES


@app.post("/reload_tasks/{command}")
async def reload_tasks_named(command):
    print("[Info]         ♾️ Task Reload Triggered")
    cmd = re.sub(r'-', '_', command)
    await bot.reload_extension("src.tasks." + cmd + "_task")
    print("[ENABLED]      🟢 cogs." + command)
    print("[FINISH]       ♾️ Task Reloaded")
    return True


@app.post("/reload_commands")
async def reload_commands():
    print("[Info]         ♾️ Command Reload Triggered")

    for module in settings.MODULES:
        if module in Config.disabled_modules():
            tree.remove_command(module, guild=discord.Object(id=settings.GUILD_ID))
            print("[DISABLED]     🟡 cogs." + module)
        else:
            cog = bot.get_cog(helpers.command_to_cog(module))
            cmd = cog.get_app_commands()[0]
            tree.add_command(cmd, guild=discord.Object(id=settings.GUILD_ID))
            print("[ENABLED]      🟢 cogs." + module)
    await tree.sync(guild=discord.Object(id=settings.GUILD_ID))
    print("[FINISH]       ♾️ All Commands Loaded")

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
