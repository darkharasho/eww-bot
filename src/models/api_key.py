import discord
from peewee import *
from playhouse.sqlite_ext import *
from src.models.base_model import BaseModel
from src.models.member import Member


class ApiKey(BaseModel):
    member = ForeignKeyField(Member, backref="api_keys")
    value = CharField(unique=True)
    name = TextField(null=False, default="Default")
    primary = BitField(default=True)

    @staticmethod
    def find_or_create(member=discord.Member, name=None, value=None, primary=None):
        api_key = ApiKey.select().where((ApiKey.member == member) & (ApiKey.value == value)).first()
        if api_key:
            return api_key
        else:
            return ApiKey.create(
                member=member,
                name=name,
                value=value,
                primary=primary
            )
