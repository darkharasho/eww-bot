import json
import pdb
import openai
import discord

import requests
import aiohttp

from requests.adapters import HTTPAdapter, Retry
from src import settings


class CatFact:
    @staticmethod
    async def catfact(channel):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://catfact.ninja/fact") as response:
                fact = (await response.json())["fact"]
                length = (await response.json())["length"]
                embed = discord.Embed(title=f'Random Cat Fact Number: **{length}**', description=f'Cat Fact: {fact}',
                                      colour=0x400080)
                embed.set_footer(text="")
                await channel.send(embed=embed)
                # await session.close() # <--- here, but is not necessary
