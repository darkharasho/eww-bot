from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from discord.ui import Button, View, Select
from tabulate import SEPARATING_LINE
from src.views import set_multi_config_view


class KeyManagementView(discord.ui.View):
    def __init__(self, channel, options):
        super().__init__(timeout=None)
        self.channel = channel
        self.guild = bot.get_guild(settings.GUILD_ID)
        self.options = options

    @discord.ui.select(options=options(), placeholder="Select key...")
    async def on_select(self, interaction, options):
        await interaction.response.defer()
        selected_option = interaction.data['values'][0]

        if selected_option == "GuildMemberRole":
            role_options = self.role_select()
            self.clear_items()
            self.embed.description = "```Guild Member Role:\nPlease select the main role for guild members below.```"
            self.add_item(item=discord.ui.Select(placeholder="Select Guild Member Role...",
                                                 options=role_options))
