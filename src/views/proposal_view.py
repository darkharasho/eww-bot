from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from discord.ui import Button, View, Select
from tabulate import SEPARATING_LINE


class ProposalView(discord.ui.View):
    def __init__(self, embed):
        super().__init__(timeout=604800)
        self.embed = embed
        if not hasattr(self, 'responses'):
            self.responses = {}

    @discord.ui.button(label="Yay", style=discord.ButtonStyle.green, custom_id=f"yay_{datetime.datetime.now()}")
    async def yay(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        msg = interaction.message

        for index, field in enumerate(self.embed.fields):
            if field.name == "Yays":
                field_values = field.value.split("\n")
                field_values.append(f"{interaction.user.mention}")
                field.values = "\n".join(field_values)
                self.embed.set_field_at(index, name="Yays", value=field.values, inline=False)
            elif field.name == "Nays":
                field_values = field.value.split("\n")
                if interaction.user.mention in field_values:
                    field_values.remove(interaction.user.mention)
                    field.values = "\n".join(field_values)
                    self.embed.set_field_at(index, name="Nays", value=field.values, inline=False)

        await msg.edit(embed=self.embed, view=self)

    @discord.ui.button(label="Nay", style=discord.ButtonStyle.red, custom_id=f"nay_{datetime.datetime.now()}")
    async def nay(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        msg = interaction.message

        for index, field in enumerate(self.embed.fields):
            if field.name == "Nays":
                field_values = field.value.split("\n")
                field_values.append(f"{interaction.user.mention}")
                field.values = "\n".join(field_values)
                self.embed.set_field_at(index, name="Nays", value=field.values, inline=False)
            elif field.name == "Yays":
                field_values = field.value.split("\n")
                if interaction.user.mention in field_values:
                    field_values.remove(interaction.user.mention)
                    field.values = "\n".join(field_values)
                    self.embed.set_field_at(index, name="Yays", value=field.values, inline=False)

        await msg.edit(embed=self.embed, view=self)
