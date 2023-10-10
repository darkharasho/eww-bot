from peewee import *
from playhouse.sqlite_ext import *

database = SqliteDatabase('eww_bot.db')


class BaseModel(Model):
    class Meta:
        database = database
