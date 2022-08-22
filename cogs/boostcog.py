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


async def post_to_cringe_gallery(payload, client):
    """Get the original message content, embeds and attachments and post and Embed with the message author's details in the cringe gallery channel."""
    clogger(f"Cringe was posted...")
    cringe_gallery_channel_id = 1011283927924744212
    message_content = ""
    message_embeds = []
    message_attachments = []

    # Get the original message content, embeds and attachments
    guild = client.get_guild(payload.guild_id)
    message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
    author = message.author
    message_content = message.content
    message_embeds = message.embeds
    message_attachments = message.attachments

    # Create a new embed with the original message content, embeds and attachments
    cringe_gallery_embed = discord.Embed(title=f"{author.display_name} just posted cringe in {message.channel.name}...", description=f"{author.mention}", color=0xffc0cb)
    cringe_gallery_embed.add_field(name="Cringe:", value=message_content, inline=False)

    if len(message_embeds) > 0:
        for e in message_embeds:
            cringe_gallery_embed.add_field(name="Cringe Embeds", value=e, inline=False)
    
    if len(message_attachments) > 0:
        for a in message_attachments:
            cringe_gallery_embed.add_field(name="Cringe Attachments", value=a, inline=False)

    # Post the new embed to the cringe gallery channel
    await client.get_channel(cringe_gallery_channel_id).send(embed=cringe_gallery_embed)

