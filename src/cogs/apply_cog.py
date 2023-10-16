from config.imports import *
from discord.ui import Button
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from src.views import apply_view, apply_mod_view, reason_view

tree = bot.tree


class ApplyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tree.command(
        name="apply",
        description="Apply to the guild",
        guild=discord.Object(id=settings.GUILD_ID)
    )
    async def apply(self, interaction):
        guild = discord.utils.get(bot.guilds, name=settings.GUILD)
        # Send an initial message to the user
        embed = discord.Embed(title="Application",
                              description="I'm going to ask you a few "
                                          "questions. Please check your DMs for "
                                          "questions and select your responses.")
        file_name = helpers.select_icon("clipboard")
        file = discord.File(file_name)
        embed.set_thumbnail(url=f"attachment://{file.filename}")
        embed.set_author(name=settings.GUILD, icon_url=guild.icon.url)
        await interaction.response.send_message(embed=embed, file=file, ephemeral=True)

        # Create a list of questions in the specified format
        questions = settings.APPLICATIONS["questions"]
        user = interaction.user
        dm_channel = await user.create_dm()
        answers = {}

        # Create the QuestionView and send the first question
        index = 0
        for question in questions:
            question_view = apply_view.ApplyView(interaction, user, dm_channel, question, len(questions))
            answer = await question_view.send_question(index)
            answers[question["text"]] = answer
            index += 1
            if answer == "APPLICATION_CANCEL":
                break

        contains_cancel = any("APPLICATION_CANCEL" in value for value in answers.values())
        if contains_cancel:
            return

        embed = discord.Embed(title=f"Application Submitted!",
                              description="Thank you for Applying!",
                              color=0x0ff000)
        file_name = helpers.select_icon("clipboard")
        file = discord.File(file_name)
        embed.set_thumbnail(url=f"attachment://{file.filename}")
        embed.set_author(name=settings.GUILD, icon_url=guild.icon.url)
        embed.add_field(name="Discord User", value=str(interaction.user.mention), inline=False)

        for answer_key, answer_value in answers.items():
            embed.add_field(name=answer_key[:256], value=f"```{answer_value}```", inline=False)

        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)

        await dm_channel.send(embed=embed, file=file)

        # Post in the application channel
        channel = interaction.guild.get_channel(int(settings.APPLICATIONS["application_channel_id"]))
        await apply_mod_view.ApplyModView(interaction, answers, channel).send_mod_notification()


async def setup(bot):
    await bot.add_cog(ApplyCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
