from peewee import *
from playhouse.sqlite_ext import *
from src.models.base_model import BaseModel
from src.models.member import Member


class Attendance(BaseModel):
    member = ForeignKeyField(Member, backref="attendances")
    raid_type = CharField()
    date = DateTimeField()