class Boostcog(commands.Cog):
    def __init__(self, client):
        config = load_json_config("config.json")
        self.client = client

        self.basedlog = load_json_config("basedlog.json")
        self.based_role = None
        self.cringe_role = None
        self.based_emoji = None
        self.cringe_emoji = None
        
    # Based Cog Events

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Update basedlog when a reaction is added."""
        self.basedlog = load_json_config("basedlog.json")
        message_id = payload.message_id
        guild = self.client.get_guild(payload.guild_id)
        roles = guild.roles
        emojis = guild.emojis
        message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
        author = message.author
        user_id = author.id

        if self.based_emoji == None:
            self.based_emoji = [e for e in emojis if e.name== "based"][0]
        
        if self.cringe_emoji == None:
            self.cringe_emoji = [e for e in emojis if e.name == "cringe"][0]

        if self.based_role == None:
            self.based_role = [r for r in roles if r.name== "Based"][0]
        
        if self.cringe_role == None:
            self.cringe_role = [r for r in roles if r.name == "Afflicted with Cringe"][0]

        if not str(author.id) in self.basedlog:
            self.basedlog[str(author.id)] = {
                "based_count": 0,
                "based_expires": None,
                "cringe_count": 0,
                "cringe_expires": None,
                "last_reacted_user_id": None,
                "last_reacted_timestamp": None,
                "based_react_log": [],
                "cringe_react_log": []
            }

        if author.id == payload.user_id:
            write_json_config("basedlog.json", self.basedlog)
            #clogger(f"{author.display_name} can't self-based or cringe")
            return

        if str(self.based_emoji.name) == str(payload.emoji.name):
            if str(payload.message_id) not in [m[0] for m in self.basedlog[str(user_id)]["based_react_log"]] and str(payload.user_id) not in [m[1] for m in self.basedlog[str(user_id)]["based_react_log"]] or len(self.basedlog[str(user_id)]["based_react_log"]) < 1:
                #clogger(
                #    f"User {user_id} reacted with based on message {message_id}")
                # increment based count and set new expiry time
                self.basedlog[str(user_id)]["based_count"] += 1
                # If the based expiry time has not expired, increase it by +1 minute. If it has expired, set it to now+5minutes.
                if self.basedlog[str(user_id)]["based_expires"] != None:
                    if datetime.datetime.fromtimestamp(int(self.basedlog[str(user_id)]["based_expires"])).timestamp() > datetime.datetime.now(pytz.timezone('Europe/Dublin')).timestamp():
                        d = datetime.datetime.fromtimestamp(int(self.basedlog[str(
                            user_id)]["based_expires"])) + datetime.timedelta(minutes=1)
                        self.basedlog[str(user_id)]["based_expires"] = int(
                            d.timestamp())
                else:
                    d = datetime.datetime.now(pytz.timezone('Europe/Dublin')) + datetime.timedelta(minutes=5)
                    self.basedlog[str(user_id)]["based_expires"] = int(
                        d.timestamp())

                self.basedlog[str(user_id)]["based_react_log"].append(
                    (str(payload.message_id), str(user_id)))

                for role in author.roles:
                    if role in [self.based_role, self.cringe_role]:
                        return


                self.basedlog[str(author.id)]["last_reacted_user_id"] = payload.user_id
                self.basedlog[str(author.id)]["last_reacted_timestamp"] = datetime.datetime.now(pytz.timezone('Europe/Dublin')).timestamp()
                write_json_config("basedlog.json", self.basedlog)
                await author.add_roles(self.based_role, reason="User is based.")


        elif str(self.cringe_emoji.name) == str(payload.emoji.name):
            await post_to_cringe_gallery(payload, self.client)
            if str(payload.message_id) not in [m[0] for m in self.basedlog[str(user_id)]["cringe_react_log"]] and str(payload.user_id) not in [m[1] for m in self.basedlog[str(user_id)]["cringe_react_log"]] or len(self.basedlog[str(user_id)]["cringe_react_log"]) < 1:
                #clogger(
                #    f"User {user_id} reacted with cringe on message {message_id}")
                # increment based count and set new expiry time
                self.basedlog[str(user_id)]["cringe_count"] += 1
                # If the cringe expiry time has not expired, increase it by +30 seconds. If it has expired, set it to now+5minutes.
                if self.basedlog[str(user_id)]["cringe_expires"] != None:
                    if datetime.datetime.fromtimestamp(int(self.basedlog[str(user_id)]["cringe_expires"])).timestamp() > datetime.datetime.now(pytz.timezone('Europe/Dublin')).timestamp():
                        d = datetime.datetime.fromtimestamp(int(self.basedlog[str(user_id)]["cringe_expires"])) + datetime.timedelta(seconds=30)
                        self.basedlog[str(user_id)]["cringe_expires"] = int(
                            d.timestamp())
                else:
                    d = datetime.datetime.now(pytz.timezone('Europe/Dublin')) + datetime.timedelta(minutes=5)
                    self.basedlog[str(user_id)]["cringe_expires"] = int(
                        d.timestamp())

                self.basedlog[str(user_id)]["cringe_react_log"].append(
                    (str(payload.message_id), str(user_id)))

                for role in author.roles:
                    if role in [self.based_role, self.cringe_role]:
                        return

                await author.add_roles(self.cringe_role, reason="User is afflicted with cringe.")

                self.basedlog[str(author.id)]["last_reacted_user_id"] = payload.user_id
                self.basedlog[str(author.id)]["last_reacted_timestamp"] = datetime.datetime.now(pytz.timezone('Europe/Dublin')).timestamp()
                write_json_config("basedlog.json", self.basedlog)

        else:
            return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Update basedlog when a reaction is removed."""

        self.basedlog = load_json_config("basedlog.json")
        # Get message from payload (raw event format)
        guild = self.client.get_guild(payload.guild_id)
        roles = guild.roles
        message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
        author = message.author  # Message author (discord object format)
        emojis = guild.emojis

        if self.based_emoji == None:
            self.based_emoji = [e for e in emojis if e.name== "based"][0]
        
        if self.cringe_emoji == None:
            self.cringe_emoji = [e for e in emojis if e.name == "cringe"][0]

        if self.based_role == None:
            self.based_role = [r for r in roles if r.name== "Based"][0]
        
        if self.cringe_role == None:
            self.cringe_role = [r for r in roles if r.name == "Afflicted with Cringe"][0]

        if not str(author.id) in self.basedlog:
            self.basedlog[str(author.id)] = {
                "based_count": 0,
                "based_expires": None,
                "cringe_count": 0,
                "cringe_expires": None,
                "last_reacted_user_id": None,
                "last_reacted_timestamp": None,
                "based_react_log": [],
                "cringe_react_log": []
            }


        if author.id == payload.user_id:
            write_json_config("basedlog.json", self.basedlog)
            #clogger(f"{author.display_name} removed a self-based or self-cringe")
            return

        if str(self.based_emoji.name) == (payload.emoji.name):
            #clogger("Got a based emoji.")
            if str(message.id) in self.basedlog[str(author.id)]["based_react_log"]:
                #clogger(
                #    f"User {author.id} removed based reaction on message {message.id}.")

                # decrement based count and set new expiry time
                self.basedlog[str(author.id)]["based_count"] -= 1
                if self.basedlog[str(author.id)]["based_count"] < 0:
                    self.basedlog[str(author.id)]["based_count"] = 0
                # If the based expiry time has not expired, decrease it by -1 minute. If it has expired, set it to now+5minutes.
                if self.basedlog[str(author.id)]["based_expires"] != None:
                    if datetime.datetime.fromtimestamp(int(self.basedlog[str(author.id)]["based_expires"]) / 1000) > datetime.datetime.now(pytz.timezone('Europe/Dublin')):
                        d = self.basedlog[str(
                            author.id)]["based_expires"] + datetime.timedelta(minutes=-1)
                        self.basedlog[str(author.id)]["based_expires"] = int(
                            d.timestamp())

                    self.basedlog[str(author.id)]["last_reacted_user_id"] = payload.user_id
                    self.basedlog[str(author.id)]["last_reacted_timestamp"] = datetime.datetime.now(pytz.timezone('Europe/Dublin')).timestamp()
                    
                else:
                    pass

                #clogger(message.id)
                #self.basedlog[str(author.id)]["based_react_log"].remove(str(message.id))
                write_json_config("basedlog.json", self.basedlog)

        elif str(self.cringe_emoji.name) == str(payload.emoji.name):
            #clogger("Got a cringe emoji.")
            if str(message.id) in self.basedlog[str(author.id)]["cringe_react_log"]:
                #clogger(
                #    f"User {author.id} removed cringe reaction on message {message.id}.")

                # decrement based count and set new expiry time
                self.basedlog[str(author.id)]["cringe_count"] -= 1
                if self.basedlog[str(author.id)]["cringe_count"] < 0:
                    self.basedlog[str(author.id)]["cringe_count"] = 0
                # If the based expiry time has not expired, decrease it by -1 minute. If it has expired, set it to now+5minutes.
                if self.basedlog[str(author.id)]["cringe_expires"] != None:
                    if self.basedlog[str(author.id)]["cringe_expires"] > datetime.datetime.now(pytz.timezone('Europe/Dublin')).timestamp():
                        d = datetime.datetime.fromtimestamp(self.basedlog[str(
                            author.id)]["cringe_expires"]) + datetime.timedelta(minutes=-1)
                        self.basedlog[str(author.id)]["cringe_expires"] = int(
                            d.timestamp())

                    self.basedlog[str(author.id)]["last_reacted_user_id"] = payload.user_id
                    self.basedlog[str(author.id)]["last_reacted_timestamp"] = datetime.datetime.now(pytz.timezone('Europe/Dublin')).timestamp()
                
                else:
                    pass
                #clogger(message.id)                
                #self.basedlog[str(author.id)]["cringe_react_log"].remove(str(message.id))

                write_json_config("basedlog.json", self.basedlog)

    # Based Cog Commands

    # Display based count of user to the channel (message author)

    @commands.command(hidden = True)
    async def bcount(self, ctx):

        await ctx.channel.send("Counting...")

        self.basedlog = load_json_config("basedlog.json")

        if not str(ctx.author.id) in self.basedlog:
            self.basedlog[str(ctx.author.id)] = {
                "based_count": 0,
                "based_expires": None,
                "cringe_count": 0,
                "cringe_expires": None,
                "last_reacted_user_id": None,
                "last_reacted_timestamp": None,
                "based_react_log": [],
                "cringe_react_log": []
            }

        if str(ctx.author.id) not in self.basedlog:
            return

        #clogger("Counting based level for user.")

        await ctx.channel.send("```Based rating: " + str(self.basedlog[str(ctx.author.id)]["based_count"]) + "```", delete_after=15)

    # Display cringe count of user to the channel (message author)
    @commands.command(hidden = True)
    async def ccount(self, ctx):

        await ctx.channel.send("Counting...")

        self.basedlog = load_json_config("basedlog.json")

        if not str(ctx.author.id) in self.basedlog:
            self.basedlog[str(ctx.author.id)] = {
                "based_count": 0,
                "based_expires": None,
                "cringe_count": 0,
                "cringe_expires": None,
                "last_reacted_user_id": None,
                "last_reacted_timestamp": None,
                "based_react_log": [],
                "cringe_react_log": []
            }

        if str(ctx.author.id) not in self.basedlog:
            return

        #clogger("Counting cringe level for user.")

        await ctx.channel.send("```Cringe rating is: " + str(self.basedlog[str(ctx.author.id)]["cringe_count"]) + "```", delete_after=15)

def setup(client):  # Add cog to bot when loaded with extension command (e.g !load cogName). See https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html
    client.add_cog(Boostcog(client))
