from config.imports import *
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot


class DBMigrate():
    def __init__(self):
        self.db = SqliteDatabase('eww_bot.db')
        self.guild = bot.get_guild(settings.GUILD_ID)

    def migrate(self):
        migrator = SqliteMigrator(self.db)
        migrations = []
        try:
            with self.db.atomic():
                migrate(
                    migrator.add_column('member', 'gw2_api_key', Member.gw2_api_key)
                )
                migrations.append(["🟢", "Member", "gw2_api_key"])
        except OperationalError as oe:
            migrations.append(["🟡", "Member", "gw2_api_key"])
            pass
        try:
            with self.db.atomic():
                migrate(
                    migrator.add_column('member', 'gw2_stats', Member.gw2_stats)
                )
                migrations.append(["🟢", "Member", "gw2_stats"])
        except OperationalError as oe:
            migrations.append(["🟡", "Member", "gw2_stats"])
            pass
        try:
            with self.db.atomic():
                migrate(
                    migrator.add_column('member', 'gw2_username', Member.gw2_username)
                )
                migrations.append(["🟢", "Member", "gw2_username"])
        except OperationalError as oe:
            migrations.append(["🟡", "Member", "gw2_username"])
            pass
        try:
            with self.db.atomic():
                migrate(
                    migrator.add_column('member', 'created_at', DateTimeField(default=datetime.datetime.now())),
                    migrator.add_column('member', 'updated_at', Member.updated_at)
                )
                migrations.append(["🟢", "Member", "created_at"])
                migrations.append(["🟢", "Member", "updated_at"])
        except OperationalError as oe:
            migrations.append(["🟡", "Member", "created_at"])
            migrations.append(["🟡", "Member", "updated_at"])
            pass
        try:
            with self.db.atomic():
                migrate(
                    migrator.add_column('member', 'user_id', Member.user_id)
                )
                migrations.append(["🟢", "Member", "user_id"])
        except OperationalError as oe:
            migrations.append(["🟡", "Member", "user_id"])
            pass

        return migrations


async def setup(bot):
    await bot.add_cog(MigratorCog(bot), guild=settings.GUILD_ID, override=True)
