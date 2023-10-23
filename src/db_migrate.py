from config.imports import *
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot


class DBMigrate:
    def __init__(self):
        self.db = SqliteDatabase('eww_bot.db')
        self.guild = bot.get_guild(settings.GUILD_ID)

    def migrate(self):
        migrator = SqliteMigrator(self.db)
        migrations = []
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
