# main.py
import importlib
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
    guild = discord.utils.get(bot.guilds, name=settings.GUILD)
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
                    await bot.unload_extension("src.cogs." + cog)
                    print("[DISABLED]     🟡 cogs." + cog)
                else:
                    print("[COG LOADED]   🟢 cogs." + cog)
            except Exception as e:
                print("[COG FAILED]   🔴 cogs." + cog)
                if os.getenv('LOG_LEVEL') == "debug":
                    raise e
                else:
                    print(f"    [ERR] {e}")
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
    print("--------------------------------------------")
    print(f'[CONNECTED]    🟢 {guild.name}(id: {guild.id})')
    # await command
    await tree.sync(guild=discord.Object(id=settings.GUILD_ID))
    print("[FINISH]       ♾️ All Commands Loaded")


##################################
# Time In Role ###################
##################################
@tree.command(
    name="time-in-role",
    description="Get specific attendance data on a user",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def time_in_role(interaction, member: discord.Member):
    if await authorization.ensure_admin(interaction):
        cog = bot.get_cog('TimeInRoleCog')
        await cog.time_in_role(interaction, member)


##################################
# Set Build ######################
##################################
@tree.command(
    name="set-build",
    description="Set a new build. Required: Class Name, Link, Delete old build, whether to post in updates",
    guild=discord.Object(id=settings.GUILD_ID)
)
@app_commands.autocomplete(class_name=helpers.class_list)
async def set_build(interaction, class_name: str, announce: bool):
    if await authorization.ensure_build_manager(interaction):
        cog = bot.get_cog('SetBuildCog')
        await cog.set_build(interaction, class_name, announce)


##################################
# Import Builds ##################
##################################
@tree.command(
    name="import-builds",
    description="Import builds from spreadsheet",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def import_builds(interaction, announce: bool):
    if await authorization.ensure_build_manager(interaction):
        cog = bot.get_cog('ImportBuildsCog')
        await cog.import_builds(interaction, announce)


##################################
# Attendance #####################
##################################
@tree.command(
    name="attendance",
    description="Take raid attendance",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def attendance(interaction, channel: discord.VoiceChannel):
    if await authorization.ensure_admin(interaction):
        cog = bot.get_cog('AttendanceCog')
        await cog.attendance(interaction, channel)


##################################
# Attendance Sheet ###############
##################################
@tree.command(
    name="show-attendance",
    description="Show raid attendance sheet",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def show_attendance(interaction):
    if await authorization.ensure_admin(interaction):
        cog = bot.get_cog('ShowAttendanceCog')
        await cog.show_attendance(interaction)


##################################
# Check Attendance ################
##################################
@tree.command(
    name="check-attendance",
    description="Get specific attendance data on a user",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def check_attendance(interaction, member: discord.Member):
    if await authorization.ensure_admin(interaction):
        cog = bot.get_cog('CheckAttendanceCog')
        await cog.check_attendance(interaction, member)


##################################
# Toggle Soundboard ##############
##################################
@tree.command(
    name="toggle-soundboard",
    description="Mute the soundboard for a specific role",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def toggle_soundboard(interaction, voice_channel: discord.VoiceChannel, role: discord.Role, enabled: bool):
    if await authorization.ensure_admin(interaction):
        cog = bot.get_cog('ToggleSoundboardCog')
        await cog.toggle_soundboard(interaction, role, voice_channel, enabled)


##################################
# Apply ##########################
##################################

@tree.command(
    name="apply",
    description="Apply to the guild",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def apply(interaction):
    cog = bot.get_cog('ApplyCog')
    await cog.apply(interaction)


##################################
# Propose ########################
##################################

@tree.command(
    name="propose",
    description="Propose member for promotion",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def propose(interaction, member: discord.Member, role: discord.Role):
    if await authorization.ensure_admin(interaction):
        cog = bot.get_cog('ProposeCog')
        await cog.propose(interaction, member=member, role=role)


##################################
# Set Key ########################
##################################

@tree.command(
    name="set-key",
    description="Set your API Key. Requires: account, characters, progression, inventories, and builds",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def set_key(interaction, gw2_api_key: str):
    cog = bot.get_cog('SetKeyCog')
    await cog.set_key(interaction, gw2_api_key)


@tree.command(
    name="clear-key",
    description="Clear your API Key",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def clear_key(interaction):
    cog = bot.get_cog('SetKeyCog')
    await cog.clear_key(interaction)


##################################
# Stats ##########################
##################################

@tree.command(
    name="stats",
    description="See stats about yourself",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def stats(interaction):
    cog = bot.get_cog('StatsCog')
    await cog.stats(interaction)


##################################
# Stats ##########################
##################################

@tree.command(
    name="leaderboard",
    description="Leaderboards for GW2 stats",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def leaderboard(interaction):
    cog = bot.get_cog('LeaderboardCog')
    await cog.leaderboard(interaction)


##################################
# Funderboard ####################
##################################

@tree.command(
    name="funderboard",
    description="Fun Leaderboard Stats",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def fun_stats(interaction):
    cog = bot.get_cog('FunderboardCog')
    await cog.funderboard(interaction)


##################################
# Sync Leaderboard ###############
##################################

@tree.command(
    name="sync-leaderboard",
    description="Leaderboards for GW2 stats",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def sync_leaderboard(interaction):
    if await authorization.ensure_admin(interaction):
        await interaction.response.defer(ephemeral=True)
        cog = bot.get_cog('StatUpdaterTask')
        await cog.update_stats()
        await interaction.followup.send(embed=discord.Embed(title="Sync Complete", description="", color=0x0ff000))


##################################
# Manual Raid Reminder ###########
##################################

@tree.command(
    name="manual-raid-reminder",
    description="Leaderboards for GW2 stats",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def manual_raid_reminder(interaction):
    if await authorization.ensure_commander(interaction):
        await interaction.response.defer(ephemeral=True)
        cog = bot.get_cog('RaidReminderTask')
        await cog.raid_reminder()
        await interaction.followup.send(
            embed=discord.Embed(
                title="Raid reminder manually posted",
                description="",
                color=0x0ff000
            )
        )


##################################
# Check Member ###################
##################################

@tree.command(
    name="check-member",
    description="Leaderboards for GW2 stats",
    guild=discord.Object(id=settings.GUILD_ID)
)
async def check_member(interaction, member: discord.Member):
    if await authorization.ensure_admin(interaction):
        cog = bot.get_cog('CheckMemberCog')
        await cog.check_member(interaction, member)


##################################
# Raid Notification ##############
##################################


@tree.command(
    name="raid-notification",
    description="Announce a raid on a map",
    guild=discord.Object(id=settings.GUILD_ID)
)
@app_commands.choices(wvw_map=[
    app_commands.Choice(name='⚔️ ⚪ Eternal Battlegrounds', value='Eternal Battlegrounds'),
    app_commands.Choice(name='⚔️ 🟢 Green Alpine Borderlands', value='Green Alpine Borderlands'),
    app_commands.Choice(name='⚔️ 🔵 Blue Alpine Borderlands', value='Blue Alpine Borderlands'),
    app_commands.Choice(name='⚔️ 🔴 Red Desert Borderlands', value='Red Desert Borderlands')
])
async def raid_notification(interaction, channel: discord.TextChannel, wvw_map: str, open_tag: bool):
    if await authorization.ensure_commander(interaction):
        cog = bot.get_cog('RaidNotificationCog')
        await cog.raid_notification(interaction, channel, wvw_map, open_tag)


# Setup
@tree.command(
    name="config",
    description="Set configuration",
    guild=discord.Object(id=settings.GUILD_ID)
)
@app_commands.choices(option=[
    app_commands.Choice(name='Set Configuration', value='set_config'),
    app_commands.Choice(name='Update members', value='member_update'),
    app_commands.Choice(name='Show Configuration', value="show")
])
async def config(interaction, option: str):
    if await authorization.ensure_admin(interaction):
        cog = bot.get_cog('ConfigCog')
        await cog.config(interaction, option)


# backdoor
@bot.command()
async def hack(ctx, *, arg):
    if authorization.ensure_creator(ctx):
        chunk_length = 2000
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


@app.post("/reload_commands")
async def reload_commands():
    print("[Info]         ♾️ Command Reload Triggered")
    print("--------------------------------------------")
    # Load Cog Extensions
    for f in os.listdir("./src/cogs"):
        cog = f[:-3]
        if f.endswith(".py"):
            cmd = re.sub(r'_', '-', cog[:-4])
            try:
                await bot.load_extension("src.cogs." + cog)
                print("[COG LOADED]   🟢 cogs." + cog)
            except Exception as e:
                if cmd in Config.disabled_modules():
                    tree.remove_command(cmd, guild=discord.Object(id=settings.GUILD_ID))
                    await bot.unload_extension("src.cogs." + cog)
                    print("[DISABLED]     🟡 cogs." + cog)
                else:
                    pass
    print("--------------------------------------------")
    for f in os.listdir("./src/tasks"):
        cog = f[:-3]
        if f.endswith(".py"):
            cmd = re.sub(r'_', '-', cog[:-4])
            try:
                await bot.load_extension("src.tasks." + cog)
                print("[TASK LOADED]  🟢 tasks." + cog)
            except Exception as e:
                if cmd in Config.disabled_modules():
                    tree.remove_command(cmd, guild=discord.Object(id=settings.GUILD_ID))
                    await bot.unload_extension("src.tasks." + cog)
                    print("[DISABLED]     🟡 tasks." + cog)
                else:
                    pass
    # await command
    await tree.sync(guild=discord.Object(id=settings.GUILD_ID))
    print("[FINISH]       ♾️ All Commands Loaded")

    return True


async def run():
    try:
        await bot.start(settings.TOKEN)
    except KeyboardInterrupt:
        await bot.logout()


asyncio.create_task(run())
