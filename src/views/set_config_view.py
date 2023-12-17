from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from discord.ui import Button, View, Select
from tabulate import SEPARATING_LINE
from src.views import set_multi_config_view

options = [
    SelectOption(label="Guild Member Role",
                 value="GuildMemberRole",
                 description="Used In: Attendance, Raid Notifications, Raid Reminders",
                 emoji="🛡️"),
    SelectOption(label="Disable Module",
                 value="DisableModule",
                 description="Used In: None - Disables a module so the slash command is inaccessible",
                 emoji="❌"),
    SelectOption(label="Allowed Admin Roles",
                 value="AllowedAdminRoles",
                 description="Used In: All - which roles are allowed to run all bot commands",
                 emoji="👑"),
    SelectOption(label="Build Manager Roles",
                 value="BuildManagerRoles",
                 description="Used In: set-build, import-builds - which roles are allowed to run all build commands",
                 emoji="🦺"),
    SelectOption(label="Commander Roles",
                 value="CommanderRoles",
                 description="Used In: raid-notifications - which roles are allowed to run all raid commands",
                 emoji="🔰"),
    SelectOption(label="Set Raid Days",
                 value="RaidDays",
                 description="Used In: Raid Reminder, Attendance, Auto Attendance",
                 emoji="⚔️"),
    SelectOption(label="Set Build Forum Channel",
                 value="BuildForumChannel",
                 description="Used In: Set Build, Import Builds",
                 emoji="💬"),
    SelectOption(label="Set Build Update Channel",
                 value="BuildUpdateChannel",
                 description="Used In: Set Build, Import Builds",
                 emoji="🔔"),
    SelectOption(label="Setup Auto Attendance",
                 value="AutoAttendance",
                 description="Requires: Attendance Module, Show Attendance Module",
                 emoji="📋"),
    SelectOption(label="Setup Raid Notifications",
                 value="RaidNotification",
                 description="Used In: Raid Notification",
                 emoji="💥"),
    SelectOption(label="Setup Raid Reminders",
                 value="RaidReminder",
                 description="Requires: Raid Days - Sets up a timed reminder post for your raid schedule.",
                 emoji="🎮"),
    SelectOption(label="Set Vod Review Channel",
                 value="ReviewForumChannel",
                 description="Used In: Propose - Which forum channel your vod reviews live in.",
                 emoji="🎬"),
    SelectOption(label="Setup ArcDPS Updates",
                 value="ArcdpsUpdates",
                 description="Sets up automatic notifications for ArcDPS updates",
                 emoji="🧮"),
    SelectOption(label="Setup Game Update Notifications",
                 value="GameUpdates",
                 description="Sets up automatic notifications for Guild Wars 2 updates",
                 emoji="📰"),
    SelectOption(label="Setup User Allowed Channels",
                 value="UserAllowedChannels",
                 description="Limit which channels commands that can be run by anyone are allowed in",
                 emoji="🤖")
]


