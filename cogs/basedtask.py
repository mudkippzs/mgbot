import discord
import json
import asyncio
import datetime
from discord.ext import commands, tasks
import os
import sys
import pytz

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger
from utils import *


class Basedtask(commands.Cog):

    def __init__(self, client):
        self.client = client
        # Check if the task loop is already running
        self.based_task.start()

    def cog_unload(self):
        self.based_task.cancel()

    @tasks.loop(seconds=30.0)
    async def based_task(self):
        #clogger("Based/Cringe Check running")
        for guild in self.client.guilds:
            basedlog = load_json_config("basedlog.json")
            for member in guild.members:
                # False if member has left the server or has not had any reaction logged yet
                if member == None or str(member.id) not in basedlog:
                    continue

                roles = [r for r in member.roles if str(
                    r) in ["Based", "Afflicted with Cringe"]]
                if len(roles):
                    while len(roles):
                        role = roles.pop()
                        if str(role) == "Based":
                            # Remove Based role (if exists) and clear data from log file if expiration time is passed and not null
                            if basedlog[str(member.id)]['based_expires'] != None and int(str(basedlog[str(member.id)]['based_expires']) + "000") < int(str(datetime.datetime.now(pytz.timezone('Europe/Dublin')).timestamp()).split(".")[0] + "000"):
                                #clogger("Unbased now...")
                                await member.remove_roles(role, reason=f"Aura of Based has faded.")
                                basedlog[str(member.id)
                                         ]['based_expires'] = None
                        else:
                            # Remove Cringe role (if exists) and clear data from log file if expiration time is passed and not null
                            if basedlog[str(member.id)]['cringe_expires'] != None and int(str(basedlog[str(member.id)]['cringe_expires']) + "000") < int(str(datetime.datetime.now(pytz.timezone('Europe/Dublin')).timestamp()).split(".")[0] + "000"):
                                #clogger("Uncringe now...")
                                await member.remove_roles(role, reason=f"Aura of Cringe has faded.")
                                basedlog[str(member.id)
                                         ]['cringe_expires'] = None

            write_json_config("basedlog.json", basedlog)


def setup(client):
    client.add_cog(Basedtask(client))
