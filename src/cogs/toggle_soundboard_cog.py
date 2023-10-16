from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot

tree = bot.tree


class ToggleSoundboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tree.command(
        name="toggle-soundboard",
        description="Mute the soundboard for a specific role",
        guild=discord.Object(id=settings.GUILD_ID)
    )
    async def toggle_soundboard(self, interaction, role: discord.Role, voice_channel: discord.VoiceChannel,
                                enabled: bool):
        if await authorization.ensure_admin(interaction):
            async def toggle_soundboard_permission_universally(guild: discord.Guild, role: discord.Role,
                                                               voice_channel: discord.VoiceChannel, enabled: bool):
                # Create a new permission overwrite for the role
                overwrite = discord.PermissionOverwrite()

                # Set or clear the permission to send messages in a specific voice_channel
                if enabled:
                    enabled = None
                overwrite.use_soundboard = enabled

                await voice_channel.set_permissions(role, overwrite=overwrite)

            # Example usage:
            # Replace GUILD_ID and ROLE_ID with the actual guild ID and role ID you want to modify
            guild_id = settings.GUILD_ID

            # Fetch the guild and role objects
            guild = discord.utils.get(bot.guilds, id=guild_id)
            if enabled is True:
                # Enable the soundboard permission for the role universally
                await toggle_soundboard_permission_universally(guild, role, voice_channel, True)
                color = 0x0ff000
                soundboard_status="Enabled 🔔"
            else:
                # Disable the soundboard permission for the role universally
                await toggle_soundboard_permission_universally(guild, role, voice_channel, False)
                color = 0xff0000
                soundboard_status="Disabled 🔕"

            embed = discord.Embed(title=role.name,
                                  description=f"{voice_channel.jump_url}\n **Status**: {soundboard_status}",
                                  color=color)
            if role.display_icon:
                embed.set_thumbnail(url=role.display_icon.url)

            await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(ToggleSoundboardCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
