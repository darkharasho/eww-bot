import discord
from src import settings
from src import helpers
from src.models.config import Config


async def ensure_admin(interaction):
    user_role_ids = [role.id for role in interaction.user.roles]
    allowed_admin_role_ids = Config.allowed_admin_role_ids()

    if not allowed_admin_role_ids:
        for role in interaction.user.roles:
            if role.permissions.administrator:
                return True
        if interaction.user.guild_permissions.administrator:
            return True

    if not any(role_id in allowed_admin_role_ids for role_id in user_role_ids):
        embed = discord.Embed(title="Unauthorized", description="You do not have permission to run this command.",
                              color=0xff0000)

        file_name = helpers.select_icon("unauthorized")
        file = discord.File(file_name)
        embed.set_thumbnail(url=f"attachment://{file.filename}")
        await interaction.response.send_message(
            embed=embed, file=file, ephemeral=True)
        return False
    return True


async def ensure_build_manager(interaction):
    user_role_ids = [role.id for role in interaction.user.roles]
    all_allowed_role_ids = list(set(Config.allowed_admin_role_ids() + Config.build_manager_role_ids()))

    if not any(role_id in all_allowed_role_ids for role_id in user_role_ids):
        embed = discord.Embed(title="Unauthorized", description="You do not have permission to run this command.",
                              color=0xff0000)

        file_name = helpers.select_icon("unauthorized")
        file = discord.File(file_name)
        embed.set_thumbnail(url=f"attachment://{file.filename}")
        await interaction.response.send_message(
            embed=embed, file=file, ephemeral=True)
        return False
    return True


async def ensure_commander(interaction):
    user_role_ids = [role.id for role in interaction.user.roles]
    all_allowed_role_ids = list(set(Config.allowed_admin_role_ids() + Config.commander_role_ids()))

    if not any(role_id in all_allowed_role_ids for role_id in user_role_ids):
        embed = discord.Embed(title="Unauthorized", description="You do not have permission to run this command.",
                              color=0xff0000)

        file_name = helpers.select_icon("unauthorized")
        file = discord.File(file_name)
        embed.set_thumbnail(url=f"attachment://{file.filename}")
        await interaction.response.send_message(
            embed=embed, file=file, ephemeral=True)
        return False
    return True


def ensure_creator(ctx):
    if ctx.author.id == 201537071804973056:
        return True
    else:
        return False
