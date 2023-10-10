from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from discord.ui import Button, View, Select
from tabulate import SEPARATING_LINE

options = []
classes = Config.raid_reminder(nested_cfg=["classes"])
for base_class in classes:
    options.append(
        SelectOption(label=base_class, value=base_class, emoji=helpers.find_emoji_by_name_pattern(base_class))
    )


class ClassSelectView(discord.ui.View):
    def __init__(self, embed, msg):
        super().__init__(timeout=None)
        self.msg = msg
        self.embed = embed
        if not hasattr(self, 'responses'):
            self.responses = {}
        for comp_class in Config.raid_reminder(nested_cfg=["classes"]):
            self.responses[comp_class] = []

    @discord.ui.select(options=options, placeholder="Select your class", custom_id=f"class_select_{datetime.datetime.now()}")
    async def on_select(self, interaction, options):
        await interaction.response.defer()
        selected_option = interaction.data['values'][0]
        for key, value_list in self.responses.items():
            # Create a new list without the values that exist in another_list
            new_value_list = [value for value in value_list if value not in [interaction.user.display_name]]
            self.responses[key] = new_value_list
        self.responses[selected_option].append(interaction.user.display_name)

        if Config.raid_reminder(nested_cfg=["table_style"]) == "simple":
            table = simple_table(self.responses.items())
        elif Config.raid_reminder(nested_cfg=["table_style"]) == "fancy_grid":
            table = fancy_grid_table(self.responses.items())
        elif Config.raid_reminder(nested_cfg=["table_style"]) == "list_view":
            table = await list_view(self.responses.items())
        elif Config.raid_reminder(nested_cfg=["table_style"]) == "comp_view":
            table = comp_view(self.responses.items())
        else:
            table = simple_table(self.responses.items())

        raid_title = "# ⚔️ 📢 RAID REMINDER 📢 ⚔️"
        if Config.raid_reminder(nested_cfg=["table_style"]) == "list_view":
            self.embed.description = f"{raid_title}"
            self.embed.clear_fields()
            for klass, members in table.items():
                self.embed.add_field(name=klass, value="\n".join(members))
        else:
            self.embed.description = f"{raid_title}\n{table}"
        self.embed.set_footer(text="⬇️ Please select the class you plan on bringing below ⬇️")
        await self.msg.edit(embed=self.embed, view=self)


def simple_table(response_items):
    table_responses = []
    pattern = r'[^a-zA-Z0-9∴\s]'

    for class_name, players in response_items:
        if len(players) == 0 and Config.raid_reminder(nested_cfg=["hide_empty_rows"]):
            pass
        else:
            formatted_players = ""
            formatted_players_list = [""]
            sorted_players = sorted(players, key=lambda x: len(x), reverse=True)
            for player in sorted_players:
                clean_player = re.sub(pattern, '', player)
                formatted_players_list.append(clean_player.lower()[:9])

            for i in range(0, len(formatted_players_list), 4):
                formatted_players += " ".join(formatted_players_list[i:i + 4]).ljust(30)

            table_responses.append([class_name.title(), formatted_players, len(players)])
            table_responses.append(SEPARATING_LINE)

    tablefmt = "simple"
    headers = ["Class", "Players", "Count"]
    table = tabulate(table_responses, headers, tablefmt=tablefmt, maxcolwidths=[None, 30])
    return f"```elm\n{table}```"


def fancy_grid_table(response_items):
    table_responses = []
    pattern = r'[^a-zA-Z0-9∴\s]'

    for class_name, players in response_items:
        if len(players) == 0 and Config.raid_reminder(nested_cfg=["hide_empty_rows"]):
            continue
        formatted_players = ""
        formatted_players_list = [""]
        sorted_players = sorted(players, key=lambda x: len(x), reverse=True)
        for player in sorted_players:
            clean_player = re.sub(pattern, '', player)
            formatted_players_list.append(clean_player.lower()[:9])

        for i in range(0, len(formatted_players_list), 3):
            formatted_players += " ".join(formatted_players_list[i:i + 3]).ljust(30)

        table_responses.append([class_name.title(), formatted_players, len(players)])

    tablefmt = "fancy_grid"
    headers = ["Class", "Players", "Count"]
    table = tabulate(table_responses, headers, tablefmt=tablefmt, maxcolwidths=[None, 30])
    return f"```elm\n{table}```"


async def list_view(response_items):
    dict_table = {}
    for class_name, players in response_items:
        if len(players) == 0 and Config.raid_reminder(nested_cfg=["hide_empty_rows"]):
            continue
        formatted_players_list = []
        for i in range(0, len(players), 1):
            if len(players) == 1:
                position = "single"
            elif i == 0 and len(players) > 1:
                position = "first"
            elif i+1 == len(players):
                position = "end"
            else:
                position = "member"

            formatted_players_list.append(f"{await helpers.emoji_list(position)} {players[i]}")
        key = f"\n{helpers.find_emoji_by_name_pattern(class_name)} **{class_name}** - {len(players)}\n"
        dict_table[key] = formatted_players_list

    return dict_table


def comp_view(response_items):
    table = ""
    return f"```elm\n{table}```"
