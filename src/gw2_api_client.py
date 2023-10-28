import json
import pdb

import requests
import aiohttp

from requests.adapters import HTTPAdapter, Retry
from src import settings


class GW2ApiClient:
    def __init__(self, *args, **kwargs):
        # Define the URL you want to make a GET request to
        self.url = "https://api.guildwars2.com/v2"
        api_key = kwargs.get('api_key', settings.GW2_API_KEY)

        # Define your authorization headers (replace with your actual credentials)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Schema-Version": "latest"
        }
        with open("api_achievements_map.json", 'r') as json_file:
            self.api_achievements_map = json.load(json_file)

    def account(self):
        ping_url = self.url + "/account"
        response = requests.get(ping_url, headers=self.headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"Request failed with status code {response.status_code}")

    def world(self):
        world_id = self.account()["world"]
        ping_url = self.url + f"/worlds?id={world_id}"
        response = requests.get(ping_url, headers=self.headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"Request failed with status code {response.status_code}")


    def characters(self, *args, **kwargs):
        ids = kwargs.get('ids', None)
        ping_url = self.url + "/characters"
        if ids:
            ping_url += f"?ids={ids}"
        response = requests.get(ping_url, headers=self.headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"Request failed with status code {response.status_code}")

    async def aio_account_achievements(self, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            ids = kwargs.get('ids', None)
            name = kwargs.get('name', None)
            ping_url = self.url + "/account/achievements"
            if ids:
                ping_url += f"?ids={ids}"
            elif name:
                ping_url += f"?ids={self.api_achievements_map[name]}"
            async with session.get(ping_url, headers=self.headers) as resp:
                account_achievements = await resp.json()
                return account_achievements

    async def aio_account(self, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            ping_url = self.url + "/account"
            async with session.get(ping_url, headers=self.headers) as resp:
                account = await resp.json()
                return account

    async def aio_characters(self, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            ids = kwargs.get('ids', None)
            ping_url = self.url + "/characters"
            if ids:
                ping_url += f"?ids={ids}"
            async with session.get(ping_url, headers=self.headers) as resp:
                characters = await resp.json()
                return characters

    def achievements(self, *args, **kwargs):
        ids = kwargs.get('ids', None)
        ping_url = self.url + "/achievements"
        if ids:
            ping_url += f"?ids={ids}"
        response = requests.get(ping_url, headers=self.headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"Request failed with status code {response.status_code}")

    def bank(self, *args, **kwargs):
        ids = kwargs.get('ids', None)
        ping_url = self.url + "/account/bank"
        if ids:
            ping_url += f"?ids={ids}"
        response = requests.get(ping_url, headers=self.headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return list(filter(None, json.loads(response.text)))
        else:
            print(f"Request failed with status code {response.status_code}")

    def builds(self, *args, **kwargs):
        characters = self.characters()
        index = kwargs.get('index', None)
        tabs = kwargs.get('tabs', None)

        ping_url = self.url + "/characters"
        if index:
            character_name = characters[index]
            ping_url += f"/{character_name}/buildtabs"
        if tabs:
            ping_url += f"?tabs={tabs}"
        response = requests.get(ping_url, headers=self.headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"Request failed with status code {response.status_code}")

    def achievement_categories(self, *args, **kwargs):
        id = kwargs.get('id', None)
        # ping_url = self.url + "/achievements/categories/1?v=2022-03-23T19:00:00.000Z"
        ping_url = self.url + "/achievements/categories/"
        if id:
            ping_url += f"/{id}?v=2022-03-23T19:00:00.000Z"
        response = requests.get(ping_url, headers=self.headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"Request failed with status code {response.status_code}")

    def account_achievements(self, *args, **kwargs):
        ids = kwargs.get('ids', None)
        name = kwargs.get('name', None)
        ping_url = self.url + "/account/achievements"
        if ids:
            ping_url += f"?ids={ids}"
        elif name:
            ping_url += f"?ids={self.api_achievements_map[name]}"
        response = requests.get(ping_url, headers=self.headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"Request failed with status code {response.status_code}")

    def wvw_matches(self):
        account = self.account()
        wvw_matches_url = self.url + f"/wvw/matches?world={account['world']}"
        response = requests.get(wvw_matches_url, headers=self.headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"Request failed with status code {response.status_code}")

    def wvw_maps(self):
        account = self.account()
        wvw_matches_url = self.url + f"/wvw/matches/maps?world={account['world']}"
        response = requests.get(wvw_matches_url, headers=self.headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"Request failed with status code {response.status_code}")

    def find_world_by_id(self, world_id: int):
        world_url = self.url + f"/worlds?id={world_id}"
        response = requests.get(world_url, headers=self.headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"Request failed with status code {response.status_code}")

    def cached_find_world_by_id(self, server_id: int):
        for listed_server in settings.SERVER_NAMES:
            if listed_server["id"] == server_id:
                return listed_server
