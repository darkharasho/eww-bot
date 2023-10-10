import json
import pdb

from src.gw2_api_client import GW2ApiClient


def start():
    api_client = GW2ApiClient()
    achievements = api_client.achievement_categories(id=13)

    categories = {}
    for index, achievement_id in enumerate(achievements['achievements']):
        achievement = api_client.achievements(ids=achievement_id['id'])
        print(f"{index}/{len(achievements['achievements'])} - {achievement[0]['name']} - {achievement[0]['id']}")
        categories[achievement[0]["name"]] = achievement[0]["id"]

    with open('./api_achievements_map.json', 'w') as file:
        file.write(json.dumps(categories))


start()
