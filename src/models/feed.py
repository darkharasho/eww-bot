from peewee import *
from playhouse.sqlite_ext import *
from src.models.base_model import BaseModel


class Feed(BaseModel):
    name = CharField(unique=True)
    guild_id = IntegerField()
    modified = CharField()
