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
        self.target = 514859386116767765
        self.active = False
        config = load_json_config("config.json")
        
        for guild in config["guilds"]:
            config["guilds"][str(guild)]["modules"]["bakerbot"] = False
        
        write_json_config("config.json", config)

    @commands.Cog.listener()
    async def on_message(self, message):
        config = load_json_config("config.json")
        counter = load_json_config("bread.json")
    
        if message.author.id != self.target:
            return

        if self.target == self.client.user.id:
            return
    
        if self.active == False:
            return

        oven = [
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


    @discord.commands.slash_command(name='bakerbot', description='BAKE BREAD!.')
    @commands.has_any_role(820078638712094793)
    async def bakerbot(self, ctx, target: discord.Member = None):
        config = load_json_config("config.json")
        
        if config["guilds"][str(ctx.guild.id)]["modules"]["bakerbot"] == False:
            self.active = True
            config["guilds"][str(ctx.guild.id)]["modules"]["bakerbot"] = True;
            
            if target is None:
                self.target = 514859386116767765
            else:
                self.target = target.id
        
            await ctx.send_response("```Commencing Breadening...```", delete_after=5)
        else:
            config["guilds"][str(ctx.guild.id)]["modules"]["bakerbot"] = False;
            self.active = False
            await ctx.send_response("```Breadening terminated.```", delete_after=5)

        write_json_config("config.json", config)

def setup(client):
    client.add_cog(Bakerbot(client))
