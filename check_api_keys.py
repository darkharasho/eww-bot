from config.imports import *
from src import settings
from src.bot_client import bot
from src.models.member import Member
from src.gw2_api_client import GW2ApiClient

members = Member.select().where(Member.gw2_api_key.is_null(False))


def check_api_keys():
    for member in members:
        print(member.username)

        api_client = GW2ApiClient(api_key=member.gw2_api_key)
        try:
            if not api_client.account():
                raise
            print("✅ Account")
        except:
            print("❌ Account")

        try:
            if not api_client.account_achievements():
                raise
            print("✅ Progression")
        except:
            print("❌ Progression")

        try:
            if not api_client.characters():
                raise
            print("✅ Characters")
        except:
            print("❌ Characters")

        try:
            if not api_client.builds(index=0, tabs="all"):
                raise
            print("✅ Builds")
        except:
            print("❌ Builds")
        try:
            if not api_client.bank():
                raise
            print("✅ Inventories")
        except:
            print("❌ Inventories")


check_api_keys()
