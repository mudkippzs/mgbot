import discord
import json
import asyncio
import datetime
from discord.ext import commands, tasks
import os
import sys
import pytz
import copy
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
                quotas = load_json_config("quotas.json")
                bots = [bot for bot in quotas.keys()]
                current_members = [str(member.id) for member in self.client.guilds[0].members]
                del_count = 0
                quota_copy = copy.deepcopy(quotas)
                for bot in bots:
                    for member in quotas[bot]:
                        if member not in current_members:
                            del_count += 1
                            clogger(f"Clearing {member} from {bot} quotas list as they are no longer a server member...")
                            del quota_copy[bot][member]

                clogger(f"Current member count: {len(current_members)}, removed {del_count} dead members from the quota list.")
                write_json_config("quotas.json", quota_copy)

            except Exception as e:
                clogger("Automated quota cleanup failed")
                clogger(f"Error: {e}")
                pass

            try:                
                quotas = load_json_config("quotas.json")

                bots = ["jarvis", "emgee"]

                member_count = self.client.guilds[0].member_count

                for b in bots:
                    for member in self.client.guilds[0].members:
                        user = member
                        quotas[b][str(user.id)] = QUOTA_LIMIT

                write_json_config("quotas.json", quotas)
            except Exception as e:
                clogger("Automated quota reset failed")
                clogger(f"Error: {e}")
                pass
            else:
                clogger(f"AI Bot Quota Reset to: {QUOTA_LIMIT}")
            

def setup(client):
    client.add_cog(Quotatask(client))
