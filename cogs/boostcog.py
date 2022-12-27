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


async def add_to_based_log(member):
    basedlog = load_json_config("basedlog.json")
    
    if not str(member.id) in basedlog:
        basedlog[str(member.id)] = {
            "based_count": 0,
            "based_expires": None,
            "cringe_count": 0,
            "cringe_expires": None,
            "last_reacted_user_id": None,
            "last_reacted_timestamp": None,
            "based_react_log": [],
            "cringe_react_log": []
        }
    
    write_json_config("basedlog.json", basedlog)

    return

async def post_to_cringe_gallery(payload, client):
    """Get the original message content, embeds and attachments and post and Embed with the message author's details in the cringe gallery channel."""
    clogger(f"Cringe was posted...")
    cringelog = load_json_config("cringelog.json")

    cringe_gallery_channel_id = 1011283927924744212
    message_content = ""
    message_embeds = []
    message_attachments = []

    # Get the original message content, embeds and attachments
    guild = client.get_guild(payload.guild_id)
    if str(guild.id) not in cringelog.keys():
        cringelog[str(guild.id)] = []

    message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
    if message.id in cringelog[str(guild.id)]:
        return

    author = message.author
    message_content = message.content
    message_embeds = message.embeds
    message_attachments = message.attachments

    # Create a new embed with the original message content, embeds and attachments
    cringe_gallery_embed = discord.Embed(title=f"{author.display_name} just posted cringe in {message.channel.name}...", description=f"{author.mention}", color=0xffc0cb, url=message.jump_url)
    cringe_gallery_embed.add_field(name="Cringe Post:", value=message_content if len(message_content) > 0 else "None", inline=False)
    cringe_gallery_embed.set_thumbnail(url=author.avatar.url)

    if len(message_embeds) > 0:
        for e in message_embeds:
            cringe_gallery_embed.set_image(url=e.url)
    
    if len(message_attachments) > 0:
        for a in message_attachments:
            cringe_gallery_embed.set_image(url=a.url)

    # Post the new embed to the cringe gallery channel
    await client.get_channel(cringe_gallery_channel_id).send(embed=cringe_gallery_embed)
    cringelog[str(guild.id)].append(message.id)
    write_json_config("cringelog.json", cringelog)

