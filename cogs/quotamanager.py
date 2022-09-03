import asyncio
import datetime
import discord
from discord.ext import commands
import sys
import os
import pytz

import copy

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger
from jarvis import QUOTA_LIMIT
from utils import *


class QuotaManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="quota", description="Check your BOT quota.")
    async def quota(self, ctx, user: discord.Member = None):
        """Get info about a user"""
        if user == None:
            user = ctx.author

        quotas = load_json_config("quotas.json")

        for q in quotas:
            if str(user.id) not in quotas[q]:
                quotas[q][str(user.id)] = QUOTA_LIMIT

        embed = discord.Embed(title=f"{user.display_name}'s Bot usage quota remaining...",
                              description=f"Bot quota is currently {QUOTA_LIMIT} per day. It refreshes at 00:05 GMT+1.", color=0x00ff00)

        for q in quotas:
            if str(user.id) not in quotas[q]:
                quotas[q][str(user.id)] = QUOTA_LIMIT
            embed.add_field(name=f"{q}",
                            value=f"```{quotas[q][str(user.id)]}```", inline=True)

        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send_response(embed=embed, delete_after=15)

    @commands.slash_command(name='addquota', description='Set a user\'s bot quota.')
    async def setquota(self, ctx, user: discord.Member = None, value=0, bot=None):

        def add_quota(member_id, value, quota_list):
            quota_list[str(member_id)] += value
            return quota_list

        quotas = load_json_config("quotas.json")

        if user == None:
            user == ctx.author

        if bot == None:
            bot = ["jarvis", "emgee"]
        else:
            bot = [bot, ]

        for b in bot:
            quotas[b][str(user.id)] += int(value)

        write_json_config("quotas.json", quotas)
        await ctx.send_response(f"```Added {value} to {str(user)}'s quota.```", delete_after=15)

    @commands.slash_command(name='resetquotas', description='Reset AI bot quotas for all members. Optional: specify bot.')
    @commands.has_role('Admin')
    async def resetquotas(self, ctx, user: discord.Member = None, bot=None):

        quotas = load_json_config("quotas.json")

        if bot == None:
            bot = ["jarvis", "emgee"]
        else:
            bot = [bot, ]

        member_count = ctx.guild.member_count

        if user == None:
            for b in bot:
                for member in ctx.guild.members:
                    user = member
                    quotas[b][str(user.id)] = QUOTA_LIMIT
        else:
            for b in bot:
                quotas[b][str(user.id)] = QUOTA_LIMIT

        write_json_config("quotas.json", quotas)
        await ctx.send_response(f"```Reset ({member_count}) member's bot quotas.```", delete_after=15)


    @commands.slash_command(name='cleanupquotas', description='Clean up AI bot quotas list by removing ex-members.')
    @commands.has_role('Admin')
    async def cleanupquotas(self, ctx):

        quotas = load_json_config("quotas.json")
        bots = [bot for bot in quotas.keys()]
        current_members = [str(member.id) for member in ctx.message.guild.members]
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
        await ctx.send_response(f"```Cleaned up ({del_count}) ex-members from internal cache.```", delete_after=15)


def setup(bot):
    bot.add_cog(QuotaManager(bot))
