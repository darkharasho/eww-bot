from config.imports import *
from discord.ext import commands
from src import settings
from src.gw2_api_client import GW2ApiClient
from src.bot_client import bot
from src.tasks.stat_updater_task import StatUpdaterTask


class SetKeyCog(commands.Cog):
    def __init__(self, option):
        self.option = option
        self.db = SqliteDatabase('eww_bot.db')
        self.guild = bot.get_guild(settings.GUILD_ID)

    @commands.command(pass_context=True)
    async def set_key(self, interaction, gw2_api_key):
        await interaction.response.defer(ephemeral=True)
        db_member = Member.find_or_create(interaction.user)
        api_client = GW2ApiClient(api_key=gw2_api_key)
        api_checks = []
        api_checks_display = []
        try:
            if not api_client.account():
                raise
            api_checks.append(True)
            api_checks_display.append("✅ Account")
        except:
            api_checks.append(False)
            api_checks_display.append("❌ Account")

        try:
            if not api_client.account_achievements():
                raise
            api_checks.append(True)
            api_checks_display.append("✅ Progression")
        except:
            api_checks.append(False)
            api_checks_display.append("❌ Progression")

        try:
            if not api_client.characters():
                raise
            api_checks.append(True)
            api_checks_display.append("✅ Characters")
        except:
            api_checks.append(False)
            api_checks_display.append("❌ Characters")

        try:
            if not api_client.builds(index=0, tabs="all"):
                raise
            api_checks.append(True)
            api_checks_display.append("✅ Builds")
        except:
            api_checks.append(False)
            api_checks_display.append("❌ Builds")
        try:
            if not api_client.bank():
                raise
            api_checks.append(True)
            api_checks_display.append("✅ Inventories")
        except:
            api_checks.append(False)
            api_checks_display.append("❌ Inventories")

        if all(api_checks):
            Member.update(gw2_api_key=gw2_api_key).where(Member.id == db_member.id).execute()

            suc = StatUpdaterTask(bot, api_key=gw2_api_key)
            await suc.update_kill_count(db_member)
            await suc.update_capture_count(db_member)
            await suc.update_rank_count(db_member)
            await suc.update_deaths_count(db_member)
            await suc.update_supply_spent(db_member)
            await suc.update_yaks_escorted(db_member)

            await interaction.followup.send(
                embed=discord.Embed(
                    title="Guild Wars 2 API Key",
                    description=f"**API key registered for:** {interaction.user.mention}```{gw2_api_key}```",
                    color=0x0ff000),
                ephemeral=True)
        else:
            embed = discord.Embed(
                    title="Guild Wars 2 API Key - Invalid GW2 API Key or Insufficient Permissions",
                    color=0xff0000)
            for api_check in api_checks_display:
                embed.add_field(name=api_check, value="")
            embed.add_field(name="", value="")
            embed.add_field(name="GW2 API Key", value=f"```{gw2_api_key}```", inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True)

    @commands.command(pass_context=True)
    async def clear_key(self, interaction):
        db_member = Member.find_or_create(interaction.user)
        with self.db.atomic():
            Member.update(gw2_api_key=None).where(Member.id == db_member.id).execute()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Guild Wars 2 API Key",
                description=f"**API key cleared for:** {interaction.user.mention}",
                color=0x0ff000),
            ephemeral=True)


async def setup(bot):
    await bot.add_cog(SetKeyCog(bot), guild=settings.GUILD_ID, override=True)
