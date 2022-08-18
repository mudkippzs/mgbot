import datetime
import discord
import asyncio
from discord.ext import commands, tasks
import random
import json
import os
import re
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))


from clogger import clogger
from utils import *


class Bakerbot(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        config = load_json_config("config.json")
        counter = load_json_config("bread.json")

        if message.author.id != 514859386116767765:
            return
    
        if config["guilds"][str(message.guild.id)]["modules"]["bakerbot"] == False:
            return

        oven = [
        "🍞",
        "🥖",
        "🥐",
        "🥨",
        "🥪",
        "🥯",
        "🥙",
        "🫓",
        "🌯",
        "🧆",
        "🥞",
        "🥞",
        "🧇",
        "🫔"
        ]

        for bread in oven:
            await message.add_reaction(f"{bread}")
            counter["bot"] += 1

        write_json_config("bread.json", counter)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        config = load_json_config("config.json")
    
        if config["guilds"][str(payload.guild_id)]["modules"]["bakerbot"] == False:
            return

        counter = load_json_config("bread.json")

        if payload.user_id == 514859386116767765:
            counter["tom"] += 1

        write_json_config("bread.json", counter)


def setup(client):
    client.add_cog(Bakerbot(client))