class SetConfigView(discord.ui.View):
    def __init__(self, embed, msg):
        super().__init__(timeout=None)
        self.msg = msg
        self.embed = embed
        if not hasattr(self, 'responses'):
            self.responses = {}
        self.guild = bot.get_guild(settings.GUILD_ID)

    @discord.ui.select(options=options, placeholder="Select config...")
    async def on_select(self, interaction, options):
        await interaction.response.defer()
        selected_option = interaction.data['values'][0]

        if selected_option == "GuildMemberRole":
            role_options = self.role_select()
            self.clear_items()
            self.embed.description = "```Guild Member Role:\nPlease select the main role for guild members below.```"
            self.add_item(item=discord.ui.Select(placeholder="Select Guild Member Role...",
                                                 options=role_options))
        elif selected_option == "DisableModule":
            module_options = []
            mod_config = Config.select().where(Config.name == "disabled_modules").first()
            for module in settings.MODULES:
                if mod_config:
                    if module in mod_config.value:
                        default = True
                    else:
                        default = False
                else:
                    default = False
                module_options.append(
                    discord.SelectOption(
                        label=module,
                        value=module,
                        default=default
                    )
                )
            self.clear_items()
            self.embed.description = ("```Disable Modules:\nMulti select which slash commands you would like to "
                                      "disable.```")
            self.add_item(item=discord.ui.Select(placeholder="Select Modules to Disable...",
                                                 options=module_options,
                                                 min_values=0,
                                                 max_values=len(module_options)), )
        elif selected_option == "AllowedAdminRoles":
            admin_role_ids = Config.select().where(Config.name == "allowed_admin_role_ids").first()
            admin_options = self.role_select(existing=admin_role_ids)

            self.clear_items()
            self.embed.description = ("```Allowed Admin Roles:\nPlease select which roles you would like to give bot "
                                      "access to.```")
            self.add_item(item=discord.ui.Select(placeholder="Select Admin Roles...",
                                                 options=admin_options,
                                                 min_values=0,
                                                 max_values=len(admin_options)))
        elif selected_option == "BuildManagerRoles":
            build_manager_role_ids = Config.select().where(Config.name == "build_manager_role_ids").first()
            build_manager_options = self.role_select(existing=build_manager_role_ids)

            self.clear_items()
            self.embed.description = ("```Build Manager Roles:\nPlease select which roles you would like to grant"
                                      "build access to.```")
            self.add_item(item=discord.ui.Select(placeholder="Select Build Manager Roles...",
                                                 options=build_manager_options,
                                                 min_values=0,
                                                 max_values=len(build_manager_options)))
        elif selected_option == "CommanderRoles":
            answers = []
            for index, question in enumerate(settings.SET_COMMANDER_ROLES, start=0):
                question_view = set_multi_config_view.SetMultiConfigView(config_name=selected_option,
                                                                         question=question,
                                                                         channel=interaction.channel,
                                                                         user=interaction.user)
                answer = await question_view.send_question(index)
                answers = answer
                if answer == "APPLICATION_CANCEL":
                    break

            self.clear_items()
            await self.set_generic_config(name="commander_role_ids",
                                          value=answers,
                                          send_response=False)
        elif selected_option == "RaidDays":
            day_options = []
            raid_days = Config.select().where(Config.name == "raid_days").first()
            cal_days = list(calendar.day_name)
            for day in [0, 1, 2, 3, 4, 5, 6]:
                if raid_days:
                    if day in raid_days.value:
                        default = True
                    else:
                        default = False
                else:
                    default = False
                day_options.append(
                    discord.SelectOption(
                        label=cal_days[day],
                        value=str(day),
                        default=default
                    )
                )
            self.clear_items()
            self.embed.description = ("```Raid Days:\nWhat days are your official raid days?\n"
                                      "- Monday: 0\n- Tuesday: 1\n- Wednesday: 2\n- Thursday: 3\n- Friday: 4\n- "
                                      "Saturday: 5\n- Sunday: 6```")
            self.add_item(item=discord.ui.Select(placeholder="Select Raid Days...",
                                                 options=day_options,
                                                 min_values=0,
                                                 max_values=len(day_options)))
        elif selected_option == "ReviewForumChannel":
            review_channel_options = []
            for forum in self.guild.forums:
                review_channel_options.append(
                    discord.SelectOption(
                        label=forum.name,
                        value=forum.id
                    )
                )
            self.clear_items()
            self.embed.description = ("```Vod Review Channel:\nWhich channel your members post their videos for review```")
            self.add_item(item=discord.ui.Select(placeholder="Select Review Forum Channel...",
                                                 options=review_channel_options))
        elif selected_option == "BuildForumChannel":
            build_channel_options = []
            for forum in self.guild.forums:
                build_channel_options.append(
                    discord.SelectOption(
                        label=forum.name,
                        value=forum.id
                    )
                )
            self.clear_items()
            self.embed.description = ("```Build Forum Channel:\nWhich channel you would like your builds to be posted "
                                      "to. Must be a forum channel.```")
            self.add_item(item=discord.ui.Select(placeholder="Select Build Forum Channel...",
                                                 options=build_channel_options))
        elif selected_option == "BuildUpdateChannel":
            answer_key = ["build_update_channel_id"]
            answers = {}
            for index, question in enumerate(settings.SET_BUILD_UPDATE_CHANNEL, start=0):
                question_view = set_multi_config_view.SetMultiConfigView(config_name=selected_option,
                                                                         question=question,
                                                                         channel=interaction.channel,
                                                                         user=interaction.user)
                answer = await question_view.send_question(index)
                answers[answer_key[index]] = answer
                if answer == "APPLICATION_CANCEL":
                    break
            self.clear_items()
            await self.set_generic_channel_config(name="build_update_channel_id",
                                                  value=answers["build_update_channel_id"],
                                                  send_response=False)
        # Start of Multi Configs
        elif selected_option == "AutoAttendance":
            answer_key = ["enabled", "channel_id", "time"]
            answers = {}
            for index, question in enumerate(settings.AUTO_ATTENDANCE_CONFIG, start=0):
                question_view = set_multi_config_view.SetMultiConfigView(config_name=selected_option,
                                                                         question=question,
                                                                         channel=interaction.channel,
                                                                         user=interaction.user)
                answer = await question_view.send_question(index)
                answers[answer_key[index]] = answer
                if answer == "APPLICATION_CANCEL":
                    break

            await self.handle_multi_question_response(name="auto_attendance", answers=answers,
                                                      description="```Auto Attendance:\nConfiguration for auto "
                                                                  "attendance. Note: you will need to reload"
                                                                  "the bot after any changes.```")

            await bot.reload_extension("src.cogs.auto_attendance_cog")

        elif selected_option == "RaidReminder":
            answer_key = [
                "channel_id",
                "role_ids",
                "table_style",
                "hide_empty_rows",
                "time",
                "classes"
            ]
            answers = {}
            for index, question in enumerate(settings.RAID_REMINDER_CONFIG, start=0):
                question_view = set_multi_config_view.SetMultiConfigView(config_name=selected_option,
                                                                         question=question,
                                                                         channel=interaction.channel,
                                                                         user=interaction.user)
                answer = await question_view.send_question(index)
                answers[answer_key[index]] = answer
                if answer == "APPLICATION_CANCEL":
                    break

            await self.handle_multi_question_response(name="raid_reminder", answers=answers,
                                                      description="```Raid Reminder:\nConfiguration for raid "
                                                                  "reminders. Note: you will need to"
                                                                  "reload the bot after changes.```")

            try:
                await bot.reload_extension("src.tasks.raid_reminder_task")
            except:
                pass

        elif selected_option == "RaidNotification":
            answer_key = ["role_ids", "closed_raid_channel_id", "open_tag_role_ids", "open_raid_channel_id"]
            answers = {}
            for index, question in enumerate(settings.RAID_NOTIFICATION_CONFIG, start=0):
                question_view = set_multi_config_view.SetMultiConfigView(config_name=selected_option,
                                                                         question=question,
                                                                         channel=interaction.channel,
                                                                         user=interaction.user)
                answer = await question_view.send_question(index)
                answers[answer_key[index]] = answer
                if answer == "APPLICATION_CANCEL":
                    break

            await self.handle_multi_question_response(name="raid_notification", answers=answers,
                                                      description="```Raid Notification:\nConfiguration for tagging "
                                                                  "up notifications.```")

        elif selected_option == "UserAllowedChannels":
            answer_key = ["leaderboard_channel_ids", "funderboard_channel_ids", "chat_channel_ids"]
            answers = {}
            for index, question in enumerate(settings.SET_USER_CHANNELS, start=0):
                question_view = set_multi_config_view.SetMultiConfigView(config_name=selected_option,
                                                                         question=question,
                                                                         channel=interaction.channel,
                                                                         user=interaction.user)
                answer = await question_view.send_question(index)
                answers[answer_key[index]] = answer
                if answer == "APPLICATION_CANCEL":
                    break

            await self.handle_multi_question_response(name="user_allowed_channels", answers=answers,
                                                      description="```User Allowed Channels:\nChoose which channels a "
                                                                  "user can interact with the bot in.```")

        elif selected_option == "ArcdpsUpdates":
            answer_key = ["enabled", "channel_id"]
            answers = {}
            for index, question in enumerate(settings.SET_ARCDPS_UPDATES, start=0):
                question_view = set_multi_config_view.SetMultiConfigView(config_name=selected_option,
                                                                         question=question,
                                                                         channel=interaction.channel,
                                                                         user=interaction.user)
                answer = await question_view.send_question(index)
                answers[answer_key[index]] = answer
                if answer == "APPLICATION_CANCEL":
                    break

            self.clear_items()
            await self.set_generic_config(name="arcdps_updates",
                                          value=answers,
                                          send_response=False)
            try:
                await bot.reload_extension("src.cogs.arcdps_updates_cog")
            except:
                pass

        elif selected_option == "GameUpdates":
            answer_key = ["enabled", "channel_id"]
            answers = {}
            for index, question in enumerate(settings.SET_GAME_UPDATES, start=0):
                question_view = set_multi_config_view.SetMultiConfigView(config_name=selected_option,
                                                                         question=question,
                                                                         channel=interaction.channel,
                                                                         user=interaction.user)
                answer = await question_view.send_question(index)
                answers[answer_key[index]] = answer
                if answer == "APPLICATION_CANCEL":
                    break

            self.clear_items()
            await self.set_generic_config(name="game_updates",
                                          value=answers,
                                          send_response=False)

            try:
                await bot.reload_extension("src.cogs.game_updates_cog")
            except:
                pass

        await self.msg.channel.send(embed=self.embed, view=self)

        events = [
            bot.wait_for('message',
                         check=lambda inter: inter.author == interaction.user and inter.channel == interaction.channel),
            bot.wait_for('interaction',
                         check=lambda inter: inter.user == interaction.user and inter.channel == interaction.channel)
        ]

        # with asyncio.FIRST_COMPLETED, this triggers as soon as one of the events is fired
        done, pending = await asyncio.wait(events, return_when=asyncio.FIRST_COMPLETED)
        event = done.pop().result()
        try:
            await event.response.defer()
        except:
            pass

        # cancel the other check
        for future in pending:
            future.cancel()

        if type(event) == discord.Interaction:
            if selected_option == "GuildMemberRole":
                await self.set_generic_role_config(pretty_name=selected_option,
                                                   name="guild_member_role_id",
                                                   event=event,
                                                   multi=False)
            elif selected_option == "AllowedAdminRoles":
                await self.set_generic_role_config(pretty_name=selected_option,
                                                   name="allowed_admin_role_ids",
                                                   event=event)
            elif selected_option == "BuildManagerRoles":
                await self.set_generic_role_config(pretty_name=selected_option,
                                                   name="build_manager_role_ids",
                                                   event=event)
            elif selected_option == "RaidDays":
                await self.set_generic_config(name="raid_days",
                                              value=[int(rid) for rid in event.data["values"]])
            elif selected_option == "ReviewForumChannel":
                await self.set_generic_channel_config(name="review_forum_channel_id",
                                                      value=int(event.data["values"][0]))
            elif selected_option == "BuildForumChannel":
                await self.set_generic_channel_config(name="build_forum_channel_id",
                                                      value=int(event.data["values"][0]))
            elif selected_option == "DisableModule":
                await self.set_generic_config(name="disabled_modules", value=event.data["values"])
                for module in settings.MODULES:
                    if module in Config.disabled_modules():
                        tree.remove_command(module, guild=discord.Object(id=settings.GUILD_ID))
                        await bot.unload_extension("src.cogs." + f"{inflection.underscore(module)}_cog")
                    else:
                        # noinspection PyBroadException
                        try:
                            await bot.load_extension("src.cogs." + f"{inflection.underscore(module)}_cog")
                        except:
                            pass
                await tree.sync(guild=discord.Object(id=settings.GUILD_ID))
        else:
            pass

    async def set_generic_config(self, name=None, value=None, send_response=True):
        configuration, action = Config.create_or_update(name=name, value=value)
        if not configuration:
            self.embed.color = 0xf23f42
            self.embed.description = "```ERR:\nUnable to create/update config```"
        else:
            self.embed.add_field(name="Action", value=f"`{action}`", inline=False)
            config_value = configuration.get_value()
            if type(config_value) == dict:
                for key, value in config_value.items():
                    formatted_value = value
                    if type(formatted_value) == list:
                        formatted_value = "\n".join([str(v) for v in value])
                    elif type(formatted_value) == dict:
                        formatted_value = ""
                        for k, v in value.items():
                            formatted_value += f"{k}: {v}\n"
                    self.embed.add_field(name=key.title(), value=f"{formatted_value}")
            else:
                self.embed.add_field(name=name.title(), value=f"`{configuration.get_value()}`", inline=True)

        self.clear_items()
        if send_response:
            await self.msg.channel.send(embed=self.embed, view=self)

    async def set_generic_role_config(self, pretty_name=None, name=None, event=None, multi=True):
        if multi:
            roles = [int(rid) for rid in event.data["values"]]
        else:
            roles = int(event.data["values"][0])

        db_role_ids, action = Config.create_or_update(name=name, value=roles)
        if not db_role_ids:
            self.embed.color = 0xf23f42
            self.embed.description = "```ERR:\nUnable to create/update config```"
        else:
            if multi:
                db_roles = db_role_ids.get_value()
            else:
                db_roles = [db_role_ids.get_value()]
            discord_roles = []
            for role_id in db_roles:
                discord_roles.append(self.guild.get_role(role_id))
            self.embed.add_field(name=pretty_name,
                                 value="\n".join([f"`@{role.name}`" for role in discord_roles]),
                                 inline=True)
            self.embed.add_field(name="Action", value=f"`{action}`", inline=True)
        self.clear_items()
        await self.msg.channel.send(embed=self.embed, view=self)

    async def set_generic_channel_config(self, name=None, value=None, send_response=True):
        configuration, action = Config.create_or_update(name=name, value=value)
        if not configuration:
            self.embed.color = 0xf23f42
            self.embed.description = "```ERR:\nUnable to create/update config```"
        else:
            channel = bot.get_channel(configuration.get_value())
            self.embed.add_field(name=name.title(), value=channel.mention, inline=True)
            self.embed.add_field(name="Action", value=f"`{action}`", inline=True)
        self.clear_items()
        if send_response:
            await self.msg.channel.send(embed=self.embed, view=self)

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
                    default=default
                )
            )
        return list(reversed(opts))

    async def handle_multi_question_response(self, name=None, answers=None, description=None):
        if answers is None:
            answers = {}
        contains_cancel = "APPLICATION_CANCEL" in answers.values()
        if contains_cancel:
            return
        await self.set_generic_config(name=name,
                                      value=answers,
                                      send_response=False)
        self.embed.description = description