class Boostcog(commands.Cog):
    def __init__(self, client):
        config = load_json_config("config.json")
        self.client = client
        self.blacklist_channels = [938444879682478121]

        self.basedlog = load_json_config("basedlog.json")
        self.based_role = None
        self.cringe_role = None
        self.based_emoji = None
        self.cringe_emoji = None
        
    # Based Cog Events

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Update basedlog when a reaction is added."""
        if payload.channel_id in self.blacklist_channels:
            return

        self.basedlog = load_json_config("basedlog.json")

        # Extract metadata objects
        message_id = payload.message_id
        guild = self.client.get_guild(payload.guild_id)
        roles = guild.roles
        emojis = guild.emojis
        message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
        author = message.author
        user_id = author.id    
        current_time =  datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        # if payload.author_id == user_id:
        #     return

        if self.based_emoji == None:
            self.based_emoji = [e for e in emojis if e.name== "based"][0]

        if self.cringe_emoji == None:
            self.cringe_emoji = [e for e in emojis if e.name == "cringe"][0]

        if self.based_role == None:
            self.based_role = [r for r in roles if r.name== "Based"][0]

        if self.cringe_role == None:
            self.cringe_role = [r for r in roles if r.name == "Afflicted with Cringe"][0]
            
        try:
            based_react_log = self.basedlog[str(user_id)]["based_react_log"]
        except:
            add_to_based_log(author)
            # reload based log instance.
            self.basedlog = load_json_config("basedlog.json")

        cringe_react_log = self.basedlog[str(user_id)]["cringe_react_log"]

        based_expiry_log = self.basedlog[str(user_id)]["based_expires"]
        cringe_expiry_log = self.basedlog[str(user_id)]["cringe_expires"]
        localtz = pytz.timezone('Europe/Dublin')
        
        if str(self.based_emoji.name) == str(payload.emoji.name):

            if str(payload.message_id) not in [m[0] for m in based_react_log] and str(payload.user_id) not in [m[1] for m in based_react_log] or len(based_react_log) < 1:
                #clogger(
                #    f"User {user_id} reacted with based on message {message_id}")
                # increment based count and set new expiry time
                self.basedlog[str(user_id)]["based_count"] += 1
                # If the based expiry time has not expired, increase it by +1 minute. If it has expired, set it to now+5minutes.
                if based_expiry_log != None:
                    based_expiry = datetime.datetime.fromtimestamp(int(based_expiry_log))
                    based_expiry = localtz.localize(based_expiry)
                    based_expiry = based_expiry.replace(tzinfo=pytz.timezone('Europe/Dublin'))
                    if based_expiry > current_time:
                        d = based_expiry + datetime.timedelta(minutes=1)
                        self.basedlog[str(user_id)]["based_expires"] = int(d.timestamp())
                else:
                    based_expiry = None
                    d = current_time + datetime.timedelta(minutes=5)
                    self.basedlog[str(user_id)]["based_expires"] = int(d.timestamp())

                self.basedlog[str(user_id)]["based_react_log"].append((str(payload.message_id), str(user_id)))
            else:
                if based_expiry_log != None:
                    based_expiry = datetime.datetime.fromtimestamp(int(based_expiry_log))
                    based_expiry = based_expiry.replace(tzinfo=pytz.timezone('Europe/Dublin'))
                    if based_expiry > current_time:
                        d = based_expiry + datetime.timedelta(minutes=1)
                        self.basedlog[str(user_id)]["based_expires"] = int(d.timestamp())
                else:
                    based_expiry = None
                    d = current_time + datetime.timedelta(minutes=5)
                    self.basedlog[str(user_id)]["based_expires"] = int(d.timestamp())

            for role in author.roles:
                if role in [self.based_role, self.cringe_role]:
                    return

            self.basedlog[str(author.id)]["last_reacted_user_id"] = payload.user_id
            self.basedlog[str(author.id)]["last_reacted_timestamp"] = current_time.timestamp()
            write_json_config("basedlog.json", self.basedlog)
            await author.add_roles(self.based_role, reason="User is based.")
            # Send message to channel with delete_after = 5, wrapped in ```formatting tilde``` with: old expiry, new expiry, additional time amount added and the based emoji.
            clogger(f"```diff\n+ {author.mention}'s based expiry has been extended by 1 minute.\n- Old expiry: {based_expiry}\n+ New expiry: {d}\n- New expiry: {d}\n- {self.based_emoji}```")

        elif str(self.cringe_emoji.name) == str(payload.emoji.name):
            await post_to_cringe_gallery(payload, self.client)
            if str(payload.message_id) not in [m[0] for m in cringe_react_log] and str(payload.user_id) not in [m[1] for m in cringe_react_log] or len(cringe_react_log) < 1:
                #clogger(
                #    f"User {user_id} reacted with cringe on message {message_id}")
                # increment based count and set new expiry time
                self.basedlog[str(user_id)]["cringe_count"] += 1
                # If the cringe expiry time has not expired, increase it by +30 seconds. If it has expired, set it to now+5minutes.
                if cringe_expiry_log != None:
                    cringe_expiry = datetime.datetime.fromtimestamp(int(cringe_expiry_log))
                    cringe_expiry = localtz.localize(cringe_expiry)
                    cringe_expiry = cringe_expiry.replace(tzinfo=pytz.timezone('Europe/Dublin'))
                    if cringe_expiry > current_time:
                        d = cringe_expiry + datetime.timedelta(seconds=30)
                        self.basedlog[str(user_id)]["cringe_expires"] = int(d.timestamp())
                else:
                    cringe_expiry = None
                    d = current_time + datetime.timedelta(minutes=5)
                    self.basedlog[str(user_id)]["cringe_expires"] = int(d.timestamp())

                self.basedlog[str(user_id)]["cringe_react_log"].append((str(payload.message_id), str(user_id)))
            else:
                if cringe_expiry_log != None:
                    cringe_expiry = datetime.datetime.fromtimestamp(int(cringe_expiry_log))
                    cringe_expiry = cringe_expiry.replace(tzinfo=pytz.timezone('Europe/Dublin'))
                    if cringe_expiry > current_time:
                        d = cringe_expiry + datetime.timedelta(seconds=30)
                        self.basedlog[str(user_id)]["cringe_expires"] = int(d.timestamp())
                else:
                    cringe_expiry = None
                    d = current_time + datetime.timedelta(minutes=5)
                    self.basedlog[str(user_id)]["cringe_expires"] = int(d.timestamp())

            for role in author.roles:
                if role in [self.based_role, self.cringe_role]:
                    return

            await author.add_roles(self.cringe_role, reason="User is afflicted with cringe.")

            self.basedlog[str(author.id)]["last_reacted_user_id"] = payload.user_id
            self.basedlog[str(author.id)]["last_reacted_timestamp"] = current_time.timestamp()
            write_json_config("basedlog.json", self.basedlog)

            # Send message to channel with delete after = 5, wrapped in ```formatting tilde``` with: old expiry, new expiry, additional time amount added and the based emoji.
            clogger(f"```diff\n+ {author.mention}'s cringe expiry has been extended by 30 seconds\n- Old expiry: {cringe_expiry}\n+ New expiry: {d}\n- {self.cringe_emoji}```")

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


    async def _count(self, ctx, ctype: str):
        self.basedlog = load_json_config("basedlog.json")
        return self.basedlog[str(ctx.author.id)][f"{ctype}_count"]

    async def _based_or_cringe(self, ctx, based: bool= False):
        #clogger("Counting based level for user.")
        if based:
            ctype = 'based'
        else:
            ctype = 'cringe'
        await ctx.send_response(f"```Counting your {ctype}...```", delete_after=5)
        count = await self._count(ctx, ctype = ctype)
        await ctx.send_followup(f"```{ctype.title()} rating: " + str(count) + "```", delete_after=15)
        try:
            await ctx.message.delete()
        except:
            pass

    @commands.slash_command(name='bcount', description='Check your raw based score.')
    async def bcount(self, ctx):
        await self._based_or_cringe(ctx, based=True)

    # Display cringe count of user to the channel (message author)
    @commands.slash_command(name='ccount', description='Check your raw cringe score.')
    async def ccount(self, ctx):
        await self._based_or_cringe(ctx, based=False)

    # Display cringe count of user to the channel (message author)
    @commands.slash_command(name='addtobasedlog', description='Add a user to the based log if they are missing.')
    async def addtobasedlog(self, ctx, member: discord.Member):
        await add_to_based_log(member)
        await ctx.send_response(f"```{member.display_name} added to the based log...```")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await add_to_based_log(member)


def setup(client):  # Add cog to bot when loaded with extension command (e.g !load cogName). See https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html
    client.add_cog(Boostcog(client))
