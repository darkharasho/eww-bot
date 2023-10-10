from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from discord.ui import Button, View, Select
from tabulate import SEPARATING_LINE


class SetMultiConfigView(discord.ui.View):
    def __init__(self, question=str, config_name=str, channel=discord.TextChannel, user=discord.User):
        super().__init__(timeout=3600)
        self.config_name = config_name
        self.question = question
        self.response_type = question.get("response_type")
        self.channel = channel
        self.user = user
        self.responses = {}
        self.guild = bot.get_guild(settings.GUILD_ID)

    async def interaction_check(self, interaction):
        component_id = interaction.data['custom_id']
        selected_option = interaction.data['values'][0]

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
        button = Button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel")

        if question['field_type'] == 'input':
            self.add_item(button)
            # Create an embed for the question
            embed = discord.Embed(
                title=f"⚠️ Set Config - {self.config_name}",
                description=f"{question_text}\n\n\n (Please send a message with your response)",
                color=0xffcc4d
            )

            if self.response_type == "text_channel":
                embed = self.build_text_channel_picker(
                    items=[channel.name for channel in self.guild.text_channels],
                    embed=embed
                )
            elif self.response_type == "roles":
                embed = self.build_text_channel_picker(
                    items=[role.name for role in self.guild.roles],
                    embed=embed
                )
            elif self.response_type == "gw2_classes":
                embed = self.build_text_gw2_picker(embed=embed)

            await self.channel.send(embed=embed, view=self)

            events = [
                bot.wait_for('message',
                             check=lambda inter: inter.author == self.user and inter.channel == self.channel),
                bot.wait_for('interaction',
                             check=lambda inter: inter.user == self.user and inter.channel == self.channel)
            ]

            # with asyncio.FIRST_COMPLETED, this triggers as soon as one of the events is fired
            done, pending = await asyncio.wait(events, return_when=asyncio.FIRST_COMPLETED)
            event = done.pop().result()

            # cancel the other check
            for future in pending:
                future.cancel()

            if type(event) == discord.Interaction:
                embed = discord.Embed(
                    title=f"Config Cancelled",
                    description="Successfully Cancelled Configuration",
                    color=0xffcc4d
                )

                await event.response.send_message(embed=embed)
                return "APPLICATION_CANCEL"

            else:
                checked_output = []
                if not await self.check(event):
                    await event.response.send_message(embed=discord.Embed(
                        title="ERROR",
                        description="Invalid response"
                    ))
                    checked_output = await SetMultiConfigView(question=self.question,
                                                              config_name=self.config_name, channel=self.channel,
                                                              user=self.user).send_question(index)
                # Dumbest shit ever. event.content is None. Re-looking it up fixes it. Dumb.
                message_id = event.id
                msg = await self.channel.fetch_message(message_id)

                if self.response_type == "text_channel":
                    channel_name = None
                    for field in embed.fields:
                        for chnl in field.value.split("\n"):
                            if chnl.startswith(f"`{msg.content}`"):
                                channel_name = chnl.split(" - ")[-1]
                    content = helpers.get_by_name(self.guild.text_channels, channel_name).id
                elif self.response_type == "roles":
                    role_names = []
                    content = list(set(filter(None, re.sub(r'[ ,]', ', ', msg.content).split(", "))))
                    for opt in content:
                        for field in embed.fields:
                            for role in field.value.split("\n"):
                                if role.startswith(f"`{opt}`"):
                                    role_names.append(role.split(" - ")[-1])
                    content = [role.id for role in helpers.get_by_list_of_names(self.guild.roles, role_names)]
                elif self.response_type == "gw2_classes":
                    content = []
                    gw2_class_selections = list(set(filter(None, re.sub(r'[ ,]', ', ', msg.content).split(", "))))
                    gw2_class_selections = [int(x) for x in gw2_class_selections]
                    gw2_class_selections.sort()
                    for opt in gw2_class_selections:
                        for field in embed.fields:
                            for class_id in field.value.split("\n"):
                                if class_id.startswith(f"`{opt}`"):
                                    content.append(class_id.split(" - ")[-1])
                elif self.response_type == bool:
                    content = eval(msg.content)
                elif self.response_type == "time":
                    hour, minute = [int(a) for a in msg.content.split(':')]
                    content = {
                        "hour": hour,
                        "minute": minute
                    }
                else:
                    content = msg.content
                if checked_output:
                    return checked_output
                else:
                    return content

        elif question['field_type'] == 'select' or question['field_type'] == 'multi_select':
            custom_id = f"select_{index}"
            if type(question["options"][0]) == str and " ".join(question['options']) == "$ROLES":
                select_options = self.role_select()
            else:
                select_options = [SelectOption(label=option, value=option) for option in question['options']]

            select_field = self.build_generic_select(select_options=select_options, custom_id=custom_id)
            self.add_item(select_field)
            self.add_item(button)

            embed = discord.Embed(title=f"⚠️ Set Config - {self.config_name}", description=question_text,
                                  color=0xffcc4d)
            msg = await self.channel.send(embed=embed, view=self)

            response = await bot.wait_for(
                "interaction",
                check=lambda inter: inter.user == self.user and inter.channel == self.channel
            )

            if self.responses == {}:
                embed = discord.Embed(
                    title=f"Config Cancelled",
                    description="Successfully Cancelled Configuration",
                    color=0xffcc4d
                )

                await response.response.send_message(embed=embed)
                return "APPLICATION_CANCEL"
            if question['field_type'] == 'multi_select':
                return response.data["values"]
            return self.responses[custom_id]

    async def check(self, event):
        if (event.author == self.user and
                type(event) == discord.Message and
                type(self.response_type) == str):
            msg = await self.channel.fetch_message(event.id)
            if self.response_type == "time":
                pattern = r"^\d{1,2}(:)\d{1,2}$"
                return re.match(pattern, msg.content)
            elif self.response_type == "text_channel":
                pattern = r"^\d+$"
                return re.match(pattern, msg.content)
            elif self.response_type == "roles" or self.response_type == "gw2_classes":
                pattern = r"^(\d+[, ]*\d*)+$"
                return re.match(pattern, msg.content)
            elif self.response_type == "gw2_classes":
                gw2_class_selections = list(set(filter(None, re.sub(r'[ ,]', ', ', msg.content).split(", "))))
                if len(gw2_class_selections) > 25:
                    return False
                pattern = r"^(\d+[, ]*\d*)+$"
                return re.match(pattern, msg.content)
            elif self.response_type == 'comma_separated_list':
                if len(msg.content.split(",")) >= 1:
                    return True
                re.match(pattern, msg.content)

    def role_select(self, existing=None):
        opts = []
        for role in self.guild.roles[-25:]:
            if existing:
                if role.id in existing.value:
                    default = True
                else:
                    default = False
            else:
                default = False
            opts.append(
                discord.SelectOption(
                    label=role.name,
                    value=role.id,
                    default=default,
                )
            )
        return list(reversed(opts))

    def build_generic_select(self, select_options=None, custom_id=None):
        min_value = 1
        max_value = 1
        if select_options is None:
            select_options = []
        if self.question['field_type'] == 'multi_select':
            max_value = len(select_options)
        select_field = Select(
            custom_id=custom_id,
            placeholder="Choose an option...",
            options=select_options,
            min_values=min_value,
            max_values=max_value
        )

        return select_field

    def build_text_channel_picker(self, items=None, embed=None):
        max_items_per_sublist = 10
        sublists = []

        index = 1
        for i in range(0, len(items), max_items_per_sublist):
            sublist = []
            for item in items[i:i + max_items_per_sublist]:
                sublist.append(f"`{index}` - {item}")
                index += 1
            sublists.append(sublist)

        for sublist in sublists:
            embed.add_field(name="", value="\n".join(sublist), inline=True)

        return embed

    def build_text_gw2_picker(self, embed=None):
        index = 1
        gw2_class_list = {}
        if settings.RAID_REMINDER_CLASSES:
            gw2_class_list = settings.RAID_REMINDER_CLASSES
        elif Config.build_forum_channel_id():
            channel = self.guild.get_channel(Config.build_forum_channel_id())
            for thread in channel.threads:
                if gw2_class_list.get(thread.applied_tags[0].name):
                    gw2_class_list[thread.applied_tags[0].name].append(thread.name)
                else:
                    gw2_class_list[thread.applied_tags[0].name] = [thread.name]
        else:
            gw2_class_list = settings.CLASS_ELITE_SPECS
        for gw2_class, gw2_elite_specs in gw2_class_list.items():
            gw2_spec_list = []
            for espec in gw2_elite_specs:
                gw2_spec_list.append(f"`{index}` - {espec}")
                index += 1
            embed.add_field(name=gw2_class.title(), value="\n".join(gw2_spec_list), inline=True)

        return embed
