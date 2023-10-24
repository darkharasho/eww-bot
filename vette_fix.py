from config.imports import *
from src import settings
from src.bot_client import bot
from src.models.member import Member
from src.gw2_api_client import GW2ApiClient

config = Config.select().where(Config.name == "auto_attendance").first()

config.value = {
    "enabled": False,
    "channel_id": 1234,
    "time": {
        "hour": 0,
        "minute": 0
    }
}

config.save()
