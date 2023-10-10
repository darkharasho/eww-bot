from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from discord import ui


class ReasonView(discord.ui.Modal):
    reason = ui.TextInput(label='Reason', style=discord.TextStyle.paragraph, required=True)

    def __init__(self, embed=discord.Embed()):
        super().__init__(title="Application Reason")
        self.embed = embed

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.embed.add_field(name="Reason Given", value=f"```{self.reason}```", inline=False)

        await interaction.channel.send(embed=self.embed, reference=interaction.message)
