from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from src.views import set_config_view


class ConfigCog(commands.Cog):
    def __init__(self, option):
        self.option = option
        self.db = SqliteDatabase('eww_bot.db')
        self.guild = bot.get_guild(settings.GUILD_ID)

    @commands.command(pass_context=True)
    async def config(self, interaction, option: str):
        dm_channel = await interaction.user.create_dm()
        await interaction.response.send_message(
            embed=discord.Embed(title="⚠️ Set Config", description="I've sent you a DM!", color=0xffcc4d),
            ephemeral=True
        )

        try:
            self.db.connect()
        except:
            pass
        if option == "set_config":
            await self.set_config(interaction)
        elif option == "member_update":
            embed = await self.members_update()
            await dm_channel.send(embed=embed)
        elif option == 'show':
            embed = self.show()
            await dm_channel.send(embed=embed)

    @staticmethod
    async def set_config(interaction):
        channel = interaction.channel
        dm_channel = await interaction.user.create_dm()

        embed = discord.Embed(
            title="️⚠️ Set Config",
            description="```Please choose the config below you would like to add/edit```",
            color=0xffcc4d
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

        msg = await dm_channel.send(embed=embed)
        view = set_config_view.SetConfigView(embed, msg)
        await msg.edit(embed=embed, view=view)

    async def members_update(self):
        all_db_members = Member.select()
        all_db_members_ids = [db_member.discord_id for db_member in all_db_members]

        all_guild_members = []
        for member in self.guild.members:
            if helpers.check_guild_role(member=member):
                all_guild_members.append(member)
        all_guild_members_ids = [member.id for member in all_guild_members]

        added = []
        for member in all_guild_members:
            if member.id in all_db_members_ids:
                continue
            else:
                try:
                    with self.db.atomic():
                        added.append(Member.create(username=member.name, discord_id=member.id))
                except IntegrityError:
                    pass

        removed = []
        for member in all_db_members:
            if member.discord_id in all_guild_members_ids:
                continue
            else:
                removed.append(member.username)
                Member.delete().where(Member.discord_id == member.discord_id).execute()
                Attendance.delete().where(Attendance.member == member).execute()

        added_member_str = await format_with_position(added)
        removed_members_str = await format_with_position(removed, deleted=True)
        body = f"### Added:\n{added_member_str}\n"
        body += f"### Removed:\n{removed_members_str}\n"

        return discord.Embed(title="Successfully Updated Members", description=body)

    @staticmethod
    def show():
        table_data = []
        configs = Config.select()

        for config in configs:
            table_data.append([config.name, config.get_value()])

        tablefmt = "simple"
        headers = ["Config Name", "Config Value"]
        table = tabulate(table_data, headers, tablefmt=tablefmt, maxcolwidths=[None, 25])

        embed = discord.Embed(title="⚠️ Show Config", description=f"```{table}```", color=0xffcc4d)

        return embed


async def format_with_position(members: list, deleted=False):
    members_list = []
    for i in range(0, len(members), 1):
        if len(members) == 1:
            position = "single"
        elif i == 0 and len(members) > 1:
            position = "first"
        elif i + 1 == len(members):
            position = "end"
        else:
            position = "member"

        if deleted:
            member_name = members[i]
        else:
            member_name = members[i].username
        members_list.append(f"{await helpers.emoji_list(position)} {member_name}")
    return "\n".join(members_list)


async def setup(bot):
    await bot.add_cog(ConfigCog(bot), guild=settings.GUILD_ID, override=True)
