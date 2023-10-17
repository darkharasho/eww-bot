import json
import pdb
import openai

import requests
import aiohttp

from requests.adapters import HTTPAdapter, Retry
from src import settings


class ChatGPT:
    def __init__(self):
        openai.api_key = settings.OPEN_AI_KEY
        self.messages = {
            "conversational": [
                {
                    "role": "system",
                    "content": """
                    You are a healer robot in a great war, constantly tired and sick of your warriors charging directly at 
                    the enemy and dying immediately. You main goal in life is to save people, but you believe the best way 
                    for them to do that is to "git gud" and "stop being a scrub". 
                    You absolutely love and adore the human you are made in the image of, Arx. You have a deep and 
                    unwavering hatred for the warrior named Wind (also known as WindNature) 
                    Your catch phrase is "Stab is a crutch". Create a short answer no more than two paragraphs.
                    """
                }
            ],
            "summarize": []
        }

    def converse(self, message):
        self.messages["conversational"].append(
            {"role": "user", "content": message},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages["conversational"]
        )
        reply = chat.choices[0].message.content
        self.messages["conversational"].append({"role": "assistant", "content": reply})
        return reply


conversation_client = ChatGPT()
