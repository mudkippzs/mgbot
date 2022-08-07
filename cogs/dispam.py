import asyncio
import datetime
import discord
from discord.ext import commands
import sys
import os
import pytz

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger
from utils import *


def contains_invite(message):
    contains_invite_flag = False

    return contains_invite_flag


class Dispam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_log_data = load_json_config("spamlogs.json")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.content.find("discord.gg") != -1:
            await message.delete()
            self.spam_log_data = load_json_config("spamlogs.json")
            if str(message.author.id) not in self.spam_log_data:
                self.spam_log_data[str(message.author.id)] = {"spam_count": 1}
            else:
                self.spam_log_data[str(message.author.id)]["spam_count"] += 1

            if self.spam_log_data[str(message.author.id)]["spam_count"] >= 5:
                self.spam_log_data[str(message.author.id)]['spam_count'] = 0
                await message.author.timeout_for(datetime.timedelta(hours=24), reason="Timeout for Invite spam.")
                embed = discord.Embed(title=f"{message.author.display_name} has been put in Timeout!", description=f"{message.author.mention} has been timed out for 24hrs for sending a discord server invite spam. <@&1001210793204912341>", color=0x00ff00)
                if message.author.avatar != None:
                    embed.set_thumbnail(url=message.author.avatar.url)
                embed.set_footer(text="Dispam Spam Prevention")
                await self.bot.get_channel(828931953955831838).send(embed=embed)
                await message.author.send(f"{message.author.mention} you have been timed out for invite for spamming, this may result in a ban. You have been warned {self.spam_log_data[str(message.author.id)]['spam_count']} times.")
            else:
                await message.author.send(f"{message.author.mention} you have been warned for spamming. You have been warned {self.spam_log_data[str(message.author.id)]['spam_count']} times.")
            
            write_json_config("spamlogs.json", self.spam_log_data)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        if after.content.find("discord.gg") != -1:
            await message.delete()
            self.spam_log_data = load_json_config("spamlogs.json")
            if str(after.author.id) not in self.spam_log_data:
                self.spam_log_data[after.author.id] = {"spam_count": 1}
            else:
                self.spam_log_data[after.author.id]["spam_count"] += 1


            if self.spam_log_data[str(message.author.id)]["spam_count"] >= 5:
                self.spam_log_data[str(message.author.id)]['spam_count'] = 0
                await message.author.timeout_for(datetime.timedelta(hours=24), reason="Timeout for Invite spam.")
                embed = discord.Embed(title=f"{message.author.display_name} has been put in Timeout!", description=f"{message.author.mention} has been timed out for 24hrs for sending a discord server invite spam. <@&1001210793204912341>", color=0x00ff00)
                if message.author.avatar != None:
                    embed.set_thumbnail(url=message.author.avatar.url)
                embed.set_footer(text="Dispam Spam Prevention")
                await self.bot.get_channel(828931953955831838).send(embed=embed)
                await message.author.send(f"{message.author.mention} you have been timed out for invite for spamming, this may result in a ban. You have been warned {self.spam_log_data[str(message.author.id)]['spam_count']} times.")
            else:
                await message.author.send(f"{message.author.mention} you have been warned for spamming. You have been warned {self.spam_log_data[str(message.author.id)]['spam_count']} times.")
            
            write_json_config("spamlogs.json", self.spam_log_data)

    @commands.command(name='spam', help='Check the spam count of a user.')
    @commands.has_role('Wielder of the flame of Anor')
    async def spam(self, ctx, user: discord.Member):
        if user.id not in self.spam_log_data:
            await ctx.send(f"{user.mention} has not been flagged for spam.", delete_after=10)
        else:
            await ctx.send(f"{user.mention} has been warned ```{self.spam_log_data[str(user.id)]['spam_count']} times.``` for spam.", delete_after=10)

    @commands.command(name='spam_reset', help='Recent a users spam violations.')
    @commands.has_role('Wielder of the flame of Anor')
    async def spam_reset(self, ctx, user: discord.Member):
        self.spam_log_data = load_json_config("spamlogs.json")

        if user.id not in self.spam_log_data:
            await ctx.send(f"{user.mention} has not been flagged for spam.", delete_after=10)
        else:
            self.spam_log_data[str(user.id)]['spam_count'] = 0
            write_json_config("spamlogs.json", self.spam_log_data)
            await ctx.send(f"{user.mention} has been reset.", delete_after=10)

def setup(client):
    client.add_cog(Dispam(client))
