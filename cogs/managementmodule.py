import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ui import View, Item, Button, Select
import re
import sys
import os
import time
import random
import requests
from typing import List, Union
from io import BytesIO
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from PIL.JpegImagePlugin import JpegImageFile

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger


class ManagementModule(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command()
    @commands.has_role('Admin')
    async def nicknameupdate(self, ctx, new_nickname):
        """This command will allow the Admin to update the bot's nickname"""

        await ctx.guild.me.edit(nick=new_nickname)

        await ctx.send_response(f"{ctx.author.mention} Nickname updated")

    @commands.slash_command()
    @commands.has_role('Admin')
    async def avatarupdate(self, ctx, file_or_url):
        """
        This command will allow the Admin to update the bot's avatar"""

        if isinstance(file_or_url, PngImageFile) is False and isinstance(file_or_url, JpegImageFile) is False:
            response = requests.get(
                'https://cdn.discordapp.com/attachments/823656840701149194/1009932579065053324/mg_logo.png')
            with open('tempimg', 'wb') as stream:
                stream.write(response.content)

            with open('tempimg', 'rb') as stream:
                img = stream.read()
                await self.client.user.edit(avatar=img)

            os.remove('tempimg')

        else:
            with open(file_or_url, 'rb') as f:
                data = f.read()
                await self.client.user.edit(avatar=data)

        await ctx.send_response(f"{ctx.author.mention} Avatar updated")

    @commands.slash_command(name="purge", description="Purge messages by channel, user, bot-only, attachment/embed only, url pattern")
    @commands.has_role('Admin')
    async def purge(self, ctx, channel: discord.TextChannel = None, user: discord.Member = None, bot_only: bool = False, count: int = 1, embeds: bool = False, attachments_only: bool = False, url_pattern: str = None):
        """
        This command will allow the Admin to purge messages from a channel.
        """

        if channel is None:
            channel = ctx.channel

        if count < 1:
            await ctx.send_followup(f"{ctx.author.mention} Count must be greater than 0")
            return

        if user is None:
            await ctx.send_response(f"```Purging {count} messages in {channel.name}...```", delete_after=5)
        else:
            await ctx.send_response(f"```Purging {count} messages in {channel.name} belonging to {user.display_name}...```", delete_after=5)

        async for message in channel.history(limit=count):
            time.sleep(1)
            if user is not None and message.author != user:
                continue

            if bot_only is True and message.author != self.client.user:
                continue

            if embeds is True and len(message.embeds) == 0:
                continue

            if attachments_only is True and len(message.attachments) == 0:
                continue

            if url_pattern is not None and re.search(url_pattern, message.content) is None:
                continue

            try:
                await message.delete()

            except discord.errors.Forbidden:
                await ctx.send_followup(f"{ctx.author.mention} I don't have permission to delete messages in {channel.mention}")
                return

        await ctx.send_followup(f"```{ctx.author.mention} {count} messages deleted```", delete_after=10)

    @commands.slash_command(name="lockrole", description="Restrict a role from postings or reacting in any channel.")
    @commands.has_role('Admin')
    async def lockrole(self, ctx, role: str = None):
        role = discord.utils.get(ctx.guild.roles, name=role)
        await ctx.send_response(f"```Locking out role: {role}```")

        # Create a dictionary of permissions that will be applied to all channels
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.read_messages = False

        for channel in ctx.guild.channels:
            if "totw" not in channel.name:
                await channel.set_permissions(role, overwrite=overwrite)

        await ctx.send_followup("```Done!```")

    @commands.slash_command(name="unlockrole", description="Restrict a role from postings or reacting in any channel.")
    @commands.has_role('Admin')
    async def unlockrole(self, ctx, role: str = None):
        role = discord.utils.get(ctx.guild.roles, name=role)
        await ctx.send_response(f"```Unlocking role: {role}```")

        for channel in ctx.guild.channels:
            if "totw" not in channel.name:
                await channel.set_permissions(role, overwrite=None)

        await ctx.send_followup("```Done!```")

    @commands.Cog.listener()
    async def on_message(self, message):
        # check if the message mentions user with id 123123123
        if len(message.mentions):
            if message.mentions[0].id == 218521566412013568 and message.author.id not in [self.client.user.id]:
                ganj = message.mentions[0]
                if str(ganj.status) in ['idle', 'offline', 'dnd']:
                    # create a string with the orangutan emoji and the mention
                    if random.randint(0, 3) == 1:
                        zoo = [
                            '🦧',
                            '🐵',
                            '🙈',
                            '🙉',
                            '🙊',
                            '🐱',
                            '🦝',
                            '🦊',
                            '🐺',
                            '🐶',
                            '🦁',
                            '🐯',
                            '🐴',
                            '🦄',
                            '🦓',
                            '🐮',
                            '🐷',
                            '🐭',
                            '🐹',
                            '🐰',
                            '🐻',
                            '🐼',
                            '🐨',
                            '🐸',
                            '🎅',
                            '🎅',
                            '🎅',
                            '🎅'
                        ]
                        random.shuffle(zoo)
                        response = zoo[0]
                        # send the response
                        await message.reply(response)
                    # do nothing

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.client.user.id:
            return

        if payload.channel_id == 1032057550201430087:
            channel = self.client.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if payload.emoji.name == '\u2705':
                embed = message.embeds[0]
                embed.colour = discord.Colour(0x00FF00)
                embed.title = embed.title.replace('[In progress]', '[Fixed]')
                embed.title = embed.title.replace('[Bug]', '[Fixed]')
                await message.edit(embed=embed)
            elif payload.emoji.name == '\U0001F41B':
                embed = message.embeds[0]
                embed.colour = discord.Colour(0xFFA500)
                embed.title = embed.title.replace('[Bug]', '[In progress]')
                embed.title = embed.title.replace('[Fixed]', '[In progress]')
                await message.edit(embed=embed)
            elif payload.emoji.name == '\U0001F5D1':
                try:
                    await message.delete()
                except discord.errors.NotFound:
                    pass  # Message not found in message cache.

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.channel_id == 1032057550201430087:
            channel = self.client.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            # Revert title prefix to [Bug] if all other reacts are 0. Otherwise set to the respective prefix.
            if payload.emoji.name == '\u2705':
                embed = message.embeds[0]
                embed.colour = discord.Colour(0xFF0000)
                embed.title = embed.title.replace('[Fixed]', '[Bug]')
                await message.edit(embed=embed)
            elif payload.emoji.name == '\U0001F41B':
                embed = message.embeds[0]
                embed.colour = discord.Colour(0xFF0000)
                embed.title = embed.title.replace('[In progress]', '[Bug]')
                await message.edit(embed=embed)
        

def setup(client):
    client.add_cog(ManagementModule(client))
