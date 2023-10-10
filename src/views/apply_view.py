from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from discord.ui import Button, View, Select


class ApplyView(View):
    def __init__(self, interaction, user, channel, question, total_questions):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.user = user
        self.channel = channel
        self.question = question
        self.responses = {}
        self.total_questions = total_questions

    async def interaction_check(self, interaction):
        component_id = interaction.data['custom_id']
        selected_option = interaction.data['values'][0]
        question_text = self.responses.get(component_id)

        self.responses[component_id] = selected_option

        await interaction.response.defer()
        return selected_option

    async def on_timeout(self):
        pass

    async def on_error(self, error, item, ctx):
        pass

    async def send_question(self, index=0):
        question = self.question
        question_text = question['text']
        guild = discord.utils.get(bot.guilds, name=settings.GUILD)
        button = Button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel")

        if question['field_type'] == 'input':
            self.add_item(button)
            # Create an embed for the question
            embed = discord.Embed(
                title=f"Question #{index + 1}/{self.total_questions}",
                description=f"{question_text}\n\n\n (Please send a message with your response)",
                color=0x6b1709
            )

            file_name = helpers.select_icon("clipboard")
            file = discord.File(file_name)
            embed.set_thumbnail(url=f"attachment://{file.filename}")
            embed.set_author(name=f"{settings.GUILD} - Application", icon_url=guild.icon.url)
            await self.channel.send(embed=embed, file=file, view=self)

            events = [
                bot.wait_for('message', check=lambda inter: inter.author == self.user and inter.channel == self.channel),
                bot.wait_for('interaction', check=lambda inter: inter.user == self.user and inter.channel == self.channel)
            ]

            # with asyncio.FIRST_COMPLETED, this triggers as soon as one of the events is fired
            done, pending = await asyncio.wait(events, return_when=asyncio.FIRST_COMPLETED)
            event = done.pop().result()

            # cancel the other check
            for future in pending:
                future.cancel()

            if type(event) == discord.Interaction:
                embed = discord.Embed(
                    title=f"Application Cancelled",
                    description="Successfully Cancelled Application",
                    color=0x6b1709
                )

                file_name = helpers.select_icon("clipboard")
                file = discord.File(file_name)
                embed.set_thumbnail(url=f"attachment://{file.filename}")
                embed.set_author(name=f"{settings.GUILD} - Application", icon_url=guild.icon.url)

                await event.response.send_message(embed=embed, file=file)
                return "APPLICATION_CANCEL"

            else:
                return event.content

        elif question['field_type'] == 'select':
            custom_id = f"select_{index}"
            select_field = Select(
                custom_id=custom_id,
                placeholder="Choose an option...",
                options=[
                    SelectOption(label=option, value=option) for option in question['options']
                ],
            )
            self.add_item(select_field)
            self.add_item(button)

            embed = discord.Embed(title=f"Question #{index + 1}/{self.total_questions}", description=question_text,
                                  color=0x6b1709)
            file_name = helpers.select_icon("clipboard")
            file = discord.File(file_name)
            embed.set_thumbnail(url=f"attachment://{file.filename}")
            embed.set_author(name=f"Question #{index}/{self.total_questions}", icon_url=guild.icon.url)
            await self.user.send(embed=embed, file=file, view=self)

            response = await bot.wait_for(
                "interaction",
                check=lambda inter: inter.user == self.user and inter.channel == self.channel
            )

            if self.responses == {}:
                embed = discord.Embed(
                    title=f"Application Cancelled",
                    description="Successfully Cancelled Application",
                    color=0x6b1709
                )

                file_name = helpers.select_icon("clipboard")
                file = discord.File(file_name)
                embed.set_thumbnail(url=f"attachment://{file.filename}")
                embed.set_author(name=f"{settings.GUILD} - Application", icon_url=guild.icon.url)

                await response.response.send_message(embed=embed, file=file)
                return "APPLICATION_CANCEL"

            return self.responses[custom_id]
