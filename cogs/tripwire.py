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


class Tripwire(commands.Cog):

    def __init__(self, client):
        self.client = client

    def format(self, guild_id, message, block_target, blocker, violations):
        blocker_user = self.client.get_guild(guild_id).get_member(
            blocker)

        blocked_user = self.client.get_guild(guild_id).get_member(
            block_target)

        return message.format(blocked_user, blocker_user, violations)

    @commands.Cog.listener()
    async def on_message(self, message):
        config = load_json_config("config.json")
        triggers = load_json_config("triggers.json")
        strings = load_json_config("strings.json")

        if message.guild is None:
            return

        if config["guilds"][str(message.guild.id)]["modules"]["tripwire"] == False:
            return

        author = message.author
        for key in triggers:
            trigger = triggers[key]
            if trigger["active"]:
                if author.id == trigger["block_pairs"][0]:
                    clogger(f"blocker sent a message: {message.content}")
                    if trigger["mentions_trigger"] == True and trigger["block_pairs"][1] in [m.id for m in message.mentions]:
                        # counting violations so increment count and check against violations threshold (zero-based index)
                        clogger(
                            f"Regex or Mention flag enabled; current violations: {trigger['violations']}")
                        if trigger["count_violations"]:
                            trigger["violations"] += 1
                            if trigger["auto_timeout"] and trigger["violations"] >= 5:
                                timeout = datetime.timedelta(
                                    hours=trigger['auto_timeout_duration'])
                                await message.guild.get_member(trigger['block_pairs'][1]).timeout_for(duration=timeout, reason=f"Timeout triggered by violations threshold by {author}".format(author=author))
                                trigger["violations"] = 0  # Reset counter.
                            # not timeouting the user, just send message to blocker, admins and owner with violation count; useful for stealth flagging violations.
                            if trigger["send_message_blocker"]:
                                member = self.client.get_guild(message.guild.id).get_member(
                                    trigger['block_pairs'][1])
                                try:
                                    await member.send(self.format(message.guild.id, trigger['message_member'], trigger['block_pairs'][0], trigger['block_pairs'][1], trigger['violations']))
                                except Exception as e:
                                    clogger(
                                        f"Couldn't send message for trigger: send_message_blocker\n{e}")
                            if trigger["send_message_blockee"]:
                                member = self.client.get_guild(message.guild.id).get_member(
                                    trigger['block_pairs'][0])
                                try:
                                    await member.send(self.format(message.guild.id, trigger['message_member'], trigger['block_pairs'][0], trigger['block_pairs'][1], trigger['violations']))
                                except Exception as e:
                                    clogger(
                                        f"Couldn't send message for trigger: send_message_blockee\n{e}")
                            if trigger['send_message_admins']:
                                admins = discord.utils.get(
                                    message.guild.roles, name="Administrator")
                                # anyone with Admin role receive the message
                                recipients = [
                                    i for i in message.guild.members if admins in i.roles]
                                for person in recipients:
                                    try:
                                        await person.send(self.format(message.guild.id, trigger['message_staff'], trigger['block_pairs'][0], trigger['block_pairs'][1], trigger['violations']))
                                    except Exception as e:
                                        clogger(
                                            f"Couldn't send message for trigger: send_message_admins\n{e}")
                            # owner is the individual that created this server, not the owner of the bot!
                            if trigger["send_message_owner"]:
                                try:
                                    await message.guild.owner.send(self.format(message.guild.id, trigger['message_owner'], trigger['block_pairs'][0], trigger['block_pairs'][1], trigger['violations']))
                                except Exception as e:
                                    clogger(
                                        f"Couldn't send message for trigger: send_message_owner\n{e}")

        write_json_config("triggers.json", triggers)
        write_json_config("config.json", config)


def setup(client):
    client.add_cog(Tripwire(client))
