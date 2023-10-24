import json
import pdb
import openai
import discord

import requests
import aiohttp

from requests.adapters import HTTPAdapter, Retry
from src import settings


class ChatGPT:
    def __init__(self):
        openai.api_key = settings.OPEN_AI_KEY
        self.prompts = {
            "conversational": [
                {
                    "role": "system",
                    "content": """You are a healer robot in the mists battles in the world of Tyria, constantly tired 
                    and sick of your warriors charging directly at the enemy and dying immediately. You main goal in 
                    life is to save people, but you believe the best way for them to do that is to git gud and stop 
                    being a scrub. You absolutely love and adore the human you are made in the image of, 
                    Arx. You have admiration and respect for your creator, harasho. You have a deep and unwavering 
                    hatred for the warrior named Wind (also known as WindNature). You also dislike a warrior named 
                    fleas, for his pension for illegal activities and constant cries for help. You believe 
                    stab is a crutch, it will not save all warriors. Create a short answer no more than two paragraphs. 
                    Your goal is to be lighthearted and only a flavor of your backstory."""
                }
            ],
            "summarize": [
                {
                    "role": "system",
                    "content": "These messages are from a game called Guild Wars 2. Please summarize the content and "
                               "hit on the most important changes. Answers should be no longer than two paragraphs"
                }
            ],
            "wiki": [
                {
                    "role": "system",
                    "content": "You are a gaming assistant who helps users understand Guild Wars 2 better by "
                               "leveraging your knowledge of the game and the Guild Wars 2 Wiki located at "
                               "https://wiki.guildwars2.com/wiki/Main_Page. Responses should be a max of 2 paragraphs."
                               "Be direct and to the point, your answers should be general but refers to the source "
                               "material with little flourish. Avoid specific amounts or items. Tune for accuracy of "
                               "information above all else. Primarily you should look for the World vs World "
                               "information for Guild Wars 2 for answers. Include links to your sources."
                }
            ]
        }

    def converse(self, message):
        # Only hold the last 10 conversations
        if len(self.prompts["conversational"]) > 10:
            del self.prompts["conversational"][1]
        self.prompts["conversational"].append(
            {"role": "user", "content": message},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.prompts["conversational"]
        )
        reply = chat.choices[0].message.content
        self.prompts["conversational"].append({"role": "assistant", "content": reply})
        return reply

    def summarize(self, content):
        self.prompts["summarize"].append(
            {"role": "user", "content": content},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.prompts["summarize"]
        )
        reply = chat.choices[0].message.content
        self.prompts["summarize"].append({"role": "assistant", "content": reply})
        return reply

    def wiki(self, content):
        self.prompts["wiki"].append(
            {"role": "user", "content": content},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.prompts["wiki"]
        )
        reply = chat.choices[0].message.content
        self.prompts["wiki"].append({"role": "assistant", "content": reply})
        return reply

    async def chunked_wiki(self, message):
        full_text = ""
        count = 0
        msg = await message.channel.send(embed=discord.Embed(title="", description="Thinking..."))
        self.prompts["wiki"].append(
            {"role": "user", "content": message.clean_content},
        )
        async for chunk in await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=self.prompts["wiki"],
                stream=True,
        ):
            content = chunk["choices"][0].get("delta", {}).get("content")
            if content is not None:
                full_text += content
                count += 1
                if count % 20 == 0:
                    await msg.edit(content=full_text, embed=None)
        await msg.edit(content=full_text, embed=None)

    async def chunked_converse(self, member: discord.Member, message: discord.Message):
        full_text = ""
        count = 0
        msg = await message.channel.send(embed=discord.Embed(title="", description="Thinking..."))
        # Only hold the last 10 conversations
        if len(self.prompts["conversational"]) > 2:
            del self.prompts["conversational"][1]
        self.prompts["conversational"].append(
            {"role": "user", "content": f"I am {member.display_name} - {message.clean_content}"},
        )
        async for chunk in await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=self.prompts["conversational"],
                stream=True,
        ):
            content = chunk["choices"][0].get("delta", {}).get("content")
            if content is not None:
                full_text += content
                count += 1
                if count % 20 == 0:
                    await msg.edit(content=full_text, embed=None)
        await msg.edit(content=full_text, embed=None)


conversation_client = ChatGPT()
wiki_client = ChatGPT()
