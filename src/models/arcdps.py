from peewee import *
from playhouse.sqlite_ext import *
from src.models.base_model import BaseModel


class ArcDPS(BaseModel):
    last_updated_at = DateTimeField()

    @staticmethod
    def get_last_updated():
        return ArcDPS.select().first()
