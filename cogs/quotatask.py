import discord
import json
import asyncio
import datetime
from discord.ext import commands, tasks
import os
import sys
import pytz

from jarvis import QUOTA_LIMIT

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger
from utils import *


class Quotatask(commands.Cog):

    def __init__(self, client):
        self.client = client
        # Check if the task loop is already running
        self.quotas_task.start()

    def cog_unload(self):
        self.quotas_task.cancel()

    @tasks.loop(minutes=1)
    async def quotas_task(self):
        #clogger("+ Quota reset running")
        now = datetime.datetime.now(pytz.timezone('Europe/Dublin'))
        if now.hour == 0 and now.minute >= 0 and now.minute <= 3:
            
            try:
                await self.client.get_command("cleanup").callback(self.client, None)
            except Exception as e:
                clogger("Automated quota cleanup failed")
                pass

            try:
                await self.client.get_command("cleanup").callback(self.client, None)
            except Exception as e:
                clogger("Automated quota cleanup failed")
                pass

            clogger(f"AI Bot Quota Reset to: {QUOTA_LIMIT}")
            

def setup(client):
    client.add_cog(Quotatask(client))
