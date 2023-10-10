from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from discord.ui import Button, View, Select
from src.views import reason_view


class ApplyModView(View):
    def __init__(self, interaction, application, channel):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.user = interaction.user
        self.channel = channel
        self.application = application
        self.message = None

    async def on_timeout(self):
        pass

    async def on_error(self, error, item, ctx):
        pass

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id=f"accept_{datetime.datetime.now()}")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = discord.utils.get(bot.guilds, name=settings.GUILD)
        # Handle the Accept button click
        # Add roles defined in settings.APPLICATIONS["accepted_roles"]
        roles = []
        for role_name in settings.APPLICATIONS["accepted_roles"]:
            roles.append(await helpers.find_role_by_name(guild, role_name))

        try:
            await self.user.add_roles(*roles)
        except discord.Forbidden:
            print("Bot doesn't have permission to assign roles.")
        except discord.HTTPException as e:
            print(f"An error occurred: {e}")

        self.clear_items()
        await self.message.edit(view=self)
        embed = discord.Embed(title="✅ Application Accepted!", description="", color=0x0ff000)
        embed.add_field(name="Application", value=self.message.jump_url, inline=False)
        embed.add_field(name="Handle", value=self.user.mention)
        embed.add_field(name="Username", value=self.user.name)
        embed.add_field(name="Roles Added", value=" ".join(role.mention for role in roles), inline=False)
        embed.set_author(name=f"{interaction.user.display_name} ({interaction.user.name})",
                         icon_url=interaction.user.display_avatar.url)
        embed.set_thumbnail(url=self.user.display_avatar.url)

        modal = reason_view.ReasonView(embed=embed)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red, custom_id=f"reject_{datetime.datetime.now()}")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        await self.message.edit(view=self)

        reject_embed = discord.Embed(title="🚫 Application Rejected", description="",
                                     color=0xff0000)
        reject_embed.add_field(name="Application", value=self.message.jump_url, inline=False)
        reject_embed.add_field(name="Handle", value=self.user.mention)
        reject_embed.add_field(name="Username", value=self.user.name)
        reject_embed.set_author(
            name=f"{interaction.user.display_name} ({interaction.user.name})",
            icon_url=interaction.user.display_avatar.url)
        reject_embed.set_thumbnail(url=interaction.user.display_avatar.url)

        modal = reason_view.ReasonView(embed=reject_embed)
        await interaction.response.send_modal(modal)

    async def send_mod_notification(self):
        guild = discord.utils.get(bot.guilds, name=settings.GUILD)
        embed = discord.Embed(title=f"New Application",
                              description="",
                              color=0x6b1709)
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.set_author(name=settings.GUILD, icon_url=guild.icon.url)
        embed.add_field(name="Discord User", value=str(self.user.mention), inline=False)

        for key, value in self.application.items():
            embed.add_field(name=key[:256], value=f"```{value}```", inline=False)

        embed.set_footer(text=self.user.name, icon_url=self.user.display_avatar.url)

        # Send the message with the buttons
        self.message = await self.channel.send(f"Application for {self.user.mention} submitted", embed=embed, view=self)
