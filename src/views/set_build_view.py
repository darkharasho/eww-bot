from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from discord import ui


class SetBuildView(discord.ui.Modal):
    name = ui.TextInput(label='Build Name', style=discord.TextStyle.short, required=True)
    build_link = ui.TextInput(label='Build Link', style=discord.TextStyle.paragraph, required=True)
    chat_code = ui.TextInput(label='Chat Code', style=discord.TextStyle.paragraph, required=True)
    description = ui.TextInput(label='Description', style=discord.TextStyle.paragraph, required=False)

    def __init__(self, class_name=str, announce=bool):
        if announce:
            title = f"New {class_name} Build 🔔"
        else:
            title = f"New {class_name} Build 🔕"
        super().__init__(title=title)
        self.class_name = class_name
        self.announce = announce

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        channel = interaction.guild.get_channel(Config.build_forum_channel_id())

        if str(self.name) in (thread.name for thread in channel.threads):
            await helpers.delete_thread(channel, str(self.name))

        # Find the correct tag
        available_tags = channel.available_tags
        tag = helpers.select_tag(available_tags, self.class_name)

        embed, file = helpers.build_embed(user=interaction.user, class_name=self.class_name, name=self.name, link=self.build_link,
                                          chat_code=self.chat_code, description=self.description)

        thread_with_message = await channel.create_thread(
            name=str(self.name),
            embed=embed,
            file=file,
            applied_tags=[tag],
            mention_author=True
        )

        if self.announce is True:
            update_channel = interaction.guild.get_channel(Config.build_update_channel_id())
            await helpers.post_update(update_channel, thread_with_message.thread, file.filename, self.class_name,
                                      interaction.user)

        # Dumb, dumb discord.py closes the file and embed before this point for ✨ reasons ✨
        embed, file = helpers.build_embed(user=interaction.user, class_name=self.class_name, name=self.name, link=self.build_link,
                                          chat_code=self.chat_code, description=self.description)

        # Edit spreadsheet
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        gc = gspread.service_account(filename=settings.GOOGLE_CREDS_FILE)

        # Open the Google Sheet by name
        worksheet = gc.open(settings.GOOGLE_SHEET_NAME).sheet1  # You can specify the sheet by index or name
        cell_list = worksheet.findall(str(self.name), in_column=2)

        # Check if any cells were found
        if cell_list:
            # Assuming you want to update the first occurrence found
            cell = cell_list[0]
            row_number = cell.row
            update_count = 0

            # Update the values in columns C and D of the same row
            if not worksheet.cell(row_number, 3).value == str(self.build_link):
                worksheet.update(f'C{row_number}', str(self.build_link))
                update_count += 1
            if not worksheet.cell(row_number, 4).value == str(self.chat_code):
                worksheet.update(f'D{row_number}', str(self.chat_code))
                update_count += 1
            if update_count == 0:
                embed.add_field(name="SS Status", value="None needed")
            elif update_count >= 1:
                embed.add_field(name="SS Status", value="Partial update")
        else:
            column_b_values = worksheet.col_values(2)  # Assuming column B is the second column (index 2)
            first_empty_row = len(column_b_values) + 1
            new_row = [[str(self.class_name), str(self.name), str(self.build_link), str(self.chat_code)]]

            worksheet.insert_rows(list(new_row), row=first_empty_row)  # Insert the new row at the first free line
            embed.add_field(name="SS Status", value="Added")

        file_name = helpers.select_file(self.class_name)
        file = discord.File(file_name)

        await interaction.followup.send(embed=embed, file=file)
