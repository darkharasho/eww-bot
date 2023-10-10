from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot


class ImportBuildsCog(commands.Cog):
    def __init__(self, passed_bot):
        self.passed_bot = passed_bot

    @commands.command(pass_context=True)
    async def import_builds(self, interaction, announce: bool):
        await interaction.response.defer(ephemeral=True)
        today = datetime.datetime.today().strftime("%m/%d/%y")

        # Define the scope and authenticate using the JSON key file
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        gc = gspread.service_account(filename=settings.GOOGLE_CREDS_FILE)

        # Open the Google Sheet by name
        worksheet = gc.open(settings.GOOGLE_SHEET_NAME).sheet1  # You can specify the sheet by index or name

        # Get all the values from the worksheet
        data = worksheet.get_all_records()

        channel = interaction.guild.get_channel(Config.build_forum_channel_id())
        all_builds = []
        new_builds = [obj for obj in data if obj.get('New?', '').strip().upper() == 'TRUE']
        for build in new_builds:
            if build['Name'] in (thread.name for thread in channel.threads):
                await helpers.delete_thread(channel, build['Name'])
            # Find the correct tag
            available_tags = channel.available_tags
            tag = helpers.select_tag(available_tags, build['Class'])

            embed, file = helpers.build_embed(
                user=interaction.user,
                class_name=build['Class'],
                name=build['Name'],
                link=build['Link'],
                chat_code=build['ChatCode']
            )

            thread_with_message = await channel.create_thread(
                name=build['Name'],
                embed=embed,
                file=file,
                applied_tags=[tag],
                mention_author=True
            )

            if announce is True:
                update_channel = interaction.guild.get_channel(Config.build_update_channel_id())
                await helpers.post_update(update_channel, thread_with_message.thread, file.filename, build['Class'],
                                          interaction.user)

            all_builds.append(
                helpers.find_emoji_by_name_pattern(build['Class']) + " " + thread_with_message.thread.jump_url)

            cell = worksheet.find(build['Name'])  # Find the cell corresponding to the build name
            worksheet.update('E{row}'.format(row=cell.row), '')

        if not all_builds:
            embed = discord.Embed(title="Import Builds", description="No new builds to import.", color=0x0ff000)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="✅ Successfully posted new builds", description="\n".join(all_builds),
                                  color=0x0ff000)
            embed.add_field(name="Updated By", value=interaction.user.name, inline=True)
            embed.add_field(name="Updated On", value=today)
            embed.add_field(name="Announced?", value=announce, inline=False)
            await interaction.followup.send(embed=embed)


async def setup(passed_bot):
    await passed_bot.add_cog(ImportBuildsCog(passed_bot), guild=settings.GUILD_ID, override=True)
