from config.imports import *
from src import settings
from src.bot_client import bot
from src.models.member import Member
from src.gw2_api_client import GW2ApiClient

members = list(set([api_key.member for api_key in ApiKey.select()]))


def check_api_keys():
    for member in members:
        print(member.username)

        api_client = GW2ApiClient(api_key=member.api_key)
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


def reset_weeklies():
    members = Member.select()
    for member in members:
        member.gw2_stats = None
        member.save()


def migrate_api_keys():
    members = Member.select().where(Member.gw2_api_key.is_null(False))
    for member in members:
        ApiKey.find_or_create(member=member, value=member.gw2_api_key, primary=True)


if __name__ == '__main__':
    verify_type = True
    while verify_type:
        print(f"Available Options: [check, migrate, reset]")
        api_action = input(">> Option: ")
        if api_action not in ["check", "migrate", "reset"]:
            print("Invalid Selection.")
        else:
            if api_action == "check":
                check_api_keys()
            elif api_action == "migrate":
                migrate_api_keys()
            elif api_action == "reset":
                confirm = input(">> This will reset everyone's weekly stats. Type Y to confirm: ")
                if confirm == "Y" or confirm == "y":
                    reset_weeklies()
                else:
                    print("Weekly Reset Stats Cancelled.")
            verify_type = False
