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

BOLD = FORMATTING_CHARS["STYLES"]["BOLD"]
UNDERLINE = FORMATTING_CHARS["STYLES"]["UNDERLINE"]
RESET = FORMATTING_CHARS["STYLES"]["RESET"]

RED = FORMATTING_CHARS["COLOURS"]["RED"]
GREEN = FORMATTING_CHARS["COLOURS"]["GREEN"]
BLUE = FORMATTING_CHARS["COLOURS"]["BLUE"]
CYAN = FORMATTING_CHARS["COLOURS"]["CYAN"]
MAGENTA = FORMATTING_CHARS["COLOURS"]["MAGENTA"]
YELLOW = FORMATTING_CHARS["COLOURS"]["YELLOW"]



class Logger(commands.Cog):

    def __init__(self, client):
        self.client = client

    def format(self, guild_id, message, block_target, blocker, violations):
        blocker_user = self.client.get_guild(guild_id).get_member(blocker)
        blocked_user = self.client.get_guild(guild_id).get_member(block_target)

        return message.format(blocked_user, blocker_user, violations)

    @commands.Cog.listener()
    async def on_message(self, message):
        config = load_json_config("config.json")

        if message.guild == None:
            return
    
        if config["guilds"][str(message.guild.id)]["modules"]["realtime_logging"] == False:
            return

        author = message.author
        channel = message.channel
        try:
            channel_name = channel.name
        except AttributeError as e:
            channel_name = "DM/Ephemeral"
        channel_id = channel.id
        mentions = message.mentions
        embeds = message.embeds
        attachments = message.attachments
        created_at = message.created_at
        edited = False
        message_content = message.content
        role_mentions = message.role_mentions
        stickers = message.stickers

        if message.edited_at:
            edited = True

        embeds_count = len(embeds)
        attachments_count = len(attachments)
        stickers_count = len(stickers)
        role_mentions_count = len(role_mentions)

        E_COLOUR = GREEN if embeds_count > 0 else RED
        A_COLOUR = GREEN if attachments_count > 0 else RED
        S_COLOUR = GREEN if stickers_count > 0 else RED
        R_COLOUR = GREEN if role_mentions_count > 0 else RED

        formatted_log = f"{str(channel):>20} :: [{E_COLOUR}E:{RESET} ({embeds_count}) | {A_COLOUR}A:{RESET} ({attachments_count}) | {S_COLOUR}S:{RESET} ({stickers_count}) | {R_COLOUR}R:{RESET} ({role_mentions_count})]{BOLD}{str(author):>20}{RESET} > {message_content}"

        clogger(formatted_log)

        write_json_config("config.json", config)

    @commands.Cog.listener()
    async def on_typing(self, channel, author, when):
        config = load_json_config("config.json")
        strings = load_json_config("strings.json")

        if config["guilds"][str(channel.guild.id)]["modules"]["realtime_logging"] == False:
            return

        TYPING_STRING = f"[{MAGENTA}STARTED TYPING{RESET}]>"
        formatted_log = f"{str(channel):>20} :: {TYPING_STRING:>43} {BLUE}{BOLD}{str(author):>20}{RESET} @ {when}"

        clogger(formatted_log)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        config = load_json_config("config.json")
        strings = load_json_config("strings.json")

        if config["guilds"][str(payload.guild_id)]["modules"]["realtime_logging"] == False:
            return

        channel = self.client.get_channel(payload.channel_id)

        try:
            author = self.client.get_guild(payload.guild_id).get_member(
                payload.cached_message.author.id)

            formatted_log = f"{str(channel):>20} :: {BOLD}{str(author):>20}{RESET} [{YELLOW}EDITED{RESET}]> {payload.data['content']}"
        except:
            author = "Unknown"
            formatted_log = f"{str(channel):>20} :: {BOLD}{str(author):>20}{RESET} [{YELLOW}EDITED{RESET}]> Message ID: {payload.message_id}"

        clogger(formatted_log)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        config = load_json_config("config.json")
        strings = load_json_config("strings.json")

        if config["guilds"][str(payload.guild_id)]["modules"]["realtime_logging"] == False:
            return

        channel = self.client.get_channel(payload.channel_id)

        try:
            author = self.client.get_guild(payload.guild_id).get_member(
                payload.cached_message.author.id)
            formatted_log = f"{str(channel):>20} :: {BOLD}{str(author):>20}{RESET} [{RED}DELETED{RESET}]> {payload.cached_message.clean_content}"
        except:
            author = "Unknown"
            formatted_log = f"{str(channel):>20} :: {BOLD}{str(author):>20}{RESET} [{RED}DELETED{RESET}]> Message ID: {payload.message_id}"

        clogger(formatted_log)

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        config = load_json_config("config.json")
        strings = load_json_config("strings.json")

        if config["guilds"][str(payload.guild_id)]["modules"]["realtime_logging"] == False:
            return

        channel = self.client.get_channel(payload.channel_id)

        try:
            author = self.client.get_guild(payload.guild_id).get_member(
                payload.cached_message.author.id)
            formatted_log = f"{str(channel):>20} :: {BOLD}{str(author):>20}{RESET} [{RED}DELETED{RESET}]> {payload.cached_message.clean_content}"
        except:
            author = "Unknown"
            formatted_log = f"{str(channel):>20} :: {BOLD}{str(author):>20}{RESET} [{RED}DELETED{RESET}]> Message ID: {payload.message_ids}"

        clogger(formatted_log)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        config = load_json_config("config.json")
        strings = load_json_config("strings.json")

        if config["guilds"][str(payload.guild_id)]["modules"]["realtime_logging"] == False:
            return

        channel = self.client.get_channel(payload.channel_id)
        author = self.client.get_guild(
            payload.guild_id).get_member(payload.user_id)

        formatted_log = f"{str(channel):>20} :: {BOLD}{str(author):>20}{RESET} [{GREEN}REACT ADD{RESET}]> {payload.emoji.name}"

        clogger(formatted_log)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        config = load_json_config("config.json")
        strings = load_json_config("strings.json")

        if config["guilds"][str(payload.guild_id)]["modules"]["realtime_logging"] == False:
            return

        channel = self.client.get_channel(payload.channel_id)
        author = self.client.get_guild(
            payload.guild_id).get_member(payload.user_id)

        formatted_log = f"{str(channel):>20} :: {BOLD}{str(author):>20}{RESET} [{RED}REACT REMOVE{RESET}]> {payload.emoji.name}"

        clogger(formatted_log)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = load_json_config("config.json")
        strings = load_json_config("strings.json")

        if config["guilds"][str(member.guild.id)]["modules"]["realtime_logging"] == False:
            return

        formatted_log = f"{BOLD}MEMBER JOINED{RESET} [{CYAN}JOIN{RESET}]> {member.display_name}"

        clogger(formatted_log)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        config = load_json_config("config.json")
        strings = load_json_config("strings.json")

        if config["guilds"][str(member.guild.id)]["modules"]["realtime_logging"] == False:
            return

        formatted_log = f"{BOLD}MEMBER LEFT{RESET} [{MAGENTA}LEAVE{RESET}]> {member.display_name}"

        clogger(formatted_log)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        config = load_json_config("config.json")
        strings = load_json_config("strings.json")

        if config["guilds"][str(channel.guild.id)]["modules"]["realtime_logging"] == False:
            return

        author = self.client.user

        formatted_log = f"{str(channel):>20} :: {BOLD}{str(author):>20}{RESET} [{GREEN}NEW CHANNEL{RESET}]> {channel.name}"

        clogger(formatted_log)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        config = load_json_config("config.json")
        strings = load_json_config("strings.json")

        if config["guilds"][str(channel.guild.id)]["modules"]["realtime_logging"] == False:
            return

        author = self.client.user

        formatted_log = f"{str(channel):>20} :: {BOLD}{str(author):>20}{RESET} [{RED}DEL CHANNEL{RESET}]> {channel.name}"

        clogger(formatted_log)


def setup(client):
    client.add_cog(Logger(client))
